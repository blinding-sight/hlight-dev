import os
from utils.logger import setup_logger

logger = setup_logger("drive_uploader")

def upload_to_drive(file_path: str) -> str:
    """
    Placeholder for Google Drive upload.
    For now, just log and return a fake URL.
    Later you can integrate rclone or the Drive API here.
    """
    file_path = os.path.abspath(file_path)
    logger.info(f"(Stub) Uploading to Drive: {file_path}")

    # TODO: replace this with real upload logic
    fake_url = f"https://drive.example.com/fake/{os.path.basename(file_path)}"
    logger.info(f"(Stub) Drive URL: {fake_url}")
    return fake_url

if __name__ == "__main__":
    # Simple manual test
    test_path = "test_clip.mp4"
    print(upload_to_drive(test_path))
