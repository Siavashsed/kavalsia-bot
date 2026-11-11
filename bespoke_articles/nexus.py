"""Nexus hub bespoke article presentations.

Two editorial formats get their own layout in the hub's dark look (tokens from
templates/nexus-index.html :root, which the page shell already defines):

  article["nexus_layout"] == "faq-index"  numbered index grid + numbered answer cards
  article["nexus_layout"] == "interview"  Q&A transcript: chapters, labelled turns, one pull quote

Anything else falls back to the shared builder bot.py would have used, so other
Nexus articles build exactly as before. Bot helpers not injected into this module
are reached through G (bot's own globals).
"""
import html as _html
import re

SITE_ID = "nexus"


def _G():
    return _wrap_block.__globals__  # noqa: F821  (injected by bot)


def _fallback(article, site, image_url, photographer, t):
    G = _G()
    builder = G["ARTICLE_BUILDERS"].get(site.get("article_layout", "standard"), G["article_standard"])
    return builder(article, site, image_url, photographer, t)


def _tail(article, site, author, t):
    """Sources, author card, comments placeholder (swapped inline by build_article_page)."""
    G = _G()
    return (f'{_sources_block(article, t)}'  # noqa: F821
            f'</div>' + G["_author_card"](site, author, t) + G["_comments_section_js"](t) + _giscus(site))  # noqa: F821


_SHARED_CSS = """
.nxf,.nxi{box-sizing:border-box;width:100%;margin:0 auto;font-family:'Inter',system-ui,sans-serif;color:var(--text)}
.nxf *,.nxi *{box-sizing:border-box;min-width:0;overflow-wrap:break-word}
.nxf h1,.nxf h2,.nxi h1,.nxi h2{text-wrap:balance;margin:0}
.nxf p,.nxi p{text-wrap:pretty}
.nxf a,.nxi a{color:var(--blue2);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
.nxf a:focus,.nxi a:focus,.nxf a:focus-visible,.nxi a:focus-visible{outline:none}
.nx-kick{font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--text3);margin:0 0 20px}
.nx-kick b{color:var(--blue);font-weight:600}
.nx-concl{font-family:'Lora',Georgia,serif;font-size:18px;line-height:1.7;color:var(--text);background:var(--card);border-radius:16px;padding:32px 36px;margin:56px 0 0}
.nx-concl p{margin:0 0 16px;color:var(--text)}
.nx-concl p:last-child{margin-bottom:0}
.nx-cap{font-size:12px;color:var(--text3);margin:10px 0 0}
@media(max-width:640px){.nx-concl{padding:24px 22px;font-size:17px}}
"""


# ── FAQ: numbered index grid ────────────────────────────────────────────────
_FAQ_CSS = """
.nxf{max-width:1168px;padding:56px 24px 24px}
.nxf-head{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:48px;align-items:center;margin:0 0 64px}
.nxf-head h1{font-size:clamp(32px,4.6vw,52px);font-weight:800;line-height:1.06;letter-spacing:-.02em;color:var(--text);margin:0 0 22px}
.nxf-lede{font-family:'Lora',Georgia,serif;font-size:19px;line-height:1.6;color:var(--text2);margin:0}
.nxf-lede p{margin:0 0 14px;color:var(--text2)}
.nxf-lede p:last-child{margin:0}
.nxf-fig{margin:0}
.nxf-fig img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:16px}
.nxf-ix-h{font-size:13px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--text3);margin:0 0 18px}
.nxf-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:0 0 80px;scroll-margin-top:80px}
.nxf a.nxf-tile{display:flex;flex-direction:column;gap:14px;min-height:148px;padding:22px 22px 24px;background:var(--card);border-radius:14px;color:var(--text);text-decoration:none;transition:transform .2s ease,background .2s ease}
.nxf a.nxf-tile:hover{transform:translateY(-3px);background:var(--card2)}
.nxf-tile .nxf-n{font-size:34px;font-weight:700;line-height:1;letter-spacing:-.02em;font-variant-numeric:tabular-nums;color:var(--blue)}
.nxf-tile .nxf-q{font-size:15px;font-weight:400;line-height:1.45;color:var(--text);text-wrap:pretty}
.nxf-list{max-width:780px;margin:0 auto}
.nxf-card{background:var(--card);border-radius:16px;padding:36px 40px 30px;margin:0 0 16px;scroll-margin-top:80px}
.nxf-card-h{display:flex;align-items:baseline;gap:16px;margin:0 0 18px}
.nxf-card-h .nxf-n{flex:none;font-size:14px;font-weight:700;letter-spacing:.04em;font-variant-numeric:tabular-nums;color:var(--blue)}
.nxf-card h2{font-size:clamp(21px,2.2vw,25px);font-weight:700;line-height:1.25;letter-spacing:-.01em;color:var(--text)}
.nxf-ans{font-family:'Lora',Georgia,serif;font-size:17.5px;line-height:1.7;color:var(--text2)}
.nxf-ans p{margin:0 0 16px;color:var(--text2)}
.nxf-ans ul,.nxf-ans ol{margin:0 0 16px 22px}
.nxf a.nxf-back{display:inline-block;font-size:13px;font-weight:500;color:var(--text3);text-decoration:none;margin:4px 0 0}
.nxf a.nxf-back:hover{color:var(--blue2)}
.nxf .nx-concl,.nxf .art-sources,.nxf .sources{max-width:780px;margin-left:auto;margin-right:auto}
@media(max-width:1024px){.nxf-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.nxf-head{gap:36px}}
@media(max-width:820px){.nxf-head{grid-template-columns:1fr;gap:28px;margin-bottom:48px}.nxf-fig{order:-1}}
@media(max-width:640px){
  .nxf{padding:36px 16px 16px}
  .nxf-lede{font-size:17.5px}
  .nxf-grid{gap:10px;margin-bottom:56px}
  .nxf a.nxf-tile{min-height:132px;padding:16px 14px 18px;gap:10px}
  .nxf-tile .nxf-n{font-size:26px}
  .nxf-tile .nxf-q{font-size:13.5px}
  .nxf-card{padding:26px 22px 22px}
  .nxf-card-h{gap:12px}
  .nxf-ans{font-size:17px}
}
"""

_NUM_PREFIX = re.compile(r"^\s*(\d{1,2})\s*[.):]\s*")


def _faq(article, site, image_url, photographer, t):
    author = _resolve_author(site, article)["name"]  # noqa: F821
    secs = article.get("sections") or []
    tiles, cards = [], []
    for i, s in enumerate(secs, 1):
        head = s.get("heading", "")
        m = _NUM_PREFIX.match(head)
        n = f"{int(m.group(1)) if m else i:02d}"
        q = _NUM_PREFIX.sub("", head, count=1)
        tiles.append(f'<a class="nxf-tile" href="#q{n}"><span class="nxf-n">{n}</span><span class="nxf-q">{q}</span></a>')
        cards.append(
            f'<article class="nxf-card" id="q{n}"><div class="nxf-card-h"><span class="nxf-n">{n}</span><h2>{q}</h2></div>'
            f'<div class="nxf-ans">{s.get("content", "")}</div>'
            f'<a class="nxf-back" href="#nxf-index">Back to the index</a></article>')
    fig = (f'<figure class="nxf-fig"><img src="{image_url}" alt="{_html.escape(article.get("image_alt", article["title"]), quote=True)}" loading="eager">'
           f'<figcaption class="nx-cap">Photo by {photographer}</figcaption></figure>') if image_url else ""
    intro = _wrap_block(article.get("intro", ""), "p") + _wrap_block(article.get("intro2", ""), "p")  # noqa: F821
    body = f"""<div class="nxf">
  <header class="nxf-head">
    <div>
      <p class="nx-kick"><b>{len(secs)} questions</b> &nbsp;&middot;&nbsp; {article.get("date", "")}</p>
      <h1>{article["title"]}</h1>
      <div class="nxf-lede">{intro}</div>
    </div>
    {fig}
  </header>
  <p class="nxf-ix-h">The index</p>
  <nav class="nxf-grid" id="nxf-index" aria-label="Questions">{"".join(tiles)}</nav>
  <div class="nxf-list">{"".join(cards)}</div>
  <div class="nx-concl">{article.get("conclusion", "")}</div>
  """ + _tail(article, site, author, t)
    return _SHARED_CSS + _FAQ_CSS, body


# ── Interview: Q&A transcript ───────────────────────────────────────────────
_INT_CSS = """
.nxi{max-width:1168px;padding:56px 24px 24px}
.nxi-hero{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:56px;align-items:center;margin:0 0 64px}
.nxi-hero h1{font-family:'Lora',Georgia,serif;font-size:clamp(34px,4.4vw,54px);font-weight:500;line-height:1.08;letter-spacing:-.015em;color:var(--text);margin:0 0 24px}
.nxi-by{font-size:14px;color:var(--text2);margin:0}
.nxi-by strong{color:var(--text);font-weight:600}
.nxi-rule{display:block;width:56px;height:2px;border-radius:2px;background:linear-gradient(90deg,var(--blue),var(--indigo));margin:20px 0 0}
.nxi-fig{margin:0}
.nxi-fig img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:16px;filter:grayscale(1) contrast(1.05)}
.nxi-col{max-width:740px;margin:0 auto}
.nxi-stand{font-family:'Lora',Georgia,serif;font-size:21px;line-height:1.6;color:var(--text);margin:0 0 72px}
.nxi-stand p{margin:0 0 16px;color:var(--text)}
.nxi-ch{margin:0 0 64px}
.nxi-ch-h{margin:0 0 32px}
.nxi-ch-h .nxi-part{display:block;font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--blue);margin:0 0 10px;font-variant-numeric:tabular-nums}
.nxi-ch-h h2{font-family:'Lora',Georgia,serif;font-size:clamp(26px,3vw,34px);font-weight:500;line-height:1.15;color:var(--text)}
.nxi-turn{display:grid;grid-template-columns:96px minmax(0,1fr);column-gap:24px;margin:0 0 26px}
.nxi-lab{font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;line-height:1;padding-top:7px}
.nxi-q .nxi-lab{color:var(--blue)}
.nxi-a .nxi-lab{color:var(--text3)}
.nxi-q .nxi-txt{font-size:18px;font-weight:600;line-height:1.5;color:var(--text)}
.nxi-q .nxi-txt p{margin:0;color:var(--text)}
.nxi-a .nxi-txt{font-family:'Lora',Georgia,serif;font-size:18px;line-height:1.7;color:var(--text2)}
.nxi-a .nxi-txt p{margin:0 0 14px;color:var(--text2)}
.nxi-a .nxi-txt p:last-child{margin-bottom:0}
.nxi-raw{font-family:'Lora',Georgia,serif;font-size:18px;line-height:1.7;color:var(--text2)}
.nxi-pull{margin:8px 0 72px;padding:40px 44px;background:var(--card);border-radius:18px}
.nxi-pull::before{content:'';display:block;width:56px;height:2px;border-radius:2px;background:linear-gradient(90deg,var(--blue),var(--indigo));margin:0 0 22px}
.nxi-pull p{font-family:'Lora',Georgia,serif;font-style:italic;font-size:clamp(23px,2.6vw,30px);line-height:1.38;color:var(--text);margin:0 0 16px;text-wrap:balance}
.nxi-pull cite{font-style:normal;font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--text3)}
.nxi .nx-concl{margin-top:24px}
@media(max-width:900px){
  .nxi-hero{grid-template-columns:1fr;gap:28px;margin-bottom:48px}
  .nxi-fig{order:-1}
  .nxi-fig img{aspect-ratio:4/5;max-height:520px}
}
@media(max-width:640px){
  .nxi{padding:32px 16px 16px}
  .nxi-stand{font-size:19px;margin-bottom:56px}
  .nxi-turn{grid-template-columns:1fr;row-gap:8px;margin-bottom:22px}
  .nxi-lab{padding-top:0}
  .nxi-q .nxi-txt{font-size:17px}
  .nxi-a .nxi-txt{font-size:17px}
  .nxi-pull{padding:28px 24px;margin-bottom:56px}
  .nxi-ch{margin-bottom:52px}
}
"""

_P = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)
_Q = re.compile(r"\s*<strong>(.*?)</strong>\s*", re.S)


def _turns(content, subject):
    """[(kind, html)] where kind is 'q', 'a' (one or more <p>) or 'raw'."""
    out, pos = [], 0
    for m in _P.finditer(content):
        gap = content[pos:m.start()].strip()
        if gap:
            out.append(["raw", gap])
        pos = m.end()
        q = _Q.fullmatch(m.group(1))
        if q:
            out.append(["q", f"<p>{q.group(1)}</p>"])
        elif out and out[-1][0] == "a":
            out[-1][1] += m.group(0)
        else:
            out.append(["a", m.group(0)])
    rest = content[pos:].strip()
    if rest:
        out.append(["raw", rest])
    return out


def _pull_quote(sections):
    """One complete sentence from the subject's answers: no trailing-off ellipsis,
    55 to 150 chars, an opinion turn ("but", "rather", "instead") preferred."""
    sents = []
    for s in sections:
        for kind, h in _turns(s.get("content", ""), ""):
            if kind != "a":
                continue
            txt = re.sub(r"<[^>]+>", " ", h)
            txt = re.sub(r"\s+", " ", txt).strip()
            for sent in re.split(r"(?:(?<=[.!?])|(?<=[.!?][\"”]))\s+(?=[A-Z\"“])", txt):
                sent = sent.strip().strip('"“”').strip()
                if 55 <= len(sent) <= 150 and "..." not in sent and "…" not in sent:
                    sents.append(sent)
    turn = [x for x in sents if re.search(r"\b(but|rather|instead)\b", x, re.I)]
    return (turn or sents or [""])[0]


def _interview(article, site, image_url, photographer, t):
    author = _resolve_author(site, article)["name"]  # noqa: F821
    secs = article.get("sections") or []
    subject = "Sadighi"
    asker = "Nexus"
    pull = _pull_quote(secs)
    pull_at = max(1, len(secs) // 2)
    chapters = []
    for i, s in enumerate(secs, 1):
        rows = []
        for kind, h in _turns(s.get("content", ""), subject):
            if kind == "q":
                rows.append(f'<div class="nxi-turn nxi-q"><span class="nxi-lab">{asker}</span><div class="nxi-txt">{h}</div></div>')
            elif kind == "a":
                rows.append(f'<div class="nxi-turn nxi-a"><span class="nxi-lab">{subject}</span><div class="nxi-txt">{h}</div></div>')
            else:
                rows.append(f'<div class="nxi-raw">{h}</div>')
        chapters.append(
            f'<section class="nxi-ch" id="part-{i}"><header class="nxi-ch-h"><span class="nxi-part">Part {i:02d}</span>'
            f'<h2>{s.get("heading", "")}</h2></header>{"".join(rows)}</section>')
        if pull and i == pull_at:
            chapters.append(f'<blockquote class="nxi-pull"><p>{pull}</p><cite>Siavash Sadighi</cite></blockquote>')
    fig = (f'<figure class="nxi-fig"><img src="{image_url}" alt="{_html.escape(article.get("image_alt", article["title"]), quote=True)}" loading="eager">'
           f'<figcaption class="nx-cap">Photo by {photographer}</figcaption></figure>') if image_url else ""
    stand = _wrap_block(article.get("intro", ""), "p") + _wrap_block(article.get("intro2", ""), "p")  # noqa: F821
    body = f"""<div class="nxi">
  <header class="nxi-hero">
    <div>
      <p class="nx-kick"><b>The Interview</b> &nbsp;&middot;&nbsp; {article.get("date", "")}</p>
      <h1>{article["title"]}</h1>
      <p class="nxi-by">Interview by <strong>{author}</strong></p>
      <span class="nxi-rule" aria-hidden="true"></span>
    </div>
    {fig}
  </header>
  <div class="nxi-col">
    <div class="nxi-stand">{stand}</div>
    {"".join(chapters)}
    <div class="nx-concl">{article.get("conclusion", "")}</div>
  </div>
  """ + _tail(article, site, author, t)
    return _SHARED_CSS + _INT_CSS, body


def render(article, site, image_url, photographer, t):
    layout = article.get("nexus_layout") or ""
    if layout == "faq-index":
        return _faq(article, site, image_url, photographer, t)
    if layout == "interview":
        return _interview(article, site, image_url, photographer, t)
    return _fallback(article, site, image_url, photographer, t)
