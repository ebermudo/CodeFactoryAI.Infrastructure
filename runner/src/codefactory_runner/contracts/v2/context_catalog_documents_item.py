# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContextCatalogDocumentsItem(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    scopeId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=64)
    path: str = Field(min_length=1, max_length=180, pattern='^[a-z0-9][a-z0-9/_-]*\\.md$')
    ruleKind: Literal['mandatory', 'recommendation', 'example']
    version: int = Field(ge=0)
    revisionId: str
    commit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    sha256: str = Field(pattern='^([a-f0-9]{64})?$')
    content: str
    state: Literal['unpublished', 'official', 'stale']
