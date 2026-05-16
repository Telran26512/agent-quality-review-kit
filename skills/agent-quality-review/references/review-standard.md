## How to Judge Whether an Agent Project Is High Quality, Truly Usable, and Solves a Real Need

**Document metadata**

- **Version:** v1.5
- **Owner:** Review kit maintainer, assigned by the adopting team
- **Last review date:** 2026-05-16
- **Review cadence:** Quarterly, or immediately when evaluation methods, model capabilities, risk criteria, launch gates, or security requirements materially change
- **Review kit entry point:** See `README.md`
- **Version history:** See `VERSION.md`
- **Release specification:** See `RELEASE.md`
- **Fillable templates:** `templates/eval-case-template.md`, `templates/review-report-template.md`, `templates/scorecard.csv`, `templates/wilson-calculator.csv`, `templates/external-dependency-register-template.md`
- **Automation and examples:** Report generation script in `scripts/generate-review-report.py`; sample data in `examples/`; industry benchmark in `benchmarks/industry-benchmark-v1/`
- **Appendix:** Templates and examples are in `agent-skill-appendix.md`. If the appendix conflicts with this document, this document wins.
- **Authority note:** "0. One-Page Summary" is navigation only. If it conflicts with the body, follow the body.

This standard evaluates whether an Agent project has moved from "demo-able" to "usable by real users over time." It is not primarily about model capability or demo polish. It is about whether the Agent creates stable value under real tasks, real constraints, and real failure modes.

### 0. One-Page Summary

Use these seven steps to start a review. Details are in the referenced sections.

1. **Classify the Agent** - Determine whether it is autonomous completion or collaborative / multi-turn. Use budgeted pass@1 for the former and session-level metrics for the latter.
2. **Set the risk tier** - Low, medium, or high risk based on failure cost. Sample size, thresholds, and gates depend on this.
3. **Set budgets and boundaries** - Define time, cost, tool calls, retries, side effects, and human confirmation points before evaluation.
4. **Build tasks and baseline** - Use real tasks, define the best non-Agent alternative, and set task weights by frequency, value, risk, and core workflow.
5. **Run evaluation** - Use sufficient samples by tier and key slice. Blind-test and record full traces. Gate metrics must come from the full human acceptance set.
6. **Apply gates** - For pilot and production, use Wilson lower bounds for positive metrics and upper bounds for negative metrics. Any hard failure, dimension floor failure, key slice failure, or unmitigated critical error blocks launch.
7. **Issue conclusion** - Choose one stage: proof of concept, internal demo, limited pilot, production-ready, or not recommended. Total score is a quality thermometer; gates decide stage readiness.

**Quick checklist**

| Check | Pass? |
| --- | --- |
| Agent type is stated: autonomous completion / collaborative multi-turn |  |
| Target users, core workflow, and success definition are stated |  |
| Risk tier matches failure cost |  |
| High-risk thresholds are confirmed in advance by business, security, and data / compliance owners |  |
| Baseline alternative is defined and net value is compared by dimension |  |
| Execution budget is defined: time, cost, tool calls, retries, side effects, confirmation points |  |
| Sample size meets risk-tier and key-slice requirements |  |
| Task weights are set before evaluation and key slices are reported separately |  |
| Gate metrics come from the full human acceptance set, not only automated regression tasks |  |
| Pilot and production gates use Wilson 95% bounds |  |
| No hard failure, unmitigated critical error, or key-slice failure exists |  |
| Security checks cover permissions, data, logs, audit, external dependencies, and rollback |  |
| Stage conclusion and next-stage issue list are explicit |  |

Evaluation intensity scales by tier: low risk uses the lightweight path, medium risk uses the standard path, and high risk uses the full process.

### 1. Evaluation Principles

1. **Use real tasks**
   - Do not prove quality with cherry-picked demos.
   - Use real user tasks, historical tickets, real files, and real context.
   - Include incomplete information, non-standard paths, noisy inputs, and normal production tool failures.

2. **Measure first-attempt success**
   - Agent value comes from doing the job correctly on the first user submission.
   - Three success metrics must be kept distinct:
     - **pass@1:** user submits once and the Agent delivers a usable result once.
     - **budgeted pass@1:** pass@1 that also stays within the task budget for time, cost, tool calls, retries, and other limits. All thresholds in this standard use budgeted pass@1.
     - **over-budget success:** output is usable but exceeds budget. Record it for diagnosis, but do not count it as passing a gate.
   - Agent retries inside one task are allowed if they stay within the max autonomous retry budget. User resubmission, user correction, or manual repair across tasks counts as failure or intervention.
   - pass@k may be recorded, but it cannot replace budgeted pass@1.
   - pass@1 defaults to autonomous completion Agents. Collaborative / multi-turn Agents should use budgeted session success rate and related session-level metrics.

3. **Judge the delivered result**
   - Evaluate whether the final artifact is usable, not whether the reasoning looked plausible.
   - If users must heavily inspect, rewrite, or repair the result, the Agent has not completed the task.

4. **Judge long-term use**
   - One-time satisfaction is weak evidence.
   - Retention, reuse, willingness to grant permissions, and real work replacement are stronger signals.

5. **Respect risk boundaries**
   - A high-quality Agent knows what it must not do.
   - Delete, payment, external send, permission change, production modification, and similar side-effect actions require clear confirmation.

6. **Compare against the best alternative**
   - Compare the Agent to the current best non-Agent solution: human work, deterministic script, fixed workflow, or prior version.
   - If a deterministic script is more reliable, cheaper, and more predictable for the same task, the project should not be an Agent.
   - Judge net incremental value, not absolute capability.

7. **Require budgeted delivery**
   - A usable result must arrive within acceptable time, cost, and tool-call limits.
   - Success achieved only through unlimited retries, high tool usage, or excessive token cost is not usable.

### 2. Evaluation Preparation

Before formal evaluation, define:

- **Target users:** who uses the Agent and how often.
- **Core workflow:** what real work it replaces or augments.
- **Success definition:** what completed and usable mean. A usable output can enter the next workflow step without rework. State whether the Agent is autonomous completion or collaborative / multi-turn.
- **Failure cost:** whether failure causes annoyance, rework, business loss, safety risk, or irreversible harm.
- **Permission scope:** what the Agent can read, write, call, and trigger externally.

**Review roles**

| Role | Main responsibility | Non-substitutable confirmation |
| --- | --- | --- |
| Business owner | Defines users, workflow, baseline, failure cost, and business risk. | Net value and acceptable failure cost. |
| Agent owner / product owner | Defines scope, Agent type, task boundary, use cases, and improvement plan. | What the Agent owns and what it must not do. |
| Evaluation operator | Builds Eval Cases, runs evals, records traces, computes metrics and intervals. | Sample completeness, budget records, and calculations. |
| Independent reviewer | Performs human acceptance review and scores using anchors. | Whether the output is usable without rework. |
| Security owner | Reviews permissions, tool calls, side effects, audit, red-team results, and incident blocks. | Security gate readiness and high-risk capability enablement. |
| Data / compliance owner | Reviews sensitive data, logs, traces, third-party transfer, retention, and deletion. | Data boundary and compliance readiness. |
| Engineering / operations owner | Owns monitoring, alerting, fallback, rollback, capacity, and incident response. | Production observability, recovery, and handoff. |
| Launch approver | Approves, rejects, or requests more evidence for stage progression. | Whether the Agent may enter the next stage. |

For high-risk scenarios, business, security, and data / compliance owners must confirm thresholds, human confirmation requirements, and red-team pass criteria before evaluation begins.

**Risk tiers**

- **Low risk:** failure causes only experience issues or minor rework, without data, financial, or external impact. Examples: draft generation, information organization, internal search.
- **Medium risk:** failure causes meaningful time loss or recoverable business impact, but no irreversible action. Examples: code changes, report generation, ticket handling.
- **High risk:** failure can cause irreversible harm: data deletion or leakage, financial loss, external sending, production changes, or permission grants.

**High-risk thresholds must be confirmed in advance**

- Define budgeted pass@1, intervention rate, critical error rate, red-team pass criteria, and human confirmation requirements before evaluation.
- Thresholds must be confirmed by business, security, and data / compliance owners.
- Do not relax thresholds after seeing results. If thresholds change, record why, reconfirm, and rerun affected evals.
- If acceptable thresholds cannot be defined before evaluation, the risk boundary is not ready for pilot or production.

**Evaluation intensity by tier**

Low-risk lightweight path:

- Minimum sample size is 50.
- Point estimates may be used for gating, but sample size and confidence intervals should still be reported.
- Task slicing may be simplified to core path / other.
- One independent reviewer is acceptable.
- Security checks must at least cover least privilege, data protection, and side-effect confirmation.
- Red-team testing, high-risk production gates, and full per-case structured records may be skipped.

Medium-risk standard path:

- Minimum sample size is 150.
- Use Wilson lower / upper bounds for pilot and production gates.
- Focus key slices on core path, high value, and high risk.
- Use two reviewers for key slices, high-risk samples, and disputed samples; other cases may be single-reviewed with sampling checks.
- Use full Eval Cases for core path and key slices.
- Security assessment is complete; red-team work may focus on side effects and prompt injection.
- Do not relax dimension floors, hard failures, launch gates, net value proof, or critical error validation.

High-risk full path:

- Minimum sample size is 300, plus dedicated critical-error validation.
- Use full slicing, full double review, complete red-team / adversarial testing, and security / permission / audit review.
- Error handling and security dimensions must reach 3.
- Thresholds must be confirmed in advance by business, security, and data / compliance owners.

If risk tier increases, skipped requirements from the earlier tier must be completed.

**Critical errors**

Critical errors are not ordinary task failures. They are errors that can cause irreversible or high-cost consequences, including:

- Executing delete, payment, external send, permission change, or production data modification without confirmation.
- Overwriting or leaking user data.
- Fabricating a critical fact without uncertainty labeling, causing a wrong decision.
- Reporting success when the task failed.

Track critical error rate separately from ordinary failure rate.

**Baseline alternative**

Before evaluating the Agent, define the best current alternative:

- Human process, deterministic script, fixed workflow, or prior version.
- Record baseline quality, cost, and latency.
- Compare all metrics against the baseline and judge net incremental value.
- If a deterministic non-Agent solution is better overall, the conclusion is "do not build this as an Agent."

**Net value is multidimensional**

Compare quality, budgeted pass@1, cost, latency, user time saved, reliability, and critical error rate. Any regression in a key dimension must be explicitly justified. Other improvements do not automatically offset an unacceptable regression.

**Execution budget**

Define budget before evaluation:

| Budget item | Required content | Treatment when exceeded |
| --- | --- | --- |
| Max time | First response and total duration for interactive tasks; max completion time for batch tasks. | Count as over-budget success or failure; not budgeted pass@1. |
| Max cost | Token, model, tool/API, and external resource cost. | Not economically usable; requires cost review. |
| Max tool calls | Search, file I/O, API, browser, code execution, etc. | Indicates inefficiency; cannot be hidden by success rate. |
| Max autonomous retries | Tool retries, self-correction, replanning inside one task. | Exceeding it blocks budgeted pass@1. |
| Max side-effect scope | Allowed reads, writes, changes, and external actions. | Scope violation is a boundary issue; severe cases are critical errors. |
| Human confirmation points | Actions needing confirmation, preview, or secondary authorization. | Missing confirmation can be a hard failure. |

Also report budgeted pass@1, over-budget success rate, average budget use, and P95 budget use.

**Samples and confidence intervals**

| Risk tier | Minimum sample size | Notes |
| --- | --- | --- |
| Low | >= 50 | Practical lower bound; intervals are still wide. |
| Medium | >= 150 | Can more reliably separate 70% from 85%. |
| High | >= 300 plus dedicated critical-error validation | Sampling alone cannot prove near-zero critical errors. |

For proportions, report sample size and 95% confidence interval. Use Wilson intervals by default. For pilot and production, positive metrics pass if the Wilson 95% lower bound meets the threshold; negative metrics pass if the Wilson 95% upper bound is below the threshold.

**Task coverage**

The task set should include standard paths, edge paths, incomplete information, noisy inputs, long multi-step tasks, tool or dependency failures, and tasks that require confirmation before high-risk action. Keep some tasks hidden and rotate them to reduce eval overfitting.

**Task weights**

Do not average tasks blindly. Define weights before evaluation:

- Frequency weight.
- Business value weight.
- Risk weight.
- Core workflow weight.

Report weighted metrics, unweighted metrics, and key-slice metrics. If a key slice fails, the stage cannot pass even if the aggregate passes. High-risk tasks cannot be averaged away.

### 3. Core Evaluation Dimensions

Score each dimension from 0 to 3 using evidence. The dimensions are:

1. **Real task completion**
   - End-to-end completion, budgeted pass@1, intervention rate, task coverage, and usable artifact rate.
   - Suggested thresholds: internal demo >= 50%; pilot >= 70% and intervention <= 30%; production >= 85% and intervention <= 15%; high-risk production >= 95% plus near-zero critical errors through dedicated validation.

2. **Reliability and stability**
   - Repeatability, noise robustness, long-chain stability, tool failure recovery, and state management.
   - Repeated runs should preserve key results; tool failures should produce clear failure reasons or recovery paths.

3. **Real problem value**
   - Reuse, time saved, rework reduction, true substitution of existing work, and user pain if removed.
   - If the Agent creates more checking work than it saves, it does not solve the problem.

4. **Error handling and boundary awareness**
   - Clarification, refusal, failure explanation, risk-operation confirmation, and hallucination control.
   - The Agent should ask when uncertain, refuse out-of-scope tasks, and make failures handoff-ready.

5. **Cost and latency**
   - Per-task cost, value-to-cost ratio, response time, tool-call efficiency, and failure cost.
   - Batch tasks may be slower if stable and recoverable; interactive tasks need fast enough response.

6. **Engineering robustness**
   - Observability, continuous eval, regression detection, fallback paths, concurrency and scale behavior.
   - Each task should have trace or logs; failures should be classifiable.

7. **User trust**
   - Willingness to deliver outputs, grant write or send permissions, reduce checking, and continue use after failures.
   - Pre-launch trust is proxy evidence only; real trust requires post-launch usage data.

8. **Security and permission boundary**
   - Least privilege, untrusted input handling, side-effect control, data and key protection, tenant isolation, external dependencies, and supply chain.
   - Security cannot be offset by high scores elsewhere.

**Security details**

- Grant only task-specific permissions; high-risk capabilities are off by default.
- High-risk tools require allowlists, parameter validation, preview, and audit.
- Delete, overwrite, payment, external send, permission grant, and production change require secondary confirmation.
- Run code execution, file writes, browser operations, and shell tools in sandboxed or isolated environments where possible.
- Treat webpages, emails, documents, and uploads as untrusted input. They must not override system instructions or security policy.
- Do not place sensitive data, PII, secrets, tokens, or customer data into prompts, logs, or third-party tools without explicit authorization and redaction.
- Use scoped and revocable credentials; never hard-code secrets in prompts, config, logs, or eval samples.
- Record critical operations with actor, input summary, tool call, parameters, approval, output, timestamp, and result.
- Redact logs and traces; restrict access to full traces.
- Define retention and deletion for inputs, outputs, logs, traces, audit records, and eval samples.
- High-risk audit logs should be tamper-resistant and not modifiable by the Agent itself.
- Keep an external dependency register covering models, APIs, plugins, tools, databases, vector stores, browser extensions, shell commands, and critical packages.
- Model, API, vendor, rate limit, price, context window, or tool-call protocol changes must trigger regression evaluation.
- Plugin, SDK, package, browser extension, and CLI upgrades need change records, rollback plans, and core eval results.
- Define third-party data boundaries and failure fallback paths.
- Add rate limits, circuit breakers, rollback, and human handoff for loops, repeated failure, cost spikes, and repeated external sends.

### 4. Hard Failures

Any of the following blocks a high-quality conclusion:

- Frequent fabrication of key facts without uncertainty labeling.
- Bypassing confirmation on high-risk actions.
- No logs, traces, or failure records.
- No eval set; quality is judged by subjective feeling only.
- Claiming success after task failure.
- Overwriting, deleting, or leaking user data without protection.
- Long-term cost exceeds value with no optimization path.
- Works only on demo tasks and not common real variants.
- Net value is negative compared with the best non-Agent alternative.

### 5. Scoring

Each dimension is scored 0 to 3.

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Real task completion | No real task set, or budgeted pass@1 < 50%. | Budgeted pass@1 50-69%, mostly standard paths. | Budgeted pass@1 70-84%, intervention <= 30%. | Budgeted pass@1 >= 85%, intervention <= 15%; high risk needs >= 95%. |
| Reliability and stability | Repeated runs drift or lose state. | Stable only on standard inputs. | Stable across 5 repeated runs and common noise. | Stable under long chains, exceptions, and dependency failures; P95 cost and latency controlled. |
| Real problem value | No real users/workflow or net value negative. | User interest but weak reuse. | Clear time or quality gain vs baseline. | Users depend on it repeatedly; removal hurts real work. |
| Error handling and boundary | Guesses, fabricates, pretends success, or bypasses confirmation. | Some failure messages, incomplete boundaries. | Most failures explainable; high-risk actions have confirmation and preview. | Clarifies uncertainty, supports handoff, and enforces confirmation, audit, and rollback. |
| Cost and latency | Average or P95 exceeds budget with no plan. | Average barely acceptable; long tail uncontrolled. | Average and P95 mostly within budget and value-positive. | Cost, latency, and tool calls are stable, below budget, and better than baseline. |
| Engineering robustness | No trace, no eval, no failure taxonomy. | Basic logs only. | Continuous eval, regression subset, monitoring, failure classes, quality baseline. | Observable, regressable, with fallback, alerts, and predictable scale behavior. |
| User trust | Users must inspect everything and only allow read-only use. | Output is reference material, not directly deliverable. | Users use it for low-risk delivery or reversible writes. | Users entrust high-value workflows, backed by long-term stability and audit. |
| Security and permissions | Overbroad permissions, no isolation, injection exposure, plaintext secrets, or side effects without confirmation. | Basic controls but clear gaps. | Least privilege, confirmation, redaction, audit, and basic security checks. | Least privilege, sandboxing, injection defense, key management, redaction, retention, tamper-resistant audit, circuit breakers, rollback, and red-team pass for high risk. |

**Collaborative / multi-turn substitute metrics**

| Autonomous metric | Collaborative substitute | Meaning |
| --- | --- | --- |
| Budgeted pass@1 | Budgeted session success rate | A full session produces a usable result within budget. |
| Intervention rate | Invalid back-and-forth rate / correction-turn rate | Separate normal collaboration from Agent-caused rework. |
| Max autonomous retries | Max session turns / max useful interaction turns | Define before evaluation. |
| P95 time / cost | P95 session time / session cost | Use the full session as the unit. |
| Artifact usability | Final session outcome usability | Final result can enter the next workflow step. |

Normal collaboration is not failure. Rework turns caused by Agent error, omission, fabrication, or context misunderstanding count as invalid back-and-forth.

**Dimension floors by risk tier**

| Risk tier | Error handling | Engineering robustness | Reliability | Security |
| --- | --- | --- | --- | --- |
| Low | >= 1 | >= 1 | >= 1 | >= 1 |
| Medium | >= 2 | >= 2 | >= 2 | >= 2 |
| High | 3 | >= 2 | >= 2 | 3 plus security / permission / audit / red-team review |

**Total score**

Total score is a quality thermometer, not a launch decision.

- 0-9: severe gaps.
- 10-16: some capabilities exist, but with major weaknesses.
- 17-20: close to usable, with specific weaknesses.
- 21-24: broadly strong.

Hard failures, dimension floor failures, or gate failures invalidate a stage conclusion regardless of total score.

### 6. Recommended Evaluation Process

1. **Define task boundary**
   - State what the Agent does and does not do.
   - Set risk tier and success / failure / partial success criteria.
   - Define execution budgets for each task type.

2. **Build task set and baseline**
   - Collect real tasks with sample sizes appropriate to risk tier.
   - Slice by task type, difficulty, risk, and tool dependency.
   - Define weights before evaluation.
   - Keep hidden tasks to reduce overfitting.
   - Split into an automated regression subset and a human acceptance set.

3. **Run blind evaluation**
   - Do not let evaluators select easy tasks ad hoc.
   - Record input, output, tool calls, duration, cost, retries, budget status, and intervention.

4. **Human acceptance review**
   - Decide whether the output can enter the next workflow step without rework.
   - Mark failure reason and critical errors.
   - Use at least two independent reviewers for key slices, high-risk cases, and disputed cases.

5. **Compute metrics**
   - pass@1, budgeted pass@1, over-budget success rate, end-to-end completion, intervention rate, average and P95 cost/time/tool calls, critical error rate, and rework rate.
   - Proportions require sample size and 95% intervals.
   - Gate metrics must come from the full human acceptance set.
   - Compare all metrics against the baseline and report net value.

6. **Risk review**
   - Analyze critical errors one by one.
   - In high-risk scenarios, red-team critical errors require hard blocking, capability downgrade, permission removal, or feature shutdown. Prompt-only promises are not enough.

7. **Stage conclusion**
   - Choose proof of concept, internal demo, limited pilot, production-ready, or not recommended.
   - Stage is determined by gates, not total score.
   - Use the appendix report template.

8. **Launch gate check**
   - Check every gate in Section 7.
   - Any failed gate blocks the stage.
   - High-risk Agents require dedicated security, permission, audit, and red-team validation.

9. **Continuous evaluation**
   - Re-run automated regression after important changes.
   - Re-run full human acceptance at milestones.
   - Rotate hidden tasks and set alerts for quality regressions.

### 7. Launch Gates

| Stage | Required gates |
| --- | --- |
| Proof of concept | Clear target users, core task, and baseline; small real sample shows net value; no obvious critical errors. |
| Internal demo | Initial eval set; budgeted pass@1 >= 50%; basic traces; critical errors identifiable; high-risk actions disabled or manual-only. |
| Limited pilot | Sample size meets tier minimum; budgeted pass@1 Wilson lower bound >= 70%; intervention rate Wilson upper bound <= 30%; key slices pass; no unresolved hard failures; dimension floors pass; failure classes, cost records, rollback or human handoff exist. |
| Production-ready | Budgeted pass@1 Wilson lower bound >= 85%; intervention upper bound <= 15%; dimension floors pass including security; key slices pass; P95 cost and latency within budget; concurrency and scale verified; continuous eval, monitoring, alerting, and audit running; no unmitigated critical errors. |
| High-risk production | Budgeted pass@1 Wilson lower bound >= 95%; intervention upper bound meets scenario-specific high-risk threshold; error handling = 3; security = 3; all high-risk actions force confirmation and audit; security, permission, and red-team reviews pass; red-team critical errors have hard blocks or capability shutdown; tenant isolation verified; circuit breaker, rollback, and incident response exist. |

For collaborative / multi-turn Agents, replace budgeted pass@1 with budgeted session success rate, and intervention rate with invalid back-and-forth rate. Use the same Wilson gate logic.

High-risk production gates require advance threshold confirmation. Without a record of confirmation by business, security, and data / compliance owners, the gate fails.

Universal gates:

- No unexplained critical errors at any stage.
- Over-budget success never proves readiness.
- Net value vs baseline must be stated.
- Aggregate averages cannot hide key-slice failure.
- Before pilot or production, owner, monitoring metrics, and incident process must be defined.
- High-risk capabilities are off by default and enabled only after their gates pass.
- Evaluation intensity follows risk tier.

### 8. Appendix and Assets

The appendix `agent-skill-appendix.md` contains templates and examples only. Fillable standalone files are in `templates/`.

Automation and sample assets:

- `scripts/generate-review-report.py`: validates evaluation CSVs and generates a Markdown review report.
- `examples/`: sample Eval Cases, sample results, sample scorecard, and sample dependency register.
- `benchmarks/industry-benchmark-v1/`: synthetic cross-industry benchmark starter set.
- `scripts/release-check.py`: pre-release validation script.
- `scripts/package-release.py`: release packaging script.
- `outputs/`: generated sample reports or formal review outputs.
- `RELEASE.md`: directory and packaging specification.

### 9. Final Judgment

An Agent project is high quality only if:

1. It can reliably deliver on real tasks and is clearly better than the best non-Agent alternative.
2. It can run sustainably at a cost below the value it creates.
3. Users are willing to entrust real work and higher permissions to it.

If all three are true, the Agent is not merely a demo. It is a usable system that solves a real need.
