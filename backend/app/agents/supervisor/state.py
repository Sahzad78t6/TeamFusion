from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    user_id: str
    messages: List[Dict[str, str]]
    next_step: Optional[str]
    context: Dict[str, Any]
    output: Optional[str]
