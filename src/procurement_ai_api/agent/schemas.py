
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class QueryGeneration(BaseModel):
    """Structured output returned by the MQL generation model."""

    query_type: Literal["find", "aggregate"] = Field(
        description="Use find for retrieving records and aggregate for analytics."
    )

    query: dict[str, Any] = Field(
        description="MongoDB find filter. Use an empty dictionary for aggregation."
    )

    pipeline: list[dict[str, Any]] = Field(
        description=(
            "MongoDB aggregation pipeline. Use an empty list for find queries."
        )
    )

    requires_query: bool = Field(
        description="Whether the user needs information from the procurement database."
    )


    

