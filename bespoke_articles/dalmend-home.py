"""Bespoke article-page design for dalmend-home (prefix: dha-).

A refined INTERIORS / architecture editorial lookbook: airy, elegant, with
generous whitespace, a capped serif headline, a narrow readable measure and a
light off-white canvas with a warm stone/taupe accent. Layout is a single
content column paired with a sticky left-aligned SIDEBAR (author + Latest +
view-all). Deliberately DIFFERENT from the trading-tech mono/tech pilot and the
SaaS/marketing siblings: no chips, no monospace, no neon. Soft hairline rules,
small-caps labels, thin-bordered "plate" cards.

Note: dalmend-home is a custom-domain site so EVERY link stays relative (../).
The site theme is dark, but this design intentionally renders a light off-white
editorial surface per the brief; only the serif heading font and the warm
accent are taken from the theme. AA contrast: dark ink on off-white throughout.
No em dashes anywhere.

Reuses only the injected data helpers; nothing is shared with other sites.
"""

SITE_ID = "dalmend-home"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "DH"

    # Serif heading font from the theme; body also serif for the editorial vibe.
    hf = t.get("heading_font") or "'Cormorant Garamond',Georgia,serif"
    bf = t.get("font") or hf

    # Light, off-white editorial palette (self-defined, not the dark theme).
    paper = "#f7f4ee"      # off-white canvas
    plate = "#fffdf9"      # slightly lighter card surface
    ink = "#23201b"        # near-black warm ink (AA on paper)
    body_ink = "#3a352d"   # body text
    sub = "#6a6356"        # muted captions / dek
    dim = "#8c8576"        # faint meta
    line = "#e3dccf"       # hairline rule
    line2 = "#d6cdbb"      # stronger hairline
    # Warm stone/taupe accent. Prefer the theme accent if it is warm, else taupe.
    acc = "#9c8a6a"        # stone/taupe
    acc_deep = "#6f5f44"   # deeper taupe for hover/links

    cat = (article.get("category") or site.get("category") or "Interiors")

    # _count_words is defined in bot.py after the bespoke loader runs, so it is
    # not reliably injected. Count read time locally from rendered HTML.
    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len(_re.sub(r"<[^>]+>", " ", _txt or "").split())
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (f'<figure class="dha-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Photograph: {photographer}</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'dha-h2')

    css = f"""
.dha{{background:{paper};color:{body_ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.dha *,.dha *::before,.dha *::after{{box-sizing:border-box}}
.dha-wrap{{max-width:1080px;margin:0 auto;padding:clamp(32px,6vw,68px) clamp(20px,6vw,40px) 96px}}
.dha-grid{{display:grid;grid-template-columns:280px minmax(0,1fr);gap:clamp(34px,5vw,66px);align-items:start}}
.dha-main{{min-width:0;max-width:740px}}
.dha-aside{{position:sticky;top:32px;display:flex;flex-direction:column;gap:30px}}
@media(max-width:900px){{.dha-grid{{grid-template-columns:1fr;gap:48px}}.dha-aside{{position:static;order:2}}.dha-main{{order:1;max-width:none}}}}

/* header */
.dha-kicker{{font-family:{hf};font-size:13px;font-weight:600;letter-spacing:.32em;text-transform:uppercase;color:{acc};margin:0 0 22px}}
.dha-kicker::after{{content:"";display:block;width:48px;height:1px;background:{acc};margin-top:14px}}
.dha-h1{{font-family:{hf};font-size:clamp(40px,6.4vw,48px);font-weight:500;line-height:1.06;letter-spacing:-.01em;color:{ink};margin:0 0 22px;text-wrap:balance}}
.dha-dek{{font-family:{hf};font-weight:400;font-style:italic;font-size:clamp(19px,2.4vw,23px);line-height:1.45;color:{sub};margin:0 0 30px;text-wrap:pretty;max-width:30ch}}
.dha-byline{{display:flex;align-items:center;gap:14px;padding:20px 0;border-top:1px solid {line};border-bottom:1px solid {line};margin:0 0 38px}}
.dha-byline-av{{width:44px;height:44px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:600;font-size:16px;color:{plate};background:{acc}}}
.dha-byline-txt{{display:flex;flex-direction:column;gap:3px;min-width:0}}
.dha-byline-n{{font-family:{hf};font-weight:600;font-size:16px;color:{ink}}}
.dha-byline-m{{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:{dim}}}

/* hero */
.dha-hero{{margin:0 0 44px}}
.dha-hero img{{width:100%;border-radius:2px;display:block}}
.dha-hero figcaption{{font-family:{hf};font-style:italic;font-size:13.5px;letter-spacing:.02em;color:{dim};margin-top:12px}}

/* body */
.dha-body{{font-size:19px;line-height:1.85;color:{body_ink}}}
.dha-body p{{margin:0 0 26px;text-wrap:pretty}}
.dha-intro{{font-size:21px;line-height:1.6;color:{ink};margin:0 0 30px}}
.dha-intro::first-letter{{font-family:{hf};float:left;font-size:64px;line-height:.78;font-weight:500;color:{acc};padding:7px 14px 0 0}}
.dha-body a{{color:{acc_deep};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px;text-decoration-color:{line2}}}
.dha-body a:hover{{text-decoration-color:{acc_deep}}}
.dha-body strong{{color:{ink};font-weight:600}}
.dha-h2{{font-family:{hf};font-size:clamp(26px,3.6vw,33px);font-weight:500;line-height:1.16;letter-spacing:-.005em;color:{ink};margin:54px 0 18px;padding-top:26px;border-top:1px solid {line}}}
.dha-body h3{{font-family:{hf};font-size:21px;font-weight:600;color:{ink};margin:34px 0 12px}}
.dha-body ul,.dha-body ol{{margin:0 0 26px;padding-left:24px}}
.dha-body li{{margin:0 0 11px}}
.dha-body blockquote{{margin:32px 0;padding:4px 0 4px 26px;border-left:2px solid {acc};font-family:{hf};font-style:italic;font-size:23px;line-height:1.45;color:{ink}}}
.dha-concl{{margin:52px 0 0;padding:34px clamp(24px,4vw,40px);background:{plate};border:1px solid {line};border-radius:2px;font-size:18px;line-height:1.72;color:{body_ink}}}
.dha-concl::before{{content:"In closing";display:block;font-family:{hf};font-size:13px;font-weight:600;letter-spacing:.3em;text-transform:uppercase;color:{acc};margin-bottom:14px}}

/* sidebar: author plate */
.dha-author{{background:{plate};border:1px solid {line};border-radius:2px;padding:28px 26px;text-align:center}}
.dha-author-av{{width:66px;height:66px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:600;font-size:24px;color:{plate};background:{acc};margin:0 auto 16px}}
.dha-author-k{{font-family:{hf};font-size:11px;font-weight:600;letter-spacing:.3em;text-transform:uppercase;color:{dim};margin:0 0 8px}}
.dha-author-n{{font-family:{hf};font-size:21px;font-weight:500;color:{ink};margin:0 0 4px}}
.dha-author-r{{font-style:italic;font-size:13.5px;color:{acc};margin:0 0 14px;font-family:{hf}}}
.dha-author-rule{{width:36px;height:1px;background:{line2};margin:0 auto 14px}}
.dha-author-b{{font-size:14px;line-height:1.65;color:{sub};margin:0}}

/* sidebar: latest */
.dha-latest{{background:transparent}}
.dha-latest-k{{font-family:{hf};font-size:12px;font-weight:600;letter-spacing:.3em;text-transform:uppercase;color:{ink};margin:0 0 18px;padding-bottom:12px;border-bottom:1px solid {line2}}}
.dha-lat{{display:block;padding:16px 0;border-bottom:1px solid {line};text-decoration:none;color:inherit}}
.dha-lat-n{{font-family:{hf};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{acc};margin:0 0 6px}}
.dha-lat-t{{font-family:{hf};font-size:16px;font-weight:500;line-height:1.32;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;transition:color .18s}}
.dha-lat:hover .dha-lat-t{{color:{acc_deep}}}
.dha-lat-d{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:{dim};margin-top:7px}}
.dha-viewall{{display:inline-flex;align-items:center;gap:8px;margin-top:20px;font-family:{hf};font-weight:600;font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:{ink};text-decoration:none;border-bottom:1px solid {acc};padding-bottom:4px;transition:color .18s}}
.dha-viewall:hover{{color:{acc_deep}}}

/* discussion */
.dha-disc{{margin:72px 0 0;padding-top:38px;border-top:1px solid {line2}}}
.dha-disc-head{{display:flex;align-items:baseline;gap:14px;margin:0 0 26px}}
.dha-disc-k{{font-family:{hf};font-size:30px;font-weight:500;color:{ink};margin:0}}
.dha-disc-c{{font-family:{hf};font-style:italic;font-size:15px;color:{dim}}}
.dha-cm{{padding:22px 0;border-bottom:1px solid {line}}}
.dha-cm-top{{display:flex;align-items:baseline;gap:12px;margin-bottom:8px}}
.dha-cm-n{{font-family:{hf};font-weight:600;font-size:16px;color:{ink}}}
.dha-cm-d{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:{dim}}}
.dha-cm-t{{font-size:15.5px;line-height:1.68;color:{body_ink};margin:0}}
.dha-empty{{font-family:{hf};font-style:italic;font-size:16px;color:{dim};padding:14px 0}}
.dha-form{{margin-top:30px;display:flex;flex-direction:column;gap:14px;max-width:560px}}
.dha-flabel{{font-family:{hf};font-size:12px;font-weight:600;letter-spacing:.26em;text-transform:uppercase;color:{acc};margin:0}}
.dha-in,.dha-ta{{background:{plate};border:1px solid {line2};border-radius:2px;padding:13px 15px;font-family:{bf};font-size:16px;color:{ink};outline:none;transition:border-color .18s}}
.dha-in:focus,.dha-ta:focus{{border-color:{acc}}}
.dha-ta{{min-height:108px;resize:vertical;line-height:1.6}}
.dha-btn{{align-self:flex-start;background:{ink};color:{paper};border:0;border-radius:2px;padding:13px 30px;font-family:{hf};font-weight:600;font-size:13px;letter-spacing:.16em;text-transform:uppercase;cursor:pointer;transition:background .18s}}
.dha-btn:hover{{background:{acc_deep}}}
"""

    author_card = (
        f'<aside class="dha-author"><div class="dha-author-av">{initials}</div>'
        f'<div class="dha-author-k">Written by</div>'
        f'<div class="dha-author-n">{author}</div>'
        f'<div class="dha-author-r">{ai.get("title","Contributor")}</div>'
        f'<div class="dha-author-rule"></div>'
        f'<p class="dha-author-b">{ai.get("bio","")}</p></aside>')

    latest = r'''<div class="dha-latest"><div class="dha-latest-k">Latest</div>
<div id="dha-latest-list"></div>
<a class="dha-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('dha-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="dha-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><div class="dha-lat-n">'+esc(p.category||'Story')+'</div><p class="dha-lat-t">'+esc(p.title||'Untitled')+'</p><div class="dha-lat-d">'+esc(p.date_iso||'')+'</div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="dha-disc" id="dha-discussion">'
        '<div class="dha-disc-head"><h2 class="dha-disc-k">The Salon</h2>'
        '<span class="dha-disc-c" id="dha-cc"></span></div>'
        '<div id="dha-list"></div>'
        '<form class="dha-form" id="dha-form">'
        '<p class="dha-flabel">Leave a note</p>'
        '<input class="dha-in" id="dha-name" placeholder="Your name" maxlength="40">'
        '<textarea class="dha-ta" id="dha-msg" placeholder="Share your thoughts on this space" maxlength="800"></textarea>'
        '<button class="dha-btn" type="submit">Post note</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('dha-list'),CC=document.getElementById('dha-cc'),F=document.getElementById('dha-form');if(!L)return;"
        "var KEY='dhac:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function row(c){return '<div class=\"dha-cm\"><div class=\"dha-cm-top\"><span class=\"dha-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"dha-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"dha-cm-t\">'+esc(c.text||'')+'</p></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"dha-empty\">No notes yet. Begin the conversation.</div>';if(CC)CC.textContent=a.length?(a.length+(a.length===1?' note':' notes')):'';}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('dha-name').value.trim(),m=document.getElementById('dha-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>")

    body = f"""<div class="dha"><div class="dha-wrap"><div class="dha-grid">
  <aside class="dha-aside">
  {author_card}
  {latest}
  </aside>
  <main class="dha-main">
  <div class="dha-kicker">{cat}</div>
  <h1 class="dha-h1">{article["title"]}</h1>
  <p class="dha-dek">{article.get("meta_description","")}</p>
  <div class="dha-byline"><div class="dha-byline-av">{initials}</div>
    <div class="dha-byline-txt"><span class="dha-byline-n">{author}</span>
    <span class="dha-byline-m">{article.get("date","")} &middot; {read_min} min read</span></div>
  </div>
  {hero}
  <div class="dha-body">
    {_wrap_block(article["intro"], "p", "dha-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="dha-concl">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
</div></div></div>""" + _giscus(site)

    return css, body
