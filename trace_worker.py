
import sys
import json
import builtins as _builtins_module

try:
    import resource  
except ImportError:
    resource = None

MAX_STEPS = 60
MAX_VALUE_LEN = 60

ALLOWED_MODULES = {
    "math", "random", "string", "itertools", "functools",
    "collections", "re", "json", "datetime", "statistics",
    "decimal", "fractions",
}


def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".")[0]
    if root not in ALLOWED_MODULES:
        raise ImportError(f"استيراد المكتبة '{name}' غير مسموح في وضع التتبع")
    return _builtins_module.__import__(name, globals, locals, fromlist, level)


def _build_restricted_globals():
    allowed_names = [
        "abs", "all", "any", "bin", "bool", "chr", "dict", "divmod",
        "enumerate", "filter", "float", "format", "frozenset", "hex",
        "int", "isinstance", "issubclass", "len", "list", "map", "max",
        "min", "next", "oct", "ord", "pow", "print", "range", "repr",
        "reversed", "round", "set", "slice", "sorted", "str", "sum",
        "tuple", "zip", "True", "False", "None", "Exception",
        "ValueError", "TypeError", "IndexError", "KeyError",
        "ZeroDivisionError", "StopIteration", "RuntimeError",
        "AttributeError", "NameError", "object",
    ]
    safe_builtins = {n: getattr(_builtins_module, n) for n in allowed_names if hasattr(_builtins_module, n)}
    safe_builtins["__import__"] = _restricted_import
    safe_builtins["__build_class__"] = _builtins_module.__build_class__
    return {"__builtins__": safe_builtins}


def _safe_repr(value):
    try:
        text = repr(value)
    except Exception:
        text = "<تعذر عرض القيمة>"
    if len(text) > MAX_VALUE_LEN:
        text = text[:MAX_VALUE_LEN] + "…"
    return text


class _StepLimitReached(Exception):
    pass


def main():
    source = sys.stdin.read()

    try:
        code_obj = compile(source, "<trace>", "exec")
    except SyntaxError as e:
        print(json.dumps({"ok": False, "error": f"خطأ في الصياغة: {e}"}, ensure_ascii=False))
        return

    source_lines = source.splitlines()
    steps = []
    error = None

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != "<trace>":
            return tracer
        if event == "line":
            if len(steps) >= MAX_STEPS:
                raise _StepLimitReached()
            lineno = frame.f_lineno
            code_line = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else ""
            local_vars = {
                k: _safe_repr(v)
                for k, v in frame.f_locals.items()
                if not k.startswith("__")
            }
            steps.append({"line": lineno, "code": code_line, "vars": local_vars})
        return tracer

    if resource is not None:
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
            resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
        except Exception:
            pass

    restricted_globals = _build_restricted_globals()
    sys.settrace(tracer)
    try:
        exec(code_obj, restricted_globals)
    except _StepLimitReached:
        error = f"تم إيقاف التتبع بعد {MAX_STEPS} خطوة (تجنباً للحلقات الطويلة جداً)"
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.settrace(None)

    print(json.dumps({"ok": True, "steps": steps, "error": error}, ensure_ascii=False))


if __name__ == "__main__":
    main()
