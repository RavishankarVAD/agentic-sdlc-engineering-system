# Testing and Validation Approach

The prototype validates at two levels.

## System tests
`pytest` verifies the agentic workflow itself: mandatory URL-shortener generation, ambiguity detection, brownfield classification and API health/run behavior.

## Generated-output validation
The ValidationAgent checks:
1. mandatory artifact completeness for the URL-shortener use case;
2. Python syntax compilation;
3. a guardrail scan for dangerous dynamic execution primitives;
4. consistency of required API paths in the generated contract.

The workflow supports a bounded repair loop. If generated artifacts fail a correctable validation, generation is attempted again up to the configured limit. It never loops indefinitely.

## What is deliberately not claimed
- Static checks do not prove production correctness or security.
- The brownfield analyzer is heuristic, not a compiler-grade dependency analyzer.
- SQLite demonstrates persistence locally but would be replaced for high-scale production use.
- The deterministic generator keeps the assessment reproducible; a production version can add an LLM provider behind the same agent interfaces and retain the same validators and approval gates.
