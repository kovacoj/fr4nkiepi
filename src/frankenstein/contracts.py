from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Permissions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    network_hosts: list[str] = Field(default_factory=list)
    filesystem_read: list[str] = Field(default_factory=list)
    filesystem_write: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)


class Provenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origin: Literal[
        "generated", "existing_registry", "github", "gitlab", "apify", "operator"
    ]
    source_url: str | None = None
    source_revision: str | None = None
    artifact_sha256: str
    license: str | None = None
    generated_by_execution_id: str | None = None


class VerificationPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suite: str
    independent: bool = True
    permission_tests_required: bool = True
    regression_tests_required: bool = True


class CapabilityManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_.-]+$")
    name: str = Field(min_length=1, max_length=120)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    kind: Literal["skill", "mcp_proxy", "executable_tool", "python_adapter", "workflow"]
    domain: Literal["task", "capability_management"]
    summary: str = Field(min_length=1, max_length=240)
    entrypoint: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    requires: list[str] = Field(default_factory=list)
    permissions: Permissions = Field(default_factory=Permissions)
    provenance: Provenance
    verification: VerificationPolicy
    created_at: datetime


class ReleaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str = Field(min_length=1)
    releases: list[dict[str, Any]]


class NormalizedRelease(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tag: str
    title: str
    published_at: str | None
    url: str | None
    prerelease: bool
    changes: list[str]


class ReleaseOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str
    release_count: int = Field(ge=0)
    releases: list[NormalizedRelease]


class IssueInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str = Field(min_length=1)
    issues: list[dict[str, Any]]


class IssueRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    url: str | None
    risk: Literal["high", "medium", "low"]
    reasons: list[str]


class IssueRiskOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str
    issue_count: int = Field(ge=0)
    high_risk_count: int = Field(ge=0)
    issues: list[IssueRisk]


class ReadinessInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str = Field(min_length=1)
    releases: list[dict[str, Any]]
    issues: list[dict[str, Any]]


class ReadinessOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str
    status: Literal["ready", "caution", "blocked"]
    latest_release: str | None
    blocker_count: int = Field(ge=0)
    summary: str
