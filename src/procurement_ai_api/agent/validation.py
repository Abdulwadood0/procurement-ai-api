from typing import Any

ALLOWED_FIELDS = {
    "creation_date",
    "purchase_date",
    "fiscal_year",
    "purchase_order_number",
    "acquisition_type",
    "acquisition_method",
    "department_name",
    "supplier_code",
    "supplier_name",
    "supplier_qualifications",
    "supplier_zip_code",
    "calcard",
    "item_name",
    "item_description",
    "quantity",
    "unit_price",
    "total_price",
    "classification_codes",
    "normalized_unspsc",
    "commodity_title",
    "class",
    "class_title",
    "family",
    "family_title",
    "segment",
    "segment_title",
    "location",
    "lpa_number",
    "requisition_number",
    "subacquisition_type",
    "subacquisition_method",
}



ALLOWED_STAGES = {
    "$match", "$group", "$sort", "$limit", "$project", 
}

ALLOWED_OPERATORS = {
    # Query operators
    "$eq", "$gt", "$gte", "$lt", "$lte",
    "$in", "$and", "$or",
    "$regex", "$options", "$exists",

    # Aggregation operators
    "$sum", "$avg", "$min", "$max", "$push",
    "$subtract", "$cond",
    "$arrayElemAt", "$filter",

    # Date and arithmetic operators
    "$year", "$month", "$ceil", "$divide",

    # String operators
    "$toLower",

    # Expression operator
    "$expr",

    # Pipeline stages
    *ALLOWED_STAGES,
}


def validate_pipeline(pipeline: list[dict]) -> None:
    for stage in pipeline:
        if not isinstance(stage, dict) or len(stage) != 1:
            raise ValueError("Each pipeline stage must have one operator.")

        stage_name = next(iter(stage))

        if stage_name not in ALLOWED_STAGES:
            raise ValueError(f"Unsupported pipeline stage: {stage_name}")

        def check_operators(value):
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    if key.startswith("$") and key not in ALLOWED_OPERATORS:
                        raise ValueError(f"Unsupported operator: {key}")
                    check_operators(nested_value)

            elif isinstance(value, list):
                for item in value:
                    check_operators(item)

        check_operators(stage)


def validate_query(query: dict[str, Any]) -> None:
    """Raise ValueError if the generated MongoDB filter is unsafe."""

    if not isinstance(query, dict) or not query:
        raise ValueError("Query must be a non-empty dictionary.")

    def validate_filter(filter_doc: dict[str, Any]) -> None:
        for key, value in filter_doc.items():
            if key in {"$and", "$or"}:
                if not isinstance(value, list) or not value:
                    raise ValueError(f"{key} must contain a non-empty list.")

                for condition in value:
                    if not isinstance(condition, dict):
                        raise ValueError(f"Each {key} condition must be a dictionary.")
                    validate_filter(condition)

            elif key.startswith("$"):
                if key not in ALLOWED_OPERATORS:
                    raise ValueError(f"Unsupported MongoDB operator: {key}")

            elif key not in ALLOWED_FIELDS:
                raise ValueError(f"Unsupported database field: {key}")

            elif isinstance(value, dict):
                for operator in value:
                    if operator not in ALLOWED_OPERATORS - {"$and", "$or"}:
                        raise ValueError(f"Unsupported field operator: {operator}")


    validate_filter(query)
