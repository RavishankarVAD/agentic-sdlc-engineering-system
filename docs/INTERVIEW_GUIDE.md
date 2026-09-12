# Interview Presentation Guide

## 60-second opening
“I approached this as an SDLC orchestration problem rather than a chatbot problem. A requirement enters the system, a requirement agent normalizes it and identifies ambiguity, a codebase agent adds brownfield context, a planner creates dependency-aware tasks, an architecture agent makes design decisions, a generation agent produces code/API/tests/docs, and a validation agent checks the outputs. Failed validation enters a bounded repair loop. Even after automation succeeds, the final state is awaiting human approval unless approval is explicitly provided. That is how I implemented controlled autonomy.”

## Why this design
“I intentionally separated the agents by responsibility so each output is reviewable and testable. The orchestrator owns state and sequencing, while the agents do focused work. This is similar to how I think about reliable platform workflows: explicit stages, dependency management, observability, validation gates and controlled failure handling.”

## Mandatory URL shortener
“The requirement is normalized into create-short-URL, redirect, persistence and analytics capabilities. The generated reference implementation uses FastAPI, a service/repository split and SQLite so the panel can run it with no external infrastructure. The repository boundary makes the production migration to PostgreSQL or DynamoDB straightforward. For high redirect throughput I would add a cache, and for high-volume analytics I would move click events to asynchronous streaming instead of adding a synchronous database write to every redirect.”

## Why SQLite if the requirement says scalable?
“SQLite is only the local prototype persistence choice, not my production scaling recommendation. The assessment needs a working runnable prototype. I preserved scalability at the architecture level by keeping API instances stateless and storage behind an interface. In production I would use a horizontally scalable/managed datastore and likely Redis for hot redirects.”

## Where is the agentic behavior?
“The agents have distinct responsibilities, pass structured state across steps, operate autonomously inside bounded permissions, and validation can change the execution path by invoking a repair step. The final approval is deliberately human-controlled. So the system demonstrates autonomy plus governance, not just sequential prompt calls.”

## Why no external LLM dependency?
“For the assessment I optimized for reproducibility, cost-free execution and reviewability. The current agents are deterministic, which means the panel can clone and run it without API keys. The interfaces are intentionally separable, so a production version can replace requirement, planning or generation logic with an LLM while keeping the orchestrator, validators and approval controls unchanged.”

## Brownfield answer
“For brownfield inputs, the system accepts an existing codebase path and inventories likely impacted API/service/model/test files before planning. The current prototype uses heuristics. With more time I would add AST/symbol analysis, dependency graphs, git history and targeted test-impact analysis.”

## Risks to call out yourself
- Generated code must still go through normal code review, security scanning and CI/CD.
- Ambiguous non-functional requirements need measurable SLOs before production acceptance.
- Analytics design is a deliberate prototype trade-off.
- The current brownfield reasoning is lightweight.
- Deterministic generation proves orchestration; production AI would need model evaluation, prompt/version management, token/cost limits and stronger sandboxing.

## Demo sequence
1. Run tests: `pytest -q`.
2. Run the mandatory requirement without approval and show `awaiting_human_approval`.
3. Open the generated `ENGINEERING_SUMMARY.md` and show task dependencies, architecture, validation and risks.
4. Re-run with `--approve` and show the state becomes `approved` only after validations pass.
5. Show `examples/ambiguous.txt` and explain ambiguity detection.
6. Show `examples/brownfield.txt` with `--codebase` and explain impact reasoning.

## If asked about your Python/AI background
“I’m coming from an SRE/platform engineering background, so I focused on the parts I can defend strongly: workflow reliability, explicit contracts, failure handling, validation, safe automation, observability and human gates. I used Python because it gives a small, reviewable prototype. I would not claim this is a fully autonomous coding platform; it is a production-minded prototype that demonstrates the requested control flow and extension points.”
