# Generated from contracts/v2; do not edit.
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeRevision(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    documentId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    proposalId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    commit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    sha256: str = Field(pattern='^([a-f0-9]{64})?$')
    createdAt: str
    author: str
