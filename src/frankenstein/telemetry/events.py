from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TelemetryEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    phase: Literal["build", "evaluation", "execution", "system"]
    task_id: UUID | None = None
    session_id: UUID | None = None
    execution_id: UUID | None = None
    subagent_execution_id: UUID | None = None
    capability_id: str | None = None
    capability_version: str | None = None
    tool_invocation_id: UUID | None = None
    llm_request_id: UUID | None = None
    evaluation_id: UUID | None = None
    provider: str | None = None
    model: str | None = None
    agent_role: str | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cache_read_tokens: int | None = Field(default=None, ge=0)
    cache_write_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    cost_usd: Decimal | None = Field(default=None, ge=0)
    cost_status: Literal["reported", "estimated", "unknown", "free"] | None = None
    pricing_source: str | None = None
    pricing_version: str | None = None
    latency_ms: int | None = Field(default=None, ge=0)
    success: bool | None = None
    retry: bool = False
    value: Decimal | None = None

    @model_validator(mode="after")
    def validate_time_and_cost(self):
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must include a UTC offset")
        self.timestamp = self.timestamp.astimezone(timezone.utc)
        if self.cost_status == "unknown" and self.cost_usd is not None:
            raise ValueError("unknown cost must not have a numeric value")
        if self.cost_status in {"reported", "estimated", "free"} and self.cost_usd is None:
            raise ValueError("known cost status requires cost_usd")
        if self.cost_status == "free" and self.cost_usd != 0:
            raise ValueError("free operations must have zero cost")
        return self
