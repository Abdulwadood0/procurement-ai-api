from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage
from langgraph.types import RetryPolicy

from procurement_ai_api.agent.nodes import (
    execute_query,
    generate_answer,
    generate_query,
    validate_generated_query,
    add_user_message,
    return_error,
)
from procurement_ai_api.agent.routing import (
    route_after_validation,
    route_after_query
)
from procurement_ai_api.agent.state import AgentState





builder = StateGraph(AgentState)

# Nodes
builder.add_node("generate_query", generate_query)
builder.add_node("validate", validate_generated_query)
builder.add_node(
    "generate_answer",
    generate_answer,
    retry_policy=RetryPolicy(max_attempts=3),
)
builder.add_node(
    "execute",
    execute_query,
    retry_policy=RetryPolicy(max_attempts=3),
)
builder.add_node("failed", return_error)
builder.add_node("add_user_message", add_user_message)

# Starting point
builder.add_edge(START, "add_user_message")
builder.add_edge("add_user_message", "generate_query")

# builder.add_edge("generate_query", "validate")

# After generating a query
builder.add_conditional_edges(
    "generate_query",
    route_after_query,
    {
        "generate_answer": "generate_answer",
        "failed" : "failed"
    },
)
   


# After validation
builder.add_conditional_edges(
    "validate",
    route_after_validation,
    {
        "execute": "execute",
        "retry": "generate_query",
        "failed": "failed",
    },
)

# Successful execution
builder.add_edge("execute", "generate_answer")
builder.add_edge("generate_answer", END)

# Terminal paths
builder.add_edge("failed", END)

checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)