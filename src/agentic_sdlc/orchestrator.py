from __future__ import annotations

import json
import uuid
from pathlib import Path

from .agents import RequirementAgent, CodebaseAgent, PlanningAgent, ArchitectureAgent, GenerationAgent, ValidationAgent
from .models import EngineeringOutcome


class WorkflowOrchestrator:
    """Coordinates agents, dependency-aware execution, validation-driven recovery and approval."""

    def __init__(self, output_root: str = "outputs", max_repair_attempts: int = 1) -> None:
        self.output_root = Path(output_root)
        self.max_repair_attempts = max_repair_attempts
        self.requirements = RequirementAgent()
        self.codebase = CodebaseAgent()
        self.planner = PlanningAgent()
        self.architect = ArchitectureAgent()
        self.generator = GenerationAgent()
        self.validator = ValidationAgent()

    def run(self, requirement: str, codebase: str | None = None, approve: bool = False) -> EngineeringOutcome:
        run_id = uuid.uuid4().hex[:12]
        log: list[str] = []

        analysis = self.requirements.analyze(requirement, codebase)
        log.append(f"requirement-agent: normalized requirement; scenario={analysis.scenario}; ambiguities={len(analysis.ambiguities)}")

        codebase_info = self.codebase.inspect(codebase)
        log.append(f"codebase-agent: inspected {len(codebase_info['files'])} files; impact candidates={len(codebase_info['impacted'])}")

        tasks = self.planner.plan(analysis, codebase_info)
        task_map = {task.id: task for task in tasks}
        task_map["T1"].status = "completed"
        for task_id, task in task_map.items():
            if task_id == "T2" or task_id.startswith("T2"):
                task.status = "completed"
        dynamic_impacts = [task.id for task in tasks if task.id.startswith("T2") and task.id != "T2"]
        log.append(f"planner-agent: created dependency-aware execution plan; context-specific impact tasks={len(dynamic_impacts)}")

        architecture = self.architect.design(analysis)
        task_map["T3"].status = "completed"
        log.append("architecture-agent: produced architecture, API, scalability, security and observability decisions")

        artifacts = self.generator.generate(analysis, architecture)
        task_map["T4"].status = "completed"
        log.append(f"generation-agent: produced {len(artifacts)} engineering artifacts")

        validation = self.validator.validate(analysis, artifacts)
        task_map["T5"].status = "completed" if validation.passed else "failed"
        log.append(f"validation-agent: validation passed={validation.passed}; checks={len(validation.checks)}")

        attempts = 0
        while not validation.passed and attempts < self.max_repair_attempts:
            attempts += 1
            actions = "; ".join(validation.repair_actions) or "repair failed artifacts"
            log.append(f"repair-agent: bounded repair attempt {attempts}; feedback={actions}")
            artifacts = self.generator.repair(analysis, architecture, artifacts, validation)
            validation = self.validator.validate(analysis, artifacts)
            log.append(f"validation-agent: post-repair validation passed={validation.passed}")

        if attempts == 0:
            task_map["T6"].status = "not_required" if validation.passed else "blocked"
        else:
            task_map["T6"].status = "completed" if validation.passed else "blocked"
        task_map["T5"].status = "completed" if validation.passed else "failed"

        approval_status = "approved" if approve and validation.passed else "awaiting_human_approval"
        task_map["T7"].status = "completed" if approval_status == "approved" else "pending"
        log.append(f"human-gate: {approval_status}")

        outcome = EngineeringOutcome(run_id, analysis, tasks, architecture, artifacts, validation, approval_status, log)
        self._persist(outcome, codebase_info)
        return outcome

    def _persist(self, outcome: EngineeringOutcome, codebase_info: dict[str, object]) -> None:
        run_dir = self.output_root / outcome.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        for relative, content in outcome.artifacts.items():
            target = run_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        summary = outcome.to_dict()
        summary["codebase_reasoning"] = codebase_info
        (run_dir / "engineering_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (run_dir / "ENGINEERING_SUMMARY.md").write_text(self._summary_markdown(outcome, codebase_info), encoding="utf-8")

    @staticmethod
    def _summary_markdown(outcome: EngineeringOutcome, codebase_info: dict[str, object]) -> str:
        lines = [
            "# Engineering Outcome",
            "",
            f"**Run ID:** `{outcome.run_id}`  ",
            f"**Scenario:** {outcome.analysis.scenario}  ",
            f"**Approval:** {outcome.approval_status}",
            "",
            "## Normalized requirement",
            outcome.analysis.normalized,
            "",
            "## Ambiguities",
            *([f"- {x}" for x in outcome.analysis.ambiguities] or ["- None detected."]),
            "",
            "## Assumptions",
            *([f"- {x}" for x in outcome.analysis.assumptions] or ["- None recorded."]),
            "",
            "## Plan",
            *[f"- **{t.id} {t.title}** — {t.status}; depends on {', '.join(t.depends_on) or 'none'}" for t in outcome.tasks],
            "",
            "## Brownfield/codebase reasoning",
            f"- Files inspected: {len(codebase_info['files'])}",
            f"- Impact candidates: {', '.join(codebase_info['impacted']) or 'none'}",
            "",
            "## Architecture",
            *[f"- {x}" for x in outcome.architecture.components],
            "",
            "## Trade-offs",
            *[f"- {x}" for x in outcome.architecture.tradeoffs],
            "",
            "## Validation",
            *[f"- {c['name']}: {'PASS' if c['passed'] else 'FAIL'} — {c['details']}" for c in outcome.validation.checks],
            "",
            "## Risks and limitations",
            *[f"- {x}" for x in outcome.validation.risks],
            "",
            "## Execution log",
            *[f"1. {x}" for x in outcome.execution_log],
        ]
        return "\n".join(lines) + "\n"
