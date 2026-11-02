# Generated from contracts/v2; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BrainScope(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    label: str
    repositoryAlias: Literal['api', 'agents', 'infrastructure', 'client']
