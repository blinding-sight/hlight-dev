import os
from utils.logger import setup_logger

logger = setup_logger("cookie_extractor")

DEFAULT_COOKIES_PATH = os.getenv("YTDLP_COOKIES_FILE", "cookies.txt")

def get_cookies_file() -> str | None:
    """
    Return path to cookies.txt if it exists, otherwise None.
    You can point YTDLP_COOKIES_FILE to a custom path.
    """
    path = DEFAULT_COOKIES_PATH
    if os.path.exists(path):
        logger.info(f"Using cookies file: {path}")
        return path

    logger.warning(f"No cookies file found at {path}. Continuing without cookies.")
    return None

if __name__ == "__main__":
    # Simple manual test
    print(get_cookies_file())
