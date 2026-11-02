# Generated from contracts/v1; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContextPackageDocumentsItem(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    documentId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    revisionId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    sha256: str = Field(pattern='^[a-f0-9]{64}$')
    scope: Literal['global', 'project']
    status: Literal['official', 'candidate']
    required: bool
