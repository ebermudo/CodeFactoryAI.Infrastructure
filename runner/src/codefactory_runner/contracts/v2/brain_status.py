# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BrainStatus(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    scopeId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    state: Literal['empty', 'available', 'stale', 'pending', 'error']
    referenceCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    knowledgeCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    documentCount: int = Field(ge=0)
    pendingProposals: int = Field(ge=0)
    rscInstalled: Literal[False]
    autonomousExecutionEnabled: Literal[False]
