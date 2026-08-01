
import json
import os
import threading

_LOCK = threading.Lock()
_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(_DATA_DIR, exist_ok=True)

_FILES = {
    "resources": "resources.json",
    "quizzes": "quizzes.json",
    "leaderboard": "leaderboard.json",
}


def _path(name):
    return os.path.join(_DATA_DIR, _FILES[name])


def _load(name):
    path = _path(name)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(name, data):
    path = _path(name)
    with _LOCK:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def get_resources(subject_id):
    return _load("resources").get(subject_id, [])


def add_resource(subject_id, title, url):
    data = _load("resources")
    data.setdefault(subject_id, []).append({"title": title, "url": url})
    _save("resources", data)


def get_all_quizzes():
    return _load("quizzes")


def get_quiz(quiz_id):
    return _load("quizzes").get(quiz_id)


def add_quiz(quiz_id, question, options, correct_index, hint=None):
    data = _load("quizzes")
    data[quiz_id] = {
        "question": question,
        "options": options,
        "correct": correct_index,
        "hint": hint,
    }
    _save("quizzes", data)


# ---------------- لوحة الصدارة (Leaderboard) ----------------
def record_answer(user_id, name, is_correct):
    data = _load("leaderboard")
    key = str(user_id)
    entry = data.get(key, {"name": name, "score": 0, "correct": 0, "total": 0})
    entry["name"] = name
    entry["total"] += 1
    if is_correct:
        entry["correct"] += 1
        entry["score"] += 1
    data[key] = entry
    _save("leaderboard", data)


def get_leaderboard(limit=10):
    data = _load("leaderboard")
    rows = [(v["name"], v["score"], v["correct"], v["total"]) for v in data.values()]
    rows.sort(key=lambda r: r[1], reverse=True)
    return rows[:limit]
