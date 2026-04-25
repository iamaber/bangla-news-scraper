def normalize_text(value: object) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())
