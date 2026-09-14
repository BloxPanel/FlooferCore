def parse_duration(value: str) -> int:
    """
    Convert a human-readable duration into seconds.

    Examples:
        30   -> 30
        30s  -> 30
        5m   -> 300
        2h   -> 7200
        1d   -> 86400
    """

    value = value.strip().lower()

    if value.isdigit():
        return int(value)

    if len(value) < 2:
        raise ValueError("Invalid duration format")

    unit = value[-1]
    number = value[:-1]

    if not number.isdigit():
        raise ValueError("Invalid duration format")

    amount = int(number)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    if unit not in multipliers:
        raise ValueError("Invalid duration unit")

    return amount * multipliers[unit]
