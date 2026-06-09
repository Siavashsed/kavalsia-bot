"""Bespoke article page for CarVerge (prefix: cvg-).

A dark, cinematic automotive editorial. Navy/cyan/blue theme. The layout is a
WIDE main reading column (about 860px max) beside a sticky right rail. Top
padding is deliberately small so the article sits tight under the injected site
header (no large empty gap). The author box is built as a "Driver profile"
spec-sheet card with a DiceBear notionists avatar, a registration-plate style
name strip and a short stat grid. A "Latest from CarVerge" rail pulls the three
most recent posts client-side from articles.json. Discussion uses a
localStorage-backed "Garage talk" comment counter (seeded from comments.json),
matching the simplest working approach used by the other bespoke modules.

Self-contained: only the injected bot data-helpers are used (no `import bot`).
No em dashes anywhere. Unique class prefix `cvg-`, distinct from ece-/aimp-/ttr-.
"""

SITE_ID = "carverge"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "CV"
    av = ("https://api.dicebear.com/9.x/notionists/svg?seed="
          + author.replace(" ", "%20") + "&backgroundColor=0b1d36,071428,0e2040")
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Inter',system-ui,sans-serif"
    mono = "'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace"
    acc = t["accent"]      # #60a5fa cyan-blue
    acc2 = t.get("accent2", acc)   # #2563eb deeper blue
    ink = t["text"]        # #e0eeff
    sub = t.get("text2", t["meta"])  # #9ab8d8
    dim = t["meta"]        # #6494c8
    brd = t["border"]      # #0e2040
    bg = t["bg"]           # #040d1a
    bg2 = t["bg2"]         # #071428
    bg3 = t.get("bg3", bg2)  # #0b1d36
    cat = (article.get("category") or site.get("category") or "Cars, Ownership & Driving")

    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len([w for w in _re.sub(r"<[^>]+>", " ", _txt or "").split() if w])
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        credit = (f'<figcaption class="cvg-cap"><span class="cvg-cap-dot"></span>'
                  f'Photograph: {photographer}</figcaption>') if photographer else ""
        hero = (
            f'<figure class="cvg-hero"><div class="cvg-hero-frame">'
            f'<img src="{image_url}" alt="{article.get("image_alt","")}" loading="lazy" '
            f'onerror="this.style.display=\'none\'"></div>{credit}</figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'cvg-h2')

    css = f"""
.cvg{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.cvg *,.cvg *::before,.cvg *::after{{box-sizing:border-box}}
.cvg-wrap{{max-width:1280px;margin:0 auto;padding:clamp(24px,3.4vw,40px) clamp(18px,4vw,30px) 96px}}
.cvg-grid{{display:grid;grid-template-columns:minmax(0,1fr) 332px;gap:clamp(30px,4vw,58px);align-items:start}}
.cvg-main{{min-width:0;max-width:860px}}
.cvg-aside{{position:sticky;top:22px;display:flex;flex-direction:column;gap:20px}}
@media(max-width:1000px){{.cvg-grid{{grid-template-columns:1fr;gap:42px}}.cvg-aside{{position:static}}.cvg-main{{max-width:none}}}}

/* kicker as a spec-plate */
.cvg-kicker{{display:inline-flex;align-items:center;gap:9px;font-family:{mono};font-size:11px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:{acc};background:rgba(96,165,250,.07);border:1px solid rgba(96,165,250,.26);padding:6px 13px;border-radius:6px;margin:0 0 18px}}
.cvg-kicker::before{{content:"";width:7px;height:7px;border-radius:50%;background:{acc};box-shadow:0 0 9px {acc}}}
.cvg-h1{{font-family:{hf};font-size:clamp(30px,4.8vw,50px);font-weight:800;line-height:1.05;letter-spacing:-.022em;color:#fff;margin:0 0 16px;text-wrap:balance}}
.cvg-dek{{font-family:{bf};font-weight:300;font-size:clamp(17px,2vw,21px);line-height:1.55;color:{sub};margin:0 0 24px;text-wrap:pretty;max-width:64ch}}

/* byline ribbon */
.cvg-byline{{display:flex;align-items:center;gap:13px;padding:14px 0;border-top:1px solid {brd};border-bottom:1px solid {brd};margin:0 0 30px}}
.cvg-by-av{{width:42px;height:42px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:14px;color:#fff;background:linear-gradient(135deg,{acc},{acc2});position:relative;overflow:hidden}}
.cvg-by-av img,.cvg-prof-av img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%}}
.cvg-by-col{{display:flex;flex-direction:column;gap:2px;min-width:0}}
.cvg-by-name{{font-family:{hf};font-weight:700;font-size:14.5px;color:{ink}}}
.cvg-by-meta{{font-family:{mono};font-size:11.5px;color:{dim};letter-spacing:.02em}}
.cvg-by-meta b{{color:{acc};font-weight:600}}

/* hero */
.cvg-hero{{margin:0 0 36px}}
.cvg-hero-frame{{border:1px solid {brd};border-radius:16px;padding:7px;background:{bg2};box-shadow:0 24px 60px -40px rgba(0,0,0,.9)}}
.cvg-hero img{{width:100%;border-radius:11px;display:block}}
.cvg-cap{{display:flex;align-items:center;gap:8px;font-family:{mono};font-size:10.5px;letter-spacing:.08em;color:{dim};margin-top:11px;text-transform:uppercase}}
.cvg-cap-dot{{width:6px;height:6px;border-radius:50%;background:{acc};flex:0 0 auto}}

/* body */
.cvg-body{{font-size:18.5px;line-height:1.8;color:{sub}}}
.cvg-body p{{margin:0 0 22px;text-wrap:pretty}}
.cvg-intro{{font-size:21px;line-height:1.62;font-weight:400;color:{ink};margin:0 0 26px}}
.cvg-intro::first-letter{{float:left;font-family:{hf};font-weight:800;font-size:64px;line-height:.82;padding:6px 14px 0 0;color:{acc}}}
.cvg-body a{{color:{acc};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1.5px;text-decoration-color:rgba(96,165,250,.45)}}
.cvg-body a:hover{{text-decoration-color:{acc}}}
.cvg-body strong{{color:{ink};font-weight:700}}
.cvg-body ul,.cvg-body ol{{margin:0 0 22px;padding-left:22px}}
.cvg-body li{{margin:0 0 9px}}
.cvg-h2{{font-family:{hf};font-size:clamp(22px,3vw,31px);font-weight:800;line-height:1.16;letter-spacing:-.014em;color:#fff;margin:48px 0 15px;padding-left:16px;border-left:3px solid {acc}}}
.cvg-body h3{{font-family:{hf};font-size:19px;font-weight:700;color:{ink};margin:30px 0 10px}}

/* conclusion = "bench verdict" */
.cvg-verdict{{margin:46px 0 0;padding:24px 26px;background:linear-gradient(160deg,rgba(96,165,250,.10),rgba(37,99,235,.04));border:1px solid {brd};border-radius:16px;font-size:17px;line-height:1.66;color:{ink}}}
.cvg-verdict::before{{content:"The verdict";display:block;font-family:{mono};font-size:11px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:{acc};margin-bottom:11px}}

/* author = driver profile / spec sheet */
.cvg-prof{{border:1px solid {brd};border-radius:18px;background:{bg2};overflow:hidden}}
.cvg-prof-top{{display:flex;align-items:center;gap:13px;padding:18px 18px 14px;background:linear-gradient(135deg,rgba(37,99,235,.22),rgba(96,165,250,.06));border-bottom:1px solid {brd}}}
.cvg-prof-av{{width:54px;height:54px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:18px;color:#fff;background:linear-gradient(135deg,{acc},{acc2});border:2px solid {bg3};position:relative;overflow:hidden}}
.cvg-prof-id{{min-width:0}}
.cvg-prof-tag{{font-family:{mono};font-size:9.5px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:{acc};margin:0 0 4px}}
.cvg-prof-n{{font-family:{hf};font-size:17px;font-weight:800;color:#fff;margin:0;line-height:1.1}}
.cvg-prof-plate{{display:inline-flex;align-items:center;gap:6px;margin-top:6px;font-family:{mono};font-size:10.5px;font-weight:700;letter-spacing:.16em;color:{ink};background:{bg};border:1px solid {brd};border-radius:5px;padding:3px 8px}}
.cvg-prof-plate::before{{content:"";width:5px;height:9px;border-radius:1px;background:{acc}}}
.cvg-prof-body{{padding:16px 18px 18px}}
.cvg-prof-r{{font-size:12.5px;font-weight:600;color:{acc};margin:0 0 9px}}
.cvg-prof-b{{font-size:13.5px;line-height:1.62;color:{sub};margin:0 0 15px}}
.cvg-spec{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:{brd};border:1px solid {brd};border-radius:10px;overflow:hidden}}
.cvg-spec-cell{{background:{bg};padding:11px 12px}}
.cvg-spec-k{{font-family:{mono};font-size:9px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:{dim};margin:0 0 3px}}
.cvg-spec-v{{font-family:{hf};font-size:14px;font-weight:800;color:{ink}}}

/* latest rail */
.cvg-latest{{border:1px solid {brd};border-radius:18px;background:{bg2};padding:20px}}
.cvg-latest-k{{font-family:{mono};font-size:11px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin:0 0 14px;display:flex;align-items:center;gap:9px}}
.cvg-latest-k::after{{content:"";flex:1;height:1px;background:{brd}}}
.cvg-lat{{display:grid;grid-template-columns:62px 1fr;gap:13px;padding:13px 0;border-top:1px solid {brd};text-decoration:none;color:inherit;align-items:center}}
.cvg-lat:first-of-type{{border-top:0;padding-top:2px}}
.cvg-lat:hover .cvg-lat-t{{color:{acc}}}
.cvg-lat-img{{width:62px;height:54px;object-fit:cover;border-radius:9px;background:{bg3};display:block}}
.cvg-lat-t{{font-family:{hf};font-size:13.5px;font-weight:700;line-height:1.3;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.cvg-lat-d{{font-family:{mono};font-size:10px;color:{dim};margin-top:5px;letter-spacing:.04em;text-transform:uppercase}}
.cvg-viewall{{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:16px;background:{acc2};color:#fff;font-family:{hf};font-weight:800;font-size:12.5px;letter-spacing:.02em;padding:13px;border-radius:11px;text-decoration:none;transition:filter .15s}}
.cvg-viewall:hover{{filter:brightness(1.12)}}

/* discussion = "Garage talk" */
.cvg-disc{{margin:58px 0 0;padding-top:30px;border-top:1px dashed {brd}}}
.cvg-disc-head{{display:flex;align-items:center;gap:11px;margin:0 0 20px}}
.cvg-disc-k{{font-family:{hf};font-size:21px;font-weight:800;color:#fff}}
.cvg-pill{{font-family:{mono};font-size:11px;font-weight:700;color:{acc};background:rgba(96,165,250,.10);border:1px solid rgba(96,165,250,.26);padding:3px 11px;border-radius:999px}}
.cvg-cm{{display:grid;grid-template-columns:36px 1fr;gap:13px;padding:16px 0;border-bottom:1px solid {brd}}}
.cvg-cm-av{{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:12px;color:#fff;background:{acc2}}}
.cvg-cm-top{{display:flex;align-items:baseline;gap:9px;margin-bottom:4px;flex-wrap:wrap}}
.cvg-cm-n{{font-family:{hf};font-weight:700;font-size:13.5px;color:{ink}}}
.cvg-cm-d{{font-family:{mono};font-size:10.5px;color:{dim}}}
.cvg-cm-t{{font-size:14px;line-height:1.6;color:{sub};margin:0}}
.cvg-empty{{font-size:13.5px;color:{dim};padding:12px 0}}
.cvg-form{{margin-top:22px;background:{bg2};border:1px solid {brd};border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:11px}}
.cvg-form-k{{font-family:{hf};font-size:13px;font-weight:800;color:{ink};margin:0 0 2px}}
.cvg-in,.cvg-ta{{background:{bg};border:1px solid {brd};border-radius:11px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none;width:100%;transition:border-color .15s}}
.cvg-in::placeholder,.cvg-ta::placeholder{{color:{dim}}}
.cvg-in:focus,.cvg-ta:focus{{border-color:{acc};box-shadow:0 0 0 3px rgba(96,165,250,.14)}}
.cvg-ta{{min-height:94px;resize:vertical}}
.cvg-btn{{align-self:flex-start;background:{acc};color:#04121f;border:0;border-radius:11px;padding:12px 26px;font-family:{hf};font-weight:800;font-size:13.5px;cursor:pointer;transition:filter .15s}}
.cvg-btn:hover{{filter:brightness(1.08)}}
@media(max-width:560px){{.cvg-intro::first-letter{{font-size:52px}}.cvg-spec{{grid-template-columns:1fr}}}}
"""

    author_card = (
        f'<aside class="cvg-prof">'
        f'<div class="cvg-prof-top">'
        f'<div class="cvg-prof-av">{initials}<img src="{av}" alt="{author}" loading="lazy" onerror="this.style.display=\'none\'"></div>'
        f'<div class="cvg-prof-id">'
        f'<div class="cvg-prof-tag">Driver profile</div>'
        f'<p class="cvg-prof-n">{author}</p>'
        f'<span class="cvg-prof-plate">CARVERGE</span>'
        f'</div></div>'
        f'<div class="cvg-prof-body">'
        f'<div class="cvg-prof-r">{ai.get("title","Contributor")}</div>'
        f'<p class="cvg-prof-b">{ai.get("bio","")}</p>'
        f'<div class="cvg-spec">'
        f'<div class="cvg-spec-cell"><div class="cvg-spec-k">Beat</div><div class="cvg-spec-v">{cat}</div></div>'
        f'<div class="cvg-spec-cell"><div class="cvg-spec-k">Read time</div><div class="cvg-spec-v">{read_min} min</div></div>'
        f'<div class="cvg-spec-cell"><div class="cvg-spec-k">Bias</div><div class="cvg-spec-v">None for sale</div></div>'
        f'<div class="cvg-spec-cell"><div class="cvg-spec-k">Source</div><div class="cvg-spec-v">Data, cited</div></div>'
        f'</div></div></aside>')

    latest = r'''<div class="cvg-latest"><div class="cvg-latest-k">Latest from CarVerge</div>
<div id="cvg-latest-list"></div>
<a class="cvg-viewall" href="../articles/">All writing &rarr;</a></div>
<script>(function(){
var L=document.getElementById('cvg-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=200&q=50';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();
a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});
a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,3);
if(!a.length){L.innerHTML='<div style="font-size:13px;color:inherit;opacity:.6;padding:8px 0">More analysis publishing soon.</div>';return;}
L.innerHTML=a.map(function(p){return '<a class="cvg-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="cvg-lat-img" loading="lazy" alt="" onerror="this.style.visibility=\'hidden\'" src="'+esc(p.image||FB)+'"><div><p class="cvg-lat-t">'+esc(p.title||'Untitled')+'</p><div class="cvg-lat-d">'+esc(p.kicker||p.category||p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="cvg-disc" id="cvg-discussion">'
        '<div class="cvg-disc-head"><span class="cvg-disc-k">Garage talk</span>'
        '<span class="cvg-pill" id="cvg-cc">0</span></div>'
        '<div id="cvg-list"></div>'
        '<form class="cvg-form" id="cvg-form">'
        '<div class="cvg-form-k">Pull up and weigh in</div>'
        '<input class="cvg-in" id="cvg-name" placeholder="Your name" maxlength="40">'
        '<textarea class="cvg-ta" id="cvg-msg" placeholder="Share your take, data or counterpoint" maxlength="800"></textarea>'
        '<button class="cvg-btn" type="submit">Post comment</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('cvg-list'),CC=document.getElementById('cvg-cc'),F=document.getElementById('cvg-form');if(!L)return;"
        "var KEY='cvgc:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function ini(n){n=String(n||'').trim();if(!n)return'R';var p=n.split(/\\s+/);return((p[0][0]||'')+(p[1]?p[1][0]:'')).toUpperCase();}"
        "function row(c){return '<div class=\"cvg-cm\"><div class=\"cvg-cm-av\">'+esc(ini(c.name))+'</div><div style=\"min-width:0\"><div class=\"cvg-cm-top\"><span class=\"cvg-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"cvg-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"cvg-cm-t\">'+esc(c.text||'')+'</p></div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"cvg-empty\">No comments yet. Be the first to weigh in.</div>';if(CC)CC.textContent=a.length;}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('cvg-name').value.trim(),m=document.getElementById('cvg-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>")

    body = f"""<div class="cvg"><div class="cvg-wrap"><div class="cvg-grid">
  <main class="cvg-main">
  <span class="cvg-kicker">{cat}</span>
  <h1 class="cvg-h1">{article["title"]}</h1>
  <p class="cvg-dek">{article.get("meta_description","")}</p>
  <div class="cvg-byline"><div class="cvg-by-av">{initials}<img src="{av}" alt="" loading="lazy" onerror="this.style.display='none'"></div>
    <div class="cvg-by-col"><span class="cvg-by-name">{author}</span>
    <span class="cvg-by-meta">{article.get("date","")} &middot; <b>{read_min} min read</b></span></div>
  </div>
  {hero}
  <div class="cvg-body">
    {_wrap_block(article["intro"], "p", "cvg-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="cvg-verdict">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="cvg-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
