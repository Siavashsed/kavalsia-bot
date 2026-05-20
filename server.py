# © 2026 Kavalsia Inc. [Siavash Sadighi]
# Local proxy server for Kavalsia Network
# Run: python server.py  → opens hub at http://localhost:8765
#
# Required: pip install flask requests
# ANTHROPIC_API_KEY env var is used for AI commands (or enter key in hub settings)

import os, json, hashlib, webbrowser, threading, time, subprocess
from pathlib import Path
from datetime import datetime, timedelta
import requests
from flask import Flask, request, jsonify, Response, send_from_directory

BASE_DIR             = Path(__file__).parent.resolve()
CONFIG_PATH          = BASE_DIR / "network-config.json"
CHANGELOG_PATH       = BASE_DIR / "changelog.json"
BACKLINKS_PATH       = BASE_DIR / "backlinks-tracker.json"
CLAUDE_HISTORY_PATH  = BASE_DIR / "claude_history.json"
PORT                 = 8765

app = Flask(__name__, static_folder=str(BASE_DIR))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

# ── Serve static files ────────────────────────────────────────────────────────
PAGES = {
    "home":      "start.html",
    "start":     "start.html",
    "hub":       "hub.html",
    "dashboard": "dashboard.html",
    "megadash":  "megadash.html",
    "mega":      "megadash.html",
    "editor":    "editor.html",
    "launcher":  "launcher.html",
    "guide":     "guide.html",
    "landing":   "landing.html",
}

@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), "hub.html")

@app.route("/home")
def home():
    links = "".join(
        f'<a href="/{k}" style="display:block;padding:14px 20px;margin-bottom:8px;background:#0d1410;'
        f'border:1px solid #1e3024;border-radius:10px;color:#3ecf8e;font-size:15px;font-weight:600;'
        f'text-decoration:none">{k} <span style="color:#4d7059;font-size:12px;font-weight:400">→ {v}</span></a>'
        for k, v in PAGES.items() if (BASE_DIR / v).exists()
    )
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8">
    <title>SiaAI Network</title>
    <style>body{{background:#080c09;font-family:system-ui;padding:40px;max-width:480px;margin:0 auto}}
    h1{{color:#fff;font-size:22px;margin-bottom:6px}} p{{color:#b8d4c0;font-size:13px;margin-bottom:24px}}</style>
    </head><body>
    <h1>SiaAI Network</h1>
    <p>All tools - running on localhost:8765</p>
    {links}
    </body></html>'''

@app.route("/<page>")
def named_page(page):
    if page in PAGES and (BASE_DIR / PAGES[page]).exists():
        return send_from_directory(str(BASE_DIR), PAGES[page])
    return send_from_directory(str(BASE_DIR), page)

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
    """Save a named snapshot of the current config before any change - enables restore."""
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
    # Always pop _api_key first so it is NEVER forwarded to Anthropic (causes 400)
    _body_api_key = body.pop("_api_key", "")
    api_key = os.environ.get("ANTHROPIC_API_KEY") or _body_api_key
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


# ── Cloudflare DNS management proxy ───────────────────────────────────────────
def _cf_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@app.route("/api/cloudflare/zones", methods=["GET"])
def cf_list_zones():
    token = request.headers.get("X-CF-Token", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    r = requests.get("https://api.cloudflare.com/client/v4/zones",
                     headers=_cf_headers(token),
                     params={"per_page": 50, "status": "active"},
                     timeout=15)
    return Response(r.content, status=r.status_code, content_type="application/json")

@app.route("/api/cloudflare/zones/<zone_id>/dns_records", methods=["GET", "POST"])
def cf_dns_records(zone_id):
    token = request.headers.get("X-CF-Token", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    if request.method == "GET":
        r = requests.get(url, headers=_cf_headers(token),
                         params={"per_page": 100}, timeout=15)
    else:
        r = requests.post(url, headers=_cf_headers(token),
                          json=request.json, timeout=15)
    return Response(r.content, status=r.status_code, content_type="application/json")

@app.route("/api/cloudflare/zones/<zone_id>/dns_records/<record_id>", methods=["PUT", "PATCH", "DELETE"])
def cf_dns_record(zone_id, record_id):
    token = request.headers.get("X-CF-Token", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    if request.method in ("PUT", "PATCH"):
        r = requests.put(url, headers=_cf_headers(token), json=request.json, timeout=15)
    else:
        r = requests.delete(url, headers=_cf_headers(token), timeout=15)
    return Response(r.content, status=r.status_code, content_type="application/json")

@app.route("/api/cloudflare/zones/<zone_id>/settings/ssl", methods=["GET", "PATCH"])
def cf_ssl_setting(zone_id):
    token = request.headers.get("X-CF-Token", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl"
    if request.method == "GET":
        r = requests.get(url, headers=_cf_headers(token), timeout=10)
    else:
        r = requests.patch(url, headers=_cf_headers(token), json=request.json, timeout=10)
    return Response(r.content, status=r.status_code, content_type="application/json")

@app.route("/api/cloudflare/verify", methods=["GET"])
def cf_verify_token():
    token = request.headers.get("X-CF-Token", "")
    if not token:
        return jsonify({"error": "No token"}), 401
    r = requests.get("https://api.cloudflare.com/client/v4/user/tokens/verify",
                     headers=_cf_headers(token), timeout=10)
    return Response(r.content, status=r.status_code, content_type="application/json")


# ── Claude Terminal history ───────────────────────────────────────────────────
@app.route("/api/claude-history", methods=["GET"])
def get_claude_history():
    try:
        return Response(CLAUDE_HISTORY_PATH.read_text(encoding="utf-8"), content_type="application/json")
    except FileNotFoundError:
        return jsonify([])

@app.route("/api/claude-history", methods=["POST"])
def save_claude_history():
    session = request.json or {}
    try:
        existing = json.loads(CLAUDE_HISTORY_PATH.read_text()) if CLAUDE_HISTORY_PATH.exists() else []
    except Exception:
        existing = []
    idx = next((i for i, s in enumerate(existing) if s.get("id") == session.get("id")), -1)
    if idx >= 0:
        existing[idx] = session
    else:
        existing.insert(0, session)
    CLAUDE_HISTORY_PATH.write_text(json.dumps(existing[:100], indent=2))
    return jsonify({"ok": True})

@app.route("/api/claude-history/<session_id>", methods=["DELETE"])
def delete_claude_session(session_id):
    if not CLAUDE_HISTORY_PATH.exists():
        return jsonify({"ok": True})
    existing = json.loads(CLAUDE_HISTORY_PATH.read_text())
    existing = [s for s in existing if s.get("id") != session_id]
    CLAUDE_HISTORY_PATH.write_text(json.dumps(existing, indent=2))
    return jsonify({"ok": True})

# ── Daily report ──────────────────────────────────────────────────────────────
@app.route("/api/daily-report", methods=["POST"])
def daily_report():
    body     = request.json or {}
    token    = body.get("token", "")
    days     = int(body.get("days", 1))
    cutoff   = datetime.utcnow() - timedelta(days=days)
    cutoff_s = cutoff.strftime("%Y-%m-%d")

    try:
        cfg   = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        sites = cfg.get("sites", [])
    except Exception:
        return jsonify({"error": "Could not read config"}), 500

    articles = []
    for site in sites:
        repo = site.get("repo", "")
        if not repo or "YOUR_" in repo:
            continue
        hdrs = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        try:
            r = requests.get(f"https://api.github.com/repos/{repo}/contents/_posts",
                             headers=hdrs, timeout=10)
            if r.status_code != 200:
                continue
            posts = r.json()
            if not isinstance(posts, list):
                continue
            for p in posts:
                name = p.get("name", "")
                m = __import__("re").match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", name)
                if not m:
                    continue
                date_s, slug = m.group(1), m.group(2)
                if date_s < cutoff_s:
                    continue
                title = slug.replace("-", " ").capitalize()
                domain = site.get("domain", "")
                url = f"https://{domain}/{date_s.replace('-','/')}/{slug}/" if domain else ""
                articles.append({
                    "site_id":   site["id"],
                    "site_name": site.get("category", site["id"]),
                    "domain":    domain,
                    "title":     title,
                    "date":      date_s,
                    "url":       url,
                    "repo":      repo,
                })
        except Exception:
            continue

    articles.sort(key=lambda x: x["date"], reverse=True)
    return jsonify({"articles": articles, "days": days, "total": len(articles),
                    "generated_at": datetime.utcnow().isoformat()})

@app.route("/api/push-sites", methods=["POST"])
def push_sites():
    """Run push-sites.py --push TOKEN [--only ID | --sites ID1,ID2] and stream output."""
    data = request.get_json(force=True, silent=True) or {}
    token    = (data.get("token") or "").strip()
    site_ids = [s.strip() for s in (data.get("site_ids") or []) if s.strip()]
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    script = BASE_DIR / "push-sites.py"
    if not script.exists():
        return jsonify({"error": "push-sites.py not found"}), 404

    cmd = ["python3", str(script), "--push", token]
    if len(site_ids) == 1:
        cmd += ["--only", site_ids[0]]
    elif len(site_ids) > 1:
        cmd += ["--sites", ",".join(site_ids)]

    def generate():
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


@app.route("/api/backup", methods=["POST"])
def api_backup():
    """Run backup.py and stream log output line by line."""
    data     = request.get_json(force=True, silent=True) or {}
    gh_token = (data.get("gh_token") or "").strip()

    backup_script = BASE_DIR / "backup.py"
    if not backup_script.exists():
        return jsonify({"error": "backup.py not found"}), 404

    cmd = ["python3", str(backup_script)]
    if gh_token:
        cmd += ["--gh-token", gh_token]

    def generate():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── Rebuild homepages ────────────────────────────────────────────────────────
@app.route("/api/rebuild-homepages", methods=["POST"])
def rebuild_homepages():
    data  = request.get_json(force=True, silent=True) or {}
    token = (data.get("token") or "").strip()
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    cmd = [
        "python3", str(BASE_DIR / "bot.py"), "--rebuild-homepages",
        "--gh-token", token,
    ]
    env = dict(os.environ, GITHUB_TOKEN=token)

    def generate():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1, env=env,
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

# ── Fix double nav (patch existing articles) ──────────────────────────────────
@app.route("/api/fix-double-nav", methods=["POST"])
def fix_double_nav():
    data  = request.get_json(force=True, silent=True) or {}
    token = (data.get("token") or "").strip()
    repo  = (data.get("repo") or "").strip()
    if not token or not repo:
        return jsonify({"error": "token and repo required"}), 400

    cmd = [
        "python3", str(BASE_DIR / "patch_supplementverge_nav.py"),
    ]
    env = dict(os.environ, GITHUB_TOKEN=token, PATCH_REPO=repo)

    def generate():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1, env=env,
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── Newsletter Subscribe ──────────────────────────────────────────────────────
@app.route("/api/subscribe", methods=["POST", "OPTIONS"])
def newsletter_subscribe():
    if request.method == "OPTIONS":
        resp = jsonify({"ok": True})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp, 200

    data     = request.get_json(force=True, silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    list_id  = data.get("list_id")

    if not email or "@" not in email:
        resp = jsonify({"error": "Valid email required"}), 400
        return resp

    brevo_key = os.environ.get("BREVO_API_KEY", "")
    if not brevo_key:
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            brevo_key = cfg.get("settings", {}).get("brevo_api_key", "")
        except Exception:
            pass
    if not brevo_key:
        resp = jsonify({"error": "Brevo not configured"}), 503
        return resp

    payload = {
        "email": email,
        "updateEnabled": True,
    }
    if list_id:
        payload["listIds"] = [int(list_id)]

    try:
        r = requests.post(
            "https://api.brevo.com/v3/contacts",
            headers={"api-key": brevo_key, "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        if r.status_code in (200, 201):
            resp = jsonify({"ok": True, "message": "Subscribed!"})
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp, 200
        elif r.status_code == 204:
            resp = jsonify({"ok": True, "message": "Already subscribed - updated!"})
            resp.headers["Access-Control-Allow-Origin"] = "*"
            return resp, 200
        else:
            err = r.json() if r.content else {}
            resp = jsonify({"error": err.get("message", f"Brevo error {r.status_code}")}), 400
            return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Patch Authors ────────────────────────────────────────────────────────────
@app.route("/api/patch-authors", methods=["POST"])
def patch_authors():
    data     = request.get_json(force=True, silent=True) or {}
    token    = (data.get("token") or "").strip()
    only     = (data.get("only") or "").strip()
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    env = dict(os.environ, GITHUB_TOKEN=token)
    cmd = ["python3", str(BASE_DIR / "patch-authors.py")]
    if only:
        cmd += ["--only", only]

    def generate():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1, env=env,
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── Domain Setup ─────────────────────────────────────────────────────────────
@app.route("/api/setup-domains", methods=["POST"])
def setup_domains():
    data     = request.get_json(force=True, silent=True) or {}
    gh_token = (data.get("gh_token") or "").strip()
    cf_token = (data.get("cf_token") or "").strip()
    only     = (data.get("only") or "").strip()
    if not gh_token:
        return jsonify({"error": "GitHub token required"}), 400

    cmd = ["python3", str(BASE_DIR / "setup-domains.py"), "--gh-token", gh_token]
    if cf_token:
        cmd += ["--cf-token", cf_token]
    if only:
        cmd += ["--only", only]

    def generate():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR), text=True, bufsize=1,
        )
        for line in proc.stdout:
            yield line.rstrip("\n") + "\n"
        proc.wait()
        yield f"__EXIT__{proc.returncode}\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── Fix Em Dashes ────────────────────────────────────────────────────────────
@app.route("/api/fix-em-dashes", methods=["POST"])
def fix_em_dashes():
    data  = request.get_json(force=True, silent=True) or {}
    token = (data.get("token") or "").strip()
    repo  = (data.get("repo") or "").strip()
    if not token or not repo:
        return jsonify({"error": "token and repo required"}), 400

    import base64, re as _re

    def generate():
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        # Fetch articles.json to get slugs
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json", headers=headers, timeout=10)
        if not r.ok:
            yield f"Could not fetch articles.json: {r.status_code}\n"
            yield "__EXIT__1\n"
            return
        articles = json.loads(base64.b64decode(r.json()["content"]).decode())
        yield f"Found {len(articles)} articles\n"
        patched = 0
        for art in articles:
            slug = art.get("slug", "")
            if not slug:
                continue
            path = f"{slug}/index.html"
            fr = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, timeout=10)
            if not fr.ok:
                continue
            sha = fr.json()["sha"]
            html = base64.b64decode(fr.json()["content"]).decode("utf-8", errors="replace")
            cleaned = _re.sub(r'—', '-', html)
            cleaned = _re.sub(r' --- ', ' - ', cleaned)
            if cleaned == html:
                yield f"  {slug}: ok\n"
                continue
            payload = {"message": "fix: remove em dashes", "content": base64.b64encode(cleaned.encode("utf-8")).decode(), "sha": sha}
            pr = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, json=payload, timeout=10)
            if pr.status_code in (200, 201):
                yield f"  {slug}: pushed ok\n"
                patched += 1
            else:
                yield f"  {slug}: push failed {pr.status_code}\n"
            import time; time.sleep(0.3)
        yield f"Done: {patched} articles patched\n"
        yield "__EXIT__0\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── AI Custom Fix Articles ────────────────────────────────────────────────────
@app.route("/api/ai-fix-articles", methods=["POST"])
def ai_fix_articles():
    data       = request.get_json(force=True, silent=True) or {}
    token      = (data.get("token") or "").strip()
    repo       = (data.get("repo") or "").strip()
    prompt_txt = (data.get("prompt") or "").strip()
    api_key    = (data.get("_api_key") or "").strip() or os.environ.get("ANTHROPIC_API_KEY", "")
    if not token or not repo or not prompt_txt:
        return jsonify({"error": "token, repo, and prompt required"}), 400
    if not api_key:
        return jsonify({"error": "Anthropic API key required"}), 401

    import base64, anthropic as _ant

    def generate():
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json", headers=headers, timeout=10)
        if not r.ok:
            yield f"Could not fetch articles.json: {r.status_code}\n"
            yield "__EXIT__1\n"
            return
        articles = json.loads(base64.b64decode(r.json()["content"]).decode())
        yield f"Found {len(articles)} articles\n"
        client = _ant.Anthropic(api_key=api_key)
        patched = 0
        for art in articles:
            slug = art.get("slug", "")
            if not slug:
                continue
            path = f"{slug}/index.html"
            fr = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, timeout=10)
            if not fr.ok:
                continue
            sha = fr.json()["sha"]
            html = base64.b64decode(fr.json()["content"]).decode("utf-8", errors="replace")
            yield f"  {slug}: sending to AI...\n"
            try:
                msg = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=8192,
                    messages=[{
                        "role": "user",
                        "content": f"You are an HTML editor with full authority to modify this page. Apply this fix to the HTML below and return ONLY the complete modified HTML with no commentary:\n\nFIX: {prompt_txt}\n\nHTML:\n{html}"
                    }]
                )
                new_html = msg.content[0].text.strip()
                if new_html.startswith("```"):
                    new_html = new_html.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            except Exception as e:
                yield f"  {slug}: AI error - {e}\n"
                continue
            payload = {"message": f"fix: {prompt_txt[:60]}", "content": base64.b64encode(new_html.encode("utf-8")).decode(), "sha": sha}
            pr = requests.put(f"https://api.github.com/repos/{repo}/contents/{path}", headers=headers, json=payload, timeout=10)
            if pr.status_code in (200, 201):
                yield f"  {slug}: pushed ok\n"
                patched += 1
            else:
                yield f"  {slug}: push failed {pr.status_code}\n"
            import time; time.sleep(0.5)
        yield f"Done: {patched}/{len(articles)} articles updated\n"
        yield "__EXIT__0\n"

    return Response(generate(), mimetype="text/plain",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


# ── Broadcast / post queue ────────────────────────────────────────────────────
BROADCAST_PATH = BASE_DIR / "broadcast.json"

@app.route("/api/write-broadcast", methods=["POST"])
def write_broadcast():
    body = request.json or {}
    topic    = body.get("topic", "").strip()
    site_ids = body.get("site_ids", [])
    if not topic:
        return jsonify({"error": "topic required"}), 400
    payload = {
        "topic":    topic,
        "site_ids": site_ids,
        "created_at": datetime.now().isoformat(),
    }
    BROADCAST_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return jsonify({"ok": True, "file": str(BROADCAST_PATH)})

# ── Telegram ──────────────────────────────────────────────────────────────────
@app.route("/api/telegram/send", methods=["POST"])
def telegram_send():
    body     = request.json or {}
    token    = body.get("token", "").strip()
    chat_id  = str(body.get("chat_id", "")).strip()
    text     = body.get("text", "").strip()
    if not token or not chat_id or not text:
        return jsonify({"error": "token, chat_id and text are required"}), 400
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/backup/status", methods=["GET"])
def backup_status():
    """Return date of most recent local backup zip if any."""
    zips = sorted(BASE_DIR.glob("kavalsia-backup-*.zip"), reverse=True)
    if zips:
        stat = zips[0].stat()
        return jsonify({"last_backup": zips[0].name,
                        "size_mb": round(stat.st_size / 1024 / 1024, 1),
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")})
    return jsonify({"last_backup": None})

# ── Article Author update (articles.json + article HTML byline) ───────────────
@app.route("/api/article-author", methods=["POST"])
def update_article_author():
    """
    Body: { site_id, slug, author, token? }
    Token may be passed in body, X-GH-Token header, or env GITHUB_TOKEN.
    Updates the author field for an article in BOTH:
      - <repo>/articles.json (index entry's `author` field)
      - <repo>/<slug>/index.html (byline)
    Returns { ok, updated_index, updated_html, old_author, new_author, messages }.
    """
    import base64, re as _re

    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    slug    = (body.get("slug") or "").strip().strip("/")
    new_aut = (body.get("author") or "").strip()
    token   = (body.get("token") or "").strip() \
              or request.headers.get("X-GH-Token", "").strip() \
              or os.environ.get("GITHUB_TOKEN", "").strip()

    if not site_id or not slug or not new_aut:
        return jsonify({"error": "site_id, slug, and author are required"}), 400
    if not token:
        return jsonify({"error": "GitHub token required (body.token, X-GH-Token header, or GITHUB_TOKEN env)"}), 400

    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    site = next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)
    if not site:
        return jsonify({"error": f"Unknown site_id '{site_id}'"}), 404
    repo = (site.get("repo") or "").strip()
    if not repo or "YOUR_" in repo:
        return jsonify({"error": f"Site '{site_id}' has no valid repo configured"}), 400

    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
    }
    messages = []

    # 1. Load articles.json
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json",
                         headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error fetching articles.json: {e}"}), 502
    if r.status_code == 404:
        return jsonify({"error": f"articles.json not found in {repo}"}), 404
    if r.status_code == 401 or r.status_code == 403:
        return jsonify({"error": f"GitHub auth failed for {repo} (status {r.status_code}). Check token permissions."}), r.status_code
    if r.status_code != 200:
        return jsonify({"error": f"GitHub returned {r.status_code} for articles.json: {r.text[:200]}"}), r.status_code

    try:
        idx_data = r.json()
        idx_sha  = idx_data["sha"]
        articles = json.loads(base64.b64decode(idx_data["content"]).decode("utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not parse articles.json: {e}"}), 500

    art = next((a for a in articles if (a.get("slug","").strip("/") == slug)), None)
    if art is None:
        return jsonify({"error": f"Article slug '{slug}' not found in articles.json"}), 404

    old_aut = (art.get("author") or "").strip()
    if old_aut == new_aut:
        return jsonify({
            "ok": True, "updated_index": False, "updated_html": False,
            "old_author": old_aut, "new_author": new_aut,
            "messages": ["Author unchanged."]
        })

    # 2. Fetch + patch article HTML byline
    html_path = f"{slug}/index.html"
    updated_html = False
    try:
        hr = requests.get(f"https://api.github.com/repos/{repo}/contents/{html_path}",
                          headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error fetching article HTML: {e}"}), 502

    if hr.status_code == 404:
        messages.append(f"Article HTML {html_path} not found - only articles.json will be updated.")
        html_sha = None
        html     = None
    elif hr.status_code in (401, 403):
        return jsonify({"error": f"GitHub auth failed for article HTML (status {hr.status_code})."}), hr.status_code
    elif hr.status_code != 200:
        return jsonify({"error": f"GitHub returned {hr.status_code} for {html_path}"}), hr.status_code
    else:
        try:
            hd       = hr.json()
            html_sha = hd["sha"]
            html     = base64.b64decode(hd["content"]).decode("utf-8", errors="replace")
        except Exception as e:
            return jsonify({"error": f"Could not parse article HTML: {e}"}), 500

    new_html = html
    if html and old_aut:
        # Replace only inside the byline contexts (don't touch quoted/commented text).
        # Pattern 1: By <strong ...>OLD</strong>
        esc = _re.escape(old_aut)
        pat_strong = _re.compile(
            r'(By\s*<strong\b[^>]*>)\s*' + esc + r'\s*(</strong>)',
            flags=_re.IGNORECASE,
        )
        new_html, n1 = pat_strong.subn(lambda m: m.group(1) + new_aut + m.group(2), new_html)

        # Pattern 2: <div class="byline">OLD ... </div>  (replace first occurrence of OLD inside)
        pat_byline_div = _re.compile(
            r'(<div\b[^>]*class="[^"]*\bbyline\b[^"]*"[^>]*>)([^<]*?)' + esc + r'([^<]*?)(</div>)',
            flags=_re.IGNORECASE | _re.DOTALL,
        )
        new_html, n2 = pat_byline_div.subn(
            lambda m: m.group(1) + m.group(2) + new_aut + m.group(3) + m.group(4),
            new_html,
        )

        # Pattern 3: any element with class containing "author" wrapping just OLD
        pat_author_el = _re.compile(
            r'(<(?:span|div|a|p)\b[^>]*class="[^"]*\bauthor\b[^"]*"[^>]*>)\s*' + esc + r'\s*(</(?:span|div|a|p)>)',
            flags=_re.IGNORECASE,
        )
        new_html, n3 = pat_author_el.subn(lambda m: m.group(1) + new_aut + m.group(2), new_html)

        # Pattern 4 (fallback): "By OLD" plain text (e.g. <p>By OLD</p>) — only if previous patterns missed
        if (n1 + n2 + n3) == 0:
            pat_by_plain = _re.compile(r'(>\s*By\s+)' + esc + r'(\b)', flags=_re.IGNORECASE)
            new_html, n4 = pat_by_plain.subn(lambda m: m.group(1) + new_aut + m.group(2), new_html, count=1)
        else:
            n4 = 0

        total_repl = n1 + n2 + n3 + n4
        if total_repl == 0:
            messages.append(f"Warning: could not locate old author '{old_aut}' in byline of {html_path}. HTML not updated.")
        else:
            messages.append(f"Patched byline ({n1} strong, {n2} byline-div, {n3} author-el, {n4} plain).")

            # 3. Push the HTML
            put_payload = {
                "message": f"Update author for {slug}: {old_aut} -> {new_aut}",
                "content": base64.b64encode(new_html.encode("utf-8")).decode(),
                "sha":     html_sha,
            }
            try:
                pr = requests.put(f"https://api.github.com/repos/{repo}/contents/{html_path}",
                                  headers=headers, json=put_payload, timeout=20)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Network error pushing article HTML: {e}"}), 502
            if pr.status_code not in (200, 201):
                return jsonify({"error": f"Failed to push article HTML ({pr.status_code}): {pr.text[:300]}"}), pr.status_code
            updated_html = True

    # 4. Patch articles.json and push (retry once on 409 stale-SHA with a fresh SHA).
    art["author"] = new_aut
    content_b64 = base64.b64encode(json.dumps(articles, indent=2).encode("utf-8")).decode()
    def _put_idx(sha):
        return requests.put(
            f"https://api.github.com/repos/{repo}/contents/articles.json",
            headers=headers,
            json={"message": f"Update author for {slug}: {old_aut} -> {new_aut}",
                  "content": content_b64, "sha": sha},
            timeout=20)
    try:
        ir = _put_idx(idx_sha)
        if ir.status_code == 409:
            # Re-fetch current SHA + re-merge our author change into the latest articles.json.
            rr = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json",
                              headers=headers, timeout=15)
            if rr.status_code == 200:
                fresh = rr.json()
                fresh_articles = json.loads(base64.b64decode(fresh["content"]).decode("utf-8"))
                for fa in fresh_articles:
                    if (fa.get("slug","").strip("/") == slug):
                        fa["author"] = new_aut
                        break
                content_b64 = base64.b64encode(json.dumps(fresh_articles, indent=2).encode("utf-8")).decode()
                ir = _put_idx(fresh["sha"])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network error pushing articles.json: {e}",
                        "updated_html": updated_html}), 502
    if ir.status_code not in (200, 201):
        return jsonify({"error": f"Failed to push articles.json ({ir.status_code}): {ir.text[:300]}",
                        "updated_html": updated_html}), ir.status_code

    return jsonify({
        "ok":             True,
        "updated_index":  True,
        "updated_html":   updated_html,
        "old_author":     old_aut,
        "new_author":     new_aut,
        "messages":       messages,
    })

# ── Posting Schedule update (historical_mode, posts_per_day_new, historical_per_week) ──
@app.route("/api/site-schedule", methods=["POST"])
def update_site_schedule():
    """
    Body: { site_id, historical_mode (bool), posts_per_day_new (int 1-5),
            historical_per_week (int 0-14) }
    Updates those three fields on the matching site inside network-config.json
    and persists the file atomically. Returns { ok, site_id, schedule }.
    """
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    if not site_id:
        return jsonify({"error": "site_id is required"}), 400

    # Validate types
    if "historical_mode" not in body or "posts_per_day_new" not in body or "historical_per_week" not in body:
        return jsonify({"error": "historical_mode, posts_per_day_new, and historical_per_week are required"}), 400

    hist_mode = body.get("historical_mode")
    if not isinstance(hist_mode, bool):
        return jsonify({"error": "historical_mode must be a boolean"}), 400

    try:
        ppdn = int(body.get("posts_per_day_new"))
    except (TypeError, ValueError):
        return jsonify({"error": "posts_per_day_new must be an integer"}), 400
    if ppdn < 1 or ppdn > 5:
        return jsonify({"error": "posts_per_day_new must be between 1 and 5"}), 400

    try:
        hpw = int(body.get("historical_per_week"))
    except (TypeError, ValueError):
        return jsonify({"error": "historical_per_week must be an integer"}), 400
    if hpw < 0 or hpw > 14:
        return jsonify({"error": "historical_per_week must be between 0 and 14"}), 400

    # Load config
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    sites = cfg.get("sites", [])
    site = next((s for s in sites if s.get("id") == site_id), None)
    if not site:
        return jsonify({"error": f"Unknown site_id '{site_id}'"}), 404

    site["historical_mode"]     = hist_mode
    site["posts_per_day_new"]   = ppdn
    site["historical_per_week"] = hpw

    # Atomic write: write to .tmp then rename
    try:
        tmp_path = CONFIG_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(CONFIG_PATH))
    except Exception as e:
        return jsonify({"error": f"Could not write network-config.json: {e}"}), 500

    return jsonify({
        "ok":      True,
        "site_id": site_id,
        "schedule": {
            "historical_mode":     hist_mode,
            "posts_per_day_new":   ppdn,
            "historical_per_week": hpw,
        },
    })

# ── Publish / Sync Center ─────────────────────────────────────────────────────
# Scans the local working copy and compares files against their remote
# counterparts on GitHub (per-file blob SHA). Anything that differs is reported
# as "pending" so the dashboard can push it from one place.

def _gh_blob_sha(data_bytes):
    """Compute the SHA that GitHub assigns to a blob: sha1("blob <len>\\0<data>")."""
    header = f"blob {len(data_bytes)}\0".encode("utf-8")
    return hashlib.sha1(header + data_bytes).hexdigest()

def _gh_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
    }

def _gh_get_remote_sha(repo, path, token, timeout=12):
    """Return (sha, error_str). sha is None if remote file does not exist."""
    try:
        r = requests.get(
            f"https://api.github.com/repos/{repo}/contents/{path}",
            headers=_gh_headers(token), timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        return None, f"network error: {e}"
    if r.status_code == 404:
        return None, None
    if r.status_code in (401, 403):
        return None, f"auth {r.status_code}: {r.text[:160]}"
    if r.status_code != 200:
        return None, f"http {r.status_code}: {r.text[:160]}"
    try:
        return r.json().get("sha"), None
    except Exception as e:
        return None, f"bad json: {e}"

def _gh_put_file(repo, path, data_bytes, message, remote_sha, token, timeout=25):
    """PUT a single file to GitHub. Returns (ok, status, message)."""
    import base64
    payload = {
        "message": message,
        "content": base64.b64encode(data_bytes).decode(),
    }
    if remote_sha:
        payload["sha"] = remote_sha
    try:
        r = requests.put(
            f"https://api.github.com/repos/{repo}/contents/{path}",
            headers=_gh_headers(token), json=payload, timeout=timeout,
        )
    except requests.exceptions.RequestException as e:
        return False, 0, f"network error: {e}"
    if r.status_code in (200, 201):
        return True, r.status_code, "OK"
    # Try to surface GitHub error body
    try:
        body = r.json()
        body_msg = body.get("message") or r.text[:240]
    except Exception:
        body_msg = r.text[:240]
    return False, r.status_code, body_msg

# Files (relative to BASE_DIR) that live in the bot repo at the same path.
# Order matters only for display.
_ENGINE_FILES = [
    "bot.py", "layout_shell.py", "push-sites.py", "rebuild-articles.py",
    "sync.py", "sync_articles.py", "categories.json", "network-config.json",
    "deploy-bot.py",
]
_DASHBOARD_FILES = ["dashboard.html", "server.py"]

def _scan_pending(token):
    """Walk all change kinds and return list of pending change descriptors."""
    pending = []
    errors  = []

    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return [], [f"Could not read network-config.json: {e}"]

    sites    = cfg.get("sites", []) or []
    bot_repo = (cfg.get("settings", {}) or {}).get("bot_repo", "").strip()
    if not bot_repo or "YOUR_" in bot_repo:
        bot_repo = ""

    def _add_check(local_path: Path, repo: str, remote_path: str, kind: str, label: str, summary: str = ""):
        if not local_path.exists():
            return
        if not repo:
            errors.append(f"{kind}: no repo configured for {local_path.name}")
            return
        try:
            data = local_path.read_bytes()
        except Exception as e:
            errors.append(f"{kind}: could not read {local_path}: {e}")
            return
        local_sha = _gh_blob_sha(data)
        remote_sha, err = _gh_get_remote_sha(repo, remote_path, token)
        if err:
            errors.append(f"{kind} {label}: {err}")
            return
        if remote_sha == local_sha:
            return
        change_id = f"{kind}::{repo}::{remote_path}"
        pending.append({
            "id":          change_id,
            "kind":        kind,
            "path":        str(local_path.relative_to(BASE_DIR)),
            "remote_path": remote_path,
            "target_repo": repo,
            "label":       label,
            "summary":     summary or ("new file" if remote_sha is None else "modified"),
            "local_sha":   local_sha,
            "remote_sha":  remote_sha,
        })

    # 1. Homepages: templates/<stem>-index.html  ->  Siavashsed/<stem>/index.html
    tpl_dir = BASE_DIR / "templates"
    if tpl_dir.exists():
        # Build a map of site id -> repo
        for site in sites:
            sid  = (site.get("id") or "").strip()
            repo = (site.get("repo") or "").strip()
            if not sid or not repo or "YOUR_" in repo:
                continue
            tpl = tpl_dir / f"{sid}-index.html"
            if tpl.exists():
                _add_check(tpl, repo, "index.html", "homepage",
                           f"templates/{tpl.name} -> {repo}/index.html",
                           "homepage template")

    # 2. About bodies: about-bodies/<stem>.html -> bot_repo/about-bodies/<stem>.html
    ab_dir = BASE_DIR / "about-bodies"
    if ab_dir.exists() and bot_repo:
        for f in sorted(ab_dir.glob("*.html")):
            rel = f"about-bodies/{f.name}"
            _add_check(f, bot_repo, rel, "about_body",
                       f"{rel} -> {bot_repo}/{rel}", "about page body")

    # 3. Engine files
    if bot_repo:
        for name in _ENGINE_FILES:
            f = BASE_DIR / name
            _add_check(f, bot_repo, name, "engine",
                       f"{name} -> {bot_repo}/{name}", "engine source")

        # 4. Workflows
        wf_dir = BASE_DIR / ".github" / "workflows"
        if wf_dir.exists():
            for f in sorted(wf_dir.glob("*.yml")):
                rel = f".github/workflows/{f.name}"
                _add_check(f, bot_repo, rel, "workflow",
                           f"{rel} -> {bot_repo}/{rel}", "GitHub Actions workflow")

        # 5. Dashboard
        for name in _DASHBOARD_FILES:
            f = BASE_DIR / name
            _add_check(f, bot_repo, name, "dashboard",
                       f"{name} -> {bot_repo}/{name}", "dashboard / server")

    return pending, errors

@app.route("/api/pending", methods=["GET"])
def list_pending():
    token = (request.headers.get("X-GH-Token", "").strip()
             or os.environ.get("GITHUB_TOKEN", "").strip())
    if not token:
        return jsonify({"error": "GitHub token required (X-GH-Token header or GITHUB_TOKEN env)"}), 400
    try:
        pending, errors = _scan_pending(token)
    except Exception as e:
        return jsonify({"error": f"Scan failed: {e}"}), 500
    return jsonify({"ok": True, "pending": pending, "errors": errors,
                    "count": len(pending)})

@app.route("/api/publish", methods=["POST"])
def publish_pending():
    body  = request.get_json(force=True, silent=True) or {}
    ids   = body.get("ids") or []
    token = (body.get("token") or "").strip() \
            or request.headers.get("X-GH-Token", "").strip() \
            or os.environ.get("GITHUB_TOKEN", "").strip()
    if not isinstance(ids, list) or not ids:
        return jsonify({"error": "ids (non-empty list) is required"}), 400
    if not token:
        return jsonify({"error": "GitHub token required (body.token, X-GH-Token header, or GITHUB_TOKEN env)"}), 400

    # Rescan so we have current remote SHAs (avoids stale-sha conflicts).
    try:
        pending, _errors = _scan_pending(token)
    except Exception as e:
        return jsonify({"error": f"Scan failed: {e}"}), 500
    by_id = {p["id"]: p for p in pending}

    results = []
    for idx, change_id in enumerate(ids):
        item = by_id.get(change_id)
        if not item:
            results.append({"id": change_id, "ok": False, "status": 0,
                            "message": "not pending (already in sync or unknown id)"})
            continue
        local_path = BASE_DIR / item["path"]
        if not local_path.exists():
            results.append({"id": change_id, "ok": False, "status": 0,
                            "message": f"local file missing: {item['path']}"})
            continue
        try:
            data = local_path.read_bytes()
        except Exception as e:
            results.append({"id": change_id, "ok": False, "status": 0,
                            "message": f"read error: {e}"})
            continue
        msg = f"Publish {item['kind']}: {item['remote_path']}"
        ok, status, body_msg = _gh_put_file(
            item["target_repo"], item["remote_path"], data, msg,
            item.get("remote_sha"), token,
        )
        results.append({
            "id":          change_id,
            "ok":          ok,
            "status":      status,
            "message":     body_msg,
            "kind":        item["kind"],
            "target_repo": item["target_repo"],
            "remote_path": item["remote_path"],
        })
        # Pace GitHub PUTs to avoid secondary rate limits.
        if idx < len(ids) - 1:
            time.sleep(0.4)

    ok_count   = sum(1 for r in results if r["ok"])
    fail_count = len(results) - ok_count
    return jsonify({
        "ok":         fail_count == 0,
        "results":    results,
        "ok_count":   ok_count,
        "fail_count": fail_count,
    })

# ── Main ──────────────────────────────────────────────────────────────────────
def open_browser():
    time.sleep(2.5)
    webbrowser.open(f"http://localhost:{PORT}/start")

if __name__ == "__main__":
    print(f"\n  Kavalsia Network")
    print(f"  ─────────────────────────────────")
    print(f"  Server: http://localhost:{PORT}")
    print(f"  Config: {CONFIG_PATH}")
    print(f"  Press Ctrl+C to stop\n")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="127.0.0.1", port=PORT, debug=False, threaded=True)
