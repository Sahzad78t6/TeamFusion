def format_reflection_summary(notes: str, risk_level: str) -> str:
    summary_notes = notes[:60] + "..." if len(notes) > 60 else notes
    return f"Reflection ({risk_level}): '{summary_notes}'"
