import json
import re
from typing import Any

def parse_json_from_llm(llm_output: str) -> Any:
    try:
        # Check if wrapped in ```json ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", llm_output)
        if match:
            return json.loads(match.group(1))
        return json.loads(llm_output)
    except Exception:
        return {"raw_text": llm_output}
