from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from procurement_ai_api.api.routes.chat import router as chat_router


app = FastAPI()
app.include_router(chat_router)
client = TestClient(app)


class TestChatEndpoint:
    @patch("procurement_ai_api.api.routes.chat.stream_chat")
    def test_chat_endpoint_success(self, mock_stream):
        async def dummy_generator(question, thread_id):
            yield "event: token\ndata: {\"token\": \"Hello\"}\n\n"
            yield f"event: done\ndata: {{\"thread_id\": \"{thread_id}\", \"answer\": \"Hello\"}}\n\n"

        mock_stream.side_effect = dummy_generator

        response = client.post(
            "/chat/",
            json={"question": "What is the total spend in 2014?", "thread_id": "test-session-123"},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert response.headers["cache-control"] == "no-cache"
        assert "event: token" in response.text
        assert "test-session-123" in response.text
        mock_stream.assert_called_once_with("What is the total spend in 2014?", "test-session-123")

    @patch("procurement_ai_api.api.routes.chat.stream_chat")
    def test_chat_endpoint_generates_thread_id_if_omitted(self, mock_stream):
        async def dummy_generator(question, thread_id):
            yield f"event: done\ndata: {{\"thread_id\": \"{thread_id}\"}}\n\n"

        mock_stream.side_effect = dummy_generator

        response = client.post("/chat/", json={"question": "Show all suppliers"})

        assert response.status_code == 200
        # Ensure a generated thread_id was passed
        called_question, called_thread_id = mock_stream.call_args[0]
        assert called_question == "Show all suppliers"
        assert isinstance(called_thread_id, str)
        assert len(called_thread_id) > 0

    def test_chat_endpoint_validation_error(self):
        # Missing required 'question' field
        response = client.post("/chat/", json={"thread_id": "123"})
        assert response.status_code == 422
