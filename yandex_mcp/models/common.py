"""Base model for all Yandex MCP input models."""

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base model with strict validation: strips whitespace, forbids extra fields."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
