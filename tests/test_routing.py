from procurement_ai_api.agent.routing import route_after_query, route_after_validation
from procurement_ai_api.core.config import settings


class TestRouteAfterQuery:
    def test_routes_to_validate_when_query_required(self):
        state = {"requires_query": True}
        assert route_after_query(state) == "validate"

    def test_routes_to_generate_answer_when_query_not_required(self):
        state = {"requires_query": False}
        assert route_after_query(state) == "generate_answer"

    def test_routes_to_generate_answer_by_default(self):
        state = {}
        assert route_after_query(state) == "generate_answer"


class TestRouteAfterValidation:
    def test_routes_to_execute_on_success(self):
        state = {"error_message": None}
        assert route_after_validation(state) == "execute"

    def test_routes_to_retry_when_under_max_retries(self):
        state = {"error_message": "Invalid field", "retry_count": 1}
        assert settings.MAX_RETRIES >= 1
        assert route_after_validation(state) == "retry"

    def test_routes_to_failed_when_max_retries_exceeded(self):
        state = {
            "error_message": "Repeated syntax error",
            "retry_count": settings.MAX_RETRIES + 1,
        }
        assert route_after_validation(state) == "failed"
