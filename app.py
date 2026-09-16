"""
StremioScrapers — Stremio addon backend (async Flask).

The addon lets users configure Python scraper scripts (hosted on GitHub).
"""
import asyncio
import base64
import inspect
import json
import logging
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.parse
from copy import deepcopy
from pathlib import Path

import aiohttp
from flask import Flask, jsonify, redirect, request, send_from_directory

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("stremioscrapers")

PORT = 7000
BASE_DIR = Path(__file__).resolve().parent
SANDBOX_PATH = BASE_DIR / "scraper_sandbox.py"
app = Flask(__name__, static_folder="static", static_url_path="/")
app.config["JSON_AS_ASCII"] = False

ADDON_ID = "org.stremioscrapers"
VERSION = "1.0.0"
ADDON_NAME = "Stremio Scrapers"
SCRIPT_TTL = 10 * 60
FETCH_TIMEOUT = 12
EXEC_TIMEOUT = 20
DESCRIPTION = (
    "StremioScrapers — pluggable Python scrapers for movies and series. "
    "Configure your own scraper scripts (GitHub) and stream content."
)
MANIFEST = {
    "id": ADDON_ID,
    "version": VERSION,
    "name": ADDON_NAME,
    "description": DESCRIPTION,
    "resources": ["stream"],
    "types": ["movie", "series"],
    "catalogs": [],
    "behaviorHints": {"configurable": True, "configurationRequired": False},
    "configureEndpoint": "/configure",
    "config": [{"key": "scrapers", "title": "Scrapers", "type": "text"}],
}
_SCRIPT_CACHE = {}


def encode_config(scrapers):
    raw = json.dumps(scrapers, ensure_ascii=False)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def decode_config(value):
    if not value:
        return []
    data = None
    try:
        data = json.loads(value)
    except (ValueError, TypeError):
        try:
            padding = "=" * (-len(value) % 4)
            raw = base64.urlsafe_b64decode((value + padding).encode("ascii")).decode("utf-8")
            data = json.loads(raw)
        except Exception:
            return []
    if isinstance(data, dict):
        data = data.get("scrapers", data.get("config", []))
    if not isinstance(data, list):
        return []
    return [s for s in data if isinstance(s, dict) and s.get("url")]


def get_scrapers_from_config(config):
    return decode_config(config)


def get_scrapers():
    config_param = request.args.get("config")
    path_config = (request.view_args or {}).get("config")
    if config_param:
        scrapers = decode_config(config_param)
    elif path_config:
        scrapers = decode_config(path_config)
    else:
        scrapers = []
    base = request.host_url.rstrip("/")
    resolved = []
    for item in scrapers:
        item = dict(item)
        item["url"] = resolve_relative(base, item.get("url", ""))
        item.setdefault("name", "Scraper")
        resolved.append(item)
    return resolved


def resolve_relative(base_url, url):
    url = url.strip()
    if url.startswith("/"):
        return base_url + url
    return url


def resolve_github_raw(url):
    url = url.strip()
    if not url:
        return url
    if "github.com/" in url and "/blob/" in url:
        return re.sub(r"github\.com/([^/]+)/([^/]+)/blob/", r"raw.githubusercontent.com/\1/\2/", url)
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/raw/(.*)$", url)
    if m:
        user, repo, path = m.group(1), m.group(2), m.group(3)
        branch = re.sub(r"^refs/heads/", "", path)
        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}"
    if url.startswith("raw.githubusercontent.com/"):
        return "https://" + url
    return url


async def _http_get(url):
    headers = {"User-Agent": f"StremioScrapers/{VERSION}", "Accept": "text/plain, application/octet-stream"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT)) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}")
            return await resp.text()


async def fetch_script(url):
    now = time.time()
    cached = _SCRIPT_CACHE.get(url)
    if cached and now - cached[1] < SCRIPT_TTL:
        return cached[0]
    try:
        script = await _http_get(url)
        _SCRIPT_CACHE[url] = (script, now)
        return script
    except Exception as exc:
        raise RuntimeError(f"Unable to fetch scraper script {url}: {exc}") from exc


FORBIDDEN_MODULES = {"os", "sys", "subprocess", "shutil", "ctypes", "multiprocessing", "signal", "resource", "pty", "gc", "code", "codeop", "pdb"}
_ORIG_IMPORT = __import__


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in FORBIDDEN_MODULES:
        raise ImportError(f"Import of '{name}' is blocked in StremioScrapers scrapers")
    return _ORIG_IMPORT(name, globals, locals, fromlist, level)


def exec_script_inline(script_content, scraper, media_type, media_id):
    real_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
    builtins_dict = dict(real_builtins)
    builtins_dict["__import__"] = _safe_import
    for name in ("open", "breakpoint", "input", "exec", "eval", "compile"):
        builtins_dict.pop(name, None)
    namespace = {"__name__": "my_megasource_scrapers", "__builtins__": builtins_dict}
    code = compile(script_content, scraper.get("url", "scraper.py"), "exec")
    exec(code, namespace)
    handler = namespace.get("get_streams")
    if not callable(handler):
        raise RuntimeError("Script must define a callable get_streams(media_type, media_id, config)")
    params = [p for p in inspect.signature(handler).parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) and p.default is inspect.Parameter.empty]
    if len(params) >= 3:
        return handler(media_type, media_id, scraper.get("config") or {})
    return handler(media_type, media_id)


def run_script_subprocess(script_content, scraper, media_type, media_id):
    tmp = tempfile.mkdtemp(prefix="stremioscrapers_")
    try:
        script_path = os.path.join(tmp, "scraper.py")
        output_path = os.path.join(tmp, "result.json")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        cmd = [sys.executable, str(SANDBOX_PATH), script_path, json.dumps({"config": scraper.get("config") or {}}, ensure_ascii=False), media_type, media_id, output_path]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            log.warning("Subprocess unavailable (%s); using inline sandbox", exc)
            return exec_script_inline(script_content, scraper, media_type, media_id)
        try:
            proc.communicate(timeout=EXEC_TIMEOUT)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except Exception:
                pass
            raise RuntimeError("Scraper execution timed out")
        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    result = json.load(f)
                if result.get("ok"):
                    return result.get("streams", [])
                raise RuntimeError(result.get("error") or "Scraper failed")
            except (ValueError, TypeError):
                pass
        return exec_script_inline(script_content, scraper, media_type, media_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def normalize_streams(result):
    if isinstance(result, dict):
        result = result.get("streams", [])
    if not isinstance(result, list):
        return []
    streams = []
    for item in result:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or item.get("file") or item.get("torrent") or item.get("magnet")
        if not url:
            continue
        stream = {"url": url, "title": item.get("title") or item.get("name") or ADDON_NAME}
        for key in ("quality", "name", "infoHash", "fileIdx", "source", "behaviorHints"):
            if item.get(key) is not None:
                stream[key] = item[key]
        streams.append(stream)
    return streams


async def run_scraper(scraper, media_type, media_id):
    url = resolve_github_raw(scraper.get("url", ""))
    script = await fetch_script(url)
    result = await asyncio.to_thread(run_script_subprocess, script, scraper, media_type, media_id)
    return normalize_streams(result)


CORS_HEADERS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS", "Access-Control-Allow-Headers": "Content-Type, X-Requested-With, Authorization, Accept", "Access-Control-Max-Age": "86400"}


@app.after_request
def add_cors_headers(response):
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value
    return response


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return ("", 204)


def _manifest_payload():
    scrapers = get_scrapers()
    current = deepcopy(MANIFEST)
    current["logo"] = "https://raw.githubusercontent.com/mykaelandradee/stremioscrapers/refs/heads/main/icon.png"
    current["behaviorHints"]["configurable"] = True
    current["behaviorHints"]["configurationRequired"] = not bool(scrapers)
    if scrapers:
        current["description"] = DESCRIPTION + f" | {len(scrapers)} scraper(s) configured."
    return jsonify(current)


@app.route("/manifest.json")
def manifest():
    return _manifest_payload()


@app.route("/<config>/manifest.json")
def manifest_configured(config):
    return _manifest_payload()


@app.route("/stream/<media_type>/<media_id>.json")
async def stream(media_type, media_id):
    media_id = urllib.parse.unquote(media_id)
    scrapers = get_scrapers()
    if media_type not in ("movie", "series") or not scrapers:
        return jsonify({"streams": []})
    results = await asyncio.gather(*(run_scraper(s, media_type, media_id) for s in scrapers), return_exceptions=True)
    streams, seen = [], set()
    for scraper, result in zip(scrapers, results):
        if isinstance(result, Exception):
            log.warning("Scraper %s failed: %s", scraper.get("url"), result)
            continue
        for item in result or []:
            key = item.get("url")
            if key in seen:
                continue
            seen.add(key)
            if not item.get("title"):
                item["title"] = scraper.get("name", ADDON_NAME)
            streams.append(item)
    return jsonify({"streams": streams})


@app.route("/<config>/stream/<media_type>/<media_id>.json")
async def stream_configured(config, media_type, media_id):
    return await stream(media_type, media_id)


@app.route("/api/state")
def api_state():
    return jsonify({"ok": True, "base_url": request.host_url.rstrip("/"), "addon": {"name": ADDON_NAME, "version": VERSION}})


@app.route("/api/test-scraper", methods=["POST"])
async def api_test_scraper():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    media_type = data.get("media_type") or "movie"
    media_id = data.get("media_id") or "tt0111161"
    if not url:
        return jsonify({"ok": False, "error": "url is required"}), 400
    scraper = {"url": resolve_relative(request.host_url.rstrip("/"), url), "name": "test", "config": data.get("config")}
    try:
        streams = await run_scraper(scraper, media_type, media_id)
        return jsonify({"ok": True, "count": len(streams), "streams": streams})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/configure")
def configure():
    config = request.args.get("config")
    if config:
        return redirect("/?config=" + urllib.parse.quote(config, safe=""), code=302)
    return redirect("/", code=302)


@app.route("/<config>/configure")
def configure_configured(config):
    # Preserve the exact manifest configuration when Stremio opens the editor.
    # The previous implementation discarded this path and redirected to '/'.
    return redirect("/?config=" + urllib.parse.quote(config, safe=""), code=302)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    if path.startswith(("api/", "stream/")):
        return jsonify({"error": "not found"}), 404
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", PORT))
    log.info("StremioScrapers addon listening on http://localhost:%s", port)
    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=12)
