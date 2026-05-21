import os
from utils.logger import setup_logger

logger = setup_logger("proxy_config")

def apply_proxy_settings():
    """
    Apply proxy settings from environment variables.
    Supports:
      HTTP_PROXY
      HTTPS_PROXY
    """
    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")

    if http_proxy:
        os.environ["HTTP_PROXY"] = http_proxy
        logger.info(f"HTTP proxy set: {http_proxy}")

    if https_proxy:
        os.environ["HTTPS_PROXY"] = https_proxy
        logger.info(f"HTTPS proxy set: {https_proxy}")

    if not http_proxy and not https_proxy:
        logger.info("No proxy settings found")

if __name__ == "__main__":
    apply_proxy_settings()
