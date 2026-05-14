# © 2026 Kavalsia Inc. [Siavash Sadighi]
# Local proxy server for Kavalsia Network
# Run: python server.py  → opens hub at http://localhost:8765
#
# Required: pip install flask requests
# ANTHROPIC_API_KEY env var is used for AI commands (or enter key in hub settings)

import os, json, hashlib, webbrowser, threading, time
from pathlib import Path
from datetime import datetime, timedelta
import requests
from flask import Flask, request, jsonify, Response, send_from_directory

BASE_DIR        = Path(__file__).parent.resolve()
CONFIG_PATH     = BASE_DIR / "network-config.json"
CHANGELOG_PATH  = BASE_DIR / "changelog.json"
BACKLINKS_PATH  = BASE_DIR / "backlinks-tracker.json"
PORT            = 8765

app = Flask(__name__, static_folder=str(BASE_DIR))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

# ── Serve static files ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "hub.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(str(BASE_DIR), filename)

# ── Config read / write ───────────────────────────────────────────────────────
@app.route("/api/config", methods=["GET"])
def get_config():
    try:
        return Response(CONFIG_PATH.read_text(encoding="utf-8"), content_type="application/json")
    except FileNotFoundError:
        return jsonify({}), 404

@app.route("/api/config", methods=["POST"])
def save_config():
    data = request.get_data(as_text=True)
    try:
        json.loads(data)  # validate before writing
    except ValueError as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400
    CONFIG_PATH.write_text(data, encoding="utf-8")
    return jsonify({"ok": True})

@app.route("/api/config/hash", methods=["GET"])
def config_hash():
    try:
        h = hashlib.md5(CONFIG_PATH.read_bytes()).hexdigest()
        return jsonify({"hash": h, "mtime": CONFIG_PATH.stat().st_mtime})
    except Exception:
        return jsonify({"hash": "", "mtime": 0})

# ── Changelog read / write ────────────────────────────────────────────────────
@app.route("/api/changelog", methods=["GET"])
def get_changelog():
    try:
        return Response(CHANGELOG_PATH.read_text(encoding="utf-8"), content_type="application/json")
    except FileNotFoundError:
        return jsonify([])

@app.route("/api/changelog", methods=["POST"])
def save_changelog():
    data = request.get_data(as_text=True)
    try:
        json.loads(data)
    except ValueError as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400
    CHANGELOG_PATH.write_text(data, encoding="utf-8")
    return jsonify({"ok": True})

# ── Snapshot / restore for undo ──────────────────────────────────────────────
SNAPSHOTS_PATH = BASE_DIR / "snapshots.json"
MAX_SNAPSHOTS  = 30

@app.route("/api/snapshot", methods=["POST"])
def create_snapshot():
    """Save a named snapshot of the current config before any change — enables restore."""
    body  = request.json or {}
    label = body.get("label", "Change")
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return jsonify({"error": "Could not read config"}), 500
    try:
        snaps = json.loads(SNAPSHOTS_PATH.read_text()) if SNAPSHOTS_PATH.exists() else []
    except Exception:
        snaps = []
    snap = {
        "id":         str(int(time.time() * 1000)),
        "label":      label,
        "created_at": datetime.now().isoformat(),
        "config":     config,
    }
    snaps.insert(0, snap)
    SNAPSHOTS_PATH.write_text(json.dumps(snaps[:MAX_SNAPSHOTS], indent=2))
    return jsonify({"ok": True, "id": snap["id"]})

@app.route("/api/snapshot", methods=["GET"])
def list_snapshots():
    try:
        snaps = json.loads(SNAPSHOTS_PATH.read_text()) if SNAPSHOTS_PATH.exists() else []
        return jsonify([{"id": s["id"], "label": s["label"], "created_at": s["created_at"]} for s in snaps])
    except Exception:
        return jsonify([])

@app.route("/api/snapshot/<snap_id>/restore", methods=["POST"])
def restore_snapshot(snap_id):
    """Restore a previously saved config snapshot."""
    try:
        snaps = json.loads(SNAPSHOTS_PATH.read_text()) if SNAPSHOTS_PATH.exists() else []
    except Exception:
        return jsonify({"error": "No snapshots found"}), 404
    snap = next((s for s in snaps if s["id"] == snap_id), None)
    if not snap:
        return jsonify({"error": "Snapshot not found"}), 404
    CONFIG_PATH.write_text(json.dumps(snap["config"], indent=2, ensure_ascii=False))
    return jsonify({"ok": True, "label": snap["label"]})

@app.route("/api/snapshot/<snap_id>", methods=["DELETE"])
def delete_snapshot(snap_id):
    if not SNAPSHOTS_PATH.exists():
        return jsonify({"ok": True})
    snaps = json.loads(SNAPSHOTS_PATH.read_text())
    snaps = [s for s in snaps if s["id"] != snap_id]
    SNAPSHOTS_PATH.write_text(json.dumps(snaps, indent=2))
    return jsonify({"ok": True})

# ── Security headers ─────────────────────────────────────────────────────────
@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# ── Backlink tracker ─────────────────────────────────────────────────────────
@app.route("/api/backlinks", methods=["GET"])
def get_backlinks():
    try:
        return Response(BACKLINKS_PATH.read_text(encoding="utf-8"), content_type="application/json")
    except FileNotFoundError:
        return jsonify([])

@app.route("/api/backlinks", methods=["POST"])
def save_backlink():
    entry = request.json or {}
    try:
        existing = json.loads(BACKLINKS_PATH.read_text()) if BACKLINKS_PATH.exists() else []
    except Exception:
        existing = []
    entry["id"] = str(int(time.time() * 1000))
    entry["recorded_at"] = datetime.now().isoformat()
    existing.insert(0, entry)
    BACKLINKS_PATH.write_text(json.dumps(existing, indent=2))
    return jsonify({"ok": True, "id": entry["id"]})

@app.route("/api/backlinks/<entry_id>", methods=["DELETE"])
def delete_backlink(entry_id):
    if not BACKLINKS_PATH.exists():
        return jsonify({"ok": True})
    existing = json.loads(BACKLINKS_PATH.read_text())
    existing = [e for e in existing if e.get("id") != entry_id]
    BACKLINKS_PATH.write_text(json.dumps(existing, indent=2))
    return jsonify({"ok": True})


# ── Claude API proxy ──────────────────────────────────────────────────────────
_claude_last = 0.0
_CLAUDE_MIN_INTERVAL = 2.0  # max 30 req/min

@app.route("/api/claude", methods=["POST"])
def claude_proxy():
    global _claude_last
    now = time.time()
    if now - _claude_last < _CLAUDE_MIN_INTERVAL:
        time.sleep(_CLAUDE_MIN_INTERVAL - (now - _claude_last))
    _claude_last = time.time()
    body = request.json or {}
    # API key: from env var first, then from request body _api_key field
    api_key = os.environ.get("ANTHROPIC_API_KEY") or body.pop("_api_key", "")
    if not api_key:
        return jsonify({"error": {"message": "No ANTHROPIC_API_KEY set. Add it in Hub settings."}}), 401
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":          api_key,
                "anthropic-version":  "2023-06-01",
                "content-type":       "application/json",
            },
            json=body,
            timeout=90,
        )
        return Response(r.content, status=r.status_code, content_type="application/json")
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "Claude API timed out (90s)"}}), 504
    except Exception as e:
        return jsonify({"error": {"message": str(e)}}), 500

# ── GitHub proxy (avoids CORS for GitHub API calls) ───────────────────────────
@app.route("/api/github/<path:gh_path>", methods=["GET", "PUT", "POST"])
def github_proxy(gh_path):
    token = request.headers.get("X-GH-Token", "")
    url   = f"https://api.github.com/{gh_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
    }
    if request.method == "GET":
        r = requests.get(url, headers=headers, params=dict(request.args), timeout=15)
    elif request.method == "PUT":
        r = requests.put(url, headers=headers, json=request.json, timeout=15)
    elif request.method == "POST":
        r = requests.post(url, headers=headers, json=request.json, timeout=15)
    return Response(r.content, status=r.status_code, content_type="application/json")

# ── Cloudflare Analytics proxy ────────────────────────────────────────────────
@app.route("/api/cloudflare/analytics", methods=["POST"])
def cloudflare_analytics():
    body      = request.json or {}
    api_token = body.get("api_token") or ""
    account_id = body.get("account_id") or ""
    zone_tag  = body.get("zone_tag") or ""
    since     = body.get("since", "-10080")   # default 7 days in minutes
    until     = body.get("until", "0")

    if not api_token:
        return jsonify({"error": "No Cloudflare API token provided"}), 401

    if not zone_tag and not account_id:
        return jsonify({"error": "Provide either zone_tag or account_id"}), 400

    # Use GraphQL Analytics API
    # If zone_tag is provided use zone-level data; otherwise fall back to account-level
    if zone_tag:
        query = """
        query($zoneTag: String!, $since: String!, $until: String!) {
          viewer {
            zones(filter: { zoneTag: $zoneTag }) {
              httpRequests1dGroups(
                limit: 30
                orderBy: [date_ASC]
                filter: { date_geq: $since, date_leq: $until }
              ) {
                dimensions { date }
                sum { requests pageViews bytes }
                uniq { uniques }
              }
            }
          }
        }"""
        variables_extra = {"zoneTag": zone_tag}
    else:
        query = """
        query($accountTag: String!, $since: String!, $until: String!) {
          viewer {
            accounts(filter: { accountTag: $accountTag }) {
              httpRequests1dGroups(
                limit: 30
                orderBy: [date_ASC]
                filter: { date_geq: $since, date_leq: $until }
              ) {
                dimensions { date }
                sum { requests pageViews bytes }
                uniq { uniques }
              }
            }
          }
        }"""
        variables_extra = {"accountTag": account_id}

    # Convert relative minutes to absolute dates
    now   = datetime.utcnow()
    since_dt = now + timedelta(minutes=int(since)) if since.lstrip("-").isdigit() else now - timedelta(days=7)
    until_dt = now

    try:
        r = requests.post(
            "https://api.cloudflare.com/client/v4/graphql",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type":  "application/json",
            },
            json={
                "query": query,
                "variables": {
                    **variables_extra,
                    "since": since_dt.strftime("%Y-%m-%d"),
                    "until": until_dt.strftime("%Y-%m-%d"),
                },
            },
            timeout=20,
        )
        return Response(r.content, status=r.status_code, content_type="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Main ──────────────────────────────────────────────────────────────────────
def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{PORT}")

if __name__ == "__main__":
    print(f"\n  Kavalsia Network")
    print(f"  ─────────────────────────────────")
    print(f"  Server: http://localhost:{PORT}")
    print(f"  Config: {CONFIG_PATH}")
    print(f"  Press Ctrl+C to stop\n")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
