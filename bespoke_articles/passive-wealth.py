"""Bespoke article-page design for the Passive Wealth site (prefix: pwa-).

A classic, trustworthy long-form WEALTH/finance essay: elegant Lora serif
editorial on warm parchment, deep forest-green accent, calm and premium.
Distinct from the trading-tech tech pilot and the SaaS siblings (different
prefix, proportions, ornamentation, author box and discussion markup).

Layout = readable serif content column + a sticky LEFT-side rail/SIDEBAR with
its own author plaque, a "Latest" 5-card block (client-side fetch of
articles.json) and a "View all articles" button, plus a unique "Letters to the
Editor" discussion section (own markup + client-side comments loader). On
mobile the rail stacks below the article.

Reuses only the injected data helpers; nothing is shared with other sites.
No em dashes anywhere.
"""

SITE_ID = "passive-wealth"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "PW"
    hf = t["heading_font"]                                  # Lora serif
    bf = t.get("body_font") or t.get("font") or "Lora,Georgia,serif"
    acc = t["accent"]                                       # deep forest green
    acc2 = t.get("accent2", acc)
    ink = t["text"]
    sub = t.get("text2", t["meta"])
    dim = t["meta"]
    brd = t["border"]
    bg = t["bg"]
    bg2 = t["bg2"]
    bg3 = t.get("bg3", bg2)
    cat = (article.get("category") or site.get("category") or "Wealth")

    # Read-time computed inline (no _count_words helper).
    _txt = (_wrap_block(article.get("intro", "")) +
            _wrap_block(article.get("intro2", "")) +
            _article_sections(article["sections"], t))
    _words = len([w for w in _txt.replace("<", " <").split() if w and not w.startswith("<")])
    read_min = max(3, _words // 215)

    hero = ""
    if image_url:
        hero = (f'<figure class="pwa-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Illustration: {photographer}</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), "pwa-h2")

    css = f"""
.pwa{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.pwa *,.pwa *::before,.pwa *::after{{box-sizing:border-box}}
.pwa-wrap{{max-width:1180px;margin:0 auto;padding:clamp(30px,5vw,64px) clamp(18px,5vw,32px) 90px}}
.pwa-grid{{display:grid;grid-template-columns:300px minmax(0,1fr);gap:clamp(30px,4.5vw,60px);align-items:start}}
.pwa-rail{{position:sticky;top:26px;display:flex;flex-direction:column;gap:24px;order:0}}
.pwa-main{{min-width:0;max-width:740px;order:1}}
@media(max-width:960px){{.pwa-grid{{grid-template-columns:1fr;gap:40px}}.pwa-rail{{position:static;order:2}}.pwa-main{{max-width:none;order:1}}}}

/* masthead / kicker */
.pwa-kicker{{font-family:{hf};font-size:12px;font-weight:700;letter-spacing:.32em;text-transform:uppercase;color:{acc};margin:0 0 18px;display:flex;align-items:center;gap:12px}}
.pwa-kicker::after{{content:"";flex:1;height:1px;background:{brd}}}
.pwa-h1{{font-family:{hf};font-size:clamp(40px,5.6vw,46px);font-weight:700;line-height:1.1;letter-spacing:-.012em;color:{ink};margin:0 0 20px;text-wrap:balance}}
.pwa-dek{{font-family:{hf};font-style:italic;font-weight:400;font-size:clamp(18px,2.1vw,22px);line-height:1.5;color:{sub};margin:0 0 26px;text-wrap:pretty}}
.pwa-byline{{display:flex;align-items:center;gap:14px;padding:18px 0;border-top:1px solid {brd};border-bottom:1px solid {brd};margin:0 0 34px}}
.pwa-by-rule{{font-family:{hf};font-size:14px;color:{dim};display:flex;align-items:center;gap:10px}}
.pwa-by-name{{font-family:{hf};font-weight:700;color:{ink}}}
.pwa-by-dot{{width:4px;height:4px;border-radius:50%;background:{acc2};display:inline-block}}

/* hero */
.pwa-hero{{margin:0 0 38px}}
.pwa-hero img{{width:100%;border-radius:4px;border:1px solid {brd};display:block}}
.pwa-hero figcaption{{font-family:{hf};font-style:italic;font-size:13px;color:{dim};margin-top:10px;text-align:center}}

/* body */
.pwa-body{{font-size:19px;line-height:1.82;color:{ink}}}
.pwa-body p{{margin:0 0 24px;text-wrap:pretty}}
.pwa-intro{{font-size:21px;line-height:1.7;color:{ink}}}
.pwa-intro::first-letter{{float:left;font-family:{hf};font-weight:700;font-size:74px;line-height:.78;padding:8px 14px 0 0;color:{acc}}}
.pwa-body a{{color:{acc};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}}
.pwa-body a:hover{{color:{acc2}}}
.pwa-body strong{{color:{ink};font-weight:700}}
.pwa-body em{{font-style:italic}}
.pwa-h2{{font-family:{hf};font-size:clamp(25px,3vw,31px);font-weight:700;line-height:1.22;letter-spacing:-.01em;color:{ink};margin:46px 0 16px;position:relative;padding-top:26px}}
.pwa-h2::before{{content:"";position:absolute;top:0;left:0;width:46px;height:2px;background:{acc}}}
.pwa-body h3{{font-family:{hf};font-size:20px;font-weight:700;color:{ink};margin:30px 0 10px}}
.pwa-body blockquote{{margin:30px 0;padding:6px 0 6px 24px;border-left:3px solid {acc};font-family:{hf};font-style:italic;font-size:21px;line-height:1.55;color:{sub}}}
.pwa-concl{{margin:44px 0 0;padding:28px 30px;background:{bg2};border:1px solid {brd};border-radius:5px;position:relative;font-size:18px;line-height:1.72;color:{ink}}}
.pwa-concl::before{{content:"In Closing";display:block;font-family:{hf};font-size:12px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:{acc};margin-bottom:12px}}

/* rail: author plaque */
.pwa-author{{padding:24px;border:1px solid {brd};border-radius:5px;background:{bg2};text-align:center}}
.pwa-author-av{{width:64px;height:64px;border-radius:50%;margin:0 auto 14px;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:22px;color:{bg};background:{acc};border:2px solid {acc2}}}
.pwa-author-k{{font-family:{hf};font-size:11px;font-style:italic;letter-spacing:.06em;color:{dim};margin:0 0 4px}}
.pwa-author-n{{font-family:{hf};font-size:18px;font-weight:700;color:{ink};margin:0 0 3px}}
.pwa-author-r{{font-family:{hf};font-size:13px;color:{acc};margin:0 0 12px}}
.pwa-author-div{{width:36px;height:1px;background:{brd};margin:0 auto 12px}}
.pwa-author-b{{font-size:14px;line-height:1.6;color:{sub};margin:0;text-align:left}}

/* rail: latest */
.pwa-latest{{border:1px solid {brd};border-radius:5px;background:{bg};padding:22px 20px}}
.pwa-latest-k{{font-family:{hf};font-size:12px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:{ink};margin:0 0 6px}}
.pwa-latest-sub{{font-family:{hf};font-style:italic;font-size:12.5px;color:{dim};margin:0 0 14px;padding-bottom:14px;border-bottom:2px solid {acc}}}
.pwa-lat{{display:block;padding:14px 0;border-bottom:1px solid {brd};text-decoration:none;color:inherit}}
.pwa-lat:last-child{{border-bottom:0}}
.pwa-lat-d{{font-family:{hf};font-size:10.5px;font-style:italic;letter-spacing:.04em;color:{acc};margin:0 0 4px}}
.pwa-lat-t{{font-family:{hf};font-size:15px;font-weight:600;line-height:1.34;color:{ink};margin:0;transition:color .15s;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.pwa-lat:hover .pwa-lat-t{{color:{acc}}}
.pwa-viewall{{display:block;text-align:center;margin-top:16px;background:{acc};color:{bg};font-family:{hf};font-weight:700;font-size:13.5px;letter-spacing:.04em;padding:12px;border-radius:4px;text-decoration:none}}
.pwa-viewall:hover{{background:{acc2}}}

/* discussion: Letters to the Editor */
.pwa-disc{{margin:60px 0 0;padding-top:34px;border-top:1px solid {brd}}}
.pwa-disc-k{{font-family:{hf};font-size:26px;font-weight:700;color:{ink};margin:0 0 4px;letter-spacing:-.01em}}
.pwa-disc-sub{{font-family:{hf};font-style:italic;font-size:15px;color:{dim};margin:0 0 24px}}
.pwa-cm{{padding:20px 0;border-bottom:1px solid {brd}}}
.pwa-cm:first-of-type{{border-top:1px solid {brd}}}
.pwa-cm-top{{display:flex;align-items:baseline;gap:10px;margin-bottom:7px}}
.pwa-cm-n{{font-family:{hf};font-weight:700;font-size:15px;color:{ink}}}
.pwa-cm-d{{font-family:{hf};font-style:italic;font-size:12px;color:{dim}}}
.pwa-cm-t{{font-size:15.5px;line-height:1.68;color:{sub};margin:0}}
.pwa-empty{{font-family:{hf};font-style:italic;font-size:15px;color:{dim};padding:14px 0}}
.pwa-cc{{font-family:{hf};font-size:13px;color:{acc};margin:0 0 18px}}
.pwa-form{{margin-top:26px;background:{bg2};border:1px solid {brd};border-radius:5px;padding:22px}}
.pwa-form-k{{font-family:{hf};font-weight:700;font-size:16px;color:{ink};margin:0 0 14px}}
.pwa-in,.pwa-ta{{width:100%;background:{bg};border:1px solid {brd};border-radius:4px;padding:12px 14px;font-family:{bf};font-size:15px;color:{ink};outline:none;margin-bottom:12px}}
.pwa-in:focus,.pwa-ta:focus{{border-color:{acc}}}
.pwa-ta{{min-height:100px;resize:vertical}}
.pwa-btn{{background:{acc};color:{bg};border:0;border-radius:4px;padding:12px 26px;font-family:{hf};font-weight:700;font-size:14px;letter-spacing:.03em;cursor:pointer}}
.pwa-btn:hover{{background:{acc2}}}
"""

    author_card = (
        f'<aside class="pwa-author"><div class="pwa-author-av">{initials}</div>'
        f'<div class="pwa-author-k">By the desk of</div>'
        f'<div class="pwa-author-n">{author}</div>'
        f'<div class="pwa-author-r">{ai.get("title","Contributing Editor")}</div>'
        f'<div class="pwa-author-div"></div>'
        f'<p class="pwa-author-b">{ai.get("bio","")}</p></aside>'
    )

    latest = r'''<div class="pwa-latest"><div class="pwa-latest-k">Latest</div>
<div class="pwa-latest-sub">More from the journal</div>
<div id="pwa-latest-list"></div>
<a class="pwa-viewall" href="../articles/">View all articles</a></div>
<script>(function(){
var L=document.getElementById('pwa-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();
a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});
a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="pwa-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><div class="pwa-lat-d">'+esc(p.date_iso||'')+'</div><p class="pwa-lat-t">'+esc(p.title||'Untitled')+'</p></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = ('<section class="pwa-disc" id="pwa-discussion">'
            '<h2 class="pwa-disc-k">Letters to the Editor</h2>'
            '<p class="pwa-disc-sub">Considered replies from fellow readers.</p>'
            '<p class="pwa-cc" id="pwa-cc"></p>'
            '<div id="pwa-list"></div>'
            '<form class="pwa-form" id="pwa-form">'
            '<div class="pwa-form-k">Write a letter</div>'
            '<input class="pwa-in" id="pwa-name" placeholder="Your name" maxlength="40">'
            '<textarea class="pwa-ta" id="pwa-msg" placeholder="Share your perspective" maxlength="900"></textarea>'
            '<button class="pwa-btn" type="submit">Submit letter</button></form></section>'
            "<script>(function(){"
            "var L=document.getElementById('pwa-list'),CC=document.getElementById('pwa-cc'),F=document.getElementById('pwa-form');if(!L)return;"
            "var KEY='pwac:'+location.pathname;"
            "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
            "function row(c){return '<div class=\"pwa-cm\"><div class=\"pwa-cm-top\"><span class=\"pwa-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"pwa-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"pwa-cm-t\">'+esc(c.text||'')+'</p></div>';}"
            "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"pwa-empty\">No letters yet. Be the first to write in.</div>';if(CC)CC.textContent=a.length?(a.length+(a.length===1?' letter published':' letters published')):'';}"
            "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
            "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
            "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('pwa-name').value.trim(),m=document.getElementById('pwa-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
            "})();</script>")

    body = f"""<div class="pwa"><div class="pwa-wrap"><div class="pwa-grid">
  <aside class="pwa-rail">
  {author_card}
  {latest}
  </aside>
  <main class="pwa-main">
  <div class="pwa-kicker">{cat}</div>
  <h1 class="pwa-h1">{article["title"]}</h1>
  <p class="pwa-dek">{article.get("meta_description","")}</p>
  <div class="pwa-byline">
    <div class="pwa-by-rule"><span class="pwa-by-name">{author}</span>
    <span class="pwa-by-dot"></span><span>{article.get("date","")}</span>
    <span class="pwa-by-dot"></span><span>{read_min} min read</span></div>
  </div>
  {hero}
  <div class="pwa-body">
    {_wrap_block(article["intro"], "p", "pwa-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="pwa-concl">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
</div></div></div>""" + _giscus(site)

    return css, body
