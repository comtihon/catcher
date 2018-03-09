TIME_MAPPING = [
    ('days', 86400),
    ('hours', 3600),
    ('minutes', 60),
    ('seconds', 1),
    ('microseconds', 0.001),
    ('milliseconds', 0.000001),
    ('nanoseconds', 0.000000001)
]


def to_seconds(body: dict) -> int:
    return sum([compute_time(t, body, m) for (t, m) in TIME_MAPPING])


def compute_time(key: str, body: dict, to_second: float) -> int:
    return body.get(key, 0) * to_second
