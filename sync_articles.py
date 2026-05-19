#!/usr/bin/env python3
"""
sync_articles.py  -  cross-site article syndication (full copy / republish).

Each destination site receives a copy of every article from its configured sources:

    SYNC_MAP[<dst stem>] = [<src stem>, ...]

For each source article missing on the destination, the script:
  1. fetches the original article HTML and articles.json entry from the source repo,
  2. extracts the article body and CSS,
  3. recolors the accent to the destination's brand color,
  4. swaps the comment block for one keyed to the destination's theme,
  5. re-wraps it in the destination's homepage shell via layout_shell,
  6. pushes the rebuilt page to the destination repo, and
  7. adds an entry to the destination's articles.json (with `syndicated_from`).

Run:  python3 sync_articles.py --gh-token TOKEN  [--only dst-stem,dst-stem2]

This is the one-time backfill. Going-forward, bot.py syndicates new articles at
publish time using the same SYNC_MAP.
"""

import os, sys, re, json, base64, time, argparse
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_shell
from bot import _seo_meta, _comments_section_js, THEMES, SITE_THEMES

BASE_DIR    = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "network-config.json"


# Destination stem -> list of source stems whose articles should appear there too.
SYNC_MAP = {
    "cryptopulse":     ["tradingtechreview"],
    "onlinebizpro":    ["cryptopulse", "tradingtechreview", "ecommerceedge", "aimarketingpro"],
    "ecommerceedge":   ["aimarketingpro"],
    "aimarketingpro":  ["ecommerceedge"],
    "fitpulsepro":     ["sportiqpro"],
    "sportiqpro":      ["fitpulsepro"],
}


# ── shared with rebuild-articles ──────────────────────────────────────────────
WRAPPERS = ("art-grid", "art-min", "mag-hero", "imm-hero", "art", "wrap", "hero", "body")


def extract_body_and_css(html):
    m = re.search(r'<style[^>]*>(.*?)</style>', html, flags=re.DOTALL | re.IGNORECASE)
    css = m.group(1).strip() if m else ""
    for sel in (r'\*', 'html', 'body', 'a', 'a:hover', 'img'):
        css = re.sub(r'(?m)^\s*' + sel + r'\s*\{[^}]*\}\s*', '', css)
    end = html.find("<footer")
    if end == -1:
        end = html.rfind("</body>")
    if end == -1:
        return None, None
    header_end = html.find("</nav>")
    start_from = header_end + 6 if 0 <= header_end < end else 0
    starts = [i for cls in WRAPPERS
              for i in [html.find(f'<div class="{cls}"', start_from)]
              if 0 <= i < end]
    if not starts:
        return None, None
    start = min(starts)
    if start >= end:
        return None, None
    return html[start:end].strip(), css


def _detect_accent(css):
    for pat in (r'\.concl[^{}]*\{[^}]*border-left:[^;]*?(#[0-9a-fA-F]{6})',
                r'\.(?:sidebar|art-side|toc-head|toc-box)[^{}]*\{[^}]*color:\s*(#[0-9a-fA-F]{6})',
                r'\.(?:sidebar|art-side)[^{}]*\{[^}]*border-top:[^;]*?(#[0-9a-fA-F]{6})'):
        m = re.search(pat, css, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def _detect_text_color(css):
    m = re.search(r'(?:^|\}|\n)\s*h1\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})', css, re.IGNORECASE)
    return m.group(1) if m else ""


def _theme_for(site):
    return dict(SITE_THEMES.get(site.get("id"),
                THEMES.get(site.get("theme", "minimal"), THEMES["minimal"])))


# ── GitHub helpers ────────────────────────────────────────────────────────────
def _headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}


def _decode(b64):
    return base64.b64decode(b64.replace("\n", "")).decode("utf-8", errors="replace")


def gh_get(repo, path, token):
    r = requests.get(f"https://api.github.com/repos/{repo}/contents/{path}",
                     headers=_headers(token), timeout=20)
    return r if r.ok else None


def gh_put(repo, path, content_str, token, sha=None, msg="syndicate article"):
    payload = {"message": msg, "content": base64.b64encode(content_str.encode("utf-8")).decode()}
    if sha:
        payload["sha"] = sha
    return requests.put(f"https://api.github.com/repos/{repo}/contents/{path}",
                        headers=_headers(token), json=payload, timeout=30)


def fetch_articles_json(repo, token):
    r = gh_get(repo, "articles.json", token)
    if not r:
        return [], None
    data = r.json()
    if data.get("content"):
        return json.loads(_decode(data["content"])), data.get("sha")
    if data.get("git_url"):
        blob = requests.get(data["git_url"], headers=_headers(token), timeout=20)
        if blob.ok:
            return json.loads(_decode(blob.json()["content"])), data.get("sha")
    return [], None


# ── re-wrap a source article into the destination's shell ─────────────────────
def rewrap_for_destination(original_html, src_meta, dst_stem, dst_site, dst_domain):
    body, css = extract_body_and_css(original_html)
    if not body:
        return None

    # Swap comment section for one keyed to the destination's theme.
    dst_t = _theme_for(dst_site)
    new_accent = layout_shell.get_shell(dst_stem).get("accent") or dst_t.get("accent", "")
    if new_accent:
        dst_t["accent"] = new_accent
        dst_t["accent2"] = new_accent
    fresh_comments = _comments_section_js(dst_t).strip()
    body = re.sub(r'<div id="comments-section".*?</script>',
                  lambda _m: fresh_comments, body, count=1, flags=re.DOTALL)

    # Recolor accent to the destination's brand color.
    if new_accent:
        olds = {_detect_accent(css).lower()}
        for oa in olds:
            if oa and oa != new_accent.lower():
                css  = re.sub(re.escape(oa), new_accent, css,  flags=re.IGNORECASE)
                body = re.sub(re.escape(oa), new_accent, body, flags=re.IGNORECASE)

    # Recolor body/h1 text to the destination's text color.
    new_text = (dst_t.get("text") or "").lower()
    old_text = (_detect_text_color(css) or "").lower()
    if new_text and old_text and old_text != new_text:
        css  = re.sub(re.escape(old_text), new_text, css,  flags=re.IGNORECASE)
        body = re.sub(re.escape(old_text), new_text, body, flags=re.IGNORECASE)

    slug      = src_meta["slug"]
    title     = src_meta.get("title", slug)
    desc      = src_meta.get("meta_description", "")
    canonical = f"https://{dst_domain}/{slug}/" if dst_domain else ""
    seo = _seo_meta(title, desc, canonical,
                    src_meta.get("image", ""),
                    src_meta.get("author", ""),
                    src_meta.get("date_iso", ""))
    return layout_shell.wrap_page(
        dst_stem, title=title, description=desc, body_html=body,
        extra_css=css, head_meta=seo, depth=1,
    )


# ── per-destination syndication run ───────────────────────────────────────────
def syndicate_into(dst_stem, dst_site, sources_sites, token, log):
    log(f"\n== {dst_stem} <- {[s['repo'].rsplit('/',1)[-1] for s in sources_sites]} ==")
    dst_repo   = dst_site.get("repo", "")
    dst_domain = dst_site.get("domain", "")
    if not dst_repo:
        log("  no dst repo, skip")
        return 0, 0

    dst_arts, dst_sha = fetch_articles_json(dst_repo, token)
    dst_slugs = {a.get("slug") for a in dst_arts}
    added = 0
    failed = 0

    for src_site in sources_sites:
        src_stem = src_site["repo"].rsplit("/", 1)[-1]
        src_arts, _ = fetch_articles_json(src_site["repo"], token)
        log(f"  source {src_stem}: {len(src_arts)} articles")

        for src_meta in src_arts:
            slug = (src_meta.get("slug") or "").strip()
            if not slug or slug in dst_slugs:
                continue

            r = gh_get(src_site["repo"], f"{slug}/index.html", token)
            if not r:
                log(f"    x {slug}: source html missing")
                failed += 1
                continue
            try:
                src_html = _decode(r.json()["content"])
            except Exception as e:
                log(f"    x {slug}: decode {e}")
                failed += 1
                continue

            rebuilt = rewrap_for_destination(src_html, src_meta, dst_stem, dst_site, dst_domain)
            if not rebuilt:
                log(f"    x {slug}: could not extract body")
                failed += 1
                continue

            # Add a tasteful "originally on <source>" line at the top of the article body
            # is left out: keep the page clean, attribution is in the articles.json marker.
            resp = gh_put(dst_repo, f"{slug}/index.html", rebuilt, token,
                          msg=f"syndicate {slug} from {src_stem}")
            if not resp.ok:
                log(f"    x {slug}: put {resp.status_code}")
                failed += 1
                continue

            entry = dict(src_meta)
            entry["syndicated_from"] = src_stem
            dst_arts.append(entry)
            dst_slugs.add(slug)
            added += 1
            log(f"    + {slug}  (from {src_stem})")
            time.sleep(0.6)

    if added:
        dst_arts.sort(key=lambda a: a.get("date_iso", ""), reverse=True)
        body = json.dumps(dst_arts, indent=2)
        resp = gh_put(dst_repo, "articles.json", body, token, sha=dst_sha,
                      msg=f"syndicate: add {added} article(s)")
        if not resp.ok:
            log(f"  ! articles.json put failed {resp.status_code}")
    log(f"  done: +{added} added, x{failed} failed")
    return added, failed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gh-token", default=os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", ""))
    p.add_argument("--only", default="", help="Comma-separated destination stems (default: all)")
    args = p.parse_args()
    if not args.gh_token:
        print("Error: --gh-token required")
        sys.exit(1)
    token = args.gh_token

    cfg   = json.loads(CONFIG_FILE.read_text())
    sites = cfg.get("sites", [])
    by_stem = {s["repo"].rsplit("/", 1)[-1]: s for s in sites if s.get("repo")}

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    total_added = total_failed = 0
    for dst_stem, src_stems in SYNC_MAP.items():
        if only and dst_stem not in only:
            continue
        dst_site = by_stem.get(dst_stem)
        if not dst_site:
            print(f"!! destination {dst_stem} not in network-config")
            continue
        src_sites = [by_stem[s] for s in src_stems if s in by_stem]
        a, f = syndicate_into(dst_stem, dst_site, src_sites, token, log=print)
        total_added += a
        total_failed += f

    print(f"\nSyndication done. +{total_added} articles, {total_failed} failed.")
    sys.exit(1 if total_failed else 0)


if __name__ == "__main__":
    main()
