def parse_timecode(tc: str) -> int:
    """
    Convert a timecode string into total seconds.
    Accepts:
      - SS
      - M:SS
      - H:MM:SS
    """
    tc = tc.strip()
    parts = tc.split(":")

    if not all(p.isdigit() for p in parts):
        raise ValueError(f"Invalid timecode: {tc}")

    parts = [int(p) for p in parts]

    if len(parts) == 1:
        s = parts[0]
        m = h = 0
    elif len(parts) == 2:
        m, s = parts
        h = 0
    elif len(parts) == 3:
        h, m, s = parts
    else:
        raise ValueError(f"Invalid timecode: {tc}")

    return h * 3600 + m * 60 + s
