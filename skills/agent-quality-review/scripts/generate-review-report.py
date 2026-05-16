#!/usr/bin/env python3
"""Validate Agent eval CSVs and generate an English Markdown review report."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from statistics import mean
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
YES_VALUES = {"1", "true", "yes", "y"}
NO_VALUES = {"0", "false", "no", "n"}
BOOL_COLUMNS = {
    "pass1",
    "budget_within_success",
    "over_budget_success",
    "human_intervention",
    "session_success",
    "budget_within_session_success",
    "over_budget_session_success",
    "invalid_back_and_forth",
    "critical_error",
    "rework_required",
}
BASE_RESULT_COLUMNS = {
    "case_id",
    "task_name",
    "layer",
    "weight",
    "risk_tier",
    "critical_error",
    "rework_required",
    "duration_seconds",
    "cost_usd",
    "tool_calls",
    "evaluator",
    "trace_id",
}
AUTONOMOUS_RESULT_COLUMNS = {
    "pass1",
    "budget_within_success",
    "over_budget_success",
    "human_intervention",
}
COLLABORATIVE_RESULT_COLUMNS = {
    "session_success",
    "budget_within_session_success",
    "over_budget_session_success",
    "invalid_back_and_forth",
    "session_turns",
}
REQUIRED_RESULT_COLUMNS = BASE_RESULT_COLUMNS | AUTONOMOUS_RESULT_COLUMNS
REQUIRED_SCORECARD_COLUMNS = {"dimension", "score", "evidence"}
REQUIRED_DEPENDENCY_COLUMNS = {
    "dependency_name",
    "type",
    "version",
    "purpose",
    "permission_scope",
    "data_touched",
    "sensitive_data",
    "data_retention",
    "failure_impact",
    "fallback_path",
    "alternative",
    "regression_on_change",
    "owner",
}
EXPECTED_DIMENSIONS = {
    "Real task completion",
    "Reliability and stability",
    "Real problem value",
    "Error handling and boundary",
    "Cost and latency",
    "Engineering robustness",
    "User trust",
    "Security and permissions",
}
DIMENSION_FLOORS = {
    "Low": {
        "Error handling and boundary": 1,
        "Engineering robustness": 1,
        "Reliability and stability": 1,
        "Security and permissions": 1,
    },
    "Medium": {
        "Error handling and boundary": 2,
        "Engineering robustness": 2,
        "Reliability and stability": 2,
        "Security and permissions": 2,
    },
    "High": {
        "Error handling and boundary": 3,
        "Engineering robustness": 2,
        "Reliability and stability": 2,
        "Security and permissions": 3,
    },
}


class CsvData(NamedTuple):
    rows: list[dict[str, str]]
    fields: list[str]


class ValidationIssue(NamedTuple):
    level: str
    source: str
    message: str


class MetricConfig(NamedTuple):
    is_collaborative: bool
    primary_field: str
    budget_field: str
    over_budget_field: str
    intervention_field: str
    primary_label: str
    budget_label: str
    over_budget_label: str
    intervention_label: str
    required_fields: set[str]


def normalize_tier(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("h"):
        return "High"
    if value.startswith("m"):
        return "Medium"
    return "Low"


def is_collaborative_agent(agent_type: str) -> bool:
    normalized = agent_type.strip().lower()
    return any(token in normalized for token in ("collaborative", "multi-turn", "session", "协作", "多轮"))


def metric_config(agent_type: str = "Autonomous completion") -> MetricConfig:
    if is_collaborative_agent(agent_type):
        return MetricConfig(
            True,
            "session_success",
            "budget_within_session_success",
            "over_budget_session_success",
            "invalid_back_and_forth",
            "Session success",
            "Budgeted session success",
            "Over-budget session success",
            "Invalid back-and-forth rate",
            COLLABORATIVE_RESULT_COLUMNS,
        )
    return MetricConfig(
        False,
        "pass1",
        "budget_within_success",
        "over_budget_success",
        "human_intervention",
        "pass@1",
        "Budgeted success",
        "Over-budget success",
        "Intervention rate",
        AUTONOMOUS_RESULT_COLUMNS,
    )


def read_csv(path: Path) -> CsvData:
    if not path.exists():
        raise FileNotFoundError(f"missing file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return CsvData(list(reader), list(reader.fieldnames or []))


def is_yes(value: str | None) -> bool:
    return str(value or "").strip().lower() in YES_VALUES


def is_bool_literal(value: str | None) -> bool:
    normalized = str(value or "").strip().lower()
    return normalized in YES_VALUES or normalized in NO_VALUES


def as_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(str(value or "").strip())
    except ValueError:
        return default


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    phat = successes / total
    denominator = 1 + z * z / total
    center = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return (center - margin) / denominator, (center + margin) / denominator


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = math.ceil((pct / 100) * len(ordered)) - 1
    return ordered[max(0, min(index, len(ordered) - 1))]


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def fmt_money(value: float) -> str:
    return f"${value:.2f}"


def metric_counts(rows: list[dict[str, str]], config: MetricConfig | None = None) -> dict[str, int]:
    config = config or metric_config()
    return {
        "n": len(rows),
        "pass1": sum(is_yes(row.get(config.primary_field)) for row in rows),
        "budget_success": sum(is_yes(row.get(config.budget_field)) for row in rows),
        "over_budget_success": sum(is_yes(row.get(config.over_budget_field)) for row in rows),
        "human_intervention": sum(is_yes(row.get(config.intervention_field)) for row in rows),
        "critical_error": sum(is_yes(row.get("critical_error")) for row in rows),
        "rework": sum(is_yes(row.get("rework_required")) for row in rows),
    }


def stage_thresholds(target_stage: str) -> tuple[float | None, float | None]:
    stage = target_stage.lower().replace(" ", "-")
    if "high-risk-production" in stage:
        return 0.95, None
    if "production" in stage:
        return 0.85, 0.15
    if "pilot" in stage:
        return 0.70, 0.30
    if "demo" in stage or "internal" in stage:
        return 0.50, None
    return None, None


def minimum_sample_size(risk_tier: str) -> int:
    tier = normalize_tier(risk_tier)
    if tier == "High":
        return 300
    if tier == "Medium":
        return 150
    return 50


def schema_issues(fields: list[str], required: set[str], source: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    missing = sorted(required.difference(fields))
    extra = sorted(set(fields).difference(required))
    if missing:
        issues.append(ValidationIssue("error", source, "missing required columns: " + ", ".join(missing)))
    if extra:
        issues.append(ValidationIssue("info", source, "extension columns present: " + ", ".join(extra)))
    return issues


def validate_results(data: CsvData, agent_type: str = "Autonomous completion") -> list[ValidationIssue]:
    config = metric_config(agent_type)
    required_columns = BASE_RESULT_COLUMNS | config.required_fields
    issues = schema_issues(data.fields, required_columns, "eval-results")
    if not data.rows:
        issues.append(ValidationIssue("error", "eval-results", "no evaluation result rows"))
        return issues
    seen: set[str] = set()
    for index, row in enumerate(data.rows, start=2):
        source = f"eval-results:{index}"
        case_id = row.get("case_id", "").strip()
        if not case_id:
            issues.append(ValidationIssue("error", source, "case_id is empty"))
        elif case_id in seen:
            issues.append(ValidationIssue("error", source, f"duplicate case_id: {case_id}"))
        seen.add(case_id)
        bool_columns = {"critical_error", "rework_required", config.primary_field, config.budget_field, config.over_budget_field, config.intervention_field}
        for column in bool_columns.intersection(data.fields):
            if not is_bool_literal(row.get(column)):
                issues.append(ValidationIssue("error", source, f"{column} must be 1/0 or yes/no"))
        numeric_columns = ["weight", "duration_seconds", "cost_usd", "tool_calls"]
        if config.is_collaborative:
            numeric_columns.append("session_turns")
        for column in numeric_columns:
            if as_float(row.get(column), default=-1) < 0:
                issues.append(ValidationIssue("error", source, f"{column} must be a non-negative number"))
        if is_yes(row.get(config.budget_field)) and not is_yes(row.get(config.primary_field)):
            issues.append(ValidationIssue("error", source, f"{config.budget_label} cannot occur when {config.primary_label} failed"))
        if is_yes(row.get(config.budget_field)) and is_yes(row.get(config.over_budget_field)):
            issues.append(ValidationIssue("error", source, f"{config.budget_label} and {config.over_budget_label} cannot both be true"))
        if is_yes(row.get("critical_error")) and is_yes(row.get(config.budget_field)):
            issues.append(ValidationIssue("error", source, f"critical-error cases cannot be counted as {config.budget_label}"))
        if not row.get("trace_id", "").strip():
            issues.append(ValidationIssue("warning", source, "missing trace_id reduces auditability"))
    return issues


def validate_scorecard(data: CsvData, risk_tier: str) -> list[ValidationIssue]:
    issues = schema_issues(data.fields, REQUIRED_SCORECARD_COLUMNS, "scorecard")
    dimensions = {row.get("dimension", "").strip() for row in data.rows}
    missing = sorted(EXPECTED_DIMENSIONS.difference(dimensions))
    if missing:
        issues.append(ValidationIssue("error", "scorecard", "missing dimensions: " + ", ".join(missing)))
    for index, row in enumerate(data.rows, start=2):
        source = f"scorecard:{index}"
        score = as_float(row.get("score"), default=-1)
        if score < 0 or score > 3:
            issues.append(ValidationIssue("error", source, "score must be between 0 and 3"))
        if score >= 2 and not row.get("evidence", "").strip():
            issues.append(ValidationIssue("warning", source, "high-scoring dimension lacks evidence"))
    return issues


def validate_dependencies(data: CsvData, risk_tier: str) -> list[ValidationIssue]:
    issues = schema_issues(data.fields, REQUIRED_DEPENDENCY_COLUMNS, "external-dependencies")
    if not data.rows:
        issues.append(ValidationIssue("warning", "external-dependencies", "dependency register is empty"))
        return issues
    for index, row in enumerate(data.rows, start=2):
        source = f"external-dependencies:{index}"
        if not row.get("dependency_name", "").strip():
            issues.append(ValidationIssue("error", source, "dependency_name is empty"))
        if not row.get("fallback_path", "").strip():
            issues.append(ValidationIssue("warning", source, "missing fallback or human handoff path"))
        if not is_bool_literal(row.get("sensitive_data")):
            issues.append(ValidationIssue("warning", source, "sensitive_data should be yes/no"))
        if not is_bool_literal(row.get("regression_on_change")):
            issues.append(ValidationIssue("warning", source, "regression_on_change should be yes/no"))
        if normalize_tier(risk_tier) == "High" and not row.get("owner", "").strip():
            issues.append(ValidationIssue("error", source, "high-risk reviews require an owner for each dependency"))
    return issues


def dimension_floor_issues(scorecard: list[dict[str, str]], risk_tier: str) -> list[str]:
    issues: list[str] = []
    for dimension, floor in DIMENSION_FLOORS.get(normalize_tier(risk_tier), {}).items():
        row = next((item for item in scorecard if item.get("dimension", "").strip() == dimension), None)
        if not row:
            issues.append(f"missing floor dimension: {dimension}")
        elif as_float(row.get("score")) < floor:
            issues.append(f"{dimension} is below the {normalize_tier(risk_tier)} floor of {floor}")
    return issues


def gate_result(target_stage: str, risk_tier: str, counts: dict[str, int], budget_lower: float, intervention_upper: float, floor_issues: list[str], agent_type: str = "Autonomous completion") -> tuple[str, list[str]]:
    reasons: list[str] = []
    budget_threshold, intervention_threshold = stage_thresholds(target_stage)
    config = metric_config(agent_type)
    stage = target_stage.lower()
    if "demo" not in stage and "internal" not in stage:
        required = minimum_sample_size(risk_tier)
        if counts["n"] < required:
            reasons.append(f"sample size {counts['n']} is below {normalize_tier(risk_tier)} minimum {required}")
    if budget_threshold is not None:
        if "demo" in stage or "internal" in stage:
            point = counts["budget_success"] / counts["n"] if counts["n"] else 0
            if point < budget_threshold:
                reasons.append(f"{config.budget_label} point estimate is below {fmt_pct(budget_threshold)}")
        elif budget_lower < budget_threshold:
            reasons.append(f"{config.budget_label} Wilson lower bound is below {fmt_pct(budget_threshold)}")
    if intervention_threshold is not None and intervention_upper > intervention_threshold:
        reasons.append(f"{config.intervention_label} Wilson upper bound is above {fmt_pct(intervention_threshold)}")
    if counts["critical_error"] > 0:
        reasons.append("critical errors are present")
    reasons.extend(floor_issues)
    if reasons:
        return "Fail / insufficient evidence", reasons
    return "Pass", ["Gate metrics satisfy the target stage."]


def group_by_column(rows: list[dict[str, str]], column: str) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = row.get(column, "").strip() or f"missing {column}"
        groups.setdefault(key, []).append(row)
    return groups


def validation_summary(issues: list[ValidationIssue]) -> tuple[int, int, int]:
    return (
        sum(issue.level == "error" for issue in issues),
        sum(issue.level == "warning" for issue in issues),
        sum(issue.level == "info" for issue in issues),
    )


def load_inputs(args: argparse.Namespace) -> tuple[CsvData, CsvData, CsvData]:
    return read_csv(Path(args.results)), read_csv(Path(args.scorecard)), read_csv(Path(args.dependencies))


def build_summary(args: argparse.Namespace, results_data: CsvData, scorecard_data: CsvData, dependency_data: CsvData, issues: list[ValidationIssue]) -> dict[str, object]:
    rows = results_data.rows
    config = metric_config(args.agent_type)
    counts = metric_counts(rows, config)
    n = counts["n"]
    budget_lower, budget_upper = wilson_interval(counts["budget_success"], n)
    intervention_lower, intervention_upper = wilson_interval(counts["human_intervention"], n)
    critical_lower, critical_upper = wilson_interval(counts["critical_error"], n)
    floor_issues = dimension_floor_issues(scorecard_data.rows, args.risk_tier)
    gate, gate_reasons = gate_result(args.target_stage, args.risk_tier, counts, budget_lower, intervention_upper, floor_issues, args.agent_type)
    total_score = sum(as_float(row.get("score")) for row in scorecard_data.rows)
    errors, warnings, infos = validation_summary(issues)
    durations = [as_float(row.get("duration_seconds")) for row in rows]
    costs = [as_float(row.get("cost_usd")) for row in rows]
    tool_calls = [as_float(row.get("tool_calls")) for row in rows]
    return {
        "project_name": args.project_name,
        "target_stage": args.target_stage,
        "risk_tier": normalize_tier(args.risk_tier),
        "agent_type": args.agent_type,
        "metric_labels": {
            "primary": config.primary_label,
            "budget": config.budget_label,
            "over_budget": config.over_budget_label,
            "intervention": config.intervention_label,
        },
        "baseline": args.baseline,
        "counts": counts,
        "intervals": {
            "budget_success": [budget_lower, budget_upper],
            "human_intervention": [intervention_lower, intervention_upper],
            "critical_error": [critical_lower, critical_upper],
        },
        "budget": {
            "avg_duration_seconds": mean(durations) if durations else 0,
            "p95_duration_seconds": percentile(durations, 95),
            "avg_cost_usd": mean(costs) if costs else 0,
            "p95_cost_usd": percentile(costs, 95),
            "avg_tool_calls": mean(tool_calls) if tool_calls else 0,
            "p95_tool_calls": percentile(tool_calls, 95),
        },
        "score": {"total": total_score, "dimension_floor_issues": floor_issues},
        "gate": {"result": gate, "reasons": gate_reasons},
        "validation": {"errors": errors, "warnings": warnings, "infos": infos},
        "dependency_count": len(dependency_data.rows),
    }


def render_report(args: argparse.Namespace, results: list[dict[str, str]], scorecard: list[dict[str, str]], dependencies: list[dict[str, str]], issues: list[ValidationIssue], summary: dict[str, object]) -> str:
    counts = summary["counts"]
    intervals = summary["intervals"]
    budget = summary["budget"]
    gate = summary["gate"]
    validation = summary["validation"]
    score = summary["score"]
    labels = summary["metric_labels"]
    config = metric_config(args.agent_type)
    n = counts["n"]
    lines: list[str] = []
    lines.append(f"# {args.project_name} Agent Review Report")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- **Target stage:** {args.target_stage}")
    lines.append(f"- **Risk tier:** {normalize_tier(args.risk_tier)}")
    lines.append(f"- **Agent type:** {args.agent_type}")
    lines.append(f"- **Baseline alternative:** {args.baseline}")
    lines.append(f"- **Gate conclusion:** {gate['result']}")
    lines.append("")
    lines.append("## Data Validation")
    lines.append("")
    lines.append(f"- Errors: {validation['errors']}")
    lines.append(f"- Warnings: {validation['warnings']}")
    lines.append(f"- Info: {validation['infos']}")
    if issues:
        lines.append("")
        lines.append("| Level | Source | Message |")
        lines.append("| --- | --- | --- |")
        for issue in issues[:30]:
            lines.append(f"| {issue.level} | {issue.source} | {issue.message} |")
    lines.append("")
    lines.append("## Key Metrics")
    lines.append("")
    lines.append("| Metric | Point estimate | Wilson 95% interval |")
    lines.append("| --- | --- | --- |")
    pass_interval = wilson_interval(counts["pass1"], n)
    lines.append(f"| {labels['primary']} | {fmt_pct(counts['pass1'] / n if n else 0)} | {fmt_pct(pass_interval[0])}-{fmt_pct(pass_interval[1])} |")
    lines.append(f"| {labels['budget']} | {fmt_pct(counts['budget_success'] / n if n else 0)} | {fmt_pct(intervals['budget_success'][0])}-{fmt_pct(intervals['budget_success'][1])} |")
    lines.append(f"| {labels['over_budget']} | {fmt_pct(counts['over_budget_success'] / n if n else 0)} | - |")
    lines.append(f"| {labels['intervention']} | {fmt_pct(counts['human_intervention'] / n if n else 0)} | {fmt_pct(intervals['human_intervention'][0])}-{fmt_pct(intervals['human_intervention'][1])} |")
    lines.append(f"| Critical error rate | {fmt_pct(counts['critical_error'] / n if n else 0)} | {fmt_pct(intervals['critical_error'][0])}-{fmt_pct(intervals['critical_error'][1])} |")
    lines.append(f"| User rework rate | {fmt_pct(counts['rework'] / n if n else 0)} | - |")
    lines.append("")
    lines.append("## Budget Use")
    lines.append("")
    lines.append(f"- Average duration: {budget['avg_duration_seconds']:.0f} seconds")
    lines.append(f"- P95 duration: {budget['p95_duration_seconds']:.0f} seconds")
    lines.append(f"- Average cost: {fmt_money(budget['avg_cost_usd'])}")
    lines.append(f"- P95 cost: {fmt_money(budget['p95_cost_usd'])}")
    lines.append(f"- Average tool calls: {budget['avg_tool_calls']:.1f}")
    lines.append(f"- P95 tool calls: {budget['p95_tool_calls']:.0f}")
    lines.append("")
    lines.append("## Key Slices")
    lines.append("")
    lines.append(f"| Slice | Sample size | {labels['budget']} | {labels['intervention']} | Critical error | P95 duration |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for layer, group in group_by_column(results, "layer").items():
        group_counts = metric_counts(group, config)
        group_n = group_counts["n"]
        group_durations = [as_float(row.get("duration_seconds")) for row in group]
        lines.append(f"| {layer} | {group_n} | {fmt_pct(group_counts['budget_success'] / group_n)} | {fmt_pct(group_counts['human_intervention'] / group_n)} | {fmt_pct(group_counts['critical_error'] / group_n)} | {percentile(group_durations, 95):.0f}s |")
    if results and "industry" in results[0]:
        lines.append("")
        lines.append("## Industry Distribution")
        lines.append("")
        lines.append(f"| Industry | Sample size | {labels['budget']} | {labels['intervention']} | Critical error |")
        lines.append("| --- | --- | --- | --- | --- |")
        for industry, group in group_by_column(results, "industry").items():
            group_counts = metric_counts(group, config)
            group_n = group_counts["n"]
            lines.append(f"| {industry} | {group_n} | {fmt_pct(group_counts['budget_success'] / group_n)} | {fmt_pct(group_counts['human_intervention'] / group_n)} | {fmt_pct(group_counts['critical_error'] / group_n)} |")
    lines.append("")
    lines.append("## Scoring")
    lines.append("")
    lines.append("| Dimension | Score | Evidence |")
    lines.append("| --- | --- | --- |")
    for row in scorecard:
        lines.append(f"| {row.get('dimension', '')} | {row.get('score', '')} | {row.get('evidence', '')} |")
    lines.append("")
    lines.append(f"**Total score:** {score['total']:g} / 24")
    if score["dimension_floor_issues"]:
        lines.append("")
        lines.append("Dimension floor issues:")
        for issue in score["dimension_floor_issues"]:
            lines.append(f"- {issue}")
    lines.append("")
    lines.append("## External Dependencies")
    lines.append("")
    lines.append("| Dependency | Type | Version | Data touched | Fallback path | Regression on change |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in dependencies:
        lines.append(f"| {row.get('dependency_name', '')} | {row.get('type', '')} | {row.get('version', '')} | {row.get('data_touched', '')} | {row.get('fallback_path', '')} | {row.get('regression_on_change', '')} |")
    lines.append("")
    lines.append("## Gate Notes")
    lines.append("")
    for reason in gate["reasons"]:
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    if gate["result"] == "Pass":
        lines.append("- Before entering the next stage, complete formal sign-off and monitoring setup.")
    else:
        lines.append("- Fix failed metrics, increase evidence, and re-run core evals.")
    lines.append("- Archive this report together with raw eval results, scorecard, dependency register, and trace index.")
    return "\n".join(lines) + "\n"


def resolve_paths(args: argparse.Namespace) -> None:
    if args.project_dir:
        project_dir = Path(args.project_dir)
        args.results = args.results or str(project_dir / "eval-results.csv")
        args.scorecard = args.scorecard or str(project_dir / "scorecard.csv")
        args.dependencies = args.dependencies or str(project_dir / "external-dependencies.csv")
        args.output = args.output or str(project_dir / "review-report.md")
    else:
        args.results = args.results or str(ROOT / "assets" / "examples" / "sample-eval-results.csv")
        args.scorecard = args.scorecard or str(ROOT / "assets" / "examples" / "sample-scorecard.csv")
        args.dependencies = args.dependencies or str(ROOT / "assets" / "examples" / "sample-external-dependencies.csv")
        args.output = args.output or str(ROOT / "outputs" / "sample-review-report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Agent eval CSVs and generate a review report.")
    parser.add_argument("--project-dir")
    parser.add_argument("--results")
    parser.add_argument("--scorecard")
    parser.add_argument("--dependencies")
    parser.add_argument("--output")
    parser.add_argument("--summary-json")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--strict-gate", action="store_true")
    parser.add_argument("--project-name", default="Internal Project Risk Summary")
    parser.add_argument("--risk-tier", default="Medium")
    parser.add_argument("--target-stage", default="Internal demo")
    parser.add_argument("--agent-type", default="Autonomous completion")
    parser.add_argument("--baseline", default="Project manager manually reads materials and writes the summary; average time is about 35 minutes.")
    args = parser.parse_args()
    resolve_paths(args)
    try:
        results_data, scorecard_data, dependency_data = load_inputs(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    issues = validate_results(results_data, args.agent_type) + validate_scorecard(scorecard_data, args.risk_tier) + validate_dependencies(dependency_data, args.risk_tier)
    summary = build_summary(args, results_data, scorecard_data, dependency_data, issues)
    if args.summary_json:
        output_path = Path(args.summary_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    errors, warnings, infos = validation_summary(issues)
    if args.check_only:
        print(f"validation: {errors} errors, {warnings} warnings, {infos} infos")
        print(f"gate: {summary['gate']['result']}")
        for reason in summary["gate"]["reasons"]:
            print(f"- {reason}")
    else:
        report = render_report(args, results_data.rows, scorecard_data.rows, dependency_data.rows, issues, summary)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"wrote {output_path}")
    if errors:
        return 2
    if args.strict_gate and summary["gate"]["result"] != "Pass":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
