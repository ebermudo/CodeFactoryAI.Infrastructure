# Generated from contracts/v1; do not edit.
from pydantic import BaseModel, ConfigDict, Field

from .context_package_documents_item import ContextPackageDocumentsItem


class ContextPackage(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    snapshotId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    projectId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    taskId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    policyVersion: str = Field(min_length=1)
    createdAt: str
    repositoryCommit: str = Field(pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    globalKnowledgeCommit: str = Field(pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    projectKnowledgeCommit: str = Field(pattern='^[a-f0-9]{40}([a-f0-9]{24})?$')
    budgetTokens: int = Field(ge=1, le=200000)
    documents: list[ContextPackageDocumentsItem]
