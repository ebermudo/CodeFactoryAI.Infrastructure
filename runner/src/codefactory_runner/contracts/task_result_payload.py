# Generated from contracts/v1; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .task_result_payload_artifacts_item import TaskResultPayloadArtifactsItem


class TaskResultPayload(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    outcome: Literal['succeeded', 'failed', 'cancelled', 'quota-blocked', 'unauthenticated']
    leaseToken: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    baseCommit: str = Field(pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    resultCommit: str | None = Field(default=None, pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    artifacts: list[TaskResultPayloadArtifactsItem]
    testRunIds: list[str]
    errorCode: str | None = Field(default=None, min_length=1, max_length=128)
