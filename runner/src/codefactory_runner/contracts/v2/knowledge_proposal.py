# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeProposal(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    scopeId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    documentId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    baseRevision: str
    baseCommit: str
    body: str = Field(max_length=200000)
    reason: str = Field(min_length=1, max_length=4000)
    evidence: list[str]
    risks: str
    author: str
    executionId: str
    state: Literal['proposed', 'validated', 'approved', 'rejected', 'promoting', 'promoted', 'conflict']
    version: int = Field(ge=0)
    diff: str
    createdAt: str
