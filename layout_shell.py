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
    site root. depth 0 (static pages, same dir as homepage) returns html unchanged."""
    if depth <= 0:
        return html
    up = "../" * depth

    def repl(mtch):
        attr, q, val = mtch.group(1), mtch.group(2), mtch.group(3)
        return f'{attr}={q}{_rewrite_one(val, up)}{q}'

    return re.sub(r'\b(href|src)=(["\'])(.*?)\2', repl, html, flags=re.IGNORECASE)


def clean(html):
    """Network-wide copy rule: never use em dashes or en dashes. Em dash becomes
    ' - ', en dash becomes '-'. Applied to every generated page so dashes can never
    reach a live site even if a source template or article still contains one."""
    return (html.replace(" — ", " - ").replace("—", " - ")
                .replace("–", "-").replace("―", "-"))


def wrap_page(stem, *, title, body_html, description="", extra_css="",
              head_meta="", depth=0):
    """Assemble a full HTML page wrapped in the homepage shell of `stem`.

    title       - <title> text.
    body_html   - the page-specific content placed between header and footer.
    description - <meta name=description> content (optional).
    extra_css   - page-specific CSS appended after the homepage style.
    head_meta   - extra raw <head> tags (canonical / OG / JSON-LD for articles).
    depth       - 0 for static pages, 1 for articles at <slug>/index.html.
    """
    shell = get_shell(stem)
    header = rewrite_links(shell["header_html"], depth)
    footer = rewrite_links(shell["footer_html"], depth)
    desc_tag = f'<meta name="description" content="{description}">' if description else ""
    page_css = f"\n/* page */\n{extra_css}" if extra_css.strip() else ""

    return clean(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{desc_tag}
{head_meta}
{shell["font_links"]}
<style>
{shell["style"]}{page_css}
</style>
</head>
<body>
{header}
{body_html}
{footer}
</body>
</html>""")
