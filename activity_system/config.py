from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "activity.db"
EXPORT_DIR = BASE_DIR / "exports"
SESSION_TIMEOUT_SECONDS = 3
FRAME_WIDTH = 960
FRAME_HEIGHT = 540
JPEG_QUALITY = 80
