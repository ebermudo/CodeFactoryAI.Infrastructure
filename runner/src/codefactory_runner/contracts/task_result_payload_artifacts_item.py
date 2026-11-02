# Generated from contracts/v1; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskResultPayloadArtifactsItem(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    artifactId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    kind: Literal['diff', 'test-report', 'review', 'document', 'log', 'source-manifest']
    sha256: str = Field(pattern='^[a-f0-9]{64}$')
