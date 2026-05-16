# External Dependency Register Template

Use this table to record models, tools, plugins, third-party APIs, databases, vector stores, browser extensions, shell tools, and critical packages. Any external component that affects output quality, security boundary, data transfer, cost, or availability should be listed.

| dependency_name | type | version | purpose | permission_scope | data_touched | sensitive_data | data_retention | failure_impact | fallback_path | alternative | regression_on_change | owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | model / API / plugin / SDK / database / vector store / browser extension / CLI / other |  |  | read-only / write / external send / production change / payment / permission management | input / output / logs / trace / user data / customer data | yes / no |  |  |  |  | yes / no |  |

## Requirements

- Record dependency version, permission scope, and data exposure before evaluation.
- Model, vendor, API behavior, price, rate limit, context window, tool-call protocol, or plugin version changes should trigger core regression evals.
- If a dependency outage can cause task failure, wrong output, or safety risk, define fallback, stop, or human handoff behavior.
- For high-risk Agents, the dependency register must be confirmed by security and data / compliance owners.
