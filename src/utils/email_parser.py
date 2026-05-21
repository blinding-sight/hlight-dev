import re
from typing import Optional, Dict

URL_REGEX = re.compile(r"https?://[^\s]+")
TIMECODE_REGEX = re.compile(r"\b(?:\d{1,2}:)?\d{1,2}:\d{2}\b|\b\d{1,2}\b")

def parse_email_body(body: str) -> Optional[Dict[str, str]]:
    """
    Extract:
      - video_url
      - start_time
      - end_time
      - label (optional)
    from a plain-text email body.
    """

    text = body.strip()

    # Extract URL
    urls = URL_REGEX.findall(text)
    if not urls:
        return None
    video_url = urls[0]

    # Extract timecodes
    times = TIMECODE_REGEX.findall(text)
    if len(times) < 2:
        return None

    start_time = times[0]
    end_time = times[1]

    # Extract label (optional)
    label = "clip"
    for line in text.splitlines():
        if line.lower().startswith(("label", "title")):
            _, _, val = line.partition(":")
            if val.strip():
                label = val.strip()
                break

    return {
        "video_url": video_url,
        "start_time": start_time,
        "end_time": end_time,
        "label": label,
    }
