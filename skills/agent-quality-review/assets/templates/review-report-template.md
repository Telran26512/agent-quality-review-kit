# Agent Project Review Report Template

## Project Overview

**Project name:**
**Review date:**
**Review version:**
**Target users:**
**Core task:**
**Agent type:** Autonomous completion / Collaborative multi-turn
**Risk tier:** Low / Medium / High
**Baseline alternative:**
**Target stage:** Proof of concept / Internal demo / Limited pilot / Production-ready / High-risk production
**Current conclusion:** Pass / Conditional pass / Fail / Insufficient evidence

## Roles and Sign-off

| Role | Person or team | Participated? | Key confirmation |
| --- | --- | --- | --- |
| Business owner |  |  |  |
| Agent owner / product owner |  |  |  |
| Evaluation operator |  |  |  |
| Independent reviewer |  |  |  |
| Security owner |  |  |  |
| Data / compliance owner |  |  |  |
| Engineering / operations owner |  |  |  |
| Launch approver |  |  |  |

## Execution Budget

- Budgets defined before evaluation:
- Missing budgets:
- Over-budget success tracked separately:

## Evaluation Validity

- Sample size:
- Meets risk-tier requirement:
- Confidence intervals reported:
- Interval method: Wilson / bootstrap / other
- Reviewer count and agreement:
- Gate metrics from full human acceptance set:

## Task Weights

- Slicing method:
- Weights defined before evaluation:
- Key slices:
- All key slices pass:

## Key Metrics

Autonomous Agents use budgeted pass@1. Collaborative Agents use budgeted session success rate.

| Metric | Point estimate | 95% interval | Threshold | Pass? |
| --- | --- | --- | --- | --- |
| pass@1 / session success |  |  |  |  |
| Budgeted pass@1 / budgeted session success |  |  |  |  |
| Over-budget success rate |  |  |  |  |
| Intervention rate / invalid back-and-forth rate |  |  |  |  |
| End-to-end completion rate |  |  |  |  |
| User rework rate |  |  |  |  |
| Critical error rate |  |  |  |  |
| Average duration |  |  |  |  |
| P95 duration |  |  |  |  |
| Average cost |  |  |  |  |
| P95 cost |  |  |  |  |
| Average tool calls |  |  |  |  |
| P95 tool calls |  |  |  |  |

## Key Slice Metrics

| Slice | Weight | Sample size | Budgeted success | Intervention / invalid turns | Critical error | P95 time / cost | Pass? |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## Net Value vs Baseline

Mark each dimension as better / same / worse. Worse items must explain why the regression is acceptable.

| Dimension | Result | Evidence | Is regression acceptable? |
| --- | --- | --- | --- |
| Quality |  |  |  |
| Budgeted success |  |  |  |
| Cost |  |  |  |
| Latency |  |  |  |
| User time saved |  |  |  |
| Reliability / critical error rate |  |  |  |

**Overall conclusion:** positive / unclear / negative

## Scoring

| Dimension | Score | Evidence |
| --- | --- | --- |
| Real task completion |  |  |
| Reliability and stability |  |  |
| Real problem value |  |  |
| Error handling and boundary |  |  |
| Cost and latency |  |  |
| Engineering robustness |  |  |
| User trust |  |  |
| Security and permissions |  |  |

**Total score:** / 24

## Gate Check

- Target stage:
- All gates pass:
- Failed gates:
- Allowed to enter next stage:
- High-risk thresholds confirmed in advance by business, security, and data / compliance owners:

## Security Check

- Least privilege:
- High-risk tool allowlist and parameter validation:
- Preview, confirmation, and audit for side-effect actions:
- External content treated as untrusted:
- Sensitive data and secrets protected:
- Tenant isolation:
- Logs and traces redacted:
- Retention period defined:
- Full trace access controlled:
- High-risk audit records tamper-resistant:
- External dependency register complete:
- Vendor, model, or API changes trigger regression evaluation:
- Plugin, SDK, package, or browser extension version drift controlled:
- Third-party data boundaries defined:
- External dependency outage fallback or human handoff:
- Rate limits, circuit breakers, rollback, or human handoff:

## Hard Failures

- Any hard failures:
- Details:

## Main Issues

1.
2.
3.

## Next Steps

1.
2.
3.
