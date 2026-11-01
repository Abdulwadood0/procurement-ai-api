from typing import Any, Literal, NotRequired, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    question: str
    messages: Annotated[list[AnyMessage], add_messages]
    requires_query: NotRequired[bool]
    query_type: NotRequired[Literal["find", "aggregate"]]
    query: NotRequired[dict[str, Any]]
    pipeline: NotRequired[list[dict[str, Any]]]
    results: NotRequired[list[dict[str, Any]]]
    answer: NotRequired[str]
    error_message: NotRequired[str | None]
    retry_count: NotRequired[int]