from procurement_ai_api.agent.state import AgentState
from procurement_ai_api.core.config import settings



def route_after_validation(state: AgentState) -> str:
    if state.get("error_message") is None:
        return "execute"

    if state.get("retry_count", 0) <= settings.MAX_RETRIES:
        return "retry"

    return "failed"

def route_after_query(state: AgentState) -> str:
    if state.get("requires_query"):
        return "validate"

    return "generate_answer"