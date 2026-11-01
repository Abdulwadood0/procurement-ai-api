from datetime import datetime
from typing import Any
from bson import ObjectId


DATE_FIELDS = {"creation_date", "purchase_date"}

def convert_date_filters(query: dict[str, Any]) -> dict[str, Any]:
    """Convert ISO date strings in date filters to Python datetime objects."""

    converted = {}

    for field, value in query.items():
        if field in {"$and", "$or"}:
            converted[field] = [
                convert_date_filters(condition) for condition in value
            ]

        elif field in DATE_FIELDS:
            def to_datetime(item: Any) -> Any:
                if isinstance(item, str):
                    return datetime.fromisoformat(item.replace("Z", "+00:00"))
                return item

            if isinstance(value, dict):
                converted[field] = {
                    operator: (
                        [to_datetime(item) for item in operand]
                        if isinstance(operand, list)
                        else to_datetime(operand)
                    )
                    for operator, operand in value.items()
                }
            elif isinstance(value, list):
                converted[field] = [to_datetime(item) for item in value]
            else:
                converted[field] = to_datetime(value)

        else:
            converted[field] = value

    return converted



def serialize_mongo_results(results: list[dict]) -> list[dict]:
    for document in results:
        if isinstance(document.get("_id"), ObjectId):
            document["_id"] = str(document["_id"])

    return results
