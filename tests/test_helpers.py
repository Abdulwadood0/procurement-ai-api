from datetime import datetime, timezone
from bson import ObjectId
from procurement_ai_api.agent.helpers import convert_date_filters, serialize_mongo_results


class TestConvertDateFilters:
    def test_converts_iso_string_to_datetime(self):
        query = {"creation_date": "2014-06-01T12:00:00Z"}
        converted = convert_date_filters(query)

        assert isinstance(converted["creation_date"], datetime)
        assert converted["creation_date"] == datetime(2014, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_converts_nested_operators(self):
        query = {
            "purchase_date": {
                "$gte": "2013-01-01T00:00:00Z",
                "$lte": "2013-12-31T23:59:59Z",
            }
        }
        converted = convert_date_filters(query)

        assert isinstance(converted["purchase_date"]["$gte"], datetime)
        assert isinstance(converted["purchase_date"]["$lte"], datetime)

    def test_converts_inside_and_or_arrays(self):
        query = {
            "$and": [
                {"creation_date": {"$gte": "2014-01-01T00:00:00Z"}},
                {"department_name": "Transportation"},
            ]
        }
        converted = convert_date_filters(query)

        assert isinstance(converted["$and"][0]["creation_date"]["$gte"], datetime)
        assert converted["$and"][1]["department_name"] == "Transportation"

    def test_leaves_non_date_fields_unaltered(self):
        query = {
            "supplier_name": "Grainger",
            "total_price": {"$gt": 500},
        }
        converted = convert_date_filters(query)

        assert converted == query


class TestSerializeMongoResults:
    def test_serializes_object_id_to_string(self):
        oid = ObjectId()
        documents = [
            {"_id": oid, "item_name": "Safety Gloves", "total_price": 45.0},
            {"_id": "string-id-123", "item_name": "Hard Hat", "total_price": 25.0},
        ]

        serialized = serialize_mongo_results(documents)

        assert serialized[0]["_id"] == str(oid)
        assert isinstance(serialized[0]["_id"], str)
        assert serialized[1]["_id"] == "string-id-123"

    def test_empty_results_handled(self):
        assert serialize_mongo_results([]) == []
