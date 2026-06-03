"""Bespoke article page for SportIQ Pro (spq-).

A bold, high-energy SPORTS desk: dark stadium-night surface, an angular
"matchday" scoreboard-style kicker, a chunky number-jersey author badge,
diagonal accent stripes, and a punchy uppercase headline capped so it never
overflows. Layout is content + a sticky right SIDEBAR built like a press box:
a unique author "lineup" card, a "Latest Drops" 5-card feed, and a full-width
"View all articles" call. Discussion is framed as "The Locker Room" with a
localStorage post box.

Self-contained: only the injected bot data-helpers are used (no import bot).
No em dashes anywhere. Unique class prefix `spq-`, distinct from the ttr- pilot
and ecommerce/onlinebiz/ai-marketing siblings.
"""

SITE_ID = "sportiq-pro"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "SQ"
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
    bg3 = t.get("bg3", bg2)
    cat = (article.get("category") or site.get("category") or "Sports")

    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len([w for w in _re.sub(r"<[^>]+>", " ", _txt or "").split() if w])
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (
            f'<figure class="spq-hero">'
            f'<img src="{image_url}" alt="{article.get("image_alt","")}" loading="lazy">'
            f'<figcaption>Photo: {photographer} / Pexels</figcaption>'
            f'</figure>'
        )

    sections = _inject_section_breaks(_article_sections(article["sections"], t), "spq-h2")

    css = f"""
.spq{{background:{bg};color:{ink};font-family:{bf}}}
.spq *,.spq *::before,.spq *::after{{box-sizing:border-box}}
.spq-wrap{{max-width:1140px;margin:0 auto;padding:clamp(26px,5vw,54px) clamp(16px,5vw,28px) 84px}}
.spq-grid{{display:grid;grid-template-columns:minmax(0,1fr) 312px;gap:clamp(28px,4vw,54px);align-items:start}}
.spq-main{{min-width:0;max-width:760px}}
.spq-aside{{position:sticky;top:22px;display:flex;flex-direction:column;gap:20px}}
@media(max-width:940px){{.spq-grid{{grid-template-columns:1fr;gap:36px}}.spq-aside{{position:static}}.spq-main{{max-width:none}}}}

/* matchday scoreboard kicker */
.spq-kicker{{display:inline-flex;align-items:center;gap:9px;background:{acc};color:#0a0d12;font-family:{hf};font-weight:800;font-size:11px;letter-spacing:.18em;text-transform:uppercase;padding:7px 13px;border-radius:4px;margin:0 0 16px;transform:skewX(-7deg)}}
.spq-kicker span{{display:inline-block;transform:skewX(7deg)}}
.spq-kicker::before{{content:'';width:7px;height:7px;border-radius:50%;background:#0a0d12;transform:skewX(7deg)}}

.spq-h1{{font-family:{hf};font-size:clamp(30px,5vw,46px);font-weight:800;line-height:1.04;letter-spacing:-.02em;text-transform:uppercase;color:{ink};margin:0 0 18px;text-wrap:balance}}
.spq-dek{{font-family:{hf};font-weight:500;font-size:clamp(16px,2vw,20px);line-height:1.5;color:{sub};margin:0 0 22px;text-wrap:pretty}}

.spq-byline{{display:flex;align-items:center;gap:13px;padding:14px 0;border-top:2px solid {acc};border-bottom:1px solid {brd};margin:0 0 30px}}
.spq-num{{width:44px;height:44px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:15px;color:#0a0d12;background:{acc};border-radius:6px;transform:skewX(-7deg)}}
.spq-num span{{display:inline-block;transform:skewX(7deg)}}
.spq-by-main{{display:flex;flex-direction:column;gap:2px;min-width:0}}
.spq-by-name{{font-family:{hf};font-weight:800;font-size:14px;letter-spacing:.02em;text-transform:uppercase;color:{ink}}}
.spq-by-meta{{font-family:{hf};font-weight:600;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:{dim}}}
.spq-by-meta b{{color:{acc};font-weight:800}}

.spq-hero{{margin:0 0 32px;position:relative}}
.spq-hero img{{width:100%;border-radius:10px;display:block;border:1px solid {brd}}}
.spq-hero figcaption{{font-family:{hf};font-size:10.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:{dim};margin-top:9px}}

.spq-body{{font-size:18px;line-height:1.78;color:{ink}}}
.spq-body p{{margin:0 0 22px;text-wrap:pretty}}
.spq-intro{{font-size:20px;line-height:1.6;font-weight:600;color:{ink};padding:0 0 0 18px;border-left:4px solid {acc};margin:0 0 26px}}
.spq-body a{{color:{acc};text-decoration:underline;text-underline-offset:3px}}
.spq-body strong{{color:{ink};font-weight:800}}
.spq-h2{{font-family:{hf};font-size:clamp(22px,3vw,30px);font-weight:800;line-height:1.12;letter-spacing:-.01em;text-transform:uppercase;color:{ink};margin:44px 0 14px;padding-top:18px;border-top:1px solid {brd};position:relative}}
.spq-h2::after{{content:'';position:absolute;top:-1px;left:0;width:54px;height:3px;background:{acc}}}
.spq-body h3{{font-family:{hf};font-size:18px;font-weight:800;letter-spacing:.01em;color:{ink};margin:26px 0 10px}}
.spq-body ul,.spq-body ol{{margin:0 0 22px;padding-left:22px}}
.spq-body li{{margin:0 0 9px}}

.spq-concl{{margin:40px 0 0;padding:24px 26px;background:{bg2};border:1px solid {brd};border-left:4px solid {acc};border-radius:10px;font-size:17px;line-height:1.66;color:{ink}}}
.spq-concl::before{{content:'Final whistle';display:block;font-family:{hf};font-size:11px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin-bottom:10px}}

/* sidebar: press box */
.spq-card{{border:1px solid {brd};border-radius:12px;background:{bg2};overflow:hidden}}
.spq-card-k{{display:flex;align-items:center;gap:8px;font-family:{hf};font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#0a0d12;background:{acc};padding:9px 15px;margin:0}}
.spq-author-body{{padding:16px 16px 18px;display:flex;flex-direction:column;gap:11px}}
.spq-author-top{{display:flex;align-items:center;gap:13px}}
.spq-author-num{{width:52px;height:52px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:18px;color:#0a0d12;background:{acc};border-radius:8px;transform:skewX(-7deg)}}
.spq-author-num span{{display:inline-block;transform:skewX(7deg)}}
.spq-author-n{{font-family:{hf};font-size:15px;font-weight:800;letter-spacing:.02em;text-transform:uppercase;color:{ink};margin:0}}
.spq-author-r{{font-family:{hf};font-size:12px;font-weight:700;color:{acc};margin:2px 0 0}}
.spq-author-b{{font-size:13.5px;line-height:1.6;color:{sub};margin:0}}

.spq-latest-body{{padding:6px 15px 15px}}
.spq-lat{{display:grid;grid-template-columns:58px 1fr;gap:11px;padding:11px 0;border-bottom:1px solid {brd};text-decoration:none;color:inherit}}
.spq-lat:last-child{{border-bottom:0}}
.spq-lat:hover .spq-lat-t{{color:{acc}}}
.spq-lat-img{{width:58px;height:50px;object-fit:cover;border-radius:6px;background:{bg3};display:block}}
.spq-lat-t{{font-family:{hf};font-size:13px;font-weight:700;line-height:1.3;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.spq-lat-d{{font-family:{hf};font-size:10px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:{dim};margin-top:4px}}
.spq-viewall{{display:block;text-align:center;background:{acc};color:#0a0d12;font-family:{hf};font-weight:800;font-size:12px;letter-spacing:.1em;text-transform:uppercase;padding:13px;text-decoration:none}}
.spq-viewall:hover{{background:{acc2}}}

/* The Locker Room discussion */
.spq-disc{{margin:54px 0 0;padding-top:0;border-top:0}}
.spq-disc-head{{display:flex;align-items:center;gap:12px;background:{acc};color:#0a0d12;padding:11px 16px;border-radius:8px 8px 0 0}}
.spq-disc-k{{font-family:{hf};font-size:15px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:0}}
.spq-disc-c{{font-family:{hf};font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin-left:auto}}
.spq-disc-box{{border:1px solid {brd};border-top:0;border-radius:0 0 10px 10px;padding:6px 18px 18px}}
.spq-cm{{padding:14px 0;border-bottom:1px solid {brd}}}
.spq-cm:last-child{{border-bottom:0}}
.spq-cm-top{{display:flex;align-items:center;gap:9px;margin-bottom:6px}}
.spq-cm-av{{width:26px;height:26px;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:10.5px;color:#0a0d12;background:{acc};border-radius:5px}}
.spq-cm-n{{font-family:{hf};font-weight:800;font-size:13px;letter-spacing:.02em;text-transform:uppercase;color:{ink}}}
.spq-cm-d{{font-family:{hf};font-size:10.5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:{dim};margin-left:auto}}
.spq-cm-t{{font-size:14.5px;line-height:1.6;color:{sub};margin:0}}
.spq-empty{{font-size:13.5px;color:{dim};padding:14px 0}}
.spq-form{{margin-top:18px;display:flex;flex-direction:column;gap:10px}}
.spq-in,.spq-ta{{background:{bg};border:1px solid {brd};border-radius:8px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none}}
.spq-in:focus,.spq-ta:focus{{border-color:{acc}}}
.spq-ta{{min-height:92px;resize:vertical}}
.spq-btn{{align-self:flex-start;background:{acc};color:#0a0d12;border:0;border-radius:8px;padding:12px 26px;font-family:{hf};font-weight:800;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;cursor:pointer}}
.spq-btn:hover{{background:{acc2}}}
"""

    author_card = (
        f'<aside class="spq-card">'
        f'<p class="spq-card-k">On the bench</p>'
        f'<div class="spq-author-body">'
        f'<div class="spq-author-top"><div class="spq-author-num"><span>{initials}</span></div>'
        f'<div><p class="spq-author-n">{author}</p>'
        f'<p class="spq-author-r">{ai.get("title","Sports Writer")}</p></div></div>'
        f'<p class="spq-author-b">{ai.get("bio","")}</p>'
        f'</div></aside>'
    )

    latest = r'''<div class="spq-card"><p class="spq-card-k">Latest Drops</p>
<div class="spq-latest-body" id="spq-latest-list"></div>
<a class="spq-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('spq-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.length?a.map(function(p){return '<a class="spq-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="spq-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="spq-lat-t">'+esc(p.title||'Untitled')+'</p><div class="spq-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join(''):'<div class="spq-empty">No other articles yet.</div>';
}).catch(function(){});
})();</script>'''

    disc = ('<section class="spq-disc" id="spq-discussion">'
            '<div class="spq-disc-head"><p class="spq-disc-k">The Locker Room</p>'
            '<span class="spq-disc-c" id="spq-cc"></span></div>'
            '<div class="spq-disc-box">'
            '<div id="spq-list"></div>'
            '<form class="spq-form" id="spq-form">'
            '<input class="spq-in" id="spq-name" placeholder="Your name" maxlength="40">'
            '<textarea class="spq-ta" id="spq-msg" placeholder="Sound off on this one" maxlength="800"></textarea>'
            '<button class="spq-btn" type="submit">Post take</button></form>'
            '</div></section>'
            "<script>(function(){"
            "var L=document.getElementById('spq-list'),CC=document.getElementById('spq-cc'),F=document.getElementById('spq-form');if(!L)return;"
            "var KEY='spqc:'+location.pathname;"
            "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
            "function ini(n){n=(n||'Fan').trim();var p=n.split(/\\s+/);return((p[0]||'')[0]||'F').toUpperCase()+((p[1]||'')[0]||'').toUpperCase();}"
            "function row(c){return '<div class=\"spq-cm\"><div class=\"spq-cm-top\"><span class=\"spq-cm-av\">'+esc(ini(c.name))+'</span><span class=\"spq-cm-n\">'+esc(c.name||'Fan')+'</span><span class=\"spq-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"spq-cm-t\">'+esc(c.text||'')+'</p></div>';}"
            "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"spq-empty\">Be first off the bench. Drop your take.</div>';if(CC)CC.textContent=a.length+(a.length===1?' take':' takes');}"
            "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
            "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
            "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('spq-name').value.trim(),m=document.getElementById('spq-msg').value.trim();if(!m)return;mine.push({name:n||'Fan',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
            "})();</script>")

    body = f"""<div class="spq"><div class="spq-wrap"><div class="spq-grid">
  <main class="spq-main">
  <div class="spq-kicker"><span>{cat}</span></div>
  <h1 class="spq-h1">{article["title"]}</h1>
  <p class="spq-dek">{article.get("meta_description","")}</p>
  <div class="spq-byline"><div class="spq-num"><span>{initials}</span></div>
    <div class="spq-by-main"><span class="spq-by-name">{author}</span>
    <span class="spq-by-meta">{article.get("date","")} &middot; <b>{read_min} min read</b></span></div>
  </div>
  {hero}
  <div class="spq-body">
    {_wrap_block(article["intro"], "p", "spq-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="spq-concl">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="spq-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
