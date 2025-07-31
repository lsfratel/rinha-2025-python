from datetime import datetime


def iso_to_unix(iso8601: str) -> int:
    dt = datetime.fromisoformat(iso8601.replace("Z", "+00:00"))
    return dt.timestamp()
