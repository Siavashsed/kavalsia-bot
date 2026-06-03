"""Bespoke per-site article design for cryptopulse (cpa- prefix).

Refined dark crypto/markets editorial. DISTINCT from the trading-tech terminal
reference: no mono-terminal kicker stack, no orange. Instead a calm magazine
feel with a living "pulse" dot, a thin index rule on section headings, an
italic pull-quote conclusion, and a sidebar styled like a quiet market card.
Layout = content column + sticky sidebar (CSS grid, stacks on mobile).

Self-contained CSS, no em dashes. Reuses only the injected data helpers.
"""

SITE_ID = "cryptopulse"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "CP"
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Space Grotesk',system-ui,sans-serif"
    acc, acc2 = t["accent"], t.get("accent2", t["accent"])
    ink, sub, meta = t["text"], t.get("text2", t["meta"]), t["meta"]
    brd, bg, bg2 = t["border"], t["bg"], t["bg2"]
    bg3 = t.get("bg3", bg2)
    cat = (article.get("category") or site.get("category") or "Markets")

    # read-time computed inline (no _count_words)
    raw = (article.get("intro", "") + " " + article.get("intro2", "") + " " +
           _article_sections(article.get("sections", []), t) + " " +
           article.get("conclusion", ""))
    import re as _re
    words = len(_re.sub(r"<[^>]+>", " ", raw).split())
    read_min = max(2, round(words / 220))

    hero = ""
    if image_url:
        hero = (f'<figure class="cpa-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Image: {photographer} / Pexels</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), "cpa-h2")

    css = f"""
.cpa{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.cpa *,.cpa *::before,.cpa *::after{{box-sizing:border-box}}
.cpa-wrap{{max-width:1160px;margin:0 auto;padding:clamp(26px,5vw,58px) clamp(18px,5vw,30px) 90px}}
.cpa-grid{{display:grid;grid-template-columns:minmax(0,1fr) 312px;gap:clamp(30px,4.5vw,60px);align-items:start}}
.cpa-main{{min-width:0;max-width:740px}}
.cpa-aside{{position:sticky;top:26px;display:flex;flex-direction:column;gap:20px}}
@media(max-width:940px){{.cpa-grid{{grid-template-columns:1fr;gap:36px}}.cpa-aside{{position:static}}.cpa-main{{max-width:none}}}}

/* header / pulse kicker */
.cpa-tag{{display:inline-flex;align-items:center;gap:9px;font-family:{hf};font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:{acc};margin:0 0 18px}}
.cpa-pulse{{width:9px;height:9px;border-radius:50%;background:{acc};box-shadow:0 0 0 0 {acc};animation:cpa-pulse 2.4s ease-out infinite}}
@keyframes cpa-pulse{{0%{{box-shadow:0 0 0 0 rgba(0,230,118,.55)}}70%{{box-shadow:0 0 0 9px rgba(0,230,118,0)}}100%{{box-shadow:0 0 0 0 rgba(0,230,118,0)}}}}
@media(prefers-reduced-motion:reduce){{.cpa-pulse{{animation:none}}}}
.cpa-tag-sep{{color:{meta};font-weight:400;letter-spacing:.08em}}

.cpa-h1{{font-family:{hf};font-size:clamp(30px,5vw,44px);font-weight:700;line-height:1.1;letter-spacing:-.02em;color:{ink};margin:0 0 18px;text-wrap:balance}}
.cpa-dek{{font-family:{hf};font-weight:400;font-size:clamp(16px,2vw,20px);line-height:1.5;color:{sub};margin:0 0 26px;text-wrap:pretty}}

.cpa-byline{{display:flex;align-items:center;gap:13px;padding:16px 0;border-top:1px solid {brd};border-bottom:1px solid {brd};margin:0 0 32px}}
.cpa-av{{width:42px;height:42px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:14px;color:{bg};background:{acc}}}
.cpa-by-name{{font-family:{hf};font-weight:600;font-size:14.5px;color:{ink};display:block}}
.cpa-by-meta{{font-size:12.5px;color:{meta};margin-top:2px;display:block}}
.cpa-by-meta b{{color:{acc};font-weight:600}}

.cpa-hero{{margin:0 0 34px}}
.cpa-hero img{{width:100%;border-radius:14px;border:1px solid {brd};display:block}}
.cpa-hero figcaption{{font-size:11.5px;color:{meta};margin-top:9px;letter-spacing:.02em}}

.cpa-body{{font-size:18px;line-height:1.78;color:{ink}}}
.cpa-body p{{margin:0 0 22px;text-wrap:pretty}}
.cpa-body a{{color:{acc};text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}}
.cpa-body strong{{color:{ink};font-weight:700}}
.cpa-intro{{font-size:20px;line-height:1.62;font-weight:500;color:{ink};margin:0 0 26px}}
.cpa-intro::first-letter{{float:left;font-family:{hf};font-weight:700;font-size:3.1em;line-height:.82;padding:6px 12px 0 0;color:{acc}}}

/* section headings with thin index rule */
.cpa-h2{{position:relative;font-family:{hf};font-size:clamp(20px,2.8vw,27px);font-weight:700;line-height:1.22;letter-spacing:-.01em;color:{ink};margin:46px 0 14px;padding-top:22px}}
.cpa-h2::before{{content:"";position:absolute;top:0;left:0;width:46px;height:2px;background:{acc}}}
.cpa-body h3{{font-family:{hf};font-size:18px;font-weight:600;color:{ink};margin:28px 0 10px}}

/* italic pull-quote conclusion */
.cpa-concl{{margin:44px 0 0;padding:28px 30px;background:linear-gradient(180deg,{bg2},{bg});border:1px solid {brd};border-radius:14px;position:relative}}
.cpa-concl-k{{font-family:{hf};font-size:11px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin:0 0 12px;display:block}}
.cpa-concl p,.cpa-concl{{font-size:18px;line-height:1.62;color:{ink}}}
.cpa-concl p:last-child{{margin-bottom:0}}

/* sidebar: author card styled like a quiet market panel */
.cpa-card{{border:1px solid {brd};border-radius:14px;background:{bg2};padding:20px}}
.cpa-author-top{{display:flex;align-items:center;gap:13px;margin:0 0 13px}}
.cpa-author-av{{width:50px;height:50px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:17px;color:{bg};background:linear-gradient(135deg,{acc},{acc2})}}
.cpa-author-k{{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:{meta};margin:0 0 3px}}
.cpa-author-n{{font-family:{hf};font-size:15.5px;font-weight:700;color:{ink};margin:0}}
.cpa-author-r{{font-size:12px;color:{acc};margin:1px 0 0}}
.cpa-author-b{{font-size:13px;line-height:1.6;color:{sub};margin:0;padding-top:13px;border-top:1px solid {brd}}}

/* latest feed */
.cpa-latest-k{{font-family:{hf};font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin:0 0 6px;display:flex;align-items:center;gap:8px}}
.cpa-latest-k::after{{content:"";flex:1;height:1px;background:{brd}}}
.cpa-lat{{display:grid;grid-template-columns:52px 1fr;gap:11px;padding:12px 0;border-bottom:1px solid {brd};text-decoration:none;color:inherit}}
.cpa-lat:last-of-type{{border-bottom:0}}
.cpa-lat:hover .cpa-lat-t{{color:{acc}}}
.cpa-lat-img{{width:52px;height:46px;object-fit:cover;border-radius:8px;background:{bg3};display:block}}
.cpa-lat-t{{font-family:{hf};font-size:12.5px;font-weight:600;line-height:1.32;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.cpa-lat-d{{font-size:10px;color:{meta};margin-top:4px}}
.cpa-viewall{{display:block;text-align:center;margin-top:15px;border:1px solid {acc};color:{acc};font-family:{hf};font-weight:600;font-size:12.5px;padding:11px;border-radius:9px;text-decoration:none;transition:background .15s,color .15s}}
.cpa-viewall:hover{{background:{acc};color:{bg}}}

/* discussion / comments */
.cpa-disc{{margin:54px 0 0;padding-top:30px;border-top:1px solid {brd}}}
.cpa-disc-head{{display:flex;align-items:center;gap:10px;margin:0 0 6px}}
.cpa-disc-k{{font-family:{hf};font-size:19px;font-weight:700;color:{ink}}}
.cpa-disc-c{{font-size:12px;color:{meta};background:{bg2};border:1px solid {brd};border-radius:20px;padding:3px 11px}}
.cpa-disc-sub{{font-size:13px;color:{meta};margin:0 0 22px}}
.cpa-cm{{display:flex;gap:12px;padding:16px 0;border-bottom:1px solid {brd}}}
.cpa-cm-av{{width:34px;height:34px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:12px;color:{bg};background:{acc2}}}
.cpa-cm-body{{flex:1;min-width:0}}
.cpa-cm-top{{display:flex;align-items:baseline;gap:10px;margin-bottom:4px}}
.cpa-cm-n{{font-family:{hf};font-weight:600;font-size:13.5px;color:{ink}}}
.cpa-cm-d{{font-size:11px;color:{meta}}}
.cpa-cm-t{{font-size:14px;line-height:1.6;color:{sub};margin:0;word-wrap:break-word}}
.cpa-empty{{font-size:14px;color:{meta};padding:14px 0}}
.cpa-form{{margin-top:24px;display:grid;gap:11px;max-width:560px}}
.cpa-in,.cpa-ta{{background:{bg2};border:1px solid {brd};border-radius:10px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none;width:100%}}
.cpa-in::placeholder,.cpa-ta::placeholder{{color:{meta}}}
.cpa-in:focus,.cpa-ta:focus{{border-color:{acc}}}
.cpa-ta{{min-height:96px;resize:vertical}}
.cpa-btn{{justify-self:start;background:{acc};color:{bg};border:0;border-radius:10px;padding:12px 26px;font-family:{hf};font-weight:700;font-size:13.5px;cursor:pointer;transition:background .15s}}
.cpa-btn:hover{{background:{acc2}}}
"""

    author_card = (
        '<aside class="cpa-card">'
        f'<div class="cpa-author-top"><div class="cpa-author-av">{initials}</div>'
        f'<div><div class="cpa-author-k">Author</div>'
        f'<p class="cpa-author-n">{author}</p>'
        f'<p class="cpa-author-r">{ai.get("title","Markets Contributor")}</p></div></div>'
        f'<p class="cpa-author-b">{ai.get("bio","")}</p></aside>'
    )

    latest = r'''<div class="cpa-card"><div class="cpa-latest-k">Latest</div>
<div id="cpa-latest-list"></div>
<a class="cpa-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('cpa-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1640340434855-6084b1f4901c?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();
a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});
a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="cpa-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="cpa-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="cpa-lat-t">'+esc(p.title||'Untitled')+'</p><div class="cpa-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="cpa-disc" id="cpa-discussion">'
        '<div class="cpa-disc-head"><span class="cpa-disc-k">Signal &amp; noise</span>'
        '<span class="cpa-disc-c" id="cpa-cc"></span></div>'
        '<p class="cpa-disc-sub">Trade ideas, not insults. Add your read on the market below.</p>'
        '<div id="cpa-list"></div>'
        '<form class="cpa-form" id="cpa-form">'
        '<input class="cpa-in" id="cpa-name" placeholder="Your name" maxlength="40" autocomplete="off">'
        '<textarea class="cpa-ta" id="cpa-msg" placeholder="Share your take" maxlength="800"></textarea>'
        '<button class="cpa-btn" type="submit">Post</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('cpa-list'),CC=document.getElementById('cpa-cc'),F=document.getElementById('cpa-form');if(!L)return;"
        "var KEY='cpac:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function ini(n){n=(n||'R').trim().split(/\\s+/);return((n[0]||'')[0]||'R').toUpperCase()+((n[1]||'')[0]||'').toUpperCase();}"
        "function row(c){return '<div class=\"cpa-cm\"><div class=\"cpa-cm-av\">'+esc(ini(c.name))+'</div><div class=\"cpa-cm-body\"><div class=\"cpa-cm-top\"><span class=\"cpa-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"cpa-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"cpa-cm-t\">'+esc(c.text||'')+'</p></div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"cpa-empty\">No takes yet. Be the first to call it.</div>';if(CC)CC.textContent=a.length+(a.length===1?' reply':' replies');}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('cpa-name').value.trim(),m=document.getElementById('cpa-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>"
    )

    body = f"""<div class="cpa"><div class="cpa-wrap"><div class="cpa-grid">
  <main class="cpa-main">
  <div class="cpa-tag"><span class="cpa-pulse"></span>{cat}<span class="cpa-tag-sep">/</span>{read_min} min read</div>
  <h1 class="cpa-h1">{article["title"]}</h1>
  <p class="cpa-dek">{article.get("meta_description","")}</p>
  <div class="cpa-byline"><div class="cpa-av">{initials}</div>
    <div><span class="cpa-by-name">{author}</span>
    <span class="cpa-by-meta">{article.get("date","")} &middot; <b>Live coverage</b></span></div>
  </div>
  {hero}
  <div class="cpa-body">
    {_wrap_block(article["intro"], "p", "cpa-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="cpa-concl"><span class="cpa-concl-k">The takeaway</span>{_wrap_block(article["conclusion"], "p")}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="cpa-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
