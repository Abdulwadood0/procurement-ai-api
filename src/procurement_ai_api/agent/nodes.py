
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from procurement_ai_api.agent.prompts import ANSWER_SYSTEM_PROMPT
from procurement_ai_api.agent.prompts import MQL_SYSTEM_PROMPT
from procurement_ai_api.agent.schemas import QueryGeneration
from procurement_ai_api.agent.state import AgentState
from procurement_ai_api.core.config import settings
from procurement_ai_api.core.database import db_manager
from procurement_ai_api.agent.validation import validate_query, validate_pipeline
from procurement_ai_api.agent.helpers import convert_date_filters, serialize_mongo_results



import json
from copy import deepcopy
import logging
from copy import deepcopy
from time import perf_counter

logger = logging.getLogger(__name__)




llm = ChatOpenAI(
    model=settings.AI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0,
)

query_generator = llm.with_structured_output(
    QueryGeneration,
    method="function_calling",
)

max_msgs = settings.MAX_HISTORY_MESSAGES



async def generate_query(state: AgentState) -> dict:


    error_message = state.get("error_message")
    history = state.get("messages", [])[-max_msgs:]

    messages = [
    ("system", MQL_SYSTEM_PROMPT),
    *history,
    ]

    if error_message:
            messages.append(
            HumanMessage(
                content=f"""
                Your previous query failed validation.

                Error:
                {error_message}

                Generate a corrected MongoDB query.
                Preserve the user's original intent.
                Use only supported operators.
                """
                )
            )
    
    response = await query_generator.ainvoke(messages)


    return {
        "requires_query": response.requires_query,
        "query_type": response.query_type,
        "query": response.query,
        "pipeline": response.pipeline,

    }








async def execute_query(state: AgentState) -> dict:
    query_type = state["query_type"]
    query_type = state["query_type"]

    start_time = perf_counter()

    logger.info("Executing MongoDB query | type=%s", query_type)

    try:
        db = db_manager.get_db()
        collection = db["purchases"]

        if query_type == "find":
            query = deepcopy(state["query"])
            query = convert_date_filters(query)

            cursor = collection.find(query).limit(20)
            results = await cursor.to_list(length=20)

        elif query_type == "aggregate":
            pipeline = deepcopy(state["pipeline"])

            for stage in pipeline:
                if "$match" in stage:
                    stage["$match"] = convert_date_filters(stage["$match"])

            cursor = await collection.aggregate(
                pipeline,
                maxTimeMS=10_000,
            )
            results = await cursor.to_list(length=100)

        else:
            raise ValueError(f"Unsupported query type: {query_type}")

        duration = perf_counter() - start_time

        logger.info(
            "MongoDB query completed | type=%s | results=%d | duration=%.2fs",
            query_type,
            len(results),
            duration,
        )

        return {"results": serialize_mongo_results(results)}

    except Exception:
        logger.exception(
            "MongoDB query failed | type=%s",
            query_type,
        )
        raise


async def generate_answer(state: AgentState) -> dict:
    """Turn retrieved database records into a grounded natural-language answer."""

    start_time = perf_counter()

    results = state.get("results", [])
    history = state.get("messages", [])[-max_msgs:]
    question = state["question"]

    logger.info(
        "Generating answer | documents=%d | history_messages=%d",
        len(results),
        len(history),
    )

    messages = [
        ("system", ANSWER_SYSTEM_PROMPT),
        *history,
        (
            "human",
            f"""
            User question:
            {question}

            MongoDB filter used:
            {json.dumps(state.get("query", {}), default=str)}

            Number of documents returned:
            {len(results)}

            Important: results are capped at 20 documents.
            This is not necessarily the total number of matching documents.

            Retrieved documents:
            {json.dumps(results, default=str, ensure_ascii=False)}
            """,
        ),
    ]

    try:
        response = await llm.ainvoke(messages)
        answer = response.content

        duration = perf_counter() - start_time

        logger.info(
            "Answer generated successfully | duration=%.2fs | documents=%d",
            duration,
            len(results),
        )

        return {
            "answer": answer,
            "messages": [AIMessage(content=answer)],
        }

    except Exception:
        logger.exception(
            "Answer generation failed | documents=%d",
            len(results),
        )
        raise




async def validate_generated_query(state: AgentState) -> dict:
    query_type = state["query_type"]
    user_question = state["question"]
    try:
        if query_type == "find":
            validate_query(state["query"])

        elif query_type == "aggregate":
            validate_pipeline(state["pipeline"])

        else:
            raise ValueError("Unsupported query type.")

        logger.debug(
            "Query validation successful | type=%s",
            query_type,
        )

        return {"error_message": None}

    except (ValueError, TypeError) as e:
        retry_count = state.get("retry_count", 0) + 1

        logger.warning(
        "Query validation failed | type = %s | question = %s | retry = %d | reason = %s",
        query_type,
        user_question,
        retry_count,
        e,
)

        return {
            "error_message": str(e),
            "retry_count": retry_count,
        }


    
async def add_user_message(state: AgentState) -> dict:
    return {
        "messages": [
            HumanMessage(content=state["question"])
        ],
        "error_message": None,
        "retry_count": 0,
        "query": {},
        "pipeline": [],
        "results": [],

    }


async def return_error(state: AgentState) -> dict:
    return {
        "answer": (
            "I couldn't generate a valid database query."
            "Please try rephrasing your question."
        )
    }
