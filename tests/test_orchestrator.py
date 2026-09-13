from pathlib import Path

from agentic_sdlc.agents import ArchitectureAgent, GenerationAgent, RequirementAgent, ValidationAgent
from agentic_sdlc.orchestrator import WorkflowOrchestrator

MANDATORY = "Build a scalable URL shortener service with APIs, persistence, and analytics."


def test_mandatory_url_shortener_workflow(tmp_path: Path):
    outcome = WorkflowOrchestrator(str(tmp_path)).run(MANDATORY, approve=True)
    assert outcome.analysis.scenario == "greenfield"
    assert outcome.validation.passed is True
    assert outcome.approval_status == "approved"
    assert "generated/url_shortener_api.py" in outcome.artifacts
    assert "generated/openapi.yaml" in outcome.artifacts
    assert any(t.depends_on for t in outcome.tasks)
    assert any(c["name"] == "generated_tests" and c["passed"] for c in outcome.validation.checks)
    assert (tmp_path / outcome.run_id / "ENGINEERING_SUMMARY.md").exists()


def test_ambiguous_requirement_is_flagged(tmp_path: Path):
    outcome = WorkflowOrchestrator(str(tmp_path)).run("Make the API fast and secure")
    assert outcome.analysis.ambiguities
    assert outcome.approval_status == "awaiting_human_approval"


def test_brownfield_codebase_reasoning_changes_plan(tmp_path: Path):
    codebase = tmp_path / "existing"
    codebase.mkdir()
    (codebase / "api_routes.py").write_text("def route(): pass\n")
    (codebase / "service.py").write_text("def service(): pass\n")
    (codebase / "models.py").write_text("class URL: pass\n")
    (codebase / "test_api.py").write_text("def test_api(): pass\n")

    outcome = WorkflowOrchestrator(str(tmp_path / "out")).run(
        "Enhance the existing URL shortener with analytics",
        str(codebase),
    )

    assert outcome.analysis.scenario == "brownfield"
    task_ids = {task.id for task in outcome.tasks}
    assert {"T2A", "T2B", "T2C", "T2D"}.issubset(task_ids)
    architecture_task = next(task for task in outcome.tasks if task.id == "T3")
    assert {"T2A", "T2B", "T2C", "T2D"}.issubset(set(architecture_task.depends_on))


def test_validation_feedback_drives_targeted_repair():
    analysis = RequirementAgent().analyze(MANDATORY)
    architecture = ArchitectureAgent().design(analysis)
    generator = GenerationAgent()
    validator = ValidationAgent()

    artifacts = generator.generate(analysis, architecture)
    artifacts["generated/openapi.yaml"] = "openapi: 3.1.0\npaths: {}\n"

    failed = validator.validate(analysis, artifacts)
    assert failed.passed is False
    assert "Repair failed validation: contract_consistency" in failed.repair_actions

    repaired = generator.repair(analysis, architecture, artifacts, failed)
    validated = validator.validate(analysis, repaired)
    assert validated.passed is True
