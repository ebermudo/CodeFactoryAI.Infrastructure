# Generated from contracts/v2; do not edit.
from pydantic import BaseModel, ConfigDict, Field

from .context_catalog_documents_item import ContextCatalogDocumentsItem


class ContextCatalog(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    projectId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    referenceCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    knowledgeCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    globalCommit: str = Field(pattern='^([a-f0-9]{40}([a-f0-9]{24})?)?$')
    documents: list[ContextCatalogDocumentsItem]
