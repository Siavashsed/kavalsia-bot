"""Bespoke article page for Supplement Verge (sva-).

A clean, clinical, evidence-review look in the spirit of a rigorous
supplement-science publication. Dark surface, light-lime (#84cc16) accent.
Distinct from the trading-tech pilot and the commerce/marketing siblings:

  - A "peer-reviewed" header band: a mono "EVIDENCE REVIEW" eyebrow plus an
    inline grade chip, then a serious-but-clean H1 and a measured abstract dek.
  - A reading-measure body (~720px) with a clinical intro "abstract" block,
    underlined-stat conclusion styled as a "Verdict" card.
  - A sticky sidebar built like a journal masthead: a "Reviewed by" reviewer
    card (lab-coat style avatar tile + credentials), a numbered
    "Recently reviewed" list (citation-style index), and a full-width
    "Browse the evidence library" button.
  - Discussion styled as "Reader notes" with annotation markers + localStorage
    posting.

Self-contained: only the injected bot data-helpers are used (no import bot).
NO em dashes anywhere. Unique class prefix `sva-`. The lime accent is light,
so all text/icons placed ON the accent are dark (#0c1208) for AA contrast.
"""

SITE_ID = "supplement-verge"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "SV"
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Inter',system-ui,sans-serif"
    acc = t["accent"]
    ink = t["text"]
    sub = t.get("text2", t["meta"])
    dim = t["meta"]
    brd = t["border"]
    bg = t["bg"]
    bg2 = t["bg2"]
    # Dark ink to sit ON the light-lime accent (AA contrast).
    on_acc = "#0c1208"
    cat = (article.get("category") or site.get("category") or "Review")

    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len([w for w in _re.sub(r"<[^>]+>", " ", _txt or "").split() if w])
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (
            f'<figure class="sva-hero">'
            f'<img src="{image_url}" alt="{article.get("image_alt","")}" loading="lazy">'
            f'<figcaption><span class="sva-fig-tag">FIG.</span>'
            f'Image: {photographer} / Pexels</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'sva-h2')

    css = f"""
.sva{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.sva *,.sva *::before,.sva *::after{{box-sizing:border-box}}
.sva-wrap{{max-width:1160px;margin:0 auto;padding:clamp(26px,5vw,56px) clamp(18px,5vw,30px) 90px}}
.sva-grid{{display:grid;grid-template-columns:minmax(0,1fr) 308px;gap:clamp(30px,4.5vw,60px);align-items:start}}
.sva-main{{min-width:0;max-width:720px}}
.sva-aside{{position:sticky;top:24px;display:flex;flex-direction:column;gap:18px}}
@media(max-width:940px){{.sva-grid{{grid-template-columns:1fr;gap:38px}}.sva-aside{{position:static}}.sva-main{{max-width:none}}}}

/* header: peer-review eyebrow + grade chip */
.sva-eyebrow{{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin:0 0 18px}}
.sva-kicker{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:{acc}}}
.sva-grade{{display:inline-flex;align-items:center;gap:6px;font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{on_acc};background:{acc};padding:4px 10px;border-radius:999px}}
.sva-grade::before{{content:"";width:6px;height:6px;border-radius:50%;background:{on_acc}}}
.sva-h1{{font-family:{hf};font-size:clamp(29px,4.4vw,44px);font-weight:800;line-height:1.12;letter-spacing:-.022em;color:{ink};margin:0 0 16px;text-wrap:balance;overflow-wrap:break-word}}
.sva-dek{{font-family:{bf};font-weight:400;font-size:clamp(17px,2vw,20px);line-height:1.55;color:{sub};margin:0 0 24px;text-wrap:pretty}}

/* byline: clinical metadata row */
.sva-byline{{display:flex;align-items:center;gap:13px;padding:14px 0;border-top:1px solid {brd};border-bottom:1px solid {brd};margin:0 0 32px}}
.sva-av{{width:42px;height:42px;border-radius:9px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:14px;color:{on_acc};background:{acc}}}
.sva-by-col{{display:flex;flex-direction:column;gap:3px;min-width:0}}
.sva-by-name{{font-family:{hf};font-weight:700;font-size:14px;color:{ink}}}
.sva-by-meta{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;letter-spacing:.04em;color:{dim};display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.sva-by-meta b{{color:{acc};font-weight:700}}
.sva-by-sep{{color:{brd}}}

/* hero */
.sva-hero{{margin:0 0 34px}}
.sva-hero img{{width:100%;border-radius:12px;border:1px solid {brd};display:block}}
.sva-hero figcaption{{display:flex;align-items:center;gap:9px;font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{dim};margin-top:10px}}
.sva-fig-tag{{font-weight:700;color:{acc}}}

/* body */
.sva-body{{font-size:18px;line-height:1.78;color:{ink}}}
.sva-body p{{margin:0 0 22px;text-wrap:pretty}}
.sva-body a{{color:{acc};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1.5px}}
.sva-body strong{{color:{ink};font-weight:700}}
.sva-body ul,.sva-body ol{{margin:0 0 22px;padding-left:22px}}
.sva-body li{{margin:0 0 9px}}

/* intro = "abstract" panel */
.sva-intro{{position:relative;font-size:18.5px;line-height:1.7;font-weight:450;color:{ink};background:{bg2};border:1px solid {brd};border-left:3px solid {acc};border-radius:0 12px 12px 0;padding:20px 22px 20px 24px;margin:0 0 28px}}
.sva-intro::before{{content:"Abstract";display:block;font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:{acc};margin-bottom:9px}}

/* section headers numbered like a paper */
.sva-h2{{counter-increment:sva-sec;font-family:{hf};font-size:clamp(21px,2.9vw,28px);font-weight:800;line-height:1.2;letter-spacing:-.014em;color:{ink};margin:46px 0 14px;padding-top:22px;border-top:1px solid {brd};display:flex;gap:12px;align-items:baseline}}
.sva-h2::before{{content:counter(sva-sec,decimal-leading-zero);font-family:ui-monospace,'JetBrains Mono',monospace;font-size:13px;font-weight:700;color:{acc};letter-spacing:.04em;flex:0 0 auto;padding-top:3px}}
.sva-body{{counter-reset:sva-sec}}
.sva-body h3{{font-family:{hf};font-size:18px;font-weight:700;color:{ink};margin:28px 0 10px}}

/* verdict / conclusion card */
.sva-verdict{{margin:44px 0 0;padding:24px 26px;background:{bg2};border:1px solid {acc};border-radius:14px;font-size:17px;line-height:1.66;color:{ink};box-shadow:0 0 0 4px rgba(132,204,22,.06)}}
.sva-verdict::before{{content:"The verdict";display:flex;align-items:center;gap:8px;font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10.5px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin-bottom:11px}}

/* sidebar: reviewer card (lab masthead) */
.sva-card{{border:1px solid {brd};border-radius:14px;background:{bg2};overflow:hidden}}
.sva-rev-k{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:{on_acc};background:{acc};padding:8px 16px}}
.sva-rev-body{{padding:16px 18px 18px}}
.sva-rev-top{{display:flex;align-items:center;gap:12px;margin-bottom:11px}}
.sva-rev-av{{width:48px;height:48px;border-radius:10px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:16px;color:{on_acc};background:{acc};border:2px solid {bg}}}
.sva-rev-n{{font-family:{hf};font-size:15px;font-weight:800;color:{ink};margin:0 0 2px;line-height:1.2}}
.sva-rev-r{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;font-weight:600;color:{acc};margin:0}}
.sva-rev-b{{font-size:13px;line-height:1.6;color:{sub};margin:0;padding-top:11px;border-top:1px solid {brd}}}

/* recently reviewed = numbered citation index */
.sva-lib{{border:1px solid {brd};border-radius:14px;background:{bg2};padding:18px}}
.sva-lib-k{{display:flex;align-items:center;gap:8px;font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:{ink};margin:0 0 6px}}
.sva-lib-k::before{{content:"";width:13px;height:13px;border-radius:3px;background:{acc}}}
.sva-lat{{display:grid;grid-template-columns:26px 1fr;gap:10px;padding:12px 0;border-top:1px solid {brd};text-decoration:none;color:inherit;align-items:start}}
.sva-lat:hover .sva-lat-t{{color:{acc}}}
.sva-lat-no{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;font-weight:700;color:{acc};padding-top:2px;text-align:right}}
.sva-lat-t{{font-family:{hf};font-size:13px;font-weight:700;line-height:1.32;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.sva-lat-d{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10px;color:{dim};margin-top:4px;letter-spacing:.02em}}
.sva-viewall{{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:15px;background:{acc};color:{on_acc};font-family:{hf};font-weight:800;font-size:12.5px;letter-spacing:.02em;padding:13px;border-radius:10px;text-decoration:none;transition:opacity .15s}}
.sva-viewall:hover{{opacity:.88}}

/* discussion = "Reader notes" */
.sva-disc{{margin:56px 0 0;padding-top:28px;border-top:2px solid {acc}}}
.sva-disc-head{{display:flex;align-items:baseline;gap:10px;margin:0 0 6px}}
.sva-disc-k{{font-family:{hf};font-size:20px;font-weight:800;color:{ink}}}
.sva-disc-c{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;letter-spacing:.06em;color:{dim}}}
.sva-disc-sub{{font-size:13px;color:{dim};margin:0 0 20px}}
.sva-cm{{display:grid;grid-template-columns:auto 1fr;gap:13px;padding:15px 0;border-bottom:1px solid {brd}}}
.sva-cm-mk{{width:8px;height:8px;border-radius:50%;background:{acc};margin-top:7px;flex:0 0 auto;box-shadow:0 0 0 4px rgba(132,204,22,.12)}}
.sva-cm-top{{display:flex;align-items:baseline;gap:9px;margin-bottom:4px;flex-wrap:wrap}}
.sva-cm-n{{font-family:{hf};font-weight:700;font-size:13.5px;color:{ink}}}
.sva-cm-d{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:10.5px;color:{dim}}}
.sva-cm-t{{font-size:14px;line-height:1.62;color:{sub};margin:0}}
.sva-empty{{font-size:13.5px;color:{dim};padding:12px 0}}
.sva-form{{margin-top:22px;background:{bg2};border:1px solid {brd};border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:11px}}
.sva-form-k{{font-family:ui-monospace,'JetBrains Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{acc};margin:0 0 2px}}
.sva-in,.sva-ta{{background:{bg};border:1px solid {brd};border-radius:10px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none;width:100%}}
.sva-in:focus,.sva-ta:focus{{border-color:{acc};box-shadow:0 0 0 3px rgba(132,204,22,.14)}}
.sva-ta{{min-height:92px;resize:vertical}}
.sva-btn{{align-self:flex-start;background:{acc};color:{on_acc};border:0;border-radius:10px;padding:12px 24px;font-family:{hf};font-weight:800;font-size:13.5px;cursor:pointer;transition:opacity .15s}}
.sva-btn:hover{{opacity:.88}}
@media(max-width:560px){{.sva-h2{{gap:9px}}}}
"""

    author_card = (
        f'<div class="sva-card"><div class="sva-rev-k">Reviewed by</div>'
        f'<div class="sva-rev-body"><div class="sva-rev-top">'
        f'<div class="sva-rev-av">{initials}</div>'
        f'<div><div class="sva-rev-n">{author}</div>'
        f'<div class="sva-rev-r">{ai.get("title","Contributor")}</div></div></div>'
        f'<p class="sva-rev-b">{ai.get("bio","")}</p></div></div>')

    latest = r'''<div class="sva-lib"><div class="sva-lib-k">Recently reviewed</div>
<div id="sva-lib-list"></div>
<a class="sva-viewall" href="../articles/">Browse the evidence library &rarr;</a></div>
<script>(function(){
var L=document.getElementById('sva-lib-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function pad(n){return n<10?('0'+n):(''+n);}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();
a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});
a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p,i){return '<a class="sva-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><span class="sva-lat-no">'+pad(i+1)+'</span><div><p class="sva-lat-t">'+esc(p.title||'Untitled')+'</p><div class="sva-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="sva-disc" id="sva-discussion">'
        '<div class="sva-disc-head"><span class="sva-disc-k">Reader notes</span>'
        '<span class="sva-disc-c" id="sva-cc"></span></div>'
        '<p class="sva-disc-sub">Annotations from readers. Cite a study, flag a dosage, or add context.</p>'
        '<div id="sva-list"></div>'
        '<form class="sva-form" id="sva-form">'
        '<div class="sva-form-k">Add a note</div>'
        '<input class="sva-in" id="sva-name" placeholder="Your name" maxlength="40">'
        '<textarea class="sva-ta" id="sva-msg" placeholder="Share evidence, experience, or a question" maxlength="800"></textarea>'
        '<button class="sva-btn" type="submit">Post note</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('sva-list'),CC=document.getElementById('sva-cc'),F=document.getElementById('sva-form');if(!L)return;"
        "var KEY='svac:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function row(c){return '<div class=\"sva-cm\"><span class=\"sva-cm-mk\"></span><div><div class=\"sva-cm-top\"><span class=\"sva-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"sva-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"sva-cm-t\">'+esc(c.text||'')+'</p></div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"sva-empty\">No notes yet. Be the first to annotate this review.</div>';if(CC)CC.textContent=a.length+(a.length===1?' note':' notes');}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('sva-name').value.trim(),m=document.getElementById('sva-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>")

    body = f"""<div class="sva"><div class="sva-wrap"><div class="sva-grid">
  <main class="sva-main">
  <div class="sva-eyebrow"><span class="sva-kicker">Evidence Review</span>
    <span class="sva-grade">{cat}</span></div>
  <h1 class="sva-h1">{article["title"]}</h1>
  <p class="sva-dek">{article.get("meta_description","")}</p>
  <div class="sva-byline"><div class="sva-av">{initials}</div>
    <div class="sva-by-col"><span class="sva-by-name">{author}</span>
    <span class="sva-by-meta">{article.get("date","")} <span class="sva-by-sep">/</span> <b>{read_min} min read</b></span></div>
  </div>
  {hero}
  <div class="sva-body">
    {_wrap_block(article["intro"], "p", "sva-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="sva-verdict">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="sva-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
