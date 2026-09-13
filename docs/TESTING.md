# Testing and Validation Approach

The prototype validates at two levels.

## System tests
`pytest` verifies the agentic workflow itself: mandatory URL-shortener generation, ambiguity detection, context-aware brownfield planning, validation-driven repair, and API health/run behavior.

## Generated-output validation
The `ValidationAgent` checks:
1. mandatory artifact completeness for the URL-shortener use case;
2. Python syntax compilation;
3. a guardrail scan for dangerous dynamic execution primitives;
4. consistency of required API paths in the generated OpenAPI contract;
5. execution of the generated URL-shortener test suite in a temporary workspace with a fixed timeout.

Generated tests are treated as untrusted assessment artifacts. The temporary workspace provides filesystem separation from the repository, and execution is time-bounded. A production implementation should use stronger container/VM isolation, network controls, resource limits, and no production credentials.

## Validation-driven recovery
When validation fails, the `ValidationResult` records failed checks and repair actions. The orchestrator passes that feedback to `GenerationAgent.repair()`, which restores or regenerates the affected artifacts, then runs validation again. Repair attempts are bounded by `max_repair_attempts`; the workflow never retries indefinitely.

## What is deliberately not claimed
- Passing tests does not prove production correctness or security.
- The brownfield analyzer is heuristic rather than a compiler-grade dependency analyzer.
- SQLite demonstrates persistence locally but would be replaced for high-scale production use.
- The deterministic generator keeps the assessment reproducible; a production version can add an LLM provider behind the same agent interfaces while retaining validation and approval gates.
