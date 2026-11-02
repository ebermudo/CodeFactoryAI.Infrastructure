# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeApproval(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    proposalId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    decision: Literal['approved', 'rejected']
    expectedVersion: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=4000)
