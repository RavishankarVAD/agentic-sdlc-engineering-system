from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class RequirementAnalysis:
    original: str
    normalized: str
    intent: str
    scenario: str
    ambiguities: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)


@dataclass
class Task:
    id: str
    title: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    owner_agent: str = "planner"
    status: str = "pending"


@dataclass
class ArchitectureDecision:
    components: list[str]
    data_flow: list[str]
    api_contracts: list[dict[str, Any]]
    persistence: str
    scalability: list[str]
    observability: list[str]
    security: list[str]
    tradeoffs: list[str]


@dataclass
class ValidationResult:
    passed: bool
    checks: list[dict[str, Any]]
    risks: list[str]
    repair_actions: list[str] = field(default_factory=list)


@dataclass
class EngineeringOutcome:
    run_id: str
    analysis: RequirementAnalysis
    tasks: list[Task]
    architecture: ArchitectureDecision
    artifacts: dict[str, str]
    validation: ValidationResult
    approval_status: str
    execution_log: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
