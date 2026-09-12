from __future__ import annotations

import argparse
import json

from .orchestrator import WorkflowOrchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a reviewable engineering outcome from a software requirement.")
    parser.add_argument("--requirement", required=True, help="Software requirement to process")
    parser.add_argument("--codebase", help="Optional existing codebase path for brownfield reasoning")
    parser.add_argument("--approve", action="store_true", help="Simulate explicit human approval after validation")
    parser.add_argument("--output-root", default="outputs")
    args = parser.parse_args()

    outcome = WorkflowOrchestrator(args.output_root).run(args.requirement, args.codebase, args.approve)
    print(json.dumps({
        "run_id": outcome.run_id,
        "scenario": outcome.analysis.scenario,
        "ambiguities": outcome.analysis.ambiguities,
        "validation_passed": outcome.validation.passed,
        "approval_status": outcome.approval_status,
        "output_directory": f"{args.output_root}/{outcome.run_id}",
    }, indent=2))


if __name__ == "__main__":
    main()
