import os
import threading
import time
import uuid
from pathlib import Path

TEMP_DIR = Path(__file__).parent.parent.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

_stop_event = threading.Event()


def get_temp_path(filename: str) -> Path:
    return TEMP_DIR / f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}_{filename}"


def cleanup_expired(max_age_seconds: int = 1800):
    now = time.time()
    for f in TEMP_DIR.iterdir():
        if f.is_file() and now - f.stat().st_mtime > max_age_seconds:
            try:
                f.unlink()
            except FileNotFoundError:
                pass


def start_cleanup_scheduler():
    def _loop():
        while not _stop_event.is_set():
            _stop_event.wait(300)
            if not _stop_event.is_set():
                cleanup_expired()

    t = threading.Thread(target=_loop, daemon=True)
    t.start()


def stop_cleanup_scheduler():
    _stop_event.set()
