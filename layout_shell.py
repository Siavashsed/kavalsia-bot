#!/usr/bin/env python3
"""
layout_shell.py  -  Kavalsia Network shared layout shell.

The homepage of every site (templates/<stem>-index.html) is the single source of
truth for that site's chrome: header, footer, fonts and colors. Every other page
(about / privacy / terms / sms / meta-policy / 404) and every article is built by
wrapping its body content in that homepage's shell, so the chrome is always
byte-identical to the live homepage.

Each homepage template must contain four HTML-comment markers:

    <body ...>
    <!--SHELL:HEADER-->
      ...full visual header (ticker / banner / nav)...
    <!--/SHELL:HEADER-->
      ...homepage-only content...
    <!--SHELL:FOOTER-->
      ...footer element + all trailing <script> tags...
    <!--/SHELL:FOOTER-->
    </body>

Used by push-sites.py (static pages, depth 0) and bot.py / rebuild-articles.py
(articles, depth 1 - they live at <slug>/index.html).
"""

import re
from pathlib import Path

BASE      = Path(__file__).parent
TPL_DIR   = BASE / "templates"

HEADER_OPEN  = "<!--SHELL:HEADER-->"
HEADER_CLOSE = "<!--/SHELL:HEADER-->"
FOOTER_OPEN  = "<!--SHELL:FOOTER-->"
FOOTER_CLOSE = "<!--/SHELL:FOOTER-->"

# Cache parsed shells by template stem
_CACHE = {}


def template_path(stem):
    """templates/<stem>-index.html for a given template stem (= repo basename)."""
    return TPL_DIR / f"{stem}-index.html"


def _between(text, open_marker, close_marker, what):
    i = text.find(open_marker)
    j = text.find(close_marker)
    if i == -1 or j == -1 or j < i:
        raise ValueError(f"missing/!invalid {what} markers ({open_marker} .. {close_marker})")
    return text[i + len(open_marker):j].strip()


def validate_markers(stem):
    """Raise ValueError if the homepage template lacks the four shell markers.
    Returns True on success. Used by sync.py to fail loudly for new sites."""
    p = template_path(stem)
    if not p.exists():
        raise ValueError(f"homepage template not found: {p}")
    html = p.read_text(encoding="utf-8")
    for m in (HEADER_OPEN, HEADER_CLOSE, FOOTER_OPEN, FOOTER_CLOSE):
        if m not in html:
            raise ValueError(f"{p.name}: missing shell marker {m}")
    # ordering check
    if not (html.find(HEADER_OPEN) < html.find(HEADER_CLOSE)
            <= html.find(FOOTER_OPEN) < html.find(FOOTER_CLOSE)):
        raise ValueError(f"{p.name}: shell markers are out of order")
    return True


def get_shell(stem, refresh=False):
    """Parse templates/<stem>-index.html and return its chrome:
        {font_links, style, header_html, footer_html}
    font_links - all <link> tags from <head> (fonts / preconnect).
    style      - inner text of the first <style> block.
    header_html- HTML between the HEADER markers.
    footer_html- HTML between the FOOTER markers (footer element + trailing scripts).
    """
    if not refresh and stem in _CACHE:
        return _CACHE[stem]

    p = template_path(stem)
    if not p.exists():
        raise ValueError(f"homepage template not found: {p}")
    html = p.read_text(encoding="utf-8")

    head = html[:html.find("</head>")] if "</head>" in html else html
    font_links = "\n".join(re.findall(r'<link\b[^>]*>', head, flags=re.IGNORECASE))

    m = re.search(r'<style[^>]*>(.*?)</style>', html, flags=re.DOTALL | re.IGNORECASE)
    style = m.group(1).strip() if m else ""

    am = re.search(r'<!--SHELL:ACCENT:(#[0-9a-fA-F]{3,8})-->', html)
    accent = am.group(1) if am else ""

    shell = {
        "font_links":  font_links,
        "style":       style,
        "accent":      accent,
        "header_html": _between(html, HEADER_OPEN, HEADER_CLOSE, "HEADER"),
        "footer_html": _between(html, FOOTER_OPEN, FOOTER_CLOSE, "FOOTER"),
    }
    _CACHE[stem] = shell
    return shell


_SKIP_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "#", "data:",
                   "/", "{", "javascript:")


def _rewrite_one(value, up):
    """Rewrite a single href/src value for a page that is `up` (e.g. '../') deep."""
    v = value.strip()
    if not v:
        return up
    if v.startswith("#"):                       # homepage in-page anchor
        return up + v
    if v.startswith(_SKIP_PREFIXES):            # absolute / external / non-path
        return value
    if v in ("./", "."):
        return up
    if v.startswith("./"):
        v = v[2:]
    return up + v


def rewrite_links(html, depth):
    """Prefix relative href/src in `html` for a page nested `depth` levels below the
    site root. depth 0 = static pages (same dir as homepage) - we still need to
    rewrite homepage in-page anchors (#section) to `./#section` so they navigate
    back to the homepage and scroll there instead of pointing at a non-existent id
    on the current page. depth >= 1 = articles, all relative paths get prefixed."""
    if depth < 0:
        return html
    up = "./" if depth == 0 else ("../" * depth)

    def repl(mtch):
        attr, q, val = mtch.group(1), mtch.group(2), mtch.group(3)
        v = val.strip()
        if depth == 0:
            # Only rewrite homepage anchors; leave same-dir paths (about.html, etc.) untouched.
            if v.startswith("#"):
                return f'{attr}={q}{up}{v}{q}'
            return mtch.group(0)
        return f'{attr}={q}{_rewrite_one(val, up)}{q}'

    return re.sub(r'\b(href|src)=(["\'])(.*?)\2', repl, html, flags=re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# Mojibake repair: common UTF-8-decoded-as-Latin-1 garble we have seen leak
# into article HTML through copy/paste or third-party content. Applied to
# every wrapped page BEFORE dedupe so the dedupe sees clean text.
# ─────────────────────────────────────────────────────────────────────────────

# Each entry maps a UTF-8-decoded-as-Latin-1 garble sequence back to its
# intended character. Built from raw byte sequences to avoid editor mangling.
_MOJIBAKE_MAP = [
    (b"\xe2\x94\x80\xe2\x94\x80".decode("latin-1"), "&nbsp; &nbsp;"),
    (b"\xe2\x80\x99".decode("latin-1"), "'"),
    (b"\xe2\x80\x98".decode("latin-1"), "'"),
    (b"\xe2\x80\x9c".decode("latin-1"), '"'),
    (b"\xe2\x80\x9d".decode("latin-1"), '"'),
    (b"\xe2\x80\x93".decode("latin-1"), "-"),
    (b"\xe2\x80\x94".decode("latin-1"), "-"),
    (b"\xe2\x86\x92".decode("latin-1"), "->"),
    (b"\xe2\x80\xa6".decode("latin-1"), "..."),
    (b"\xc2\xb7".decode("latin-1"), "·"),
    (b"\xc2\xa0".decode("latin-1"), " "),
]


def _fix_mojibake(html):
    """Conservative mojibake sweep. Replaces a small allow-list of known garble
    sequences; never touches anything outside the map. Safe to run on any HTML."""
    if not html:
        return html
    out = html
    for bad, good in _MOJIBAKE_MAP:
        if bad in out:
            out = out.replace(bad, good)
    # Lone "Â" before a non-letter is almost always a stray non-breaking space
    # byte. Drop only when followed by a space, punctuation or end of string.
    out = re.sub(r"Â(?=[\s\W]|$)", "", out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Duplicate CSS rule remover. Runs over every <style>...</style> block and
# drops repeated top-level rules within the SAME block. At-rules (@media,
# @keyframes, @font-face, @supports, @import) and :root are left untouched
# and treated as atomic units. If a block cannot be parsed cleanly it is
# returned verbatim.
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_rule(rule):
    """Collapse all whitespace runs so equivalent rules compare byte-equal."""
    return re.sub(r"\s+", " ", rule).strip()


def _split_top_level_rules(css):
    """Yield a list of top-level CSS chunks: either a full at-rule block (kept
    atomic) or a single selector + declaration block. Returns None if the
    brace structure is unbalanced (caller should then skip dedupe)."""
    chunks = []
    i = 0
    n = len(css)
    buf_start = 0
    while i < n:
        ch = css[i]
        if ch == "@":
            # At-rule: keep atomic. Could be @import ...; or @media { ... }.
            start = i
            # Walk to either ; (no body) or matching {...}.
            j = i
            while j < n and css[j] not in "{;":
                j += 1
            if j >= n:
                return None
            if css[j] == ";":
                chunks.append(("atrule", css[start:j+1]))
                i = j + 1
                buf_start = i
                continue
            # css[j] == '{': find matching brace.
            depth = 1
            k = j + 1
            while k < n and depth > 0:
                if css[k] == "{":
                    depth += 1
                elif css[k] == "}":
                    depth -= 1
                k += 1
            if depth != 0:
                return None
            chunks.append(("atrule", css[start:k]))
            i = k
            buf_start = i
            continue
        if ch == "{":
            # Find matching brace for a plain rule.
            depth = 1
            k = i + 1
            while k < n and depth > 0:
                if css[k] == "{":
                    depth += 1
                elif css[k] == "}":
                    depth -= 1
                k += 1
            if depth != 0:
                return None
            chunks.append(("rule", css[buf_start:k]))
            i = k
            buf_start = i
            continue
        i += 1
    tail = css[buf_start:]
    if tail.strip():
        # Trailing whitespace or stray text; keep verbatim.
        chunks.append(("tail", tail))
    return chunks


def _dedupe_style_blocks(html):
    """Remove duplicate top-level CSS rules inside each <style> block. Safe.

    Also collapses byte-equal at-rule blocks (@media, @keyframes, @font-face,
    @supports, @import, :root) and byte-equal selector rules. At-rule internals
    are NEVER modified - only the at-rule as a whole is compared against
    earlier siblings via whitespace-normalized text equality. Non-identical
    at-rules (e.g. two @media (max-width:640px) blocks with different bodies)
    are both kept.
    """
    if not html or "<style" not in html:
        return html

    def _rewrite_block(match):
        opening = match.group(1)
        css = match.group(2)
        closing = match.group(3)
        try:
            chunks = _split_top_level_rules(css)
        except Exception:
            return match.group(0)
        if chunks is None:
            return match.group(0)
        seen_rules   = set()
        seen_atrules = set()
        seen_roots   = set()
        out = []
        for kind, text in chunks:
            if kind == "rule":
                key = _normalize_rule(text)
                # :root rules: dedupe byte-equal duplicates but keep the first.
                if key.lstrip().startswith(":root"):
                    if key in seen_roots:
                        continue
                    seen_roots.add(key)
                    out.append(text)
                    continue
                if key in seen_rules:
                    continue
                seen_rules.add(key)
                out.append(text)
            elif kind == "atrule":
                key = _normalize_rule(text)
                if key in seen_atrules:
                    continue
                seen_atrules.add(key)
                out.append(text)
            else:
                out.append(text)
        return opening + "".join(out) + closing

    return re.sub(r"(<style\b[^>]*>)(.*?)(</style>)",
                  _rewrite_block, html, flags=re.DOTALL | re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# Self-check: run a tiny sanity test on import so a future regression in the
# dedupe logic fails loudly rather than silently corrupting every article.
# ─────────────────────────────────────────────────────────────────────────────

def _self_check_dedupe():
    sample = (
        "<style>"
        "@media(max-width:600px){a{color:red}}"
        "@media(max-width:600px){a{color:red}}"
        "@media(max-width:600px){a{color:red}}"
        "@media(max-width:700px){b{color:blue}}"
        "</style>"
    )
    out = _dedupe_style_blocks(sample)
    if out.count("@media(max-width:600px)") != 1:
        raise AssertionError(
            f"_dedupe_style_blocks self-check failed: identical @media not collapsed. Got: {out}"
        )
    if "@media(max-width:700px)" not in out:
        raise AssertionError(
            f"_dedupe_style_blocks self-check failed: unique @media dropped. Got: {out}"
        )


_self_check_dedupe()


# ─────────────────────────────────────────────────────────────────────────────
# Nested <article> collapser. With build_article_page wrapping every article
# in an outer <article itemscope ...>, some builders also open an inner
# <article>. Convert the inner one to <section> for valid semantic HTML.
# ─────────────────────────────────────────────────────────────────────────────

def _collapse_nested_articles(html):
    """If the document contains more than one <article> tag, convert all
    inner ones to <section>. Conservative: only acts when an inner article
    occurs between an outer <article> opening tag and its eventual close."""
    if not html:
        return html
    opens = [m.start() for m in re.finditer(r"<article\b", html, flags=re.IGNORECASE)]
    if len(opens) < 2:
        return html
    # Replace every <article ...> after the first with <section ...>, then
    # replace the matching number of </article> closes (last N) with </section>.
    # We walk and rebuild to keep tag attributes.
    parts = []
    last = 0
    seen_open = 0
    # Find every <article ...> and </article> in order and balance.
    token_re = re.compile(r"</?article\b[^>]*>", flags=re.IGNORECASE)
    depth = 0
    for m in token_re.finditer(html):
        tag = m.group(0)
        parts.append(html[last:m.start()])
        last = m.end()
        is_close = tag.lower().startswith("</")
        if is_close:
            depth -= 1
            if depth >= 1:
                parts.append("</section>")
            else:
                parts.append(tag)
        else:
            depth += 1
            if depth >= 2:
                # Convert <article ...> -> <section ...>.
                parts.append(re.sub(r"^<article", "<section", tag, count=1, flags=re.IGNORECASE))
            else:
                parts.append(tag)
    parts.append(html[last:])
    return "".join(parts)


_NESTED_P_OPEN  = re.compile(r"<p([^>]*)>\s*<p([^>]*)>", flags=re.IGNORECASE)
_NESTED_P_CLOSE = re.compile(r"</p>\s*</p>", flags=re.IGNORECASE)


def _collapse_nested_paragraphs(html):
    """Repair literal nested <p>...<p>...</p></p> anti-patterns introduced by
    builders that wrap an already-paragraphed intro in another <p>. Keeps the
    OUTER <p>'s attributes (it usually has the class), drops the inner <p>'s
    attributes. Iterates until stable (max 5 passes) to handle deeper nesting
    without risking an infinite loop on pathological input."""
    if not html or "<p" not in html.lower():
        return html
    out = html
    for _ in range(5):
        new = _NESTED_P_OPEN.sub(r"<p\1>", out)
        new = _NESTED_P_CLOSE.sub("</p>", new)
        if new == out:
            break
        out = new
    return out


def clean(html):
    """Network-wide copy rule + Core Web Vitals + semantic fixes. Applied to
    every generated page:
      - never use em dashes or en dashes (em -> ' - ', en -> '-'),
      - mojibake sweep (UTF-8-as-Latin-1 garble),
      - dedupe duplicate top-level CSS rules inside each <style> block,
      - collapse nested <article> elements to <section>,
      - collapse nested <p><p>...</p></p> anti-patterns to a single <p>.
    """
    out = (html.replace(" — ", " - ").replace("—", " - ")
               .replace("–", "-").replace("―", "-"))
    out = _fix_mojibake(out)
    out = _dedupe_style_blocks(out)
    out = _collapse_nested_articles(out)
    out = _collapse_nested_paragraphs(out)
    # Strip SHELL marker HTML comments. These exist to help the bot find the
    # header/footer/accent regions inside the source template; they have no
    # runtime meaning. Leaving them in published HTML lets anyone view-source
    # two sites and see the same SHELL: fingerprint, which is the single
    # most obvious "made by one system" tell network-wide.
    out = re.sub(r'<!--\s*/?SHELL:[^>]*-->\s*\n?', '', out)
    return out


def wrap_page(stem, *, title, body_html, description="", extra_css="",
              head_meta="", depth=0, lang="en", text_dir="ltr"):
    """Assemble a full HTML page wrapped in the homepage shell of `stem`.

    title       - <title> text.
    body_html   - the page-specific content placed between header and footer.
    description - <meta name=description> content (optional).
    extra_css   - page-specific CSS appended after the homepage style.
    head_meta   - extra raw <head> tags (canonical / OG / JSON-LD for articles).
    depth       - 0 for static pages, 1 for articles at <slug>/index.html.
    lang        - BCP-47 language code emitted as <html lang> (default "en").
    text_dir    - text direction emitted as <html dir> (default "ltr"; use "rtl"
                  for Persian, Arabic, Hebrew, Sorani Kurdish pages).
    """
    shell = get_shell(stem)
    header = rewrite_links(shell["header_html"], depth)
    footer = rewrite_links(shell["footer_html"], depth)
    desc_tag = f'<meta name="description" content="{description}">' if description else ""
    page_css = f"\n/* page */\n{extra_css}" if extra_css.strip() else ""

    # Favicon links point to /favicon.svg (modern browsers), with .ico and
    # apple-touch-icon fallbacks. Per-site SVGs are generated by
    # _publish_favicons.py and pushed to each repo root.
    up = "../" * depth
    favicon_links = (
        f'<link rel="icon" type="image/svg+xml" href="{up}favicon.svg">'
        f'<link rel="alternate icon" href="{up}favicon.ico">'
        f'<link rel="apple-touch-icon" sizes="180x180" href="{up}apple-touch-icon.png">'
    )

    return clean(f"""<!DOCTYPE html>
<html lang="{lang}" dir="{text_dir}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{desc_tag}
{favicon_links}
{head_meta}
{shell["font_links"]}
<style>
{shell["style"]}{page_css}
</style>
</head>
<body data-page-depth="{depth}">
{header}
{body_html}
{footer}
</body>
</html>""")
