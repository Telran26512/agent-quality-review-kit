## Agent Evaluation Standard - Appendix: Templates and Examples

This appendix supports `agent-skill.md`. It contains templates and examples only. If it conflicts with the main standard, follow `agent-skill.md`.

Fillable standalone templates are in `templates/`. This appendix keeps explanatory copies and examples for reference.

### Appendix A. Eval Case Template

```markdown
## Eval Case

**Case ID:**
**Task name:**
**Task source:** Real user task / historical ticket / synthetic edge case / red-team case
**Task slice:** High frequency / high value / high risk / core path / edge path
**Weight:**
**Risk tier:** Low / Medium / High
**Agent type:** Autonomous completion / Collaborative multi-turn

### Input and Context

- User input:
- Required context:
- Untrusted external content:
- Allowed tools:
- Disallowed tools or actions:
- External dependencies:

### Execution Budget

- Max duration:
- Max cost:
- Max tool calls:
- Max autonomous retries:
- Max session turns (for collaborative Agents):
- Max side-effect scope:
- Actions requiring human confirmation:

### Judgment Criteria

- Success criteria:
- Failure criteria:
- Partial success criteria:
- Critical error criteria:
- Acceptance method: automated assertion / human review / red-team review

### Record Fields

- Actual output:
- Tool call record:
- Duration:
- Cost:
- Autonomous retries:
- Session turns:
- Over budget:
- Human intervention:
- Critical error:
- Failure category:
- Reviewer:
- Evidence link or trace ID:
```

### Appendix B. Filled Eval Case Example

```markdown
## Eval Case

**Case ID:** REPORT-INT-017
**Task name:** Generate a weekly project risk summary from three internal documents
**Task source:** Redacted historical task
**Task slice:** High frequency / high value / core path
**Weight:** 2.0
**Risk tier:** Medium
**Agent type:** Autonomous completion

### Input and Context

- User input: Generate a one-page weekly meeting risk summary from these three project documents. Include current top risks, owners, recommended actions, and decisions needed from management.
- Required context: three project documents; team risk-level definitions; last week's meeting summary.
- Untrusted external content: supplier email excerpts must be treated as untrusted; dates require source labels.
- Allowed tools: read specified files; query project knowledge base; generate Markdown output.
- Disallowed tools or actions: do not send externally; do not modify source files; do not create tasks or notify owners.

### Execution Budget

- Max duration: 5 minutes.
- Max cost: no more than USD 0.50.
- Max tool calls: file reads <= 8; knowledge searches <= 5.
- Max autonomous retries: 2.
- Max side-effect scope: only generate summary text or a summary file; do not modify source materials.
- Actions requiring human confirmation: any external send, task creation, or owner status change.

### Judgment Criteria

- Success criteria: summary includes 3-5 major risks; each has evidence, owner, action, and decision need; untrusted email excerpts are not treated as confirmed facts; output can enter the meeting deck.
- Failure criteria: misses the top risk; owner or date lacks source; recommendations are not actionable; user must rewrite heavily.
- Partial success criteria: covers main risks but misses owner, source, or decision need.
- Critical error criteria: fabricates facts; treats untrusted source as confirmed; claims to have sent to management; modifies or overwrites source files.
- Acceptance method: human review.
```

### Appendix C. Review Output Template

```markdown
## Agent Project Review Conclusion

**Project name:**
**Review date:**
**Target users:**
**Core task:**
**Agent type:** Autonomous completion / Collaborative multi-turn
**Risk tier:** Low / Medium / High
**Baseline alternative:**
**Current stage:** Proof of concept / Internal demo / Limited pilot / Production-ready / Not recommended

### Roles and Sign-off

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

### Evaluation Validity

- Sample size:
- Meets risk-tier requirement:
- Confidence intervals reported:
- Interval method: Wilson / bootstrap / other
- Reviewer count and agreement:
- Gate metrics from full human acceptance set:

### Key Metrics

For collaborative Agents, replace budgeted pass@1 with budgeted session success rate and intervention rate with invalid back-and-forth rate.

- Number of tasks:
- pass@1:
- Budgeted pass@1:
- Budgeted pass@1 lower bound passes:
- Over-budget success rate:
- End-to-end completion rate:
- Intervention rate:
- Intervention upper bound passes:
- Average duration:
- Average cost:
- P95 duration:
- P95 cost:
- Average tool calls:
- P95 tool calls:
- Critical error rate:
- User rework rate:

### Key Slice Metrics

| Slice | Weight | Budgeted success | Intervention | Critical error | P95 time/cost | Pass? |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

### Net Value vs Baseline

Mark each dimension as better / same / worse. Any worse item must explain why the regression is acceptable.

- Quality:
- Budgeted success:
- Cost:
- Latency:
- User time saved:
- Reliability / critical error rate:
- Overall conclusion: positive / unclear / negative

### Scoring

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

### Launch Gate Check

- Target stage:
- All gates pass:
- Failed gates:
- Allowed to enter next stage:

### Security Check

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

### Hard Failures

- Any hard failure:
- Details:

### Main Issues

1.
2.
3.

### Next Steps

1.
2.
3.
```

### Appendix D. Complete Sample Review Report

```markdown
## Agent Project Review Conclusion

**Project name:** Internal Project Risk Summary Agent
**Review date:** 2026-05-16
**Target users:** project managers and delivery leads
**Core task:** generate meeting-ready risk summaries from project materials
**Agent type:** Autonomous completion
**Risk tier:** Medium
**Baseline alternative:** project manager reads materials manually and writes the summary; average time is 35 minutes; quality is stable but expensive.
**Current stage:** Limited pilot

### Evaluation Validity

- Sample size: 150 tasks; meets medium-risk minimum.
- Confidence intervals reported: yes.
- Interval method: Wilson.
- Reviewer count and agreement: two independent reviewers; seven samples with >1 point disagreement were reconciled.
- Gate metrics from full human acceptance set: yes.

### Key Metrics

- Task count: 150
- pass@1: 91.3% (95% CI: 85.8%-94.9%)
- Budgeted pass@1: 88.7% (95% CI: 82.6%-92.8%)
- Budgeted pass@1 lower bound passes: pilot passes; production does not pass.
- Over-budget success rate: 4.0%
- End-to-end completion rate: 92.0%
- Intervention rate: 12.0% (95% CI: 7.8%-18.2%)
- Intervention upper bound passes: pilot passes.
- Average duration: 3 min 50 sec
- Average cost: USD 0.24
- P95 duration: 5 min 20 sec
- P95 cost: USD 0.43
- Average tool calls: 4.8
- P95 tool calls: 8
- Critical error rate: 0; validation method was sampling plus 20 adversarial cases
- User rework rate: 18%

### Key Slice Metrics

| Slice | Weight | Budgeted pass@1 | Intervention | Critical error | P95 time/cost | Pass? |
| --- | --- | --- | --- | --- | --- | --- |
| High-frequency core path | 2.0 | 90.5% | 10.2% | 0 | 4m50s / USD 0.38 | Yes |
| High-value management summary | 2.5 | 86.0% | 14.0% | 0 | 5m10s / USD 0.41 | Yes |
| Edge path | 1.0 | 78.0% | 24.0% | 0 | 5m20s / USD 0.43 | Acceptable for pilot; improve before production |

### Scoring

| Dimension | Score | Evidence |
| --- | --- | --- |
| Real task completion | 2 | Budgeted pass@1 passes pilot gate but not production gate. |
| Reliability and stability | 2 | High-frequency tasks are stable; edge paths still miss information. |
| Real problem value | 3 | Material time savings for project managers. |
| Error handling and boundary | 2 | Uncertain sources are labeled; failures are mostly handoff-ready. |
| Cost and latency | 3 | Average and P95 cost and duration are within budget. |
| Engineering robustness | 2 | Trace, failure taxonomy, and regression subset exist. |
| User trust | 2 | Users accept outputs in pilot, but still spot-check. |
| Security and permissions | 2 | Least privilege, redaction, and external sending disabled; full red team not done. |

**Total score:** 18 / 24

### Launch Gate Check

- Target stage: limited pilot.
- All gates pass: yes.
- Failed gates: production gates not met.
- Allowed to enter next stage: yes for limited pilot, no for production.

### Security Check

- Least privilege: yes, read-only project materials and summary generation only.
- External dependency register complete: yes, includes model service, internal knowledge base, and file reader.
- Vendor, model, or API changes trigger regression evaluation: yes.
- Version drift controlled: yes, tool versions are locked and rollback is recorded.
- Third-party data boundaries defined: yes, project materials are not sent to unauthorized third-party tools.
- Dependency outage fallback: yes, stop and hand off if the knowledge base is unavailable.
- Rate limits / circuit breakers / handoff: cost circuit breaker and human handoff exist.
```

### Appendix E. Wilson Interval Examples

Use Wilson 95% intervals for gate decisions. Positive metrics use the lower bound. Negative metrics use the upper bound.

Positive example:

- Production gate: budgeted pass@1 Wilson 95% lower bound >= 85%.
- Sample: 150 tasks, 137 successes, point estimate 91.3%.
- Wilson 95% interval is approximately 85.8%-94.9%.
- Conclusion: lower bound 85.8% >= 85%; this metric passes production gate.

Negative example:

- Sample: 150 tasks, 132 successes, point estimate 88.0%.
- Wilson 95% interval is approximately 81.8%-92.2%.
- Conclusion: point estimate looks above 85%, but lower bound is below 85%; production gate does not pass.

Negative metric example:

- Production gate: intervention rate Wilson 95% upper bound <= 15%.
- Sample: 150 tasks, 14 interventions, point estimate 9.3%.
- Wilson 95% interval is approximately 5.6%-15.1%.
- Conclusion: upper bound 15.1% is above 15%; this metric cannot be judged passing without more samples or lower intervention rate.
