# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .context_snapshot_package_documents_item import ContextSnapshotPackageDocumentsItem


class ContextSnapshotPackage(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    schemaVersion: Literal['2.0.0']
    snapshotId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    projectId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    taskId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    role: Literal['specification', 'architect', 'developer', 'qa', 'review-correctness', 'review-architecture', 'review-security', 'review-testing', 'finding-verifier', 'approval']
    goal: str
    restrictions: list[str]
    referenceCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    knowledgeCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    globalCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    contractsVersion: Literal['2.0.0']
    budgetTokens: int = Field(ge=512, le=200000)
    estimatedTokens: int = Field(ge=0)
    budgetMethod: Literal['utf8-byte-upper-bound']
    sourceTrust: Literal['context-only']
    documents: list[ContextSnapshotPackageDocumentsItem]
