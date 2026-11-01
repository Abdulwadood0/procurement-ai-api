import json

from procurement_ai_api.agent.graph import graph
import logging

import json
import logging

logger = logging.getLogger(__name__)

async def stream_chat(question: str, thread_id: str):
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        async for message_chunk, metadata in graph.astream(
            {"question": question},
            config=config,
            stream_mode="messages",
        ):
            if metadata.get("langgraph_node") == "generate_answer":
                if message_chunk.content:
                    yield (
                        f"event: token\n"
                        f"data: {json.dumps({'token': message_chunk.content})}\n\n"
                    )

        state = await graph.aget_state(config)
        answer = state.values.get("answer", "")
        query = state.values.get("query", "")
        pipeline = state.values.get("pipeline", "")

       

        yield (
            f"event: done\n"
            f"data: {json.dumps({
                'thread_id': thread_id,
                'answer': answer,
                'query': query,
                'pipeline': pipeline
            })}\n\n"
        )

    except Exception:
        logger.exception(
            "Chat request failed | thread_id=%s",
            thread_id,
        )

        yield (
            f"event: error\n"
            f"data: {json.dumps({
                'message': 'An error occurred while processing your request.'
            })}\n\n"
        )