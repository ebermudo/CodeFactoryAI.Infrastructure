# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContextRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    requestId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    projectId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    taskId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    role: Literal['specification', 'architect', 'developer', 'qa', 'review-correctness', 'review-architecture', 'review-security', 'review-testing', 'finding-verifier', 'approval']
    goal: str = Field(min_length=1, max_length=4000)
    restrictions: list[str]
    referenceCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    budgetTokens: int = Field(ge=512, le=200000)
    additionalDocumentIds: list[str]
