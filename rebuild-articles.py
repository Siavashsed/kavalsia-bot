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
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_shell
from bot import (_seo_meta, _seo_title_tag, _comments_section_js,
                 _comments_section_inline, THEMES, SITE_THEMES,
                 assign_category, _count_words, _site_name, _resolve_author,
                 _article_section_css, article_press, ARTICLE_BUILDERS,
                 normalize_theme)

# Distinct-design rollout is now DATA-DRIVEN (2026-06-01): a site keeps its
# bespoke per-layout article design through a rebuild whenever its configured
# article_layout resolves to a non-press builder in ARTICLE_BUILDERS. No manual
# allowlist to keep in sync with network-config. Press-aliased layouts
# (standard/sidebar/magazine/minimal/...) still map to article_press and get
# the homogenized press rewrap. The bespoke namespaces below are the bare
# wrapper classes each distinct builder emits; the rebuild loop uses them to
# detect a page that is ALREADY in its bespoke design (so it is preserved, not
# re-extracted and gutted).
_BESPOKE_CLASSES = ("ob", "kn", "sw", "bs", "tb", "lf")


def _theme_for(site):
    """Resolve the theme dict for a site the same way bot.py does, including the
    body_font backfill the distinct builders need (else broadsheet/tabloid/
    lifestyle KeyError and the rewrap silently falls back to the old body)."""
    return normalize_theme(SITE_THEMES.get(site.get("id"),
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
# "ap" is the press-layout wrapper produced by article_press() and is the
# canonical wrapper going forward; the others stay so rebuild can still parse
# pages last rendered by a legacy builder.
WRAPPERS = ("ap", "art-grid", "art-min", "mag-hero", "imm-hero", "art", "wrap", "hero", "body")


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


def _extract_article_structure(body_html, article):
    """Parse an already-rendered article body into a structured dict that
    article_press() can re-render. Works across the legacy layouts (.art,
    .art-grid, .mag-hero, .imm-hero, .art-min, etc.) by anchoring on the
    semantic content - h1, first image, first paragraphs, h2 + content
    pairs, conclusion - rather than wrapper-specific class names."""
    import re as _re

    # Scrub artifacts that earlier rebuilds left in the body. Multiple prior
    # passes accumulate <article> open/close pairs, author-card sections, and
    # comment placeholders inside the captured body - if we don't strip them
    # before section parsing, they leak into the LAST section's content and
    # break the .ap-body wrapper on the next render.
    body_html = _re.sub(r'</?article\b[^>]*>', '', body_html, flags=_re.IGNORECASE)
    body_html = _re.sub(r'<section[^>]*class="[^"]*\bauthor-card\b[^"]*"[^>]*>.*?</section>',
                        '', body_html, flags=_re.DOTALL|_re.IGNORECASE)
    # bot.py's _author_card() emits the bio as a styled <div>, not a <section
    # class="author-card">, so the regex above misses it. Each rebuild then
    # leaves the OLD card baked into the captured body and the renderer appends
    # a fresh one - producing the duplicate seen in production. Strip both the
    # legacy inline form and any older variants by balance-counting <div> nesting
    # starting from the outer wrapper signature.
    def _strip_inline_author_cards(html):
        marker_re = _re.compile(
            r'<div\s+style="max-width:760px;margin:24px auto 60px;padding:0 24px 8px"\s*>',
            _re.IGNORECASE,
        )
        while True:
            m = marker_re.search(html)
            if not m:
                return html
            i = m.end()
            depth = 1
            tag_re = _re.compile(r'</?div\b[^>]*>', _re.IGNORECASE)
            while depth > 0 and i < len(html):
                tm = tag_re.search(html, i)
                if not tm:
                    return html  # unbalanced; bail without modifying
                depth += -1 if tm.group(0).lower().startswith('</') else 1
                i = tm.end()
            html = html[:m.start()] + html[i:]
    body_html = _strip_inline_author_cards(body_html)
    # article_press inserts a single <blockquote class="ap-pull"> at midpoint
    # using meta_description. Without stripping it before re-rendering, every
    # rebuild leaves the prior pull-quote in the captured body and the renderer
    # adds a fresh one - producing the 3-5 stacked identical pull-quotes seen
    # on modeformstudio + kanona articles. Strip all such blockquotes so the
    # next render emits exactly one.
    body_html = _re.sub(r'<blockquote[^>]*class="[^"]*\bap-pull\b[^"]*"[^>]*>.*?</blockquote>',
                        '', body_html, flags=_re.DOTALL|_re.IGNORECASE)
    # Collapse deeply-nested empty <div><div><div>...<p> chains that pile up
    # across rebuilds when each pass re-wraps the same paragraphs. Cap at 1
    # wrapper - strip any wrapping div that has no class and no style and only
    # contains another div.
    for _ in range(8):
        new = _re.sub(r'<div>\s*(<div\b)', r'\1', body_html)
        if new == body_html:
            break
        body_html = new
    body_html = _re.sub(r'<div[^>]*id="comments-section"[^>]*>.*?</script>',
                        '', body_html, flags=_re.DOTALL|_re.IGNORECASE)
    body_html = _re.sub(r'<div[^>]*class="giscus"[^>]*>.*?</script>',
                        '', body_html, flags=_re.DOTALL|_re.IGNORECASE)
    # Strip the SERVER-RENDERED inline comments section + its trailing
    # <script>. Without this, every rebuild stacks the previous comments
    # block into the captured body and the next render adds another, which
    # is how datingedge articles ended up with 3-4 "Discussion · N"
    # headers + 4 "All articles" CTAs.
    body_html = _re.sub(r'<section[^>]*id="comments"[^>]*>.*?</section>\s*(?:<script\b[^>]*>.*?</script>)?',
                        '', body_html, flags=_re.DOTALL|_re.IGNORECASE)
    # Orphan "Discussion · N" headers (left behind when an old comments
    # section was partially stripped on a previous pass).
    body_html = _re.sub(r'<h2[^>]*class="[^"]*\bart-h2\b[^"]*"[^>]*>\s*Discussion\s*(?:&middot;|·)?\s*\d*\s*</h2>',
                        '', body_html, flags=_re.IGNORECASE)
    # Orphan "All articles" CTAs - the centered pill links to ../articles
    # that the rebuild keeps stacking. Future templates add a single CTA
    # in the section footer; body never carries it.
    body_html = _re.sub(r'<div[^>]*style="[^"]*text-align:\s*center[^"]*"[^>]*>\s*<a[^>]+href="[^"]*articles[^"]*"[^>]*>\s*All\s+articles\s*</a>\s*</div>',
                        '', body_html, flags=_re.IGNORECASE)

    # Hero image: first <img> outside obvious nav/logo, with its src and alt.
    img_url = ""; img_alt = ""; photographer = "Staff"
    for m in _re.finditer(r'<img\b[^>]*>', body_html, _re.IGNORECASE):
        tag = m.group(0)
        src = (_re.search(r'\bsrc=["\']([^"\']+)["\']', tag) or [None, ""])[1]
        if not src or "logo" in src.lower() or "avatar" in src.lower():
            continue
        # Skip anything inside the schema author block.
        before = body_html[:m.start()][-200:].lower()
        if "itemprop=\"author\"" in before or "author-card" in before:
            continue
        img_url = src
        img_alt = (_re.search(r'\balt=["\']([^"\']*)["\']', tag) or [None, ""])[1]
        # Photographer is the next "Photo[graph] by/: <name>" string after the img.
        rest = body_html[m.end(): m.end()+400]
        pm = _re.search(r'(?:Photo(?:graph)?\s*(?:by|:)\s*)([^<\n/]+?)(?:\s*/\s*Pexels)?[<\n]', rest, _re.IGNORECASE)
        if pm:
            photographer = pm.group(1).strip().rstrip(",").strip() or "Staff"
        break

    # Title comes from the article metadata; the in-body h1 is dropped from
    # the parsed sections so it isn't double-rendered by article_press().
    title = article.get("title") or ""

    # Strip the hero image block + h1 + byline scaffolding so the remaining
    # HTML is the prose body we can scan for sections.
    work = body_html
    work = _re.sub(r'<h1\b[^>]*>.*?</h1>', '', work, count=1, flags=_re.DOTALL|_re.IGNORECASE)
    work = _re.sub(r'<img\b[^>]*>\s*(?:<p[^>]*>\s*Photo[^<]*</p>)?', '', work, count=1, flags=_re.IGNORECASE)
    work = _re.sub(r'<figure\b[^>]*>.*?</figure>', '', work, count=1, flags=_re.DOTALL|_re.IGNORECASE)
    # Drop header/sidebar/TOC blocks present in some legacy layouts.
    for sel in (r'<aside\b[^>]*>.*?</aside>',
                r'<div class="art-side"[^>]*>.*?</div>\s*(?=</section>|</div>|$)'):
        work = _re.sub(sel, '', work, flags=_re.DOTALL|_re.IGNORECASE)

    # Pull out everything before the first h2 as the "intro lede". If the first
    # paragraph has class="intro" or class="lead", that wins; otherwise take the
    # first two <p>s.
    intro = ""; intro2 = ""
    pre_h2_match = _re.search(r'(?is)(.*?)(<h2\b|$)', work)
    pre_h2 = pre_h2_match.group(1) if pre_h2_match else work
    # Author byline lines look like "<div ...>By <strong>...</strong></div>" or
    # plain "By <strong>...</strong>" - strip them so they don't leak into intro.
    pre_h2 = _re.sub(r'<(?:div|p|span|section|header)[^>]*>\s*(?:&nbsp;)?\s*[Bb]y\s*<strong[^>]*>[^<]+</strong>.*?</(?:div|p|span|section|header)>',
                     '', pre_h2, flags=_re.DOTALL)
    pre_h2 = _re.sub(r'(?:&nbsp;)?\s*[Bb]y\s*<strong[^>]*>[^<]+</strong>', '', pre_h2)
    # Date / category meta strip ("date · category").
    pre_h2 = _re.sub(r'<div[^>]*class="[^"]*(?:meta|kicker)[^"]*"[^>]*>.*?</div>',
                     '', pre_h2, flags=_re.DOTALL|_re.IGNORECASE)
    # Prefer the layout-specific lede containers (.lead / .intro / .lede) and
    # fall back to the first plain <p>. Whatever wins becomes the intro; the
    # next non-empty <p> becomes the intro2 secondary lede.
    pre_h2_clean = _re.sub(r'<img\b[^>]*>', '', pre_h2)
    pre_h2_clean = _re.sub(r'<p[^>]*>\s*Photo[^<]*</p>', '', pre_h2_clean, flags=_re.IGNORECASE)
    lead_classes = ("lead", "intro", "lede", "deck")
    for cls in lead_classes:
        lm = _re.search(rf'<(?:div|p)[^>]*class="[^"]*\b{cls}\b[^"]*"[^>]*>(.*?)</(?:div|p)>',
                        pre_h2_clean, _re.DOTALL|_re.IGNORECASE)
        if lm and lm.group(1).strip():
            intro = lm.group(1).strip()
            pre_h2_clean = pre_h2_clean.replace(lm.group(0), "", 1)
            break
    paras = _re.findall(r'<p\b[^>]*>(.*?)</p>', pre_h2_clean, flags=_re.DOTALL|_re.IGNORECASE)
    paras = [p.strip() for p in paras if p.strip()]
    if not intro and paras:
        intro = paras.pop(0)
    if paras:
        intro2 = paras[0]

    # Sections: every h2 followed by content up to the next h2 or .concl/end.
    sections = []
    # Normalize art-h2 / art-h3 class wrappers - article_press regenerates them.
    section_iter = _re.finditer(
        r'<h2\b[^>]*>(?P<head>.*?)</h2>(?P<body>.*?)(?=<h2\b|<div[^>]+class="[^"]*\bconcl\b[^"]*"|<section[^>]+class="[^"]*\bauthor\b[^"]*"|<div[^>]+id="comments-section|<aside\b|$)',
        work, flags=_re.DOTALL|_re.IGNORECASE)
    for m in section_iter:
        head = _re.sub(r'<[^>]+>', '', m.group('head')).strip()
        if not head:
            continue
        sec_body = m.group('body').strip()
        # Drop a leading inner-wrapping <div> so the section content reads cleanly.
        sec_body = _re.sub(r'^\s*<div[^>]*>(.*)</div>\s*$', r'\1', sec_body, flags=_re.DOTALL)
        sections.append({"heading": head, "content": sec_body.strip()})

    # Conclusion: prefer .concl block; otherwise tail paragraph after last h2.
    conclusion = ""
    cm = _re.search(r'<div[^>]*class="[^"]*\bconcl\b[^"]*"[^>]*>(.*?)</div>', work, _re.DOTALL|_re.IGNORECASE)
    if cm:
        conclusion = cm.group(1).strip()

    return {
        "title":            title,
        "intro":            intro,
        "intro2":           intro2,
        "sections":         sections,
        "conclusion":       conclusion,
        "image":            img_url,
        "image_url":        img_url,
        "image_alt":        img_alt or title,
        "photographer":     photographer,
        "date":             article.get("date", ""),
        "date_iso":         article.get("date_iso", ""),
        "meta_description": article.get("meta_description", ""),
        "category":         article.get("category", ""),
        "author":           article.get("author", ""),
        "slug":             article.get("slug", ""),
    }


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
    # JS fallback only used when comments.json is missing AND we can't even
    # render a placeholder (we should always be able to render a placeholder).
    fresh_comments_js = _comments_section_js(t).strip()

    # Per-site counters threaded back to caller for the summary line.
    site_inlined = 0
    site_placeholder = 0
    site_js_fallback = 0

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
        # Per-site builder dispatch. Kanona / OnlineBiz keep their own builder
        # (kn- / ob- designs); all other sites use the press rewrap as before.
        _builder = ARTICLE_BUILDERS.get(site.get("article_layout") or "press", article_press)
        _is_press = _builder is article_press
        _use_distinct = not _is_press
        if not body:
            # Source HTML on GitHub is corrupted or truncated (e.g. partial file
            # left by a failed earlier push that wrote only the <head>/CSS).
            # We can't extract real content, but we have the article metadata in
            # articles.json - synthesize a minimal article shell via article_press
            # so the slug isn't lost. A future content rebuild can replace this
            # with full AI-generated text.
            try:
                synth_article = {
                    "title":            article.get("title", slug),
                    "intro":            article.get("meta_description", "") or "",
                    "intro2":           "",
                    "sections":         [],
                    "conclusion":       "",
                    "image":            article.get("image", ""),
                    "image_url":        article.get("image", ""),
                    "image_alt":        article.get("title", slug),
                    "photographer":     "Staff",
                    "date":             article.get("date", ""),
                    "date_iso":         article.get("date_iso", ""),
                    "meta_description": article.get("meta_description", ""),
                    "category":         article.get("category", ""),
                    "author":           article.get("author", ""),
                    "slug":             slug,
                }
                css, body = _builder(
                    synth_article, site,
                    article.get("image", ""), "Staff", t,
                )
                log(f"  [{i+1}] ! {slug}  -  source truncated; regenerated stub from metadata")
            except Exception as _stub_err:
                log(f"  [{i+1}] x {slug}  -  could not locate article body and stub regen failed: {_stub_err}")
                fail += 1
                continue
        if body:
            # ── Press rewrap: parse the legacy body, reconstruct as a structured
            # article dict, then re-render through article_press() so every site
            # ends up with the same long-form magazine layout regardless of which
            # builder originally produced the page. Skipped only if extraction
            # fails (we keep the original body in that case).
            # GUARD: the structure extractor only understands press/legacy
            # markup. Re-extracting an already-bespoke page (ob-/kn-) scrapes
            # almost nothing and would gut the article. If the page is already
            # in its bespoke design, keep it as-is (just refresh comments/SEO).
            _already_bespoke = _use_distinct and any(
                f'class="{c}"' in body for c in _BESPOKE_CLASSES)
            try:
                if not _already_bespoke:
                    synth = _extract_article_structure(body, article)
                    if synth.get("sections") or synth.get("intro"):
                        fresh_css, fresh_body = _builder(
                            synth, site,
                            synth.get("image_url") or article.get("image", ""),
                            synth.get("photographer") or "Staff",
                            t,
                        )
                        body = fresh_body
                        css = fresh_css
            except Exception as _press_err:
                log(f"  [{i+1}] ! {slug}  -  rewrap fell back ({_press_err})")

            # Collapse legacy nested <time><time>...</time></time> chains from
            # earlier rebuilds that re-wrapped an already-wrapped date.
            prev = None
            while prev != body:
                prev = body
                body = re.sub(r'<time\b[^>]*>\s*(<time\b[^>]*>)', r'\1', body, flags=re.IGNORECASE)
                body = re.sub(r'</time>\s*</time>', '</time>', body, flags=re.IGNORECASE)

            # Strip legacy inline heading styles introduced by the old
            # _article_sections() template (font-family + font-size:22px etc.).
            # Replace with the scoped .art-h2 / .art-h3 classes. The matching
            # CSS rule is injected below so the visual outcome is unchanged.
            had_inline_h2 = bool(re.search(
                r'<h2\b([^>]*?)\sstyle="font-family:[^"]*font-size:22px[^"]*"',
                body, flags=re.IGNORECASE))
            had_inline_h3 = bool(re.search(
                r'<h3\b([^>]*?)\sstyle="font-family:[^"]*font-size:18px[^"]*"',
                body, flags=re.IGNORECASE))
            if had_inline_h2:
                body = re.sub(
                    r'<h2\b([^>]*?)\sstyle="font-family:[^"]*font-size:22px[^"]*"',
                    lambda m: f'<h2{m.group(1)} class="art-h2"',
                    body, flags=re.IGNORECASE)
            if had_inline_h3:
                body = re.sub(
                    r'<h3\b([^>]*?)\sstyle="font-family:[^"]*font-size:18px[^"]*"',
                    lambda m: f'<h3{m.group(1)} class="art-h3"',
                    body, flags=re.IGNORECASE)
            # If neither inline form existed but the body uses .art-h2 already
            # (e.g. fresh build from updated bot.py), the class rule still
            # needs to be present in CSS. Inject when missing.
            if _is_press and (had_inline_h2 or had_inline_h3
                    or "art-h2" in body or "art-h3" in body) and ".art-h2{" not in css:
                css = css + "\n/* heading classes */\n" + _article_section_css(t)
        if not body:
            log(f"  [{i+1}] x {slug}  -  could not locate article body")
            fail += 1
            continue

        # Pull this article's comments.json from the repo (if present) and
        # render an inline, schema.org-compliant comments section. Falls back
        # to a "Comments coming soon" placeholder when no comments.json exists.
        comments_data = []
        cj = _get(f"{api}/{slug}/comments.json", token)
        if cj:
            try:
                jd = cj.json()
                raw_b64 = jd.get("content", "")
                if raw_b64:
                    comments_data = json.loads(_decode(raw_b64))
                elif jd.get("git_url"):
                    blob = requests.get(jd["git_url"], headers=_headers(token), timeout=20)
                    if blob.ok:
                        comments_data = json.loads(_decode(blob.json()["content"]))
            except Exception:
                comments_data = []

        try:
            inline_block = _comments_section_inline(article, site, comments_data, t)
            new_body, n_sub = re.subn(
                r'<div id="comments-section".*?</script>|<section id="comments".*?</script>',
                lambda _m: inline_block, body, count=1, flags=re.DOTALL,
            )
            if n_sub:
                body = new_body
                if comments_data:
                    site_inlined += 1
                else:
                    site_placeholder += 1
            else:
                # Could not locate either comment section variant: append inline.
                body = body + inline_block
                if comments_data:
                    site_inlined += 1
                else:
                    site_placeholder += 1
        except Exception as _e:
            # Last resort: keep the JS-only fallback.
            body = re.sub(r'<div id="comments-section".*?</script>',
                          lambda _m: fresh_comments_js, body, count=1, flags=re.DOTALL)
            site_js_fallback += 1
        # Recolor the article accent to the site's brand accent. Replace both the
        # theme accents and the accent actually detected in this article's CSS.
        if _is_press and new_accent:
            olds = {old_accent, old_accent2, (_detect_accent(css) or "").lower()}
            for oa in olds:
                if oa and oa != new_accent.lower():
                    css  = re.sub(re.escape(oa), new_accent, css,  flags=re.IGNORECASE)
                    body = re.sub(re.escape(oa), new_accent, body, flags=re.IGNORECASE)

        # Recolor the article's body/h1 text from the old theme's text color to the
        # current one so headlines stay visible if the theme switched dark <-> light.
        new_text = (t.get("text") or "").lower()
        old_text = (_detect_text_color(css) or "").lower()
        if _is_press and new_text and old_text and old_text != new_text:
            css  = re.sub(re.escape(old_text), new_text, css,  flags=re.IGNORECASE)
            body = re.sub(re.escape(old_text), new_text, body, flags=re.IGNORECASE)

        # Tighten article headline line-height network-wide; extra-tight for Kanona.
        lh = "1.04" if stem == "kanona-events" else "1.1"
        css = css + ("\n/* tight headlines */\n"
                     ".art h1,.wrap h1,.art-grid h1,.art-min h1,.mag-hero h1,.imm-hero h1,"
                     "article h1,h1{line-height:" + lh + "!important}")

        title = article.get("title", slug)
        desc  = article.get("meta_description", "")
        canonical = f"https://{domain}/{slug}/" if domain else ""

        # Assign a category from categories.json keywords if the article doesn't have one.
        category = article.get("category") or assign_category(title + " " + desc + " " + body, stem)
        if category and not article.get("category"):
            article["category"] = category  # persist back into articles.json later

        ainfo = _resolve_author(site, article)
        # Visible-byline substitution: when the site's author changed in the
        # dashboard, the SEO meta below gets the fresh name automatically but
        # the byline text physically baked into the article body still reads
        # the old name. Swap common byline patterns so the rendered page also
        # shows the new author. Conservative: only inside attribution markers
        # (By / by / itemprop="author" / <strong> wrappers around the name).
        old_author = (article.get("author") or "").strip()
        new_author = ainfo["name"]
        if old_author and old_author != new_author:
            import re as _re
            safe = _re.escape(old_author)
            patterns = [
                (rf"(By\s*<strong[^>]*>){safe}(</strong>)",     rf"\g<1>{new_author}\g<2>"),
                (rf"(by\s*<strong[^>]*>){safe}(</strong>)",     rf"\g<1>{new_author}\g<2>"),
                (rf"(>\s*By\s+){safe}(\s*<)",                   rf"\g<1>{new_author}\g<2>"),
                (rf"(>\s*by\s+){safe}(\s*<)",                   rf"\g<1>{new_author}\g<2>"),
                (rf'(itemprop="author"[^>]*>){safe}(<)',        rf"\g<1>{new_author}\g<2>"),
                (rf'(class="[^"]*author[^"]*"[^>]*>\s*){safe}', rf"\g<1>{new_author}"),
            ]
            for pat, repl in patterns:
                body = _re.sub(pat, repl, body, flags=_re.IGNORECASE)
            article["author"] = new_author  # persist the resolved name back to articles.json
        seo = _seo_meta(
            title, desc, canonical, article.get("image", ""),
            ainfo["name"], article.get("date_iso", ""),
            modified_iso=datetime.now().strftime("%Y-%m-%d"),
            category=category,
            site_name=_site_name(site),
            site_url=f"https://{domain}/" if domain else "",
            word_count=_count_words(body),
            keywords=category,
            author_title=ainfo["title"],
            author_bio=ainfo["bio"],
            # Per-site Schema.org @type so Google sees each site as a distinct
            # publication (NewsArticle / TechArticle / BlogPosting / Review /
            # HowTo / TravelGuide / MedicalScholarlyArticle / etc.) instead of
            # every site declaring the generic "Article".
            schema_type=site.get("schema_article_type") or "Article",
        )

        # Semantic <time> on the byline date for Google date detection. Skip
        # if the body already contains a <time> tag for this date (otherwise
        # repeated rebuilds nest <time><time><time>... infinitely).
        disp_date = article.get("date", "")
        if disp_date and article.get("date_iso") and "<time" not in body:
            body = body.replace(disp_date, f'<time datetime="{article["date_iso"]}">{disp_date}</time>', 1)

        # Wrap content in <article> for stronger schema signal.
        body = f'<article itemscope itemtype="https://schema.org/{site.get("schema_article_type") or "Article"}">{body}</article>'

        try:
            # Full title -> og/twitter/JSON-LD (uncapped). Shortened tag_title
            # -> <title> only, so SERP truncation at ~60 chars never bites.
            tag_title = _seo_title_tag(title, _site_name(site))
            rebuilt = layout_shell.wrap_page(
                stem, title=tag_title, description=desc, body_html=body,
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

    # Push articles.json back if we assigned any new categories (so the homepage
    # cards and category filters pick them up).
    idx_r = _get(f"{api}/articles.json", token)
    if idx_r:
        try:
            idx_data = idx_r.json()
            idx_sha = idx_data.get("sha")
            current = json.loads(_decode(idx_data["content"])) if idx_data.get("content") else []
            # Merge: take the in-memory `articles` list (which now has category set)
            by_slug = {a.get("slug"): a for a in articles}
            updated = False
            for entry in current:
                s = entry.get("slug")
                if s in by_slug and by_slug[s].get("category") and not entry.get("category"):
                    entry["category"] = by_slug[s]["category"]
                    updated = True
            if updated:
                body_json = json.dumps(current, indent=2)
                _put_file(repo, "articles.json", body_json, token, sha=idx_sha,
                          msg="Backfill: article categories")
                log("  + articles.json: categories backfilled")
        except Exception as e:
            log(f"  ! articles.json category push failed: {e}")

    log(f"  summary: ok={ok} fail={fail} inlined={site_inlined} placeholder={site_placeholder} js_fallback={site_js_fallback}")
    return ok, fail, site_inlined, site_placeholder, site_js_fallback


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gh-token", default=os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", ""))
    p.add_argument("--only", default="", help="Comma-separated template stems (default: all)")
    p.add_argument("gh_token_pos", nargs="?", default="", help="Positional GH token (alternative to --gh-token)")
    args = p.parse_args()
    if not args.gh_token and args.gh_token_pos:
        args.gh_token = args.gh_token_pos

    if not args.gh_token:
        print("Error: --gh-token is required")
        sys.exit(1)

    cfg   = json.loads(CONFIG_FILE.read_text())
    sites = cfg.get("sites", [])
    only  = {x.strip() for x in args.only.split(",") if x.strip()}

    total_ok = total_fail = 0
    total_inlined = total_placeholder = total_js = 0
    per_site = []
    for site in sites:
        stem = site.get("repo", "").rsplit("/", 1)[-1] or site.get("id", "")
        if only and stem not in only and site.get("id") not in only:
            continue
        if not layout_shell.template_path(stem).exists():
            continue
        try:
            ok, fail, inlined, placeholder, js_fb = patch_site(stem, site, args.gh_token, log=print)
        except Exception as e:
            print(f"  !! site {stem} crashed: {e}")
            continue
        total_ok += ok
        total_fail += fail
        total_inlined += inlined
        total_placeholder += placeholder
        total_js += js_fb
        per_site.append((stem, ok, fail, inlined, placeholder, js_fb))

    print(f"\n{'-'*50}")
    print(f"Per-site article counts:")
    for stem, ok, fail, inlined, placeholder, js_fb in per_site:
        print(f"  {stem}: ok={ok} fail={fail} inlined={inlined} placeholder={placeholder} js_fallback={js_fb}")
    print(f"\nDone. {total_ok} re-wrapped, {total_fail} failed.")
    print(f"Inlined comments: {total_inlined} | Placeholder only: {total_placeholder} | JS fallback: {total_js}")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
