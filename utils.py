from pathlib import Path


UPLOAD_DIR = Path("uploads")

DEMO_DIR = Path("demo_papers")


def create_directories():

    UPLOAD_DIR.mkdir(exist_ok=True)

    DEMO_DIR.mkdir(exist_ok=True)