"""MegaSource scalar sandbox, executed as a subprocess by the backend.

Runs one remote scraper script fully isolated from the server process:
crashes, SystemExit, os._exit-like attempts and timeouts only kill this
child, never the addon. Dangerous top-level modules are blocked, file access
is disabled and dynamic code execution (exec/eval/compile) is removed from
the script's builtins.
"""
import inspect
import json
import sys

SCRIPT_PATH, META_JSON, MEDIA_TYPE, MEDIA_ID, OUTPUT_FILE = sys.argv[1:6]

FORBIDDEN_MODULES = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "ctypes",
    "multiprocessing",
    "signal",
    "resource",
    "pty",
    "gc",
    "code",
    "codeop",
    "pdb",
}

_active_builtins = {}
_orig_import = None


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in FORBIDDEN_MODULES:
        raise ImportError(f"Import of '{name}' is blocked in MegaSource scrapers")
    return _orig_import(name, globals, locals, fromlist, level)


def main():
    result = {"ok": False, "error": ""}
    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
            source = f.read()

        meta = json.loads(META_JSON)
        config = meta.get("config") or {}

        namespace = {"__name__": "megasource_scraper"}
        namespace["__builtins__"] = dict(_active_builtins)
        namespace["__builtins__"]["__import__"] = _safe_import
        namespace["__builtins__"].pop("open", None)
        namespace["__builtins__"].pop("breakpoint", None)
        namespace["__builtins__"].pop("input", None)
        namespace["__builtins__"].pop("exec", None)
        namespace["__builtins__"].pop("eval", None)
        namespace["__builtins__"].pop("compile", None)

        code = compile(source, SCRIPT_PATH, "exec")
        exec(code, namespace)

        handler = namespace.get("get_streams")
        if not callable(handler):
            raise RuntimeError("Script must define a callable get_streams(media_type, media_id, config)")

        params = list(inspect.signature(handler).parameters.values())
        positional = [
            p
            for p in params
            if p.kind
            in (
                p.POSITIONAL_ONLY,
                p.POSITIONAL_OR_KEYWORD,
            )
            and p.default is inspect.Parameter.empty
        ]
        if len(positional) >= 3:
            streams = handler(MEDIA_TYPE, MEDIA_ID, config)
        else:
            streams = handler(MEDIA_TYPE, MEDIA_ID)

        result["ok"] = True
        result["streams"] = streams if isinstance(streams, list) else []
    except BaseException as exc:
        result["ok"] = False
        result["error"] = f"{type(exc).__name__}: {exc}"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)


if __name__ == "__main__":
    _active_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    _orig_import = _active_builtins.get("__import__", __import__)
    main()
    sys.stdout.flush()