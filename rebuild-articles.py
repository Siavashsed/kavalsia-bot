#!/usr/bin/env python3
"""
rebuild-articles.py  -  Kavalsia Network

Re-wrap every already-published article on every site so its header, footer,
fonts and colors match the current homepage (templates/<stem>-index.html).

It does NOT regenerate article text. For each article it:
  1. fetches the live <slug>/index.html,
  2. extracts the article body content and its article-layout CSS,
  3. re-wraps that content in the current homepage shell via layout_shell,
  4. pushes the result back.

Run:
    python3 rebuild-articles.py --gh-token TOKEN [--only stem,stem2]

This is the article half of sync.py. Run it whenever a homepage changes.
"""

import os, sys, json, base64, re, time, argparse
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_shell
from bot import _seo_meta, _comments_section_js, THEMES, SITE_THEMES


def _theme_for(site):
    """Resolve the theme dict for a site the same way bot.py does."""
    return dict(SITE_THEMES.get(site.get("id"),
                THEMES.get(site.get("theme", "minimal"), THEMES["minimal"])))


def _detect_accent(css):
    """Find the accent color an already-published article actually uses, so it can be
    recolored even if the site theme has since drifted from what the article was built with."""
    for pat in (r'\.concl[^{}]*\{[^}]*border-left:[^;]*?(#[0-9a-fA-F]{6})',
                r'\.(?:sidebar|art-side|toc-head|toc-box)[^{}]*\{[^}]*color:\s*(#[0-9a-fA-F]{6})',
                r'\.(?:sidebar|art-side)[^{}]*\{[^}]*border-top:[^;]*?(#[0-9a-fA-F]{6})'):
        m = re.search(pat, css, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def _detect_text_color(css):
    """Find the article's h1 text color - the site's old theme text. We replace it
    with the current theme text so headlines stay visible after a theme switch."""
    m = re.search(r'(?:^|\}|\n)\s*h1\s*\{[^}]*color:\s*(#[0-9a-fA-F]{6})', css, re.IGNORECASE)
    return m.group(1) if m else ""

BASE_DIR    = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "network-config.json"

# Known top-level wrapper classes emitted by the article builders (old and new).
WRAPPERS = ("art-grid", "art-min", "mag-hero", "imm-hero", "art", "wrap", "hero", "body")


def _headers(token):
    return {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}


def _get(url, token):
    r = requests.get(url, headers=_headers(token), timeout=20)
    return r if r.ok else None


def _decode(b64):
    return base64.b64decode(b64.replace("\n", "")).decode("utf-8", errors="replace")


def _put_file(repo, path, content_str, token, sha=None, msg="rebuild: re-wrap article in homepage shell"):
    payload = {"message": msg, "content": base64.b64encode(content_str.encode("utf-8")).decode()}
    if sha:
        payload["sha"] = sha
    return requests.put(
        f"https://api.github.com/repos/{repo}/contents/{path}",
        headers={**_headers(token), "Content-Type": "application/json"},
        json=payload, timeout=30,
    )


def extract_body_and_css(html):
    """Pull the article body content and the article-layout CSS out of a published
    article page. Returns (body_html, css) or (None, None) if it can't be parsed."""
    # Article CSS = inner text of the first <style> block.
    m = re.search(r'<style[^>]*>(.*?)</style>', html, flags=re.DOTALL | re.IGNORECASE)
    css = m.group(1).strip() if m else ""
    # Drop global/element base rules from the old <head> CSS - the homepage shell
    # already provides them, and keeping them here would restyle the shell chrome.
    for sel in (r'\*', 'html', 'body', 'a', 'a:hover', 'img'):
        css = re.sub(r'(?m)^\s*' + sel + r'\s*\{[^}]*\}\s*', '', css)

    # Body ends where the footer begins.
    end = html.find("<footer")
    if end == -1:
        end = html.rfind("</body>")
    if end == -1:
        return None, None

    # Body starts at the first known wrapper div after the header nav (the first
    # </nav>), but before the footer. The footer itself may contain its own <nav>,
    # so anchoring on the first </nav> - not the last - is what keeps this correct.
    header_end = html.find("</nav>")
    search_from = header_end + 6 if 0 <= header_end < end else 0
    starts = [i for cls in WRAPPERS
              for i in [html.find(f'<div class="{cls}"', search_from)]
              if 0 <= i < end]
    if not starts:
        return None, None
    start = min(starts)
    if start >= end:
        return None, None

    return html[start:end].strip(), css


def patch_site(stem, site, token, log):
    repo = site.get("repo", "")
    if not repo or "YOUR_" in repo:
        log(f"  skip {stem}  -  no repo")
        return 0, 0

    log(f"\n-- {stem} ({repo}) --")
    api = f"https://api.github.com/repos/{repo}/contents"

    r = _get(f"{api}/articles.json", token)
    if not r:
        log("  no articles.json  -  skipping")
        return 0, 0
    try:
        data = r.json()
        if data.get("content"):
            raw = _decode(data["content"])
        elif data.get("git_url"):
            blob = requests.get(data["git_url"], headers=_headers(token), timeout=20)
            raw = _decode(blob.json()["content"]) if blob.ok else None
        else:
            raw = None
        articles = json.loads(raw) if raw else []
    except Exception as e:
        log(f"  failed to parse articles.json: {e}")
        return 0, 0

    if not articles:
        log("  0 articles")
        return 0, 0

    log(f"  {len(articles)} articles")
    ok = fail = 0
    domain = site.get("domain", "")

    # Brand accent + fresh comment section for this site.
    t = _theme_for(site)
    old_accent  = (t.get("accent") or "").lower()
    old_accent2 = (t.get("accent2") or "").lower()
    new_accent  = layout_shell.get_shell(stem).get("accent") or t.get("accent", "")
    if new_accent:
        t["accent"] = new_accent
        t["accent2"] = new_accent
    fresh_comments = _comments_section_js(t).strip()

    for i, article in enumerate(articles):
        slug = (article.get("slug") or "").strip()
        if not slug:
            continue
        path = f"{slug}/index.html"

        r = _get(f"{api}/{path}", token)
        if not r:
            log(f"  [{i+1}] x {slug}  -  not found")
            fail += 1
            continue
        fd  = r.json()
        sha = fd.get("sha")
        try:
            original = _decode(fd["content"])
        except Exception as e:
            log(f"  [{i+1}] x {slug}  -  decode error: {e}")
            fail += 1
            continue

        body, css = extract_body_and_css(original)
        if not body:
            log(f"  [{i+1}] x {slug}  -  could not locate article body")
            fail += 1
            continue

        # Swap the comment section for the redesigned one.
        body = re.sub(r'<div id="comments-section".*?</script>',
                      lambda _m: fresh_comments, body, count=1, flags=re.DOTALL)
        # Recolor the article accent to the site's brand accent. Replace both the
        # theme accents and the accent actually detected in this article's CSS.
        if new_accent:
            olds = {old_accent, old_accent2, (_detect_accent(css) or "").lower()}
            for oa in olds:
                if oa and oa != new_accent.lower():
                    css  = re.sub(re.escape(oa), new_accent, css,  flags=re.IGNORECASE)
                    body = re.sub(re.escape(oa), new_accent, body, flags=re.IGNORECASE)

        # Recolor the article's body/h1 text from the old theme's text color to the
        # current one so headlines stay visible if the theme switched dark <-> light.
        new_text = (t.get("text") or "").lower()
        old_text = (_detect_text_color(css) or "").lower()
        if new_text and old_text and old_text != new_text:
            css  = re.sub(re.escape(old_text), new_text, css,  flags=re.IGNORECASE)
            body = re.sub(re.escape(old_text), new_text, body, flags=re.IGNORECASE)

        title = article.get("title", slug)
        desc  = article.get("meta_description", "")
        canonical = f"https://{domain}/{slug}/" if domain else ""
        seo = _seo_meta(f"{title}", desc, canonical,
                        article.get("image", ""), article.get("author", ""),
                        article.get("date_iso", ""))
        try:
            rebuilt = layout_shell.wrap_page(
                stem, title=title, description=desc, body_html=body,
                extra_css=css, head_meta=seo, depth=1,
            )
        except Exception as e:
            log(f"  [{i+1}] x {slug}  -  wrap error: {e}")
            fail += 1
            continue

        if rebuilt == original:
            log(f"  [{i+1}] = {slug} (no change)")
            ok += 1
            continue

        resp = _put_file(repo, path, rebuilt, token, sha=sha)
        if resp.ok:
            log(f"  [{i+1}] ok {slug}")
            ok += 1
        else:
            log(f"  [{i+1}] x {slug}  -  {resp.status_code} {resp.text[:100]}")
            fail += 1
        time.sleep(0.8)

    return ok, fail


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gh-token", default=os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", ""))
    p.add_argument("--only", default="", help="Comma-separated template stems (default: all)")
    args = p.parse_args()

    if not args.gh_token:
        print("Error: --gh-token is required")
        sys.exit(1)

    cfg   = json.loads(CONFIG_FILE.read_text())
    sites = cfg.get("sites", [])
    only  = {x.strip() for x in args.only.split(",") if x.strip()}

    total_ok = total_fail = 0
    for site in sites:
        stem = site.get("repo", "").rsplit("/", 1)[-1] or site.get("id", "")
        if only and stem not in only and site.get("id") not in only:
            continue
        if not layout_shell.template_path(stem).exists():
            continue
        ok, fail = patch_site(stem, site, args.gh_token, log=print)
        total_ok += ok
        total_fail += fail

    print(f"\n{'-'*50}")
    print(f"Done. {total_ok} re-wrapped, {total_fail} failed.")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
