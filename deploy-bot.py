#!/usr/bin/env python3
"""
deploy-bot.py  -  push the engine + templates to the bot repo (Siavashsed/kavalsia-bot)
so the daily GitHub Action runs the current code (homepage shell system, weekly
roundups) instead of the stale version.

Run:  python3 deploy-bot.py --gh-token TOKEN
"""

import os, sys, base64, time, argparse, glob
import requests
from pathlib import Path

BASE = Path(__file__).parent
REPO = "Siavashsed/kavalsia-bot"

# Engine modules + the auto-sync workflow.
FILES = [
    "bot.py", "layout_shell.py", "push-sites.py", "rebuild-articles.py", "sync.py",
    "network-config.json", "categories.json",
    "inject_sponsors.py", "inject_dalmend_backlinks.py",
    ".github/workflows/sync-sites.yml",
]
# Plus every homepage template and every about-page body fragment.
FILES += sorted(f"templates/{os.path.basename(p)}" for p in glob.glob(str(BASE / "templates" / "*-index.html")))
FILES += sorted(f"about-bodies/{os.path.basename(p)}" for p in glob.glob(str(BASE / "about-bodies" / "*.html")))
# Per-site bespoke article builders + bespoke /articles archive modules, so the
# daily cron renders the same bespoke designs (not just local runs).
FILES += sorted(f"bespoke_articles/{os.path.basename(p)}" for p in glob.glob(str(BASE / "bespoke_articles" / "*.py")))
FILES += sorted(f"archive_modules/{os.path.basename(p)}" for p in glob.glob(str(BASE / "archive_modules" / "*")))


def gh_put(token, path, content_bytes, msg):
    url  = f"https://api.github.com/repos/{REPO}/contents/{path}"
    hdrs = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=hdrs, timeout=20)
    payload = {"message": msg, "content": base64.b64encode(content_bytes).decode()}
    if r.status_code == 200:
        payload["sha"] = r.json()["sha"]
    resp = requests.put(url, headers=hdrs, json=payload, timeout=30)
    return resp.status_code in (200, 201), resp.status_code


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gh-token", default=os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", ""))
    args = p.parse_args()
    if not args.gh_token:
        print("Error: --gh-token required")
        sys.exit(1)

    ok = fail = 0
    for rel in FILES:
        local = BASE / rel
        if not local.exists():
            print(f"  skip (missing) {rel}")
            continue
        good, code = gh_put(args.gh_token, rel, local.read_bytes(), f"deploy: sync {rel}")
        print(f"  {'ok ' if good else 'FAIL '+str(code)} {rel}")
        ok += good
        fail += (not good)
        time.sleep(0.5)

    print(f"\nDeployed {ok} files, {fail} failed to {REPO}.")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
