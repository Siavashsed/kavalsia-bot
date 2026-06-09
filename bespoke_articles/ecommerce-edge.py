"""Bespoke article page for Ecommerce Edge (ece-).

A sharp DTC commerce/retail editorial: light magazine surface, a tactile
"price-tag" kicker, a framed hero with a caption strip, generous reading
measure, and a sticky right sidebar built like a retail shelf (profile-style
author card + "On the shelf" latest list + a full-width shop-style button).
Discussion is styled as a "Storefront" comment counter with localStorage posts.

Self-contained: only the injected bot data-helpers are used (no import bot).
No em dashes anywhere. Unique class prefix `ece-`, distinct from the ttr- pilot.
"""

SITE_ID = "ecommerce-edge"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "EE"
    av = ("https://api.dicebear.com/9.x/notionists/svg?seed="
          + author.replace(" ", "%20") + "&backgroundColor=ffd5dc,ffdfbf,d1d4f9")
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Inter',system-ui,sans-serif"
    acc = t["accent"]
    acc2 = t.get("accent2", acc)
    ink = t["text"]
    sub = t.get("text2", t["meta"])
    dim = t["meta"]
    brd = t["border"]
    bg = t["bg"]
    bg2 = t["bg2"]
    cat = (article.get("category") or site.get("category") or "Retail")

    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len([w for w in _re.sub(r"<[^>]+>", " ", _txt or "").split() if w])
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (
            f'<figure class="ece-hero">'
            f'<div class="ece-hero-frame"><img src="{image_url}" '
            f'alt="{article.get("image_alt","")}" loading="lazy"></div>'
            f'<figcaption><span class="ece-cap-dot"></span>'
            f'Photograph: {photographer}</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'ece-h2')

    css = f"""
.ece{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.ece *,.ece *::before,.ece *::after{{box-sizing:border-box}}
.ece-wrap{{max-width:1340px;margin:0 auto;padding:clamp(46px,6vw,86px) clamp(18px,4vw,30px) 90px}}
.ece-grid{{display:grid;grid-template-columns:286px minmax(0,1fr) 326px;grid-template-areas:"left main right";gap:clamp(24px,3vw,46px);align-items:start}}
.ece-main{{grid-area:main;min-width:0}}
.ece-aside{{position:sticky;top:24px;display:flex;flex-direction:column;gap:20px}}
.ece-aside-l{{grid-area:left}}
.ece-aside-r{{grid-area:right}}
.ece-aside-r .ece-disc{{margin:0;padding-top:0;border-top:0}}
@media(max-width:1180px){{.ece-grid{{grid-template-columns:1fr;grid-template-areas:"main" "left" "right";gap:38px}}.ece-aside{{position:static}}}}

/* header / kicker as a price-tag */
.ece-tag{{display:inline-flex;align-items:center;gap:8px;font-family:{hf};font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:{acc};padding:6px 13px 6px 12px;border-radius:4px 12px 12px 4px;position:relative;margin:0 0 18px}}
.ece-tag::before{{content:"";width:6px;height:6px;border-radius:50%;background:#fff;box-shadow:0 0 0 3px rgba(255,255,255,.35)}}
.ece-h1{{font-family:{hf};font-size:clamp(30px,4.6vw,44px);font-weight:800;line-height:1.1;letter-spacing:-.022em;color:{ink};margin:0 0 16px;text-wrap:balance}}
.ece-dek{{font-family:{bf};font-weight:400;font-size:clamp(17px,2vw,20px);line-height:1.5;color:{sub};margin:0 0 22px;text-wrap:pretty}}

/* byline ribbon */
.ece-byline{{display:flex;align-items:center;gap:12px;padding:14px 0;border-top:2px solid {ink};border-bottom:1px solid {brd};margin:0 0 30px}}
.ece-av{{width:40px;height:40px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:14px;color:#fff;background:linear-gradient(135deg,{acc},{acc2});position:relative;overflow:hidden}}
.ece-av img,.ece-author-av img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%}}
.ece-by-col{{display:flex;flex-direction:column;gap:2px;min-width:0}}
.ece-by-name{{font-family:{hf};font-weight:700;font-size:14px;color:{ink}}}
.ece-by-meta{{font-size:12px;color:{dim}}}
.ece-by-meta b{{color:{acc};font-weight:700}}

/* hero */
.ece-hero{{margin:0 0 36px}}
.ece-hero-frame{{border:1px solid {brd};border-radius:16px;padding:8px;background:{bg2}}}
.ece-hero img{{width:100%;border-radius:10px;display:block}}
.ece-hero figcaption{{display:flex;align-items:center;gap:8px;font-size:11px;letter-spacing:.04em;color:{dim};margin-top:11px;text-transform:uppercase}}
.ece-cap-dot{{width:7px;height:7px;border-radius:50%;background:{acc};flex:0 0 auto}}

/* body */
.ece-body{{font-size:18px;line-height:1.8;color:{ink}}}
.ece-body p{{margin:0 0 22px;text-wrap:pretty}}
.ece-intro{{font-size:20.5px;line-height:1.6;font-weight:500;color:{ink};margin:0 0 26px}}
.ece-intro::first-letter{{float:left;font-family:{hf};font-weight:800;font-size:62px;line-height:.82;padding:6px 12px 0 0;color:{acc}}}
.ece-body a{{color:{acc2};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1.5px}}
.ece-body strong{{color:{ink};font-weight:700}}
.ece-body ul,.ece-body ol{{margin:0 0 22px;padding-left:22px}}
.ece-body li{{margin:0 0 8px}}
.ece-h2{{font-family:{hf};font-size:clamp(22px,2.9vw,29px);font-weight:800;line-height:1.18;letter-spacing:-.012em;color:{ink};margin:44px 0 14px;padding-left:16px;border-left:4px solid {acc}}}
.ece-body h3{{font-family:{hf};font-size:18px;font-weight:700;color:{ink};margin:28px 0 10px}}

/* takeaway / conclusion as a receipt block */
.ece-receipt{{margin:42px 0 0;padding:24px 26px;background:{bg2};border:1px solid {brd};border-radius:14px;position:relative;font-size:17px;line-height:1.65;color:{ink}}}
.ece-receipt::before{{content:"The bottom line";display:block;font-family:{hf};font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:{acc};margin-bottom:10px}}

/* sidebar author card (profile style, distinct from ttr) */
.ece-card{{border:1px solid {brd};border-radius:16px;background:{bg};overflow:hidden}}
.ece-author{{padding:0}}
.ece-author-top{{height:54px;background:linear-gradient(135deg,{acc},{acc2})}}
.ece-author-body{{padding:0 18px 18px;margin-top:-28px}}
.ece-author-av{{width:56px;height:56px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:19px;color:#fff;background:linear-gradient(135deg,{acc},{acc2});border:3px solid {bg};box-shadow:0 1px 3px rgba(0,0,0,.12);position:relative;overflow:hidden}}
.ece-author-n{{font-family:{hf};font-size:16px;font-weight:800;color:{ink};margin:12px 0 1px}}
.ece-author-r{{font-size:12.5px;font-weight:600;color:{acc};margin:0 0 9px}}
.ece-author-b{{font-size:13px;line-height:1.6;color:{sub};margin:0}}

/* latest = "On the shelf" */
.ece-shelf{{border:1px solid {brd};border-radius:16px;background:{bg};padding:18px}}
.ece-shelf-k{{display:flex;align-items:center;gap:8px;font-family:{hf};font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:{ink};margin:0 0 8px}}
.ece-shelf-k::before{{content:"";width:14px;height:14px;border-radius:3px;background:{acc}}}
.ece-lat{{display:grid;grid-template-columns:56px 1fr;gap:12px;padding:12px 0;border-top:1px solid {brd};text-decoration:none;color:inherit;align-items:center}}
.ece-lat:hover .ece-lat-t{{color:{acc2}}}
.ece-lat-img{{width:56px;height:56px;object-fit:cover;border-radius:10px;background:{bg2};display:block}}
.ece-lat-t{{font-family:{hf};font-size:13px;font-weight:700;line-height:1.3;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.ece-lat-d{{font-size:10.5px;color:{dim};margin-top:4px;letter-spacing:.02em}}
.ece-viewall{{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:15px;background:{ink};color:{bg};font-family:{hf};font-weight:800;font-size:12.5px;letter-spacing:.03em;padding:13px;border-radius:10px;text-decoration:none;transition:background .15s}}
.ece-viewall:hover{{background:{acc}}}

/* discussion = "Storefront" */
.ece-disc{{margin:54px 0 0;padding-top:28px;border-top:1px dashed {brd}}}
.ece-disc-head{{display:flex;align-items:center;gap:10px;margin:0 0 18px}}
.ece-disc-k{{font-family:{hf};font-size:20px;font-weight:800;color:{ink}}}
.ece-pill{{font-family:{hf};font-size:11px;font-weight:800;color:{acc2};background:rgba(249,115,22,.12);padding:4px 10px;border-radius:999px}}
.ece-cm{{display:grid;grid-template-columns:34px 1fr;gap:12px;padding:15px 0;border-bottom:1px solid {brd}}}
.ece-cm-av{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:12px;color:#fff;background:{sub}}}
.ece-cm-top{{display:flex;align-items:baseline;gap:9px;margin-bottom:4px;flex-wrap:wrap}}
.ece-cm-n{{font-family:{hf};font-weight:700;font-size:13.5px;color:{ink}}}
.ece-cm-d{{font-size:10.5px;color:{dim}}}
.ece-cm-t{{font-size:14px;line-height:1.6;color:{sub};margin:0}}
.ece-empty{{font-size:13.5px;color:{dim};padding:10px 0}}
.ece-form{{margin-top:22px;background:{bg2};border:1px solid {brd};border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:11px}}
.ece-form-k{{font-family:{hf};font-size:13px;font-weight:800;color:{ink};margin:0 0 2px}}
.ece-in,.ece-ta{{background:{bg};border:1px solid {brd};border-radius:10px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none;width:100%}}
.ece-in:focus,.ece-ta:focus{{border-color:{acc};box-shadow:0 0 0 3px rgba(249,115,22,.12)}}
.ece-ta{{min-height:92px;resize:vertical}}
.ece-btn{{align-self:flex-start;background:{acc};color:#fff;border:0;border-radius:10px;padding:12px 24px;font-family:{hf};font-weight:800;font-size:13.5px;cursor:pointer;transition:background .15s}}
.ece-btn:hover{{background:{acc2}}}
@media(max-width:560px){{.ece-intro::first-letter{{font-size:52px}}}}
"""

    author_card = (
        f'<div class="ece-card ece-author"><div class="ece-author-top"></div>'
        f'<div class="ece-author-body"><div class="ece-author-av">{initials}<img src="{av}" alt="{author}" loading="lazy"></div>'
        f'<div class="ece-author-n">{author}</div>'
        f'<div class="ece-author-r">{ai.get("title","Contributor")}</div>'
        f'<p class="ece-author-b">{ai.get("bio","")}</p></div></div>')

    latest = r'''<div class="ece-shelf"><div class="ece-shelf-k">On the shelf</div>
<div id="ece-shelf-list"></div>
<a class="ece-viewall" href="../articles/">Browse all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('ece-shelf-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();
a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});
a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="ece-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="ece-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="ece-lat-t">'+esc(p.title||'Untitled')+'</p><div class="ece-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="ece-disc" id="ece-discussion">'
        '<div class="ece-disc-head"><span class="ece-disc-k">Storefront chatter</span>'
        '<span class="ece-pill" id="ece-cc">0</span></div>'
        '<div id="ece-list"></div>'
        '<form class="ece-form" id="ece-form">'
        '<div class="ece-form-k">Join the conversation</div>'
        '<input class="ece-in" id="ece-name" placeholder="Your name" maxlength="40">'
        '<textarea class="ece-ta" id="ece-msg" placeholder="Share your take on this story" maxlength="800"></textarea>'
        '<button class="ece-btn" type="submit">Post comment</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('ece-list'),CC=document.getElementById('ece-cc'),F=document.getElementById('ece-form');if(!L)return;"
        "var KEY='ecec:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function ini(n){n=String(n||'').trim();if(!n)return'R';var p=n.split(/\\s+/);return((p[0][0]||'')+(p[1]?p[1][0]:'')).toUpperCase();}"
        "function row(c){return '<div class=\"ece-cm\"><div class=\"ece-cm-av\">'+esc(ini(c.name))+'</div><div><div class=\"ece-cm-top\"><span class=\"ece-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"ece-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"ece-cm-t\">'+esc(c.text||'')+'</p></div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"ece-empty\">No comments yet. Be the first to weigh in.</div>';if(CC)CC.textContent=a.length;}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('ece-name').value.trim(),m=document.getElementById('ece-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>")

    body = f"""<div class="ece"><div class="ece-wrap"><div class="ece-grid">
  <main class="ece-main">
  <span class="ece-tag">{cat}</span>
  <h1 class="ece-h1">{article["title"]}</h1>
  <p class="ece-dek">{article.get("meta_description","")}</p>
  <div class="ece-byline"><div class="ece-av">{initials}<img src="{av}" alt="" loading="lazy"></div>
    <div class="ece-by-col"><span class="ece-by-name">{author}</span>
    <span class="ece-by-meta">{article.get("date","")} &middot; <b>{read_min} min read</b></span></div>
  </div>
  {hero}
  <div class="ece-body">
    {_wrap_block(article["intro"], "p", "ece-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="ece-receipt">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  </main>
  <aside class="ece-aside ece-aside-l">
  {author_card}
  {latest}
  </aside>
  <aside class="ece-aside ece-aside-r">
  {disc}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
