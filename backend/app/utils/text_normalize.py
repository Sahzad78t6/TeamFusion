import re
from typing import Iterable


def normalize_role_string(value: str) -> str:
    if not value:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    return text.title()


def normalize_skills(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    for value in values:
        if not value:
            continue
        text = str(value).strip()
        if not text:
            continue
        clean = re.sub(r"\s+", " ", text)
        normalized.append(clean)
    return normalized
