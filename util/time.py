
def format_time(ms: float) -> str:
    seconds = int(ms / 1000)
    minutes = seconds // 60
    remaining = seconds % 60

    return f"{minutes}:{remaining:02d}"
