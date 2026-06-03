"""Bespoke article-page design for the Mochapoo Pets site (prefix: mpa-).

A warm, friendly pet-lifestyle magazine layout: a cosy readable content column
paired with a sticky right sidebar (a rounded author "snuggle" card + a "Fresh
off the leash" Latest block + a view-all button). Everything is soft, rounded
and inviting on a warm cream canvas with a terracotta accent and serif display
headings (Fraunces). Distinct in prefix, proportions, author box, Latest block
and discussion section from the trading-tech pilot and all siblings.

Reuses only the injected data helpers; nothing is shared with other sites.
No em dashes anywhere.
"""

SITE_ID = "mochapoo-pets"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "MP"
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Plus Jakarta Sans','Inter',system-ui,sans-serif"
    acc = t["accent"]                          # warm terracotta
    acc2 = t.get("accent2", acc)               # deeper brown
    ink = t["text"]
    sub = t.get("text2", t["meta"])
    dim = t["meta"]
    brd = t["border"]
    bg = t["bg"]                               # warm cream
    bg2 = t["bg2"]
    surface = t.get("surface") or t.get("bg3") or bg2

    cat = (article.get("category") or site.get("category") or "Pet Life")

    # _count_words is defined in bot.py AFTER the bespoke loader runs, so it is
    # not reliably injected here. Count words locally for the read-time stat.
    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len(_re.sub(r"<[^>]+>", " ", _txt or "").split())
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (f'<figure class="mpa-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Photo: {photographer} / Pexels</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'mpa-h2')

    css = f"""
.mpa{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.mpa *,.mpa *::before,.mpa *::after{{box-sizing:border-box}}
.mpa-wrap{{max-width:1140px;margin:0 auto;padding:clamp(26px,5vw,52px) clamp(18px,5vw,30px) 90px}}
.mpa-grid{{display:grid;grid-template-columns:minmax(0,1fr) 308px;gap:clamp(30px,4.4vw,56px);align-items:start}}
.mpa-main{{min-width:0;max-width:740px}}
.mpa-aside{{position:sticky;top:24px;display:flex;flex-direction:column;gap:22px}}
@media(max-width:940px){{.mpa-grid{{grid-template-columns:1fr;gap:40px}}.mpa-aside{{position:static}}.mpa-main{{max-width:none}}}}

/* header */
.mpa-chip{{display:inline-flex;align-items:center;gap:8px;font-family:{bf};font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{acc2};background:{bg2};border:1px solid {brd};padding:7px 15px;border-radius:999px;margin:0 0 20px}}
.mpa-chip::before{{content:"";width:7px;height:7px;border-radius:50%;background:{acc}}}
.mpa-h1{{font-family:{hf};font-size:clamp(30px,5vw,45px);font-weight:600;line-height:1.08;letter-spacing:-.012em;color:{ink};margin:0 0 18px;text-wrap:balance}}
.mpa-dek{{font-family:{bf};font-weight:400;font-size:clamp(17px,2vw,20px);line-height:1.58;color:{sub};margin:0 0 24px;text-wrap:pretty;max-width:60ch}}
.mpa-byline{{display:flex;align-items:center;gap:13px;padding:16px 0;margin:0 0 30px;border-top:1px solid {brd};border-bottom:1px solid {brd}}}
.mpa-av{{width:44px;height:44px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:600;font-size:15px;color:{bg};background:{acc}}}
.mpa-by-main{{display:flex;flex-direction:column;gap:2px;min-width:0}}
.mpa-by-name{{font-family:{hf};font-weight:600;font-size:15px;color:{ink}}}
.mpa-by-meta{{font-family:{bf};font-size:12.5px;color:{dim}}}

/* hero */
.mpa-hero{{margin:0 0 34px}}
.mpa-hero img{{width:100%;border-radius:22px;display:block;border:1px solid {brd}}}
.mpa-hero figcaption{{font-family:{bf};font-size:12px;color:{dim};margin-top:10px;padding-left:4px}}

/* body */
.mpa-body{{font-size:18px;line-height:1.78;color:{ink}}}
.mpa-body p{{margin:0 0 22px;text-wrap:pretty}}
.mpa-intro{{font-family:{hf};font-size:21px;line-height:1.6;font-weight:500;color:{ink};background:{bg2};border-radius:18px;padding:22px 24px;margin:0 0 28px}}
.mpa-body a{{color:{acc2};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1.5px}}
.mpa-body strong{{color:{ink};font-weight:700}}
.mpa-h2{{font-family:{hf};font-size:clamp(23px,3vw,30px);font-weight:600;line-height:1.18;letter-spacing:-.01em;color:{ink};margin:44px 0 14px;display:flex;align-items:center;gap:12px}}
.mpa-h2::before{{content:"";flex:0 0 auto;width:10px;height:10px;border-radius:50%;background:{acc};box-shadow:0 0 0 4px {bg2}}}
.mpa-body h3{{font-family:{hf};font-size:19px;font-weight:600;color:{ink};margin:28px 0 10px}}
.mpa-concl{{margin:42px 0 0;padding:26px 28px;background:{bg2};border:1px solid {brd};border-radius:22px;font-size:17px;line-height:1.7;color:{ink}}}
.mpa-concl::before{{content:'The takeaway';display:block;font-family:{bf};font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{acc2};margin-bottom:10px}}

/* sidebar: author snuggle card */
.mpa-author{{padding:24px 22px;border:1px solid {brd};border-radius:24px;background:{bg2};text-align:center}}
.mpa-author-av{{width:72px;height:72px;border-radius:50%;margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:600;font-size:24px;color:{bg};background:{acc}}}
.mpa-author-k{{font-family:{bf};font-size:10.5px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:{dim};margin:0 0 6px}}
.mpa-author-n{{font-family:{hf};font-size:18px;font-weight:600;color:{ink};margin:0 0 3px}}
.mpa-author-r{{font-size:13px;color:{acc2};margin:0 0 12px}}
.mpa-author-b{{font-size:13.5px;line-height:1.62;color:{sub};margin:0}}

/* sidebar: Latest block */
.mpa-latest{{border:1px solid {brd};border-radius:24px;background:{surface};padding:20px}}
.mpa-latest-k{{font-family:{hf};font-size:16px;font-weight:600;color:{ink};margin:0 0 4px}}
.mpa-latest-s{{font-family:{bf};font-size:11.5px;color:{dim};margin:0 0 14px}}
.mpa-lat{{display:grid;grid-template-columns:56px 1fr;gap:12px;padding:12px 0;border-top:1px solid {brd};text-decoration:none;color:inherit}}
.mpa-lat:hover .mpa-lat-t{{color:{acc2}}}
.mpa-lat-img{{width:56px;height:56px;object-fit:cover;border-radius:14px;background:{bg2};display:block}}
.mpa-lat-t{{font-family:{hf};font-size:13.5px;font-weight:600;line-height:1.34;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.mpa-lat-d{{font-family:{bf};font-size:10.5px;color:{dim};margin-top:4px}}
.mpa-viewall{{display:block;text-align:center;margin-top:16px;background:{acc};color:{bg};font-family:{hf};font-weight:600;font-size:13.5px;padding:12px;border-radius:999px;text-decoration:none}}
.mpa-viewall:hover{{background:{acc2}}}

/* discussion: the "wag wall" */
.mpa-disc{{margin:54px 0 0;padding:28px;background:{bg2};border:1px solid {brd};border-radius:24px}}
.mpa-disc-head{{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:0 0 6px}}
.mpa-disc-k{{font-family:{hf};font-size:21px;font-weight:600;color:{ink}}}
.mpa-disc-c{{font-family:{bf};font-size:12px;color:{dim}}}
.mpa-disc-s{{font-family:{bf};font-size:13px;color:{sub};margin:0 0 18px}}
.mpa-cm{{display:flex;gap:12px;padding:14px 0;border-top:1px solid {brd}}}
.mpa-cm-av{{width:36px;height:36px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:600;font-size:13px;color:{bg};background:{acc}}}
.mpa-cm-b{{min-width:0;flex:1}}
.mpa-cm-top{{display:flex;justify-content:space-between;gap:10px;margin-bottom:3px}}
.mpa-cm-n{{font-family:{hf};font-weight:600;font-size:14px;color:{ink}}}
.mpa-cm-d{{font-family:{bf};font-size:11px;color:{dim}}}
.mpa-cm-t{{font-size:14px;line-height:1.62;color:{sub};margin:0}}
.mpa-empty{{font-size:13.5px;color:{dim};padding:10px 0}}
.mpa-disc-form{{margin-top:20px;display:flex;flex-direction:column;gap:11px}}
.mpa-in,.mpa-ta{{background:{bg};border:1px solid {brd};border-radius:14px;padding:12px 15px;font-family:{bf};font-size:14px;color:{ink};outline:none}}
.mpa-in:focus,.mpa-ta:focus{{border-color:{acc}}}
.mpa-ta{{min-height:92px;resize:vertical}}
.mpa-btn{{align-self:flex-start;background:{acc};color:{bg};border:0;border-radius:999px;padding:12px 26px;font-family:{hf};font-weight:600;font-size:14px;cursor:pointer}}
.mpa-btn:hover{{background:{acc2}}}
@media(max-width:560px){{.mpa-disc{{padding:22px 18px}}}}
"""

    disc = (
        '<section class="mpa-disc" id="mpa-discussion">'
        '<div class="mpa-disc-head"><span class="mpa-disc-k">The Wag Wall</span>'
        '<span class="mpa-disc-c" id="mpa-cc"></span></div>'
        '<p class="mpa-disc-s">Tell us about your furry friend. Be kind and keep it cosy.</p>'
        '<div id="mpa-list"></div>'
        '<form class="mpa-disc-form" id="mpa-form">'
        '<input class="mpa-in" id="mpa-name" placeholder="Your name" maxlength="40">'
        '<textarea class="mpa-ta" id="mpa-msg" placeholder="Share your story or a tip..." maxlength="800"></textarea>'
        '<button class="mpa-btn" type="submit">Post comment</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('mpa-list'),CC=document.getElementById('mpa-cc'),F=document.getElementById('mpa-form');if(!L)return;"
        "var KEY='mpac:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function ini(n){n=(n||'P').trim();var p=n.split(/\\s+/);return((p[0]||'')[0]||'P').toUpperCase()+((p[1]||'')[0]||'').toUpperCase();}"
        "function row(c){return '<div class=\"mpa-cm\"><div class=\"mpa-cm-av\">'+esc(ini(c.name))+'</div><div class=\"mpa-cm-b\"><div class=\"mpa-cm-top\"><span class=\"mpa-cm-n\">'+esc(c.name||'Friend')+'</span><span class=\"mpa-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"mpa-cm-t\">'+esc(c.text||'')+'</p></div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"mpa-empty\">No paw prints yet. Be the first to say hello!</div>';if(CC)CC.textContent=a.length+(a.length===1?' comment':' comments');}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('mpa-name').value.trim(),m=document.getElementById('mpa-msg').value.trim();if(!m)return;mine.push({name:n||'Friend',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>"
    )

    author_card = (
        f'<aside class="mpa-author"><div class="mpa-author-av">{initials}</div>'
        f'<div class="mpa-author-k">Written by</div>'
        f'<div class="mpa-author-n">{author}</div>'
        f'<div class="mpa-author-r">{ai.get("title","Contributor")}</div>'
        f'<p class="mpa-author-b">{ai.get("bio","")}</p></aside>'
    )

    latest = r'''<div class="mpa-latest"><div class="mpa-latest-k">Fresh off the leash</div>
<p class="mpa-latest-s">More stories from the pack</p>
<div id="mpa-latest-list"></div>
<a class="mpa-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('mpa-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="mpa-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="mpa-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="mpa-lat-t">'+esc(p.title||'Untitled')+'</p><div class="mpa-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    body = f"""<div class="mpa"><div class="mpa-wrap"><div class="mpa-grid">
  <main class="mpa-main">
  <div class="mpa-chip">{cat}</div>
  <h1 class="mpa-h1">{article["title"]}</h1>
  <p class="mpa-dek">{article.get("meta_description","")}</p>
  <div class="mpa-byline"><div class="mpa-av">{initials}</div>
    <div class="mpa-by-main"><span class="mpa-by-name">{author}</span>
    <span class="mpa-by-meta">{article.get("date","")} &middot; {read_min} min read</span></div>
  </div>
  {hero}
  <div class="mpa-body">
    {_wrap_block(article["intro"], "p", "mpa-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="mpa-concl">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="mpa-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)
    return css, body
