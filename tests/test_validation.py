import pytest
from procurement_ai_api.agent.validation import validate_query, validate_pipeline


class TestValidateQuery:
    def test_valid_simple_query(self):
        query = {"supplier_name": "OSHA Review Inc"}
        validate_query(query)  # Should not raise

    def test_valid_query_with_operators(self):
        query = {
            "total_price": {"$gt": 100, "$lte": 5000},
            "department_name": {"$in": ["Water Resources", "Transportation"]},
        }
        validate_query(query)

    def test_valid_logical_and_or_query(self):
        query = {
            "$or": [
                {"department_name": "Corrections"},
                {"total_price": {"$gte": 50000}},
            ]
        }
        validate_query(query)

    def test_empty_query_raises_value_error(self):
        with pytest.raises(ValueError, match="Query must be a non-empty dictionary"):
            validate_query({})

    def test_invalid_field_raises_value_error(self):
        query = {"unsupported_custom_field": "val"}
        with pytest.raises(ValueError, match="Unsupported database field"):
            validate_query(query)

    def test_disallowed_operator_raises_value_error(self):
        query = {"$where": "this.total_price > 100"}
        with pytest.raises(ValueError, match="Unsupported MongoDB operator"):
            validate_query(query)

    def test_invalid_field_operator_raises_value_error(self):
        query = {"total_price": {"$accumulator": {}}}
        with pytest.raises(ValueError, match="Unsupported field operator"):
            validate_query(query)

    def test_logical_operator_empty_list_raises_value_error(self):
        query = {"$and": []}
        with pytest.raises(ValueError, match="must contain a non-empty list"):
            validate_query(query)


class TestValidatePipeline:
    def test_valid_pipeline(self):
        pipeline = [
            {"$match": {"fiscal_year": "2014-2015"}},
            {
                "$group": {
                    "_id": "$department_name",
                    "total_spend": {"$sum": "$total_price"},
                }
            },
            {"$sort": {"total_spend": -1}},
            {"$limit": 10},
        ]
        validate_pipeline(pipeline)  # Should not raise

    def test_unsupported_stage_raises_value_error(self):
        pipeline = [
            {"$out": "backup_collection"}
        ]
        with pytest.raises(ValueError, match="Unsupported pipeline stage: \\$out"):
            validate_pipeline(pipeline)

    def test_stage_with_multiple_keys_raises_value_error(self):
        pipeline = [
            {"$match": {"department_name": "Water"}, "$sort": {"total_price": 1}}
        ]
        with pytest.raises(ValueError, match="must have one operator"):
            validate_pipeline(pipeline)

    def test_unsupported_nested_operator_raises_value_error(self):
        pipeline = [
            {"$group": {"_id": "$supplier_name", "data": {"$function": {}}}}
        ]
        with pytest.raises(ValueError, match="Unsupported operator: \\$function"):
            validate_pipeline(pipeline)
