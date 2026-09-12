from pathlib import Path

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
    assert (tmp_path / outcome.run_id / "ENGINEERING_SUMMARY.md").exists()


def test_ambiguous_requirement_is_flagged(tmp_path: Path):
    outcome = WorkflowOrchestrator(str(tmp_path)).run("Make the API fast and secure")
    assert outcome.analysis.ambiguities
    assert outcome.approval_status == "awaiting_human_approval"


def test_brownfield_codebase_reasoning(tmp_path: Path):
    codebase = tmp_path / "existing"
    codebase.mkdir()
    (codebase / "api_routes.py").write_text("def route(): pass\n")
    (codebase / "service.py").write_text("def service(): pass\n")
    outcome = WorkflowOrchestrator(str(tmp_path / "out")).run("Enhance the existing API with analytics", str(codebase))
    assert outcome.analysis.scenario == "brownfield"
