# Generated from contracts/v1; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskRequestedPayload(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    projectId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    role: Literal['specification', 'architect', 'developer', 'qa', 'review-correctness', 'review-architecture', 'review-security', 'review-testing', 'finding-verifier', 'approval']
    workspaceId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    contextSnapshotId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    specificationRevisionId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    expectedCommit: str = Field(pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    deadlineAt: str
    leaseToken: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    policyVersion: str = Field(min_length=1, max_length=64)
