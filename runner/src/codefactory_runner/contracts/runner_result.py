# Generated from contracts/v1; do not edit.
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RunnerResult(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    schemaVersion: Literal['1.0.0']
    attemptId: str = Field(pattern=r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
    state: Literal['disabled', 'unavailable', 'unauthenticated', 'quota-blocked', 'running', 'succeeded', 'failed', 'cancelled', 'unknown']
    reason: str = Field(min_length=1, max_length=256)
