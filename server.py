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
LATEST_ARTICLES_PATH = BASE_DIR / "latest_articles.json"
# Secrets live in the user's home so they are NEVER tracked by git or pushed by
# deploy-bot.py. Any browser/device hitting the local server reads the same
# file, so opening the dashboard fresh auto-loads every API key + token.
SECRETS_PATH         = Path.home() / ".kavalsia" / "secrets.json"
PORT                 = 8765

app = Flask(__name__, static_folder=str(BASE_DIR))
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB max

# ── Serve static files ────────────────────────────────────────────────────────
PAGES = {
    "home":      "start.html",
    "start":     "start.html",
    # /hub is the Editor (global prompt, negative prompt, global scripts, sponsor
    # posts, per-site overrides). It used to redirect to /dashboard, but the
    # dashboard duplicates none of the global-prompt UI - the editor owns it.
    "hub":       "editor.html",
    "dashboard": "dashboard.html",
    "megadash":  "megadash.html",
    "mega":      "megadash.html",
    "editor":    "editor.html",
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


# ── Secrets vault (API keys + tokens, persisted to disk) ──────────────────────
# Stored at ~/.kavalsia/secrets.json. Never committed, never deployed. Read by
# every browser tab that opens the dashboard so a new browser does not need to
# re-enter keys. Whitelisted set of allowed key names defended at write time.
SECRET_KEYS_ALLOWED = {
    "anthropicKey", "claudeModel", "ghToken", "pexelsKey", "brevoKey",
    "hubApiUrl", "botRepo", "branch", "workflow",
    "telegramToken", "telegramChatId",
    "cfToken", "cfDomToken",
    "metaPixelId", "metaCapiToken", "metaTestEvent",
    "wpUrl", "wpUser", "wpAppPass",
    "wooKey", "wooSecret",
    "shopifyDomain", "shopifyToken",
    "ghlWebhook", "ghlApiKey",
}


def _load_secrets_file():
    if not SECRETS_PATH.exists():
        return {}
    try:
        return json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_secrets_file(d):
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Restrict file perms so other users on the machine cannot read it.
    SECRETS_PATH.write_text(json.dumps(d, indent=2), encoding="utf-8")
    try:
        SECRETS_PATH.chmod(0o600)
    except Exception:
        pass


@app.route("/api/secrets", methods=["GET"])
def get_secrets():
    """Return the on-disk secrets dict. Localhost-only since the Flask server
    binds to 127.0.0.1; never exposed externally."""
    return jsonify(_load_secrets_file())


@app.route("/api/secrets", methods=["POST"])
def save_secrets():
    """Merge incoming dict into the on-disk secrets file. Unknown keys rejected
    (whitelist) so a stray POST cannot pollute the file with arbitrary data."""
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"error": "body must be an object"}), 400
    bad = [k for k in body if k not in SECRET_KEYS_ALLOWED]
    if bad:
        return jsonify({"error": f"unknown secret keys: {', '.join(bad)}"}), 400
    cur = _load_secrets_file()
    # Only string values; empty string clears that key.
    for k, v in body.items():
        v = "" if v is None else str(v)
        if v:
            cur[k] = v
        else:
            cur.pop(k, None)
    _write_secrets_file(cur)
    return jsonify({"ok": True, "path": str(SECRETS_PATH), "count": len(cur)})


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

# ── Logo bar (snippet) ───────────────────────────────────────────────────────
LOGO_BAR_PATH = BASE_DIR / "snippets" / "logo-bar.html"

@app.route("/api/logo-bar", methods=["GET"])
def logo_bar_get():
    try:
        html = LOGO_BAR_PATH.read_text(encoding="utf-8")
        return jsonify({"ok": True, "html": html, "path": "snippets/logo-bar.html"})
    except FileNotFoundError:
        return jsonify({"ok": False, "html": "", "path": "snippets/logo-bar.html"}), 404

@app.route("/api/logo-bar/rebuild", methods=["POST"])
def logo_bar_rebuild():
    import logo_bar_builder
    html = logo_bar_builder.write_logo_bar()
    return jsonify({"ok": True, "html": html, "path": "snippets/logo-bar.html"})

# Per-site include/exclude toggles for the logo bar. Stored as a small JSON
# file so the value is portable across redeploys and easy to inspect by hand.
LOGO_BAR_EXCLUDES_PATH = BASE_DIR / "snippets" / "logo-bar.excludes.json"

def _logo_bar_read_excludes():
    try:
        raw = LOGO_BAR_EXCLUDES_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (FileNotFoundError, ValueError):
        return []
    out = data.get("excluded") if isinstance(data, dict) else None
    if not isinstance(out, list):
        return []
    return [str(x) for x in out if isinstance(x, str)]

@app.route("/api/logo-bar/sites", methods=["GET"])
def logo_bar_sites():
    """Return the canonical site roster (push-sites.py SITES + Nexus) plus the
    current excludes list, so the dashboard can render the toggle UI."""
    import importlib.util as _ilu, sys as _sys
    spec = _ilu.spec_from_file_location("_push_sites_dash", str(BASE_DIR / "push-sites.py"))
    mod  = _ilu.module_from_spec(spec)
    _sys.modules["_push_sites_dash"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    sites = [{"id": s["id"], "name": s["name"], "primary": s.get("primary") or "#9ca3af"}
             for s in mod.SITES]
    sites.append({"id": "nexus", "name": "Nexus", "primary": "#4f8ef7"})
    return jsonify({"ok": True, "sites": sites, "excluded": _logo_bar_read_excludes()})

@app.route("/api/logo-bar/excludes", methods=["GET"])
def logo_bar_excludes_get():
    return jsonify({"ok": True, "excluded": _logo_bar_read_excludes()})

@app.route("/api/logo-bar/excludes", methods=["POST"])
def logo_bar_excludes_set():
    body = request.get_json(silent=True) or {}
    raw = body.get("excluded")
    if not isinstance(raw, list) or not all(isinstance(x, str) for x in raw):
        return jsonify({"ok": False, "error": "excluded must be a list of strings"}), 400
    # Deduplicate while preserving order.
    seen = set()
    cleaned = []
    for x in raw:
        if x and x not in seen:
            seen.add(x)
            cleaned.append(x)
    LOGO_BAR_EXCLUDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOGO_BAR_EXCLUDES_PATH.write_text(
        json.dumps({"excluded": cleaned}, indent=2), encoding="utf-8"
    )
    return jsonify({"ok": True, "excluded": cleaned})

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

# ── Per-site article rebuild (re-wrap with current shell + current author) ───
# Used after Site Settings → Save when the user changes the author name (or
# bio/title) so every already-published article picks up the new author in the
# byline, SEO meta, and JSON-LD without a full network sync.
@app.route("/api/site-rebuild-articles", methods=["POST"])
def site_rebuild_articles():
    data    = request.get_json(force=True, silent=True) or {}
    token   = (data.get("token") or "").strip()
    site_id = (data.get("site_id") or "").strip()
    # Token may come from secrets vault if dashboard did not pass one explicitly.
    if not token:
        token = (_load_secrets_file().get("ghToken") or "").strip()
    if not token:
        return jsonify({"error": "GitHub token required (set it in Settings -> API Keys)"}), 400
    if not site_id:
        return jsonify({"error": "site_id required"}), 400
    cmd = ["python3", str(BASE_DIR / "rebuild-articles.py"), token, "--only", site_id]
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

# ── Latest Posts: cross-network feed + per-article metadata edits ─────────────
def _gh_headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

def _resolve_gh_token(body):
    t = ((body or {}).get("token") or "").strip() \
        or request.headers.get("X-GH-Token", "").strip() \
        or os.environ.get("GITHUB_TOKEN", "").strip()
    if not t:
        try:
            t = (_load_secrets_file().get("ghToken") or "").strip()
        except Exception:
            t = ""
    return t

def _load_articles_index(repo, token):
    """Returns (articles_list, sha, error_str_or_none)."""
    import base64
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json",
                         headers=_gh_headers(token), timeout=15)
    except requests.exceptions.RequestException as e:
        return [], None, f"network: {e}"
    if r.status_code == 404:
        return [], None, "no articles.json"
    if r.status_code != 200:
        return [], None, f"http {r.status_code}"
    try:
        d = r.json()
        return json.loads(base64.b64decode(d["content"]).decode("utf-8")), d["sha"], None
    except Exception as e:
        return [], None, f"parse: {e}"

@app.route("/api/latest-articles", methods=["GET"])
def latest_articles_get():
    """Return the cached latest-articles mirror."""
    if not LATEST_ARTICLES_PATH.exists():
        return jsonify({"items": [], "last_refreshed": None, "errors": []})
    try:
        return jsonify(json.loads(LATEST_ARTICLES_PATH.read_text(encoding="utf-8")))
    except Exception as e:
        return jsonify({"items": [], "last_refreshed": None, "errors": [str(e)]}), 500

@app.route("/api/latest-articles/refresh", methods=["POST"])
def latest_articles_refresh():
    """
    Pull articles.json from every configured site's GitHub repo, build a flat
    list sorted by date desc, and write it to latest_articles.json.
    Body: { token? } - GitHub PAT (also accepted via X-GH-Token / GITHUB_TOKEN).
    """
    body  = request.get_json(force=True, silent=True) or {}
    token = _resolve_gh_token(body)
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    items, errors = [], []
    for s in cfg.get("sites", []):
        site_id = (s.get("id") or "").strip()
        repo    = (s.get("repo") or "").strip()
        if not site_id or not repo or "YOUR_" in repo:
            continue
        # Skip aggregator/non-publisher sites (e.g. nexus).
        if s.get("new_posts_enabled") is False and not s.get("historical_mode"):
            # Still include - the user may want to edit older posts.
            pass

        arts, _sha, err = _load_articles_index(repo, token)
        if err:
            errors.append({"site_id": site_id, "error": err})
            continue
        domain   = (s.get("domain") or "").strip()
        sitename = (s.get("name") or s.get("_name") or site_id).strip()
        for a in arts:
            slug = (a.get("slug") or "").strip("/")
            if not slug:
                continue
            items.append({
                "site_id":   site_id,
                "site_name": sitename,
                "repo":      repo,
                "slug":      slug,
                "title":     a.get("title", ""),
                "author":    a.get("author", ""),
                "date":      a.get("date", ""),
                "date_iso":  a.get("date_iso", ""),
                "category":  a.get("category", ""),
                "meta_description": a.get("meta_description", ""),
                "image":     a.get("image", ""),
                "url":       f"https://{domain}/{slug}/" if domain else "",
                "posted_iso": a.get("posted_iso", ""),
            })

    # Sort by ISO date desc (fallback to posted_iso, then empty last).
    items.sort(key=lambda x: (x.get("date_iso") or x.get("posted_iso") or ""), reverse=True)

    payload = {
        "items":          items,
        "last_refreshed": datetime.now().isoformat(timespec="seconds"),
        "errors":         errors,
    }
    try:
        LATEST_ARTICLES_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as e:
        return jsonify({"error": f"Could not write latest_articles.json: {e}"}), 500

    return jsonify(payload)

@app.route("/api/article-meta", methods=["POST"])
def update_article_meta():
    """
    Body: { site_id, slug, title?, author?, date?, date_iso?, category?,
            meta_description?, token? }
    Updates the article metadata in BOTH:
      - <repo>/articles.json (the index entry)
      - <repo>/<slug>/index.html (best-effort regex patches for title tag,
        og/twitter meta, article:published_time, h1, byline date/author)
    Also patches the local latest_articles.json mirror so the dashboard refresh
    reflects the change instantly.
    Returns { ok, updated_index, updated_html, changed_fields, messages }.
    """
    import base64, re as _re

    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    slug    = (body.get("slug") or "").strip().strip("/")
    token   = _resolve_gh_token(body)
    if not site_id or not slug:
        return jsonify({"error": "site_id and slug are required"}), 400
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    # Fields we accept. Missing keys = no change.
    EDITABLE = ["title", "author", "date", "date_iso", "category", "meta_description"]
    edits = {k: body[k] for k in EDITABLE if k in body and body[k] is not None}
    if not edits:
        return jsonify({"error": "no editable fields provided"}), 400
    # Normalize strings (don't strip date_iso since it must stay ISO).
    for k in list(edits.keys()):
        if isinstance(edits[k], str):
            edits[k] = edits[k].strip()

    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500
    site = next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)
    if not site:
        return jsonify({"error": f"Unknown site_id '{site_id}'"}), 404
    repo = (site.get("repo") or "").strip()
    if not repo or "YOUR_" in repo:
        return jsonify({"error": f"Site '{site_id}' has no valid repo"}), 400

    headers  = _gh_headers(token)
    messages = []

    # 1. Load articles.json
    articles, idx_sha, err = _load_articles_index(repo, token)
    if err:
        return jsonify({"error": f"articles.json: {err}"}), 502
    art = next((a for a in articles if (a.get("slug","").strip("/") == slug)), None)
    if art is None:
        return jsonify({"error": f"Article slug '{slug}' not found"}), 404

    old = {k: (art.get(k) or "") for k in EDITABLE}
    changed = {k: edits[k] for k in edits if str(edits[k]) != str(old.get(k,""))}
    if not changed:
        return jsonify({"ok": True, "updated_index": False, "updated_html": False,
                        "changed_fields": [], "messages": ["No changes."]})

    # 2. Fetch + patch the article HTML (best-effort)
    html_path = f"{slug}/index.html"
    updated_html = False
    try:
        hr = requests.get(f"https://api.github.com/repos/{repo}/contents/{html_path}",
                          headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network fetching article HTML: {e}"}), 502
    if hr.status_code in (401, 403):
        return jsonify({"error": f"GitHub auth failed ({hr.status_code})"}), hr.status_code
    if hr.status_code == 404:
        messages.append(f"{html_path} not found - articles.json only.")
        html, html_sha = None, None
    elif hr.status_code != 200:
        return jsonify({"error": f"GitHub returned {hr.status_code} for {html_path}"}), hr.status_code
    else:
        hd       = hr.json()
        html_sha = hd["sha"]
        html     = base64.b64decode(hd["content"]).decode("utf-8", errors="replace")

    if html:
        new_html = html
        patches  = []

        # --- Title ---
        if "title" in changed:
            old_t, new_t = old.get("title",""), changed["title"]
            if old_t:
                esc = _re.escape(old_t)
                # <title>OLD ...</title>  (preserve site-name suffix)
                new_html, n = _re.subn(rf"(<title[^>]*>)\s*{esc}", lambda m: m.group(1) + new_t, new_html, count=1)
                if n: patches.append(f"title:{n}")
                # og/twitter title meta
                for prop in ('property="og:title"', 'name="twitter:title"', 'name="title"'):
                    new_html, n = _re.subn(rf'(<meta\s+{prop}\s+content=")' + esc + r'(")',
                                           lambda m: m.group(1) + new_t + m.group(2), new_html)
                    if n: patches.append(f"meta-title:{n}")
                # h1 inside article body
                new_html, n = _re.subn(rf'(<h1\b[^>]*>)\s*{esc}\s*(</h1>)',
                                       lambda m: m.group(1) + new_t + m.group(2), new_html, count=1)
                if n: patches.append(f"h1:{n}")
                # JSON-LD "headline": "OLD"
                new_html, n = _re.subn(rf'("headline"\s*:\s*")' + esc + r'(")',
                                       lambda m: m.group(1) + new_t + m.group(2), new_html, count=1)
                if n: patches.append(f"ld-headline:{n}")

        # --- Description ---
        if "meta_description" in changed:
            old_d, new_d = old.get("meta_description",""), changed["meta_description"]
            if old_d:
                esc = _re.escape(old_d)
                for sel in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
                    new_html, n = _re.subn(rf'(<meta\s+{sel}\s+content=")' + esc + r'(")',
                                           lambda m: m.group(1) + new_d + m.group(2), new_html)
                    if n: patches.append(f"meta-desc:{n}")
                new_html, n = _re.subn(rf'("description"\s*:\s*")' + esc + r'(")',
                                       lambda m: m.group(1) + new_d + m.group(2), new_html, count=1)
                if n: patches.append(f"ld-desc:{n}")

        # --- Author byline (reuse the author patterns) ---
        if "author" in changed:
            old_a, new_a = old.get("author",""), changed["author"]
            if old_a:
                esc = _re.escape(old_a)
                pats = [
                    rf'(By\s*<strong\b[^>]*>)\s*{esc}\s*(</strong>)',
                    rf'(<div\b[^>]*class="[^"]*\bbyline\b[^"]*"[^>]*>)([^<]*?){esc}([^<]*?)(</div>)',
                    rf'(<(?:span|div|a|p)\b[^>]*class="[^"]*\bauthor\b[^"]*"[^>]*>)\s*{esc}\s*(</(?:span|div|a|p)>)',
                    rf'(itemprop="author"[^>]*>)\s*{esc}\s*(<)',
                    rf'(>\s*By\s+){esc}(\b)',
                ]
                total = 0
                for p in pats:
                    new_html, n = _re.subn(p, lambda m: m.group(0).replace(old_a, new_a), new_html,
                                           flags=_re.IGNORECASE | _re.DOTALL)
                    total += n
                if total: patches.append(f"author:{total}")

        # --- Date display + ISO ---
        if "date" in changed:
            old_dt, new_dt = old.get("date",""), changed["date"]
            if old_dt:
                # Inside <time>OLD</time> first (most specific)
                esc = _re.escape(old_dt)
                new_html, n = _re.subn(rf'(<time\b[^>]*>)\s*{esc}\s*(</time>)',
                                       lambda m: m.group(1) + new_dt + m.group(2), new_html, count=1)
                if n: patches.append(f"time:{n}")
                else:
                    # Loose: replace first occurrence in the body
                    new_html, n = _re.subn(esc, new_dt, new_html, count=1)
                    if n: patches.append(f"date-text:{n}")

        if "date_iso" in changed:
            old_iso, new_iso = old.get("date_iso",""), changed["date_iso"]
            if old_iso:
                esc = _re.escape(old_iso)
                # article:published_time meta
                new_html, n = _re.subn(rf'(<meta\s+property="article:published_time"\s+content=")' + esc + r'(")',
                                       lambda m: m.group(1) + new_iso + m.group(2), new_html)
                if n: patches.append(f"pub-iso:{n}")
                # <time datetime="OLD">
                new_html, n = _re.subn(rf'(<time\b[^>]*datetime=")' + esc + r'(")',
                                       lambda m: m.group(1) + new_iso + m.group(2), new_html)
                if n: patches.append(f"datetime:{n}")
                # JSON-LD datePublished
                new_html, n = _re.subn(rf'("datePublished"\s*:\s*")' + esc + r'(")',
                                       lambda m: m.group(1) + new_iso + m.group(2), new_html)
                if n: patches.append(f"ld-pub:{n}")

        if new_html != html:
            put = {
                "message": f"Edit metadata for {slug}: {', '.join(changed.keys())}",
                "content": base64.b64encode(new_html.encode("utf-8")).decode(),
                "sha":     html_sha,
            }
            try:
                pr = requests.put(f"https://api.github.com/repos/{repo}/contents/{html_path}",
                                  headers=headers, json=put, timeout=20)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Network pushing HTML: {e}"}), 502
            if pr.status_code not in (200, 201):
                return jsonify({"error": f"HTML push failed ({pr.status_code}): {pr.text[:300]}"}), pr.status_code
            updated_html = True
            messages.append("HTML patched: " + ", ".join(patches) if patches else "HTML rewritten.")
        else:
            messages.append("No regex matched in HTML - articles.json updated, but page text may still show old values until next rebuild-articles.")

    # 3. Patch articles.json
    for k, v in changed.items():
        art[k] = v
    content_b64 = base64.b64encode(json.dumps(articles, indent=2).encode("utf-8")).decode()
    def _put_idx(sha):
        return requests.put(f"https://api.github.com/repos/{repo}/contents/articles.json",
                            headers=headers,
                            json={"message": f"Edit metadata for {slug}: {', '.join(changed.keys())}",
                                  "content": content_b64, "sha": sha},
                            timeout=20)
    try:
        ir = _put_idx(idx_sha)
        if ir.status_code == 409:
            rr = requests.get(f"https://api.github.com/repos/{repo}/contents/articles.json",
                              headers=headers, timeout=15)
            if rr.status_code == 200:
                fresh = rr.json()
                fresh_articles = json.loads(base64.b64decode(fresh["content"]).decode("utf-8"))
                for fa in fresh_articles:
                    if (fa.get("slug","").strip("/") == slug):
                        for k, v in changed.items():
                            fa[k] = v
                        break
                content_b64 = base64.b64encode(json.dumps(fresh_articles, indent=2).encode("utf-8")).decode()
                ir = _put_idx(fresh["sha"])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Network pushing articles.json: {e}",
                        "updated_html": updated_html}), 502
    if ir.status_code not in (200, 201):
        return jsonify({"error": f"articles.json push failed ({ir.status_code}): {ir.text[:300]}",
                        "updated_html": updated_html}), ir.status_code

    # 4. Patch the local latest_articles.json mirror so dashboard reflects instantly.
    try:
        if LATEST_ARTICLES_PATH.exists():
            mirror = json.loads(LATEST_ARTICLES_PATH.read_text(encoding="utf-8"))
            for it in mirror.get("items", []):
                if it.get("site_id") == site_id and (it.get("slug","").strip("/") == slug):
                    for k, v in changed.items():
                        it[k] = v
                    break
            LATEST_ARTICLES_PATH.write_text(json.dumps(mirror, indent=2), encoding="utf-8")
    except Exception as e:
        messages.append(f"local mirror not updated: {e}")

    return jsonify({
        "ok":             True,
        "updated_index":  True,
        "updated_html":   updated_html,
        "changed_fields": list(changed.keys()),
        "messages":       messages,
    })

# ── Comment Date Audit + Fix (enforce comment.date_iso >= post.date_iso + 1d) ──
@app.route("/api/comments-fix", methods=["POST"])
def comments_fix():
    """
    Walk every site's articles.json, fetch each <slug>/comments.json, and enforce:
      comment.date_iso >= article.date_iso + 1 day
    Violations are spread evenly across [art+1d, art+max_age_days] (max_age from
    site.comment_schedule.max_age_days, default 4). Replies are also enforced and
    pinned to >= parent comment's adjusted date.
    Body: { token?, only_site_id?, dry_run? (default false) }
    Returns: { ok, scanned, fixed, sites:[{site_id, articles_scanned, articles_with_violations, fixes, errors:[]}] }
    """
    import base64, random as _rand
    body         = request.get_json(force=True, silent=True) or {}
    token        = _resolve_gh_token(body)
    only_site    = (body.get("only_site_id") or "").strip()
    dry_run      = bool(body.get("dry_run", False))
    if not token:
        return jsonify({"error": "GitHub token required"}), 400
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    headers = _gh_headers(token)
    today   = datetime.now()
    sites_report = []
    total_scanned = total_fixed = 0

    for site in cfg.get("sites", []):
        sid  = (site.get("id") or "").strip()
        repo = (site.get("repo") or "").strip()
        if not sid or not repo or "YOUR_" in repo: continue
        if only_site and sid != only_site:        continue

        max_age = max(1, int((site.get("comment_schedule") or {}).get("max_age_days", 4)))
        s_rep   = {"site_id": sid, "repo": repo, "articles_scanned": 0,
                   "articles_with_violations": 0, "fixes": 0, "errors": []}

        arts, _sha, err = _load_articles_index(repo, token)
        if err:
            s_rep["errors"].append(f"articles.json: {err}")
            sites_report.append(s_rep); continue

        for a in arts:
            slug   = (a.get("slug") or "").strip("/")
            artiso = (a.get("date_iso") or "").strip()
            if not slug or not artiso:
                continue
            try:
                art_dt = datetime.strptime(artiso, "%Y-%m-%d")
            except Exception:
                continue
            s_rep["articles_scanned"] += 1
            total_scanned += 1

            # Fetch comments.json
            url = f"https://api.github.com/repos/{repo}/contents/{slug}/comments.json"
            try:
                cr = requests.get(url, headers=headers, timeout=15)
            except requests.exceptions.RequestException as e:
                s_rep["errors"].append(f"{slug}: network {e}")
                continue
            if cr.status_code == 404:
                continue  # no comments yet
            if cr.status_code != 200:
                s_rep["errors"].append(f"{slug}: http {cr.status_code}")
                continue
            try:
                cdata = cr.json()
                csha  = cdata["sha"]
                comments = json.loads(base64.b64decode(cdata["content"]).decode("utf-8"))
            except Exception as e:
                s_rep["errors"].append(f"{slug}: parse {e}")
                continue
            if not isinstance(comments, list) or not comments:
                continue

            min_floor = art_dt + timedelta(days=1)
            max_ceil  = art_dt + timedelta(days=max_age)
            if max_ceil > today:
                max_ceil = today
            if max_ceil < min_floor:
                max_ceil = min_floor  # tight window for very fresh posts

            n_fixes_in_article = 0

            # Pass 1: fix top-level comments
            for c in comments:
                ciso = (c.get("date_iso") or "").strip()
                try:
                    cdt = datetime.strptime(ciso, "%Y-%m-%d") if ciso else None
                except Exception:
                    cdt = None
                if cdt is None or cdt < min_floor:
                    # Pick a new date evenly spread across [min_floor, max_ceil]
                    span = max(0, (max_ceil - min_floor).days)
                    new_dt = min_floor + timedelta(days=_rand.randint(0, span),
                                                   hours=_rand.randint(1, 22))
                    if new_dt > today:
                        new_dt = today - timedelta(hours=_rand.randint(1, 18))
                    c["date_iso"]     = new_dt.strftime("%Y-%m-%d")
                    c["date_display"] = new_dt.strftime("%b %d, %Y")
                    n_fixes_in_article += 1

            # Pass 2: fix replies (must be >= parent.date_iso AND >= min_floor)
            for c in comments:
                replies = c.get("replies") or []
                if not isinstance(replies, list): continue
                try:
                    parent_dt = datetime.strptime(c["date_iso"], "%Y-%m-%d")
                except Exception:
                    parent_dt = min_floor
                reply_floor = max(parent_dt, min_floor)
                for r in replies:
                    riso = (r.get("date_iso") or "").strip()
                    try:
                        rdt = datetime.strptime(riso, "%Y-%m-%d") if riso else None
                    except Exception:
                        rdt = None
                    if rdt is None or rdt < reply_floor:
                        span = max(0, (max_ceil - reply_floor).days)
                        new_dt = reply_floor + timedelta(days=_rand.randint(0, span),
                                                         hours=_rand.randint(1, 22))
                        if new_dt > today:
                            new_dt = today - timedelta(hours=_rand.randint(1, 18))
                        r["date_iso"]     = new_dt.strftime("%Y-%m-%d")
                        r["date_display"] = new_dt.strftime("%b %d, %Y")
                        n_fixes_in_article += 1

            if n_fixes_in_article == 0:
                continue

            # Sort comments by date_iso for tidy display.
            comments.sort(key=lambda x: x.get("date_iso", ""))
            for c in comments:
                if isinstance(c.get("replies"), list):
                    c["replies"].sort(key=lambda x: x.get("date_iso", ""))

            s_rep["articles_with_violations"] += 1
            s_rep["fixes"] += n_fixes_in_article
            total_fixed   += n_fixes_in_article

            if dry_run:
                continue

            # Push the corrected comments.json back.
            put = {
                "message": f"Fix comment dates (>= post+1d) for {slug}",
                "content": base64.b64encode(json.dumps(comments, indent=2).encode()).decode(),
                "sha":     csha,
            }
            try:
                pr = requests.put(url, headers=headers, json=put, timeout=20)
            except requests.exceptions.RequestException as e:
                s_rep["errors"].append(f"{slug}: push network {e}")
                continue
            if pr.status_code not in (200, 201):
                s_rep["errors"].append(f"{slug}: push http {pr.status_code}")
                continue

        sites_report.append(s_rep)

    return jsonify({
        "ok": True, "dry_run": dry_run,
        "scanned": total_scanned, "fixed": total_fixed,
        "sites": sites_report,
    })

# ── Article delete (removes from articles.json + deletes slug folder contents) ─
@app.route("/api/article-delete", methods=["POST"])
def article_delete():
    """
    Body: { site_id, slug, token?, files_to_delete? (default ["index.html","comments.json"]) }
    Removes the entry from <repo>/articles.json AND deletes the article's files
    under <repo>/<slug>/. Also drops the row from the local latest_articles.json
    mirror so the dashboard reflects the removal instantly.
    Returns { ok, deleted_files:[...], removed_from_index:bool, messages:[] }.
    """
    import base64
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    slug    = (body.get("slug") or "").strip().strip("/")
    token   = _resolve_gh_token(body)
    files   = body.get("files_to_delete") or ["index.html", "comments.json"]
    if not site_id or not slug:
        return jsonify({"error": "site_id and slug are required"}), 400
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500
    site = next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)
    if not site:
        return jsonify({"error": f"Unknown site_id '{site_id}'"}), 404
    repo = (site.get("repo") or "").strip()
    if not repo or "YOUR_" in repo:
        return jsonify({"error": f"Site '{site_id}' has no valid repo"}), 400

    headers  = _gh_headers(token)
    messages = []
    deleted  = []

    # 1. Delete files under <slug>/
    for fname in files:
        path = f"{slug}/{fname}"
        url  = f"https://api.github.com/repos/{repo}/contents/{path}"
        try:
            g = requests.get(url, headers=headers, timeout=15)
        except requests.exceptions.RequestException as e:
            messages.append(f"{path}: network {e}"); continue
        if g.status_code == 404:
            messages.append(f"{path}: not found - skipped"); continue
        if g.status_code != 200:
            messages.append(f"{path}: http {g.status_code} - skipped"); continue
        sha = g.json().get("sha")
        if not sha:
            messages.append(f"{path}: no sha - skipped"); continue
        try:
            d = requests.delete(url, headers=headers,
                                json={"message": f"Delete article file {path}", "sha": sha},
                                timeout=20)
        except requests.exceptions.RequestException as e:
            messages.append(f"{path}: delete network {e}"); continue
        if d.status_code not in (200, 201):
            messages.append(f"{path}: delete http {d.status_code} - {d.text[:120]}"); continue
        deleted.append(path)

    # 2. Remove from articles.json
    removed_index = False
    arts, idx_sha, err = _load_articles_index(repo, token)
    if err:
        messages.append(f"articles.json: {err}")
    else:
        new_arts = [a for a in arts if (a.get("slug","").strip("/") != slug)]
        if len(new_arts) == len(arts):
            messages.append("articles.json: entry not present (already removed?)")
        else:
            content_b64 = base64.b64encode(json.dumps(new_arts, indent=2).encode()).decode()
            put = {"message": f"Remove article {slug} from index",
                   "content": content_b64, "sha": idx_sha}
            try:
                pr = requests.put(f"https://api.github.com/repos/{repo}/contents/articles.json",
                                  headers=headers, json=put, timeout=20)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"articles.json push: {e}",
                                "deleted_files": deleted}), 502
            if pr.status_code == 409:
                # Stale SHA retry
                arts2, sha2, _ = _load_articles_index(repo, token)
                new_arts = [a for a in arts2 if (a.get("slug","").strip("/") != slug)]
                content_b64 = base64.b64encode(json.dumps(new_arts, indent=2).encode()).decode()
                pr = requests.put(f"https://api.github.com/repos/{repo}/contents/articles.json",
                                  headers=headers,
                                  json={"message": f"Remove article {slug} from index",
                                        "content": content_b64, "sha": sha2}, timeout=20)
            if pr.status_code not in (200, 201):
                messages.append(f"articles.json push: http {pr.status_code} - {pr.text[:120]}")
            else:
                removed_index = True

    # 3. Update local latest_articles.json mirror
    try:
        if LATEST_ARTICLES_PATH.exists():
            mirror = json.loads(LATEST_ARTICLES_PATH.read_text(encoding="utf-8"))
            before = len(mirror.get("items", []))
            mirror["items"] = [
                it for it in mirror.get("items", [])
                if not (it.get("site_id") == site_id and it.get("slug","").strip("/") == slug)
            ]
            if len(mirror["items"]) != before:
                LATEST_ARTICLES_PATH.write_text(json.dumps(mirror, indent=2), encoding="utf-8")
                messages.append("local mirror updated")
    except Exception as e:
        messages.append(f"mirror not updated: {e}")

    return jsonify({
        "ok": True, "deleted_files": deleted, "removed_from_index": removed_index,
        "messages": messages,
    })

# ── Anthropic token status (ping the API to verify token works) ───────────────
@app.route("/api/anthropic-status", methods=["POST"])
def anthropic_status():
    """
    Body: { token? } - sk-ant-... key. Falls back to secrets file's anthropicKey.
    Pings the Messages API with a minimal call to verify the token works.
    Returns { valid: bool, message: str, model?: str, usage?: {...} }.
    Anthropic does not expose remaining credit balance via the customer API, so
    the UI links to console.anthropic.com/settings/billing for top-ups.
    """
    body = request.get_json(force=True, silent=True) or {}
    key  = (body.get("token") or "").strip()
    if not key:
        try:
            key = (_load_secrets_file().get("anthropicKey") or "").strip()
        except Exception:
            key = ""
    if not key:
        return jsonify({"valid": False, "message": "No Anthropic key provided."})
    if not key.startswith("sk-ant-"):
        return jsonify({"valid": False, "message": "Key does not look like an Anthropic key (sk-ant-...)."})
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":        key,
                "anthropic-version":"2023-06-01",
                "content-type":     "application/json",
            },
            json={
                "model":     "claude-haiku-4-5",
                "max_tokens": 4,
                "messages":  [{"role": "user", "content": "ok"}],
            },
            timeout=15,
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"valid": False, "message": f"Network error: {e}"})
    if r.status_code == 200:
        try:
            d = r.json()
            return jsonify({
                "valid":   True,
                "message": "Token works.",
                "model":   d.get("model", ""),
                "usage":   d.get("usage", {}),
            })
        except Exception:
            return jsonify({"valid": True, "message": "Token works."})
    if r.status_code == 401:
        return jsonify({"valid": False, "message": "401 - invalid or revoked key."})
    if r.status_code == 429:
        return jsonify({"valid": False, "message": "429 - rate limited / credit balance too low."})
    # Try to surface the API error message.
    try:
        err = (r.json().get("error") or {}).get("message", r.text[:160])
    except Exception:
        err = r.text[:160]
    return jsonify({"valid": False, "message": f"{r.status_code}: {err}"})

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

# ── Site Settings (consolidated per-site update) ──────────────────────────────
# POST /api/site-settings
# Body: { "site_id": "<id>", "fields": { <key>: <value>, ... } }
# Merges the provided fields into the matching site object inside
# network-config.json. Only known per-site keys are allowed. Uses the same
# atomic write pattern as /api/site-schedule.
#
# Response: { ok: True, site_id, updated: [<keys>] }
ALLOWED_SITE_FIELDS = {
    # Identity & Persona
    "name", "default_author", "author_names", "persona", "tone",
    "custom_prompt", "custom_css",
    # Posting Schedule (canonical fields the bot reads)
    "posts_per_day_new", "posts_per_week", "historical_mode",
    "historical_per_week", "warming",
    # Pipeline on/off toggles. new_posts_enabled defaults to true if missing.
    "new_posts_enabled",
    # UI round-trip fields so the unit dropdown reopens with the user's choice
    "posts_count", "posts_unit", "historical_count", "historical_unit",
    # Content Pipeline
    "topics", "categories", "default_category", "signup_url",
    "header_scripts", "footer_scripts",
    # GHL (GoHighLevel) integration per-site overrides
    "ghl",
    # Meta Pixel + CAPI per-site overrides (added by Meta agent if missing)
    "meta",
    # WordPress / WooCommerce / Shopify per-site integration overrides
    "wordpress", "woocommerce", "shopify",
    # Translation mode (multi-language sites only)
    "translation_mode",
}

SITE_FIELD_VALIDATORS = {
    "posts_per_day_new":   lambda v: isinstance(v, int) and 1 <= v <= 10,
    "posts_per_week":      lambda v: isinstance(v, int) and 0 <= v <= 50,
    "historical_per_week": lambda v: isinstance(v, int) and 0 <= v <= 70,
    "posts_count":         lambda v: isinstance(v, int) and 0 <= v <= 200,
    "posts_unit":          lambda v: v in ("day", "week", "month", "year"),
    "historical_count":    lambda v: isinstance(v, int) and 0 <= v <= 200,
    "historical_unit":     lambda v: v in ("day", "week", "month", "year"),
    "historical_mode":     lambda v: isinstance(v, bool),
    "new_posts_enabled":   lambda v: isinstance(v, bool),
    "author_names":        lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
    "topics":              lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
    "categories":          lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
    "warming":             lambda v: isinstance(v, dict),
    "ghl":                 lambda v: isinstance(v, dict),
    "meta":                lambda v: isinstance(v, dict),
    "wordpress":           lambda v: isinstance(v, dict),
    "woocommerce":         lambda v: isinstance(v, dict),
    "shopify":             lambda v: isinstance(v, dict),
    "translation_mode":    lambda v: v in ("primary_only", "primary_plus_english", "auto_all"),
}

@app.route("/api/site-settings", methods=["POST"])
def update_site_settings():
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    fields  = body.get("fields") or {}
    if not site_id:
        return jsonify({"error": "site_id is required"}), 400
    if not isinstance(fields, dict) or not fields:
        return jsonify({"error": "fields must be a non-empty object"}), 400

    # Filter to allowed fields and validate
    clean = {}
    rejected = []
    for k, v in fields.items():
        if k not in ALLOWED_SITE_FIELDS:
            rejected.append(k)
            continue
        validator = SITE_FIELD_VALIDATORS.get(k)
        if validator and not validator(v):
            return jsonify({"error": f"Invalid value for field '{k}'"}), 400
        clean[k] = v

    if not clean:
        return jsonify({"error": "No valid fields provided", "rejected": rejected}), 400

    # Load config
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    sites = cfg.get("sites", [])
    site = next((s for s in sites if s.get("id") == site_id), None)
    if not site:
        return jsonify({"error": f"Unknown site_id '{site_id}'"}), 404

    # Merge cleaned fields into the site (warming gets shallow-merged so
    # other warming sub-keys remain intact).
    for k, v in clean.items():
        if k == "warming" and isinstance(site.get("warming"), dict) and isinstance(v, dict):
            merged = dict(site["warming"])
            merged.update(v)
            site["warming"] = merged
        else:
            site[k] = v

    # Atomic write
    try:
        tmp_path = CONFIG_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(CONFIG_PATH))
    except Exception as e:
        return jsonify({"error": f"Could not write network-config.json: {e}"}), 500

    return jsonify({
        "ok":       True,
        "site_id":  site_id,
        "updated":  sorted(clean.keys()),
        "rejected": rejected,
    })

# ── GHL (GoHighLevel) Webhook Test ───────────────────────────────────────────
# POST /api/ghl-test
# Body: { site_id?: str, webhook_url?: str }
# Resolves the effective webhook URL + tags from network-config.json:
#   site-level GHL block overrides settings.ghl global.
#   webhook_url in body overrides everything (manual test).
# POSTs a sample payload + returns status + a body excerpt.
def _ghl_resolve_for_test(cfg, site_id=None, override_url=None):
    settings = (cfg.get("settings") or {})
    g = (settings.get("ghl") or {})
    site = None
    sg = {}
    if site_id:
        site = next((s for s in (cfg.get("sites") or []) if s.get("id") == site_id), None)
        if site:
            sg = site.get("ghl") or {}
    enabled = sg.get("enabled") if "enabled" in sg else g.get("enabled", False)
    url = (override_url or "").strip() or (sg.get("webhook_url") or "").strip() or (g.get("webhook_url") or "").strip()
    tags = []
    if site_id:
        tags.append(site_id)
    for t in (sg.get("tags") or []):
        if isinstance(t, str) and t.strip():
            tags.append(t.strip())
    for t in (g.get("default_tags") or []):
        if isinstance(t, str) and t.strip():
            tags.append(t.strip())
    seen = set(); deduped = []
    for t in tags:
        if t not in seen:
            seen.add(t); deduped.append(t)
    return {
        "enabled":     bool(enabled) or bool(override_url),
        "webhook_url": url,
        "tags":        deduped,
        "site_id":     site_id or "",
        "site_name":   ((site.get("name") if site else "") or (site.get("id") if site else "")) or "",
    }

@app.route("/api/ghl-test", methods=["POST"])
def ghl_test_webhook():
    body = request.get_json(force=True, silent=True) or {}
    site_id      = (body.get("site_id") or "").strip() or None
    override_url = (body.get("webhook_url") or "").strip() or None
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return jsonify({"ok": False, "error": f"Could not read network-config.json: {e}"}), 500

    eff = _ghl_resolve_for_test(cfg, site_id=site_id, override_url=override_url)
    if not eff["enabled"]:
        return jsonify({"ok": False, "error": "GHL is disabled. Enable it globally or per-site, or pass webhook_url to test directly."}), 400
    if not eff["webhook_url"]:
        return jsonify({"ok": False, "error": "No webhook URL resolved. Set settings.ghl.webhook_url, sites[i].ghl.webhook_url, or pass webhook_url in the body."}), 400

    sample = {
        "email":        "test+ghl@kavalsia.com",
        "site_id":      eff["site_id"] or "test-site",
        "site_name":    eff["site_name"] or "Test Site",
        "page_url":     "https://example.com/test",
        "page_title":   "Kavalsia GHL Test",
        "referrer":     "",
        "tags":         eff["tags"] or ["kavalsia-network", "newsletter", "ghl-test"],
        "utm":          {"utm_source": "kavalsia-test", "utm_medium": "ghl-test"},
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "_test":        True,
    }
    try:
        r = requests.post(eff["webhook_url"], json=sample, timeout=12)
        excerpt = (r.text or "")[:600]
        return jsonify({
            "ok":          r.ok,
            "status_code": r.status_code,
            "resolved":    {"webhook_url": eff["webhook_url"], "tags": eff["tags"], "site_id": eff["site_id"]},
            "payload":     sample,
            "response":    excerpt,
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"POST failed: {e}", "resolved": eff, "payload": sample}), 502


# ── Custom Domain Status / Apply / Enforce HTTPS ─────────────────────────────
# Three small endpoints that power the "Custom Domain" card in panel-site.
#   GET  /api/domain-status         -> DNS + GitHub Pages cname + HTTPS state
#   POST /api/domain-apply          -> writes network-config.json, CNAME, Pages
#   POST /api/domain-enforce-https  -> PUT Pages config { https_enforced: true }

def _ds_token():
    """Resolve GitHub token from body/header/env."""
    body = request.get_json(force=True, silent=True) or {}
    return (body.get("token") or "").strip() \
        or request.headers.get("X-GH-Token", "").strip() \
        or os.environ.get("GITHUB_TOKEN", "").strip()

def _ds_site_for(site_id):
    """Load network-config.json and return (cfg, site) or raise ValueError."""
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    site = next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)
    if not site:
        raise ValueError(f"Unknown site_id '{site_id}'")
    return cfg, site

def _ds_is_placeholder(domain):
    """siavashsed.github.io/<id> means 'no custom domain yet'."""
    if not domain:
        return True
    d = domain.lower().strip()
    return d.startswith("siavashsed.github.io")

@app.route("/api/domain-status", methods=["GET"])
def domain_status():
    import socket
    site_id = (request.args.get("site_id") or "").strip()
    if not site_id:
        return jsonify({"error": "site_id is required"}), 400
    token = (request.args.get("token") or "").strip() \
        or request.headers.get("X-GH-Token", "").strip() \
        or os.environ.get("GITHUB_TOKEN", "").strip()

    try:
        _cfg, site = _ds_site_for(site_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    domain = (site.get("domain") or "").strip()
    repo   = (site.get("repo") or "").strip()
    out = {
        "domain":         domain,
        "is_placeholder": _ds_is_placeholder(domain),
        "dns_ok":         "pending",
        "gh_cname":       None,
        "cname_match":    None,
        "https_state":    None,
        "https_enforced": None,
        "http_status":    None,
    }
    if _ds_is_placeholder(domain) or not domain:
        return jsonify(out)

    # DNS resolution via Google DNS-over-HTTPS so the answer reflects real-world
    # state, not the user's local resolver cache (which can lag for hours).
    resolved_ip = ""
    try:
        dr = requests.get(f"https://dns.google/resolve?name={domain}&type=A",
                          timeout=8).json()
        ans = [a for a in (dr.get("Answer") or []) if a.get("type") == 1]
        if ans:
            resolved_ip = ans[0].get("data", "")
            out["dns_ok"] = "yes"
        else:
            out["dns_ok"] = "no"
    except Exception:
        # Fall back to local DNS if DoH fails entirely.
        try:
            resolved_ip = socket.gethostbyname(domain)
            out["dns_ok"] = "yes"
        except Exception:
            out["dns_ok"] = "no"

    # GitHub Pages cname / https state (requires token + repo)
    if token and repo and "YOUR_" not in repo:
        try:
            r = requests.get(
                f"https://api.github.com/repos/{repo}/pages",
                headers=_gh_headers(token), timeout=12,
            )
            if r.status_code == 200:
                jd = r.json() or {}
                out["gh_cname"]       = jd.get("cname")
                out["cname_match"]    = ((jd.get("cname") or "").lower() == domain.lower())
                out["https_enforced"] = bool(jd.get("https_enforced"))
                cert = jd.get("https_certificate") or {}
                out["https_state"]    = cert.get("state") or "none"
            elif r.status_code == 404:
                out["gh_cname"]    = None
                out["cname_match"] = False
                out["https_state"] = "none"
            else:
                out["gh_error"] = f"Pages API {r.status_code}: {r.text[:160]}"
        except requests.exceptions.RequestException as e:
            out["gh_error"] = f"Pages API network error: {e}"

    # Live HTTPS probe - also bypass the local resolver by using the IP we got from
    # public DNS, with a Host header so TLS / vhost routing still works.
    try:
        if resolved_ip:
            pr = requests.get(f"https://{resolved_ip}/", timeout=8, allow_redirects=False,
                              headers={"Host": domain}, verify=False)
        else:
            pr = requests.get(f"https://{domain}/", timeout=8, allow_redirects=True)
        out["http_status"] = pr.status_code
    except requests.exceptions.RequestException as e:
        out["http_status"] = 0
        out["http_error"]  = str(e)[:160]

    return jsonify(out)

@app.route("/api/domain-apply", methods=["POST"])
def domain_apply():
    import base64
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    domain  = (body.get("domain") or "").strip().lower().lstrip("/").rstrip("/")
    token   = (body.get("token") or "").strip() \
        or request.headers.get("X-GH-Token", "").strip() \
        or os.environ.get("GITHUB_TOKEN", "").strip()

    if not site_id or not domain:
        return jsonify({"error": "site_id and domain are required"}), 400
    if "/" in domain or " " in domain or "." not in domain:
        return jsonify({"error": "domain looks invalid (expected e.g. example.com)"}), 400
    if not token:
        return jsonify({"error": "GitHub token required (body.token, X-GH-Token header, or GITHUB_TOKEN env)"}), 400

    try:
        cfg, site = _ds_site_for(site_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    repo = (site.get("repo") or "").strip()
    if not repo or "YOUR_" in repo:
        return jsonify({"error": f"Site '{site_id}' has no valid repo configured"}), 400

    result = {"ok": True, "steps": {}}

    # 1. Update network-config.json
    try:
        site["domain"] = domain
        tmp_path = CONFIG_PATH.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        os.replace(str(tmp_path), str(CONFIG_PATH))
        result["steps"]["config"] = {"ok": True, "domain": domain}
    except Exception as e:
        return jsonify({"error": f"Could not write network-config.json: {e}"}), 500

    headers = _gh_headers(token)

    # 2. PUT CNAME file in the site repo
    cname_url = f"https://api.github.com/repos/{repo}/contents/CNAME"
    try:
        gr = requests.get(cname_url, headers=headers, timeout=12)
        sha = gr.json().get("sha") if gr.status_code == 200 else None
        payload = {
            "message": f"chore: set custom domain to {domain}",
            "content": base64.b64encode((domain + "\n").encode("utf-8")).decode(),
        }
        if sha:
            payload["sha"] = sha
        pr = requests.put(cname_url, headers=headers, json=payload, timeout=15)
        result["steps"]["cname_file"] = {
            "ok": pr.status_code in (200, 201),
            "status": pr.status_code,
            "msg": pr.text[:200] if pr.status_code not in (200, 201) else "written",
        }
    except requests.exceptions.RequestException as e:
        result["steps"]["cname_file"] = {"ok": False, "error": str(e)}

    # 3. PUT GitHub Pages cname
    pages_url = f"https://api.github.com/repos/{repo}/pages"
    try:
        pr = requests.put(pages_url, headers=headers, json={"cname": domain}, timeout=15)
        # GitHub returns 204 No Content on success.
        result["steps"]["pages_cname"] = {
            "ok": pr.status_code in (200, 201, 204),
            "status": pr.status_code,
            "msg": pr.text[:200] if pr.status_code not in (200, 201, 204) else "updated",
        }
    except requests.exceptions.RequestException as e:
        result["steps"]["pages_cname"] = {"ok": False, "error": str(e)}

    result["ok"] = all(s.get("ok") for s in result["steps"].values())
    return jsonify(result)

@app.route("/api/domain-enforce-https", methods=["POST"])
def domain_enforce_https():
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    token   = (body.get("token") or "").strip() \
        or request.headers.get("X-GH-Token", "").strip() \
        or os.environ.get("GITHUB_TOKEN", "").strip()

    if not site_id:
        return jsonify({"error": "site_id is required"}), 400
    if not token:
        return jsonify({"error": "GitHub token required"}), 400

    try:
        _cfg, site = _ds_site_for(site_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Could not read network-config.json: {e}"}), 500

    repo = (site.get("repo") or "").strip()
    if not repo or "YOUR_" in repo:
        return jsonify({"error": f"Site '{site_id}' has no valid repo configured"}), 400

    pages_url = f"https://api.github.com/repos/{repo}/pages"
    try:
        pr = requests.put(pages_url, headers=_gh_headers(token),
                          json={"https_enforced": True}, timeout=15)
        ok = pr.status_code in (200, 201, 204)
        return jsonify({
            "ok":     ok,
            "status": pr.status_code,
            "msg":    pr.text[:200] if not ok else "https_enforced set to true",
        }), (200 if ok else pr.status_code)
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": str(e)}), 502


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

# ── WordPress / WooCommerce / Shopify integrations ────────────────────────────
# Server-to-server integration endpoints. Each test endpoint returns a uniform
# shape (ok / status / message / excerpt) so the dashboard can show raw HTTP
# status + a short response excerpt for debugging. Configs resolve per-site
# override first, then fall back to global settings.<key>.

import base64 as _intg_b64

def _intg_load_cfg():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _intg_resolve(cfg, site_id, key):
    """Return effective config dict for (site_id, key). Per-site override beats global."""
    settings = (cfg.get("settings") or {})
    glob = settings.get(key) or {}
    merged = dict(glob) if isinstance(glob, dict) else {}
    if site_id:
        site = next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)
        if site and isinstance(site.get(key), dict):
            for k, v in site[key].items():
                if v not in (None, ""):
                    merged[k] = v
    return merged

def _intg_excerpt(text, n=240):
    try:
        s = text if isinstance(text, str) else str(text)
    except Exception:
        s = ""
    return s.strip().replace("\r", " ").replace("\n", " ")[:n]

def _intg_norm_url(u):
    u = (u or "").strip().rstrip("/")
    if u and not u.lower().startswith(("http://", "https://")):
        u = "https://" + u
    return u

@app.route("/api/wp-test", methods=["POST"])
def wp_test():
    body = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    cfg = _intg_load_cfg()
    wp = _intg_resolve(cfg, site_id, "wordpress")
    url  = _intg_norm_url(wp.get("url"))
    user = (wp.get("username") or "").strip()
    appp = (wp.get("app_password") or "").strip()
    if not url or not user or not appp:
        return jsonify({"ok": False, "status": 0,
                        "message": "WordPress not configured (need url, username, app_password)",
                        "excerpt": ""})
    auth = _intg_b64.b64encode(f"{user}:{appp}".encode("utf-8")).decode("ascii")
    try:
        r = requests.get(f"{url}/wp-json/wp/v2/posts",
                         params={"per_page": 1},
                         headers={"Authorization": f"Basic {auth}",
                                  "Accept": "application/json"},
                         timeout=12)
        return jsonify({
            "ok":      200 <= r.status_code < 300,
            "status":  r.status_code,
            "message": "WordPress reachable" if r.ok else f"HTTP {r.status_code}",
            "excerpt": _intg_excerpt(r.text),
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "status": 0,
                        "message": f"Network error: {e}", "excerpt": ""})

@app.route("/api/wp-push", methods=["POST"])
def wp_push():
    body = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    cfg = _intg_load_cfg()
    wp = _intg_resolve(cfg, site_id, "wordpress")
    url  = _intg_norm_url(wp.get("url"))
    user = (wp.get("username") or "").strip()
    appp = (wp.get("app_password") or "").strip()
    if not url or not user or not appp:
        return jsonify({"ok": False, "status": 0,
                        "message": "WordPress not configured", "excerpt": ""})
    title   = (body.get("title") or "").strip()
    content = body.get("content") or ""
    if not title or not content:
        return jsonify({"ok": False, "status": 0,
                        "message": "title and content are required",
                        "excerpt": ""}), 400
    payload = {
        "title":   title,
        "content": content,
        "status":  (body.get("status") or "draft"),
    }
    if body.get("slug"):       payload["slug"]       = body["slug"]
    if body.get("categories"): payload["categories"] = body["categories"]
    if body.get("tags"):       payload["tags"]       = body["tags"]
    auth = _intg_b64.b64encode(f"{user}:{appp}".encode("utf-8")).decode("ascii")
    try:
        r = requests.post(f"{url}/wp-json/wp/v2/posts", json=payload,
                          headers={"Authorization": f"Basic {auth}",
                                   "Accept": "application/json"},
                          timeout=20)
        post_url = ""
        try:
            jd = r.json()
            post_url = (jd or {}).get("link") or ""
        except Exception:
            pass
        return jsonify({
            "ok":       200 <= r.status_code < 300,
            "status":   r.status_code,
            "message":  "Post created" if r.ok else f"HTTP {r.status_code}",
            "post_url": post_url,
            "excerpt":  _intg_excerpt(r.text),
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "status": 0,
                        "message": f"Network error: {e}", "excerpt": ""})

@app.route("/api/woo-test", methods=["POST"])
def woo_test():
    body = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    cfg = _intg_load_cfg()
    wc = _intg_resolve(cfg, site_id, "woocommerce")
    url = _intg_norm_url(wc.get("url"))
    ck = (wc.get("consumer_key") or "").strip()
    cs = (wc.get("consumer_secret") or "").strip()
    if not url or not ck or not cs:
        return jsonify({"ok": False, "status": 0,
                        "message": "WooCommerce not configured (need url, consumer_key, consumer_secret)",
                        "excerpt": "", "product_count": 0})
    auth = _intg_b64.b64encode(f"{ck}:{cs}".encode("utf-8")).decode("ascii")
    try:
        r = requests.get(f"{url}/wp-json/wc/v3/products",
                         params={"per_page": 1},
                         headers={"Authorization": f"Basic {auth}",
                                  "Accept": "application/json"},
                         timeout=12)
        product_count = 0
        try:
            jd = r.json()
            if isinstance(jd, list):
                product_count = len(jd)
        except Exception:
            pass
        total = r.headers.get("X-WP-Total") or r.headers.get("x-wp-total")
        try:
            if total is not None:
                product_count = int(total)
        except Exception:
            pass
        return jsonify({
            "ok":            200 <= r.status_code < 300,
            "status":        r.status_code,
            "message":       "WooCommerce reachable" if r.ok else f"HTTP {r.status_code}",
            "product_count": product_count,
            "excerpt":       _intg_excerpt(r.text),
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "status": 0,
                        "message": f"Network error: {e}",
                        "excerpt": "", "product_count": 0})

@app.route("/api/shopify-test", methods=["POST"])
def shopify_test():
    body = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    cfg = _intg_load_cfg()
    sh = _intg_resolve(cfg, site_id, "shopify")
    domain = (sh.get("store_domain") or "").strip().lower()
    if domain.startswith("http://"):  domain = domain[7:]
    if domain.startswith("https://"): domain = domain[8:]
    domain = domain.rstrip("/")
    token = (sh.get("admin_token") or "").strip()
    if not domain or not token:
        return jsonify({"ok": False, "status": 0,
                        "message": "Shopify not configured (need store_domain + admin_token)",
                        "excerpt": "", "shop_name": "", "plan": ""})
    try:
        r = requests.get(f"https://{domain}/admin/api/2024-04/shop.json",
                         headers={"X-Shopify-Access-Token": token,
                                  "Accept": "application/json"},
                         timeout=12)
        shop_name = ""
        plan = ""
        try:
            jd = r.json() or {}
            shop = jd.get("shop") or {}
            shop_name = shop.get("name") or ""
            plan = shop.get("plan_name") or shop.get("plan_display_name") or ""
        except Exception:
            pass
        return jsonify({
            "ok":        200 <= r.status_code < 300,
            "status":    r.status_code,
            "message":   "Shopify reachable" if r.ok else f"HTTP {r.status_code}",
            "shop_name": shop_name,
            "plan":      plan,
            "excerpt":   _intg_excerpt(r.text),
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "status": 0,
                        "message": f"Network error: {e}",
                        "excerpt": "", "shop_name": "", "plan": ""})

# ── Meta Pixel + Conversions API helpers ─────────────────────────────────────
# Resolves effective Meta config (per-site overrides global), generates the
# client-side Pixel snippet that is injected into header_scripts at publish
# time, sends test events to Facebook Conversions API, and stubs Custom
# Audience sync. Kept fully independent from the GHL endpoints.

def _meta_load_cfg():
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Could not read network-config.json: {e}")

def _meta_site_for(cfg, site_id):
    if not site_id:
        return None
    return next((s for s in cfg.get("sites", []) if s.get("id") == site_id), None)

def _meta_resolve(cfg, site=None):
    """Merge global settings.meta with per-site site.meta. Per-site
    non-empty values override the global ones."""
    g = (cfg.get("settings") or {}).get("meta") or {}
    out = {
        "enabled":            bool(g.get("enabled", False)),
        "pixel_id":           str(g.get("pixel_id", "") or ""),
        "capi_token":         str(g.get("capi_token", "") or ""),
        "capi_dataset_id":    str(g.get("capi_dataset_id", "") or ""),
        "test_event_code":    str(g.get("test_event_code", "") or ""),
        "fire_pageview":      bool(g.get("fire_pageview", True)),
        "custom_audience_id": str(g.get("custom_audience_id", "") or ""),
    }
    s = (site or {}).get("meta") or {}
    if not isinstance(s, dict):
        s = {}
    if "enabled" in s:        out["enabled"]            = bool(s.get("enabled"))
    if "fire_pageview" in s:  out["fire_pageview"]      = bool(s.get("fire_pageview"))
    for k in ("pixel_id", "capi_token", "capi_dataset_id", "test_event_code", "custom_audience_id"):
        v = s.get(k)
        if isinstance(v, str) and v.strip():
            out[k] = v.strip()
    return out

def _meta_site_name(site):
    if not site:
        return "Site"
    return (site.get("name") or site.get("id") or "Site").strip() or "Site"

def _meta_visit_event(site):
    return f"{_meta_site_name(site)} Visit"

def _meta_signup_event(site):
    return f"{_meta_site_name(site)} NewsletterSignup"

def build_meta_pixel_snippet(resolved, site=None):
    """Returns the <script> block to inject into the <head> via header_scripts.
    Loads the Pixel base library, fires PageView (when enabled), fires a
    custom '<Site Name> Visit' event, and wires a delegated submit listener
    that hashes the email (SHA-256, client-side) and fires a custom
    '<Site Name> NewsletterSignup' event. Safe to inject even when CAPI is
    not configured (the server-side mirror is skipped in that case)."""
    if not resolved or not resolved.get("enabled"):
        return ""
    pixel_id = (resolved.get("pixel_id") or "").strip()
    if not pixel_id:
        return ""
    site_name = _meta_site_name(site)
    site_id   = (site or {}).get("id", "")
    visit_evt = _meta_visit_event(site)
    signup_evt = _meta_signup_event(site)
    fire_pv   = "true" if resolved.get("fire_pageview", True) else "false"
    mirror_capi = "true" if (resolved.get("capi_token") and resolved.get("capi_dataset_id")) else "false"
    return (
        "<!-- Meta Pixel (Kavalsia network) -->\n"
        "<script>\n"
        "(function(){\n"
        "  if (window.__KAVALSIA_META_LOADED) return; window.__KAVALSIA_META_LOADED = true;\n"
        "  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?\n"
        "  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;\n"
        "  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;\n"
        "  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,\n"
        "  document,'script','https://connect.facebook.net/en_US/fbevents.js');\n"
        f"  fbq('init', {json.dumps(pixel_id)});\n"
        f"  var FIRE_PV = {fire_pv};\n"
        f"  var SITE_ID = {json.dumps(site_id)};\n"
        f"  var SITE_NAME = {json.dumps(site_name)};\n"
        f"  var VISIT_EVT = {json.dumps(visit_evt)};\n"
        f"  var SIGNUP_EVT = {json.dumps(signup_evt)};\n"
        f"  var MIRROR_CAPI = {mirror_capi};\n"
        "  if (FIRE_PV) { try { fbq('track', 'PageView'); } catch(e) {} }\n"
        "  try {\n"
        "    fbq('trackCustom', VISIT_EVT, {\n"
        "      site_id: SITE_ID,\n"
        "      page_path: location.pathname,\n"
        "      page_title: document.title,\n"
        "      referrer: document.referrer || ''\n"
        "    });\n"
        "  } catch(e) {}\n"
        "  function sha256Hex(str) {\n"
        "    if (!window.crypto || !crypto.subtle) return Promise.resolve('');\n"
        "    var buf = new TextEncoder().encode(String(str || '').trim().toLowerCase());\n"
        "    return crypto.subtle.digest('SHA-256', buf).then(function(h){\n"
        "      return Array.prototype.map.call(new Uint8Array(h), function(b){\n"
        "        return ('00' + b.toString(16)).slice(-2);\n"
        "      }).join('');\n"
        "    });\n"
        "  }\n"
        "  function mirrorCAPI(evtName, payload) {\n"
        "    if (!MIRROR_CAPI) return;\n"
        "    try {\n"
        "      var hub = (window.KAVALSIA_HUB_URL || '').replace(/\\/$/, '');\n"
        "      if (!hub) return;\n"
        "      fetch(hub + '/api/meta-capi', {\n"
        "        method: 'POST',\n"
        "        headers: { 'Content-Type': 'application/json' },\n"
        "        body: JSON.stringify({ site_id: SITE_ID, event_name: evtName, payload: payload })\n"
        "      }).catch(function(){});\n"
        "    } catch(e) {}\n"
        "  }\n"
        "  mirrorCAPI(VISIT_EVT, { page_path: location.pathname });\n"
        "  document.addEventListener('submit', function(ev) {\n"
        "    try {\n"
        "      var f = ev.target;\n"
        "      if (!f || !f.tagName || f.tagName.toLowerCase() !== 'form') return;\n"
        "      var emailEl = f.querySelector('input[type=email], input[name*=email i]');\n"
        "      if (!emailEl || !emailEl.value) return;\n"
        "      var email = emailEl.value;\n"
        "      sha256Hex(email).then(function(h){\n"
        "        try { fbq('trackCustom', SIGNUP_EVT, { email_hashed: h }); } catch(e) {}\n"
        "        mirrorCAPI(SIGNUP_EVT, { email_hashed: h });\n"
        "      });\n"
        "    } catch(e) {}\n"
        "  }, true);\n"
        "})();\n"
        "</script>\n"
        f"<noscript><img height=\"1\" width=\"1\" style=\"display:none\" alt=\"\" "
        f"src=\"https://www.facebook.com/tr?id={pixel_id}&ev=PageView&noscript=1\"/></noscript>\n"
        "<!-- End Meta Pixel -->\n"
    )

def _meta_sha256(s):
    return hashlib.sha256(str(s or "").strip().lower().encode("utf-8")).hexdigest()

@app.route("/api/meta-test-pixel", methods=["POST"])
def meta_test_pixel():
    """Return the resolved Meta config + the generated client snippet so the
    user can preview exactly what will be injected into <head>."""
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    try:
        cfg = _meta_load_cfg()
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    site = _meta_site_for(cfg, site_id) if site_id else None
    if site_id and not site:
        return jsonify({"ok": False, "error": f"Unknown site_id '{site_id}'"}), 404
    resolved = _meta_resolve(cfg, site)
    snippet  = build_meta_pixel_snippet(resolved, site)
    return jsonify({
        "ok":        True,
        "site_id":   site_id,
        "resolved":  {
            "enabled":            resolved["enabled"],
            "pixel_id":           resolved["pixel_id"],
            "fire_pageview":      resolved["fire_pageview"],
            "has_capi_token":     bool(resolved["capi_token"]),
            "capi_dataset_id":    resolved["capi_dataset_id"],
            "test_event_code":    resolved["test_event_code"],
            "custom_audience_id": resolved["custom_audience_id"],
            "visit_event":        _meta_visit_event(site),
            "signup_event":       _meta_signup_event(site),
        },
        "snippet":     snippet,
        "snippet_len": len(snippet),
    })

@app.route("/api/meta-capi", methods=["POST"])
def meta_capi_relay():
    """Server-side mirror endpoint. The injected client script POSTs here so
    we can forward the event to Facebook Conversions API with hashed user
    data. Body: { site_id, event_name, payload }."""
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    evt     = (body.get("event_name") or "").strip()
    payload = body.get("payload") or {}
    try:
        cfg = _meta_load_cfg()
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    site = _meta_site_for(cfg, site_id)
    resolved = _meta_resolve(cfg, site)
    if not resolved["enabled"]:
        return jsonify({"ok": False, "error": "Meta integration disabled"}), 400
    if not resolved["capi_token"] or not resolved["capi_dataset_id"]:
        return jsonify({"ok": False, "error": "CAPI not configured"}), 400
    if not evt:
        evt = _meta_visit_event(site)
    user_data = {}
    email_h = (payload or {}).get("email_hashed")
    if email_h:
        user_data["em"] = [email_h]
    cli_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr or ""
    if cli_ip:
        user_data["client_ip_address"] = cli_ip
    ua = request.headers.get("User-Agent", "")
    if ua:
        user_data["client_user_agent"] = ua
    fb_event = {
        "event_name":       evt,
        "event_time":       int(time.time()),
        "action_source":    "website",
        "event_source_url": request.headers.get("Referer", ""),
        "user_data":        user_data,
        "custom_data":      {k: v for k, v in (payload or {}).items() if k != "email_hashed"},
    }
    fb_body = {"data": [fb_event]}
    if resolved["test_event_code"]:
        fb_body["test_event_code"] = resolved["test_event_code"]
    url = f"https://graph.facebook.com/v18.0/{resolved['capi_dataset_id']}/events?access_token={resolved['capi_token']}"
    try:
        r = requests.post(url, json=fb_body, timeout=8)
        return jsonify({"ok": r.status_code == 200, "status": r.status_code, "body": (r.text or "")[:400]})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Network error: {e}"}), 502

@app.route("/api/meta-test-capi", methods=["POST"])
def meta_test_capi():
    """Send a sample event to Facebook CAPI so the user can verify their
    token + dataset id + test_event_code wiring."""
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    evt     = (body.get("event_name") or "").strip()
    try:
        cfg = _meta_load_cfg()
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    site = _meta_site_for(cfg, site_id) if site_id else None
    if site_id and not site:
        return jsonify({"ok": False, "error": f"Unknown site_id '{site_id}'"}), 404
    resolved = _meta_resolve(cfg, site)
    if not resolved["capi_token"]:
        return jsonify({"ok": False, "error": "CAPI access token not configured"}), 400
    if not resolved["capi_dataset_id"]:
        return jsonify({"ok": False, "error": "CAPI dataset id (pixel id) not configured"}), 400
    if not evt:
        evt = _meta_visit_event(site)
    sample_email = "test@kavalsia.local"
    fb_event = {
        "event_name":       evt,
        "event_time":       int(time.time()),
        "action_source":    "website",
        "event_source_url": (site or {}).get("domain") and f"https://{site['domain']}/" or "https://localhost/",
        "user_data": {
            "em": [_meta_sha256(sample_email)],
            "client_user_agent": "Kavalsia-CAPI-Test/1.0",
        },
        "custom_data": {
            "source":  "kavalsia-dashboard-test",
            "site_id": site_id or "",
        },
    }
    fb_body = {"data": [fb_event]}
    if resolved["test_event_code"]:
        fb_body["test_event_code"] = resolved["test_event_code"]
    url = f"https://graph.facebook.com/v18.0/{resolved['capi_dataset_id']}/events?access_token={resolved['capi_token']}"
    try:
        r = requests.post(url, json=fb_body, timeout=10)
        return jsonify({
            "ok":      r.status_code == 200,
            "status":  r.status_code,
            "url":     f"https://graph.facebook.com/v18.0/{resolved['capi_dataset_id']}/events",
            "body":    (r.text or "")[:600],
            "event":   evt,
            "test_event_code": resolved["test_event_code"] or "",
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"Network error reaching Facebook: {e}"}), 502

@app.route("/api/meta-audience-sync", methods=["POST"])
def meta_audience_sync():
    """Push the site's newsletter list to a Meta Custom Audience. If no
    local contact list is available, returns a clear stub message instead
    of failing hard. Looks for contacts/<site_id>.json or contacts/all.json
    shaped as a list of emails or [{email: ...}] rows."""
    body    = request.get_json(force=True, silent=True) or {}
    site_id = (body.get("site_id") or "").strip()
    try:
        cfg = _meta_load_cfg()
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    site = _meta_site_for(cfg, site_id) if site_id else None
    if site_id and not site:
        return jsonify({"ok": False, "error": f"Unknown site_id '{site_id}'"}), 404
    resolved = _meta_resolve(cfg, site)
    if not resolved["capi_token"]:
        return jsonify({"ok": False, "error": "CAPI access token required for Custom Audience sync"}), 400
    audience_id = resolved["custom_audience_id"]
    if not audience_id:
        return jsonify({"ok": False, "error": "custom_audience_id not configured"}), 400

    emails = []
    sources_tried = []
    cand_paths = []
    if site_id:
        cand_paths.append(BASE_DIR / "contacts" / f"{site_id}.json")
    cand_paths.append(BASE_DIR / "contacts" / "all.json")
    for p in cand_paths:
        sources_tried.append(str(p.name))
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for row in data:
                        if isinstance(row, str):
                            emails.append(row)
                        elif isinstance(row, dict) and row.get("email"):
                            emails.append(row["email"])
                    break
            except Exception:
                pass
    if not emails:
        return jsonify({
            "ok":      False,
            "stub":    True,
            "message": ("No local contact list found. Drop a JSON file at "
                        "contacts/<site_id>.json (list of emails or "
                        "[{email: ...}] rows) and re-run."),
            "sources_tried": sources_tried,
        })

    hashed = [_meta_sha256(e) for e in emails if e]
    payload = {
        "payload": {
            "schema": ["EMAIL_SHA256"],
            "data":   [[h] for h in hashed],
        }
    }
    url = f"https://graph.facebook.com/v18.0/{audience_id}/users?access_token={resolved['capi_token']}"
    try:
        r = requests.post(url, json=payload, timeout=15)
        return jsonify({
            "ok":          r.status_code == 200,
            "status":      r.status_code,
            "synced":      len(hashed),
            "audience_id": audience_id,
            "body":        (r.text or "")[:600],
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"Network error reaching Facebook: {e}"}), 502

# ── Sponsors (config-driven backlink injector) ────────────────────────────────
DEFAULT_SPONSOR_SEED = [{
    "id": "dalmend-candles",
    "name": "Dalmend Candles",
    "enabled": True,
    "scope": "global",
    "exclude_sites": [],
    "url": "https://dalmend.com/",
    "eyebrow": "Sponsored - Dalmend Candles",
    "blurb": "Set the mood the way it deserves. Dalmend Candles are hand-poured, long-burning, with restrained scent profiles designed for high-end spaces.",
    "cta_text": "Explore the collection at dalmend.com",
    "accent": "#c9a55c",
    "fit_keywords": [
        "candle","fragrance","scent","aroma","ambient","ambiance","ambience","mood lighting",
        "interior","decor","decorating","living room","bedroom","dining","entryway","hallway",
        "design tip","luxury","high-end","high end","mansion","villa","estate","penthouse",
        "home","house","gift","gifting","present","holiday","cozy","atmosphere","relaxation",
        "self-care","spa","ritual","apartment","loft"
    ],
    "utm_campaign": "backlink",
    "utm_content": "candles",
}]


def _load_cfg_for_sponsors():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    settings = cfg.setdefault("settings", {})
    if "sponsors" not in settings or settings["sponsors"] is None:
        settings["sponsors"] = json.loads(json.dumps(DEFAULT_SPONSOR_SEED))
        _atomic_write_config(cfg)
    return cfg


def _atomic_write_config(cfg):
    tmp = CONFIG_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, CONFIG_PATH)


@app.route("/api/sponsors", methods=["GET"])
def sponsors_get():
    cfg = _load_cfg_for_sponsors()
    site_overrides = {}
    for s in cfg.get("sites", []) or []:
        if isinstance(s.get("sponsors"), list):
            site_overrides[s.get("id","")] = s["sponsors"]
    return jsonify({
        "sponsors": (cfg.get("settings", {}) or {}).get("sponsors", []) or [],
        "site_overrides": site_overrides,
    })


@app.route("/api/sponsors", methods=["POST"])
def sponsors_save():
    body = request.get_json(force=True, silent=True) or {}
    sponsors = body.get("sponsors")
    if not isinstance(sponsors, list):
        return jsonify({"error": "sponsors must be a list"}), 400
    # Light validation: each entry needs an id.
    seen = set()
    for sp in sponsors:
        if not isinstance(sp, dict) or not sp.get("id"):
            return jsonify({"error": "every sponsor needs an id"}), 400
        if sp["id"] in seen:
            return jsonify({"error": f"duplicate sponsor id: {sp['id']}"}), 400
        seen.add(sp["id"])
    cfg = _load_cfg_for_sponsors()
    cfg.setdefault("settings", {})["sponsors"] = sponsors
    _atomic_write_config(cfg)
    return jsonify({"ok": True, "count": len(sponsors)})


@app.route("/api/sponsors/site", methods=["POST"])
def sponsors_save_site():
    body = request.get_json(force=True, silent=True) or {}
    site_id  = (body.get("site_id") or "").strip()
    sponsors = body.get("sponsors")
    if not site_id:
        return jsonify({"error": "site_id required"}), 400
    if sponsors is not None and not isinstance(sponsors, list):
        return jsonify({"error": "sponsors must be a list or null"}), 400
    cfg = _load_cfg_for_sponsors()
    found = False
    for s in cfg.get("sites", []) or []:
        if s.get("id") == site_id:
            if sponsors is None or len(sponsors) == 0:
                s.pop("sponsors", None)
            else:
                s["sponsors"] = sponsors
            found = True
            break
    if not found:
        return jsonify({"error": f"site not found: {site_id}"}), 404
    _atomic_write_config(cfg)
    return jsonify({"ok": True})


@app.route("/api/sponsors/run", methods=["POST"])
def sponsors_run():
    body = request.get_json(force=True, silent=True) or {}
    token = (request.headers.get("X-GH-Token")
             or body.get("gh_token")
             or os.environ.get("GITHUB_TOKEN", "")).strip()
    if not token:
        return jsonify({"error": "GitHub token required (X-GH-Token header or gh_token body)"}), 400

    script = BASE_DIR / "inject_sponsors.py"
    if not script.exists():
        return jsonify({"error": "inject_sponsors.py not found"}), 404

    cmd = ["python3", str(script), "--gh-token", token]
    sponsor_id = (body.get("sponsor_id") or "").strip()
    site_id    = (body.get("site_id") or "").strip()
    remove     = bool(body.get("remove"))
    if site_id:
        cmd += ["--only", site_id]
    if remove and sponsor_id:
        cmd += ["--remove", sponsor_id]
    elif sponsor_id:
        cmd += ["--sponsor", sponsor_id]
    if body.get("dry_run"):
        cmd += ["--dry-run"]

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


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL POST: hand-written articles, optional schedule, optional auto-expire.
# Queue persists in manual-post-queue.json. Background thread sweeps every 60s.
# ─────────────────────────────────────────────────────────────────────────────
import base64 as _b64
import random as _mp_rand
from datetime import datetime as _dt, timezone as _tz

MP_QUEUE_PATH = BASE_DIR / "manual-post-queue.json"
_MP_LOCK      = threading.Lock()


def _mp_load_queue():
    if not MP_QUEUE_PATH.exists():
        return []
    try:
        data = json.loads(MP_QUEUE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _mp_save_queue(items):
    MP_QUEUE_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")


def _mp_token():
    """Resolve the GitHub token from secrets vault."""
    s = _load_secrets_file()
    return (s.get("ghToken") or os.environ.get("GITHUB_TOKEN", "")).strip()


def _mp_parse_dt(s):
    """Accept ISO/datetime-local. Return aware UTC datetime or None."""
    if not s:
        return None
    s = str(s).strip().replace("Z", "+00:00")
    try:
        d = _dt.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=_tz.utc)
        return d.astimezone(_tz.utc)
    except Exception:
        return None


def _mp_now():
    return _dt.now(_tz.utc)


def _mp_slugify(s):
    s = (s or "").lower().strip()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _mp_resolve_author(site, mode, pool_value, custom, rnd_seed=None):
    mode = (mode or "site_default").strip()
    if mode == "custom":
        return (custom or "").strip() or _mp_default_author(site)
    if mode == "pick":
        return (pool_value or "").strip() or _mp_default_author(site)
    if mode == "random":
        names = site.get("author_names") or []
        if names:
            r = _mp_rand.Random(rnd_seed) if rnd_seed else _mp_rand
            return r.choice(names)
        return _mp_default_author(site)
    return _mp_default_author(site)


def _mp_default_author(site):
    return (site.get("default_author") or site.get("author") or "Editorial Team").strip() or "Editorial Team"


def _mp_get_site(site_id):
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    for s in cfg.get("sites", []) or []:
        if s.get("id") == site_id:
            return s
    return None


def _mp_build_sections(payload):
    """Return list of {heading,content} sections from payload.
    Supports: explicit `sections` list, OR a `body` string with '## Heading' markers."""
    secs = payload.get("sections")
    if isinstance(secs, list) and secs:
        out = []
        for s in secs:
            h = (s.get("heading") or "").strip()
            c = (s.get("content") or "").strip()
            if h or c:
                out.append({"heading": h or "Section", "content": c if c.startswith("<") else f"<p>{c}</p>"})
        if out:
            return out
    body = (payload.get("body") or "").strip()
    if not body:
        return []
    parts, current = [], {"heading": "", "buf": []}
    for line in body.splitlines():
        if line.startswith("## "):
            if current["heading"] or current["buf"]:
                parts.append(current)
            current = {"heading": line[3:].strip(), "buf": []}
        else:
            current["buf"].append(line)
    if current["heading"] or current["buf"]:
        parts.append(current)
    out = []
    for p in parts:
        text = "\n".join(p["buf"]).strip()
        if not text and not p["heading"]:
            continue
        html = text if text.startswith("<") else "".join(
            f"<p>{para.strip()}</p>" for para in text.split("\n\n") if para.strip()
        )
        out.append({"heading": p["heading"] or "Section", "content": html or "<p></p>"})
    return out


def _mp_publish_one(entry, site_id, token):
    """Build + push a single article to one site. Returns (ok, msg)."""
    site = _mp_get_site(site_id)
    if not site:
        return False, f"site not found: {site_id}"
    try:
        import bot as _bot
    except Exception as e:
        return False, f"bot import failed: {e}"

    author = _mp_resolve_author(
        site,
        entry.get("author_mode"),
        entry.get("author_pool"),
        entry.get("custom_author"),
        rnd_seed=f"{entry.get('id','')}-{site_id}",
    )
    article = {
        "title":            entry.get("title", "").strip(),
        "slug":             entry.get("slug", "").strip(),
        "meta_description": entry.get("meta_description", "").strip(),
        "intro":            (entry.get("intro") or "").strip(),
        "intro2":           (entry.get("intro2") or "").strip(),
        "sections":         entry.get("_sections") or _mp_build_sections(entry),
        "conclusion":       (entry.get("conclusion") or "").strip(),
        "author":           author,
        "date_iso":         entry.get("date_iso") or _mp_now().strftime("%Y-%m-%d"),
        "image":            entry.get("image", "").strip(),
        "category":         (entry.get("category") or "").strip(),
    }
    try:
        themes = _bot.THEMES if hasattr(_bot, "THEMES") else {}
        html = _bot.build_article_page(
            article, site, article["image"], "Manual", themes,
            global_header_scripts="", global_footer_scripts=""
        )
    except Exception as e:
        return False, f"build failed: {e}"

    repo = site.get("repo", "")
    if not repo:
        return False, f"site {site_id} has no repo"
    slug = article["slug"]
    path = f"{slug}/index.html"
    data = html.encode("utf-8")
    remote_sha, _ = _gh_get_remote_sha(repo, path, token)
    ok, status, msg = _gh_put_file(repo, path, data, f"Manual post: {article['title']}", remote_sha, token)
    if not ok and status == 409:
        remote_sha, _ = _gh_get_remote_sha(repo, path, token)
        ok, status, msg = _gh_put_file(repo, path, data, f"Manual post: {article['title']}", remote_sha, token)
    if not ok:
        return False, f"push {status}: {msg}"

    # Update articles.json
    try:
        existing = _bot.load_article_index(repo, token) or []
    except Exception:
        existing = []
    by_slug = {a.get("slug"): a for a in existing}
    by_slug[slug] = {
        "title": article["title"], "slug": slug,
        "date":  article["date_iso"], "date_iso": article["date_iso"],
        "author": author, "category": article["category"],
        "image": article["image"], "meta_description": article["meta_description"],
        "tags": entry.get("tags") or [],
        "featured": bool(entry.get("featured")),
    }
    merged = list(by_slug.values())
    merged.sort(key=lambda x: x.get("date_iso", x.get("date", "")), reverse=True)
    try:
        _bot.github_push(repo, "articles.json", json.dumps(merged, indent=2),
                         f"Manual post index: {slug}", token)
    except Exception as e:
        return True, f"published but index update failed: {e}"

    # Optional newsletter
    if entry.get("send_newsletter"):
        try:
            s = _load_secrets_file()
            bk = (s.get("brevoKey") or "").strip()
            if bk and site.get("brevo_list_id"):
                _bot.send_newsletter(site, article, bk)
        except Exception:
            pass
    return True, "ok"


def _mp_expire_one(entry, site_id, token):
    """Delete <slug>/index.html on GitHub and remove its articles.json entry."""
    site = _mp_get_site(site_id)
    if not site:
        return False, f"site not found: {site_id}"
    repo = site.get("repo", "")
    if not repo:
        return False, "no repo"
    slug = entry.get("slug", "")
    if not slug:
        return False, "no slug"
    path = f"{slug}/index.html"
    sha, _ = _gh_get_remote_sha(repo, path, token)
    if sha:
        try:
            r = requests.delete(
                f"https://api.github.com/repos/{repo}/contents/{path}",
                headers=_gh_headers(token),
                json={"message": f"Manual post expired: {slug}", "sha": sha},
                timeout=20,
            )
            if r.status_code not in (200, 204):
                return False, f"delete {r.status_code}: {r.text[:160]}"
        except Exception as e:
            return False, f"delete error: {e}"
    # Remove from articles.json
    try:
        import bot as _bot
        existing = _bot.load_article_index(repo, token) or []
        filtered = [a for a in existing if a.get("slug") != slug]
        if len(filtered) != len(existing):
            _bot.github_push(repo, "articles.json", json.dumps(filtered, indent=2),
                             f"Manual post expired index: {slug}", token)
    except Exception:
        pass
    return True, "expired"


def _mp_validate(body):
    req = ["title", "slug", "meta_description"]
    missing = [k for k in req if not (body.get(k) or "").strip()]
    if missing:
        return f"missing required fields: {', '.join(missing)}"
    site_ids = body.get("site_ids") or []
    if not isinstance(site_ids, list) or not site_ids:
        return "site_ids must be a non-empty list"
    return None


@app.route("/api/manual-post", methods=["POST"])
def manual_post_create():
    body = request.get_json(force=True, silent=True) or {}
    err = _mp_validate(body)
    if err:
        return jsonify({"error": err}), 400
    token = _mp_token()
    if not token:
        return jsonify({"error": "GitHub token missing. Add ghToken in Settings > API Keys."}), 401

    publish_at = _mp_parse_dt(body.get("publish_at")) or _mp_now()
    expires_at = None if body.get("lifetime") else _mp_parse_dt(body.get("expires_at"))
    now        = _mp_now()
    site_ids   = body.get("site_ids") or []
    entry_id   = f"mp-{int(time.time()*1000)}-{_mp_rand.randint(100,999)}"

    # Pre-resolve sections once so the queue stores a stable copy.
    sections = _mp_build_sections(body)

    entry = {
        "id": entry_id,
        "title": body.get("title", "").strip(),
        "slug":  _mp_slugify(body.get("slug") or body.get("title")),
        "meta_description": body.get("meta_description", "").strip(),
        "intro":  (body.get("intro") or "").strip(),
        "intro2": (body.get("intro2") or "").strip(),
        "conclusion": (body.get("conclusion") or "").strip(),
        "_sections": sections,
        "body":   body.get("body") or "",
        "image":  (body.get("image") or "").strip(),
        "category": (body.get("category") or "").strip(),
        "author_mode": body.get("author_mode") or "site_default",
        "author_pool": body.get("author_pool") or "",
        "custom_author": body.get("custom_author") or "",
        "site_ids": list(site_ids),
        "publish_at": publish_at.isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "lifetime": bool(body.get("lifetime")),
        "tags": body.get("tags") or [],
        "featured": bool(body.get("featured")),
        "send_newsletter": bool(body.get("send_newsletter")),
        "date_iso": publish_at.strftime("%Y-%m-%d"),
        "created_at": now.isoformat(),
        "status": "queued",
        "site_results": {},
    }

    published, scheduled, errors = [], [], []
    if publish_at <= now:
        # Publish immediately to every site.
        for sid in site_ids:
            ok, msg = _mp_publish_one(entry, sid, token)
            entry["site_results"][sid] = {"ok": ok, "msg": msg, "at": _mp_now().isoformat()}
            (published if ok else errors).append(sid)
        entry["status"] = "published" if published else "failed"
        entry["published_at"] = _mp_now().isoformat()
    else:
        scheduled = list(site_ids)
        entry["status"] = "scheduled"

    with _MP_LOCK:
        q = _mp_load_queue()
        q.append(entry)
        _mp_save_queue(q)

    return jsonify({
        "ok": True, "id": entry_id,
        "published": published, "scheduled": scheduled, "errors": errors,
        "entry": entry,
    })


@app.route("/api/manual-post/queue", methods=["GET"])
def manual_post_queue():
    return jsonify({"items": _mp_load_queue()})


@app.route("/api/manual-post/cancel", methods=["POST"])
def manual_post_cancel():
    body = request.get_json(force=True, silent=True) or {}
    eid  = (body.get("id") or "").strip()
    if not eid:
        return jsonify({"error": "id required"}), 400
    with _MP_LOCK:
        q = _mp_load_queue()
        found = False
        for it in q:
            if it.get("id") == eid:
                it["status"] = "cancelled"
                it["cancelled_at"] = _mp_now().isoformat()
                found = True
                break
        if found:
            _mp_save_queue(q)
    return jsonify({"ok": True, "found": found})


@app.route("/api/manual-post/expire-check", methods=["POST"])
def manual_post_expire_check():
    res = _mp_sweep_once(force=True)
    return jsonify(res)


def _mp_sweep_once(force=False):
    """Sweep queue once: publish scheduled items whose time has come,
    expire published items past their expiry."""
    token = _mp_token()
    if not token:
        return {"ok": False, "error": "no GitHub token in secrets"}
    out = {"published": [], "expired": [], "errors": []}
    now = _mp_now()
    with _MP_LOCK:
        q = _mp_load_queue()
        changed = False
        for entry in q:
            status = entry.get("status")
            # Publish scheduled posts whose time has come
            if status == "scheduled":
                pub = _mp_parse_dt(entry.get("publish_at"))
                if pub and pub <= now:
                    for sid in entry.get("site_ids", []):
                        ok, msg = _mp_publish_one(entry, sid, token)
                        entry.setdefault("site_results", {})[sid] = {
                            "ok": ok, "msg": msg, "at": _mp_now().isoformat()
                        }
                        if ok:
                            out["published"].append({"id": entry["id"], "site": sid})
                        else:
                            out["errors"].append({"id": entry["id"], "site": sid, "msg": msg})
                    entry["status"] = "published"
                    entry["published_at"] = _mp_now().isoformat()
                    changed = True
            # Expire published posts whose expiry has passed
            elif status == "published" and not entry.get("lifetime"):
                exp = _mp_parse_dt(entry.get("expires_at"))
                if exp and exp <= now:
                    for sid in entry.get("site_ids", []):
                        ok, msg = _mp_expire_one(entry, sid, token)
                        entry.setdefault("expire_results", {})[sid] = {
                            "ok": ok, "msg": msg, "at": _mp_now().isoformat()
                        }
                        if ok:
                            out["expired"].append({"id": entry["id"], "site": sid})
                        else:
                            out["errors"].append({"id": entry["id"], "site": sid, "msg": msg})
                    entry["status"] = "expired"
                    entry["expired_at"] = _mp_now().isoformat()
                    changed = True
        if changed:
            _mp_save_queue(q)
    out["ok"] = True
    return out


def _mp_scheduler_loop():
    """Daemon thread: sweep every 60 seconds."""
    while True:
        try:
            _mp_sweep_once()
        except Exception as e:
            try:
                print(f"[manual-post scheduler] error: {e}")
            except Exception:
                pass
        time.sleep(60)


_MP_THREAD = threading.Thread(target=_mp_scheduler_loop, name="manual-post-scheduler", daemon=True)
_MP_THREAD.start()


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
