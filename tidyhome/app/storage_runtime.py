import os

from tinydb import TinyDB


DATA_DIR = os.environ.get("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "tidyhome.json")

os.makedirs(DATA_DIR, exist_ok=True)
_db = TinyDB(DB_PATH)

PHOTO_DIR = os.path.join(DATA_DIR, "photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

MAX_PHOTO_BYTES = 8 * 1024 * 1024
