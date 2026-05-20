#!/usr/bin/env python3
"""
inject_sponsors.py

Config-driven sponsor backlink injector. Reads settings.sponsors (with optional
per-site overrides at sites[i].sponsors) from network-config.json and, for each
active sponsor, walks every targeted site's articles and injects a tasteful
inline callout right before </article>.

- Each sponsor has its own marker comment (<!-- sponsor:<id> -->) so re-runs
  are idempotent on a per-sponsor basis.
- Multiple sponsors can coexist on the same article.
- Disable a sponsor + run --remove <id> to strip its callout from every
  article it had been injected into.

CLI:
  python3 inject_sponsors.py --gh-token TOKEN
                             [--only stem,stem2]
                             [--sponsor sponsor_id]
                             [--remove sponsor_id]
                             [--dry-run]
"""

import os, sys, re, json, base64, time, argparse
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

BASE_DIR    = Path(__file__).parent.resolve()
CONFIG_PATH = BASE_DIR / "network-config.json"

# Default sponsor seeded on first run.
DEFAULT_SPONSORS = [
    {
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
            "self-care","spa","ritual","apartment","loft",
        ],
        "utm_campaign": "backlink",
        "utm_content": "candles",
    }
]


# ── Config helpers ────────────────────────────────────────────────────────────
def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg):
    CONFIG_PATH.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def ensure_sponsors_seeded(cfg):
    """Insert DEFAULT_SPONSORS into settings.sponsors if missing. Returns True
    if the config was mutated."""
    settings = cfg.setdefault("settings", {})
    if "sponsors" not in settings or settings["sponsors"] is None:
        settings["sponsors"] = json.loads(json.dumps(DEFAULT_SPONSORS))
        return True
    return False


def resolve_sponsors_for_site(cfg, site):
    """Returns the effective sponsor list that should run for the given site.
    Site override (sites[i].sponsors) replaces the global list entirely if
    present and non-empty; otherwise the global list applies with scope and
    exclude rules respected."""
    site_stem = (site.get("repo","").rsplit("/",1)[-1] or site.get("id",""))
    site_id   = site.get("id","")
    overrides = site.get("sponsors")
    if isinstance(overrides, list) and len(overrides) > 0:
        return [s for s in overrides if s.get("enabled", True)]

    out = []
    for sp in (cfg.get("settings", {}) or {}).get("sponsors", []) or []:
        if not sp.get("enabled", True):
            continue
        scope = sp.get("scope", "global")
        if isinstance(scope, list):
            if site_stem not in scope and site_id not in scope:
                continue
        else:
            ex = sp.get("exclude_sites", []) or []
            if site_stem in ex or site_id in ex:
                continue
        out.append(sp)
    return out


# ── HTML ──────────────────────────────────────────────────────────────────────
def marker(sp_id):
    return f"<!-- sponsor:{sp_id} -->"


def article_fits(text, keywords):
    if not keywords:
        return True
    low = text.lower()
    return any(k.lower() in low for k in keywords)


def callout_html(sp, site_stem, slug):
    accent  = sp.get("accent", "#c9a55c")
    eyebrow = sp.get("eyebrow", f"Sponsored - {sp.get('name','')}")
    blurb   = sp.get("blurb", "")
    cta     = sp.get("cta_text", "Visit sponsor")
    base    = sp.get("url", "#").rstrip()
    utm = (
        f"utm_source={site_stem}&utm_medium=article"
        f"&utm_campaign={sp.get('utm_campaign','backlink')}"
        f"&utm_content={sp.get('utm_content', sp.get('id','sponsor'))}"
        f"&utm_term={slug}"
    )
    sep  = "&" if "?" in base else "?"
    href = f"{base}{sep}{utm}"
    sp_id = sp.get("id","sponsor")
    return (
        f'\n{marker(sp_id)}\n'
        f'<aside style="margin:40px 0 0;padding:22px 24px;border:1px solid '
        f'{accent}59;border-radius:12px;background:linear-gradient(135deg,{accent}14,transparent);'
        f'font-size:14px;line-height:1.7;color:inherit">'
        f'<div style="font-family:Georgia,serif;font-style:italic;font-size:11px;'
        f'letter-spacing:2px;text-transform:uppercase;color:{accent};margin-bottom:6px">'
        f'{_html_escape(eyebrow)}</div>'
        f'<div>{_html_escape(blurb)} '
        f'<a href="{href}" target="_blank" rel="noopener sponsored" style="color:{accent};'
        f'font-weight:600;text-decoration:underline">{_html_escape(cta)}</a>.</div>'
        f'</aside>\n'
    )


def _html_escape(s):
    return (str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                  .replace('"',"&quot;"))


def inject(html, sp, site_stem, slug):
    mk = marker(sp.get("id",""))
    if mk in html:
        return html, False
    block = callout_html(sp, site_stem, slug)
    if "</article>" in html:
        return html.replace("</article>", block + "\n</article>", 1), True
    m = re.search(r'<div id="comments-section"', html)
    if m:
        return html[:m.start()] + block + html[m.start():], True
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1), True
    return html, False


def remove_sponsor(html, sp_id):
    """Remove the entire <!-- sponsor:id --> ... </aside> block from html."""
    mk = marker(sp_id)
    if mk not in html:
        return html, False
    # Pattern: the marker line plus the aside it introduces, ending with </aside>
    pat = re.compile(
        r'\n?' + re.escape(mk) + r'\s*\n?<aside\b[^>]*>.*?</aside>\s*\n?',
        re.DOTALL,
    )
    new_html, n = pat.subn("", html)
    return new_html, (n > 0)


# ── GitHub I/O ────────────────────────────────────────────────────────────────
def _headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}


def _decode(b64):
    return base64.b64decode(b64.replace("\n","")).decode("utf-8", errors="replace")


def _put(repo, path, content, token, sha, msg):
    payload = {"message": msg, "sha": sha,
               "content": base64.b64encode(content.encode("utf-8")).decode()}
    return requests.put(f"https://api.github.com/repos/{repo}/contents/{path}",
                        headers=_headers(token), json=payload, timeout=30)


def process_site(cfg, site, token, log, only_sponsor=None,
                 remove_sponsor_id=None, dry_run=False):
    repo = site.get("repo","")
    stem = repo.rsplit("/",1)[-1] if repo else site.get("id","")
    if not repo:
        return 0, 0

    sponsors = resolve_sponsors_for_site(cfg, site)
    if only_sponsor:
        sponsors = [s for s in sponsors if s.get("id") == only_sponsor]
    if remove_sponsor_id:
        # For remove, we don't need the sponsor to currently be enabled - run on
        # every article and strip the marker if present.
        sponsors = [{"id": remove_sponsor_id, "name": remove_sponsor_id,
                     "_remove": True, "fit_keywords": []}]
    if not sponsors:
        log(f"-- {stem}: no applicable sponsors")
        return 0, 0

    log(f"\n-- {stem} ({repo}) - {len(sponsors)} sponsor(s) --")

    api = f"https://api.github.com/repos/{repo}/contents"
    r = requests.get(f"{api}/articles.json", headers=_headers(token), timeout=15)
    if not r.ok:
        log("  no articles.json")
        return 0, 0
    try:
        arts = json.loads(_decode(r.json()["content"]))
    except Exception as e:
        log(f"  parse error: {e}")
        return 0, 0

    ok = fail = 0
    for i, a in enumerate(arts):
        slug = (a.get("slug") or "").strip()
        if not slug:
            continue
        fr = requests.get(f"{api}/{slug}/index.html", headers=_headers(token), timeout=15)
        if not fr.ok:
            log(f"  [{i+1}] x {slug} not found")
            continue
        fd = fr.json()
        html = _decode(fd["content"])
        haystack = " ".join([str(a.get("title","")),
                             str(a.get("meta_description","")),
                             html[:6000]])
        new_html = html
        applied = []
        for sp in sponsors:
            if sp.get("_remove"):
                new_html, changed = remove_sponsor(new_html, sp["id"])
                if changed:
                    applied.append(f"-{sp['id']}")
            else:
                if not article_fits(haystack, sp.get("fit_keywords") or []):
                    continue
                new_html, changed = inject(new_html, sp, stem, slug)
                if changed:
                    applied.append(f"+{sp['id']}")
        if not applied:
            log(f"  [{i+1}] - {slug} (no change)")
            continue
        if dry_run:
            log(f"  [{i+1}] DRY {slug} {' '.join(applied)}")
            ok += 1
            continue
        msg = f"sponsor: {' '.join(applied)} ({slug})"
        resp = _put(repo, f"{slug}/index.html", new_html, token, fd["sha"], msg)
        if resp.ok:
            log(f"  [{i+1}] {' '.join(applied)} {slug}")
            ok += 1
        else:
            log(f"  [{i+1}] x {slug} {resp.status_code}")
            fail += 1
        time.sleep(0.5)
    return ok, fail


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gh-token", default=os.environ.get("GH_TOKEN","")
                                 or os.environ.get("GITHUB_TOKEN",""))
    p.add_argument("--only", default="",
                   help="Comma-separated list of site stems/ids to limit to.")
    p.add_argument("--sponsor", default="",
                   help="Limit run to a single sponsor id.")
    p.add_argument("--remove", default="",
                   help="Remove the named sponsor's callout from all articles.")
    p.add_argument("--dry-run", action="store_true",
                   help="Compute and log changes without writing to GitHub.")
    args = p.parse_args()

    cfg = load_config()
    if ensure_sponsors_seeded(cfg):
        save_config(cfg)
        print("Seeded settings.sponsors with default Dalmend Candles entry.")

    if not args.gh_token and not args.dry_run:
        # Dry parsing test path:
        print("No GitHub token supplied. Re-run with --gh-token or --dry-run.")
        sponsors = (cfg.get("settings", {}) or {}).get("sponsors", []) or []
        print(f"Loaded {len(sponsors)} sponsor(s) from config:")
        for sp in sponsors:
            print(f"  - {sp.get('id')} enabled={sp.get('enabled')} "
                  f"scope={sp.get('scope')}")
        sys.exit(0)

    if requests is None:
        print("Error: 'requests' library not installed.")
        sys.exit(1)

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    only_sp   = args.sponsor.strip() or None
    remove_sp = args.remove.strip() or None

    total_ok = total_fail = 0
    for s in cfg.get("sites", []):
        repo = s.get("repo","")
        if not repo:
            continue
        stem = repo.rsplit("/",1)[-1]
        if only and stem not in only and s.get("id") not in only:
            continue
        a, f = process_site(cfg, s, args.gh_token, log=print,
                            only_sponsor=only_sp,
                            remove_sponsor_id=remove_sp,
                            dry_run=args.dry_run)
        total_ok += a
        total_fail += f
    verb = "removed" if remove_sp else "injected"
    print(f"\nDone. {total_ok} callouts {verb}, {total_fail} failed.")


if __name__ == "__main__":
    main()
