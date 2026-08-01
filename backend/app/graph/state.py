from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    user_id: str
    input_text: str
    current_node: str
    context: Dict[str, Any]
    output: Optional[str]
    history: List[str]
