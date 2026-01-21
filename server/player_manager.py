import os
import sys
import json
import threading
import tempfile
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import log

LEADERBOARD_FILE = os.path.join(project_root, "leaderboard.json")
leaderboard_lock = threading.Lock()

def _load_leaderboard_unlocked() -> dict:
    if not os.path.exists(LEADERBOARD_FILE):
        return {}

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception as e:
        log(f"[Leaderboard] Lỗi đọc file, reset leaderboard: {e}")
        return {}

def _save_leaderboard_unlocked(data: dict):
    try:
        dir_name = os.path.dirname(LEADERBOARD_FILE)
        with tempfile.NamedTemporaryFile(
            "w", delete=False, dir=dir_name, encoding="utf-8"
        ) as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=4)
            tmp_path = tmp.name

        shutil.move(tmp_path, LEADERBOARD_FILE)
    except Exception as e:
        log(f"[Leaderboard] Lỗi ghi file: {e}")

def load_leaderboard() -> dict:
    with leaderboard_lock:
        return _load_leaderboard_unlocked()

def save_leaderboard(data: dict):
    with leaderboard_lock:
        _save_leaderboard_unlocked(data)

def update_score(username: str, delta: int):
    if not username:
        return

    username = username.strip()
    if not username or username.lower() == "guest":
        return

    with leaderboard_lock:
        leaderboard = _load_leaderboard_unlocked()
        old_score = leaderboard.get(username, 0)
        new_score = old_score + int(delta)
        leaderboard[username] = new_score
        _save_leaderboard_unlocked(leaderboard)

    sign = "+" if delta > 0 else ""
    log(f"[Leaderboard] {username} {sign}{delta} ({old_score} -> {new_score})")

def get_top_players(n: int = 10):
    with leaderboard_lock:
        leaderboard = _load_leaderboard_unlocked()

    if not leaderboard:
        return []

    return sorted(
        leaderboard.items(), key=lambda x: x[1], reverse=True
    )[:n]
