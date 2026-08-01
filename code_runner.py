

import requests

PISTON_BASE = "https://emkc.org/api/v2/piston"

LANGUAGE_MAP = {
    "python": "python",
    "c": "c",
    "cpp": "cpp",
    "java": "java",
    "javascript": "javascript",
}

_runtime_versions = {}


def _load_runtimes():
    global _runtime_versions
    try:
        resp = requests.get(f"{PISTON_BASE}/runtimes", timeout=10)
        resp.raise_for_status()
        for r in resp.json():
            lang = r.get("language")
            if lang in LANGUAGE_MAP.values() and lang not in _runtime_versions:
                _runtime_versions[lang] = r.get("version")
    except Exception:
        pass  


def get_version(language):
    if not _runtime_versions:
        _load_runtimes()
    return _runtime_versions.get(language, "*")


def run_code(language_key, source_code, stdin=""):
    """
    ينفذ الكود ويرجع dict:
      {"ok": True, "output": "..."}  عند النجاح
      {"ok": False, "error": "..."}  عند الفشل
    """
    lang = LANGUAGE_MAP.get(language_key)
    if not lang:
        return {"ok": False, "error": "لغة غير مدعومة"}

    if not source_code or not source_code.strip():
        return {"ok": False, "error": "لم يتم إرسال أي كود"}

    payload = {
        "language": lang,
        "version": get_version(lang),
        "files": [{"content": source_code}],
        "stdin": stdin,
        "run_timeout": 5000,
        "compile_timeout": 10000,
    }

    try:
        resp = requests.post(f"{PISTON_BASE}/execute", json=payload, timeout=20)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        return {"ok": False, "error": f"تعذر الاتصال بخدمة التنفيذ ({e})"}

    compile_info = result.get("compile") or {}
    run_info = result.get("run") or {}

    parts = []
    if compile_info.get("stderr"):
        parts.append("🔧 أخطاء الترجمة:\n" + compile_info["stderr"].strip())

    stdout = (run_info.get("stdout") or "").strip()
    stderr = (run_info.get("stderr") or "").strip()

    if stdout:
        parts.append("📤 المخرجات:\n" + stdout)
    if stderr:
        parts.append("⚠️ أخطاء التنفيذ:\n" + stderr)
    if not parts:
        parts.append("(لا توجد مخرجات)")

    return {"ok": True, "output": "\n\n".join(parts)}
