"""Bespoke article-page design for the AI Marketing site (prefix: aimp-).

A modern AI/SaaS tech-blog layout: a readable content column paired with a
sticky right sidebar (author + Latest + view-all). Distinct from the
trading-tech pilot (different prefix, proportions, author box, discussion).
Uses purple as the primary brand accent (from the theme) with a lime
secondary accent for chips, links and rules. Dark theme, mobile-first.

Reuses only the injected data helpers; nothing is shared with other sites.
"""

SITE_ID = "ai-marketing"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "AI"
    av = ("https://api.dicebear.com/9.x/notionists/svg?seed="
          + author.replace(" ", "%20") + "&backgroundColor=ddd6fe,c4b5fd")
    hf = t["heading_font"]
    bf = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif"
    acc = t["accent"]                      # purple
    lime = "#a7b06b"                        # muted secondary (toned down from neon)
    ink = t["text"]
    sub = t.get("text2", t["meta"])
    dim = t["meta"]
    brd = t["border"]
    bg = t["bg"]
    bg2 = t["bg2"]
    surface = t.get("surface") or t.get("bg3") or bg2
    cat = (article.get("category") or site.get("category") or "AI Marketing")

    # _count_words is defined in bot.py AFTER the bespoke loader runs, so it is
    # not reliably injected into this module's namespace. Count words locally.
    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len(_re.sub(r"<[^>]+>", " ", _txt or "").split())
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (f'<figure class="aimp-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Image: {photographer} / Pexels</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'aimp-h2')

    css = f"""
.aimp{{background:{bg};color:{ink};font-family:{bf};-webkit-font-smoothing:antialiased}}
.aimp *,.aimp *::before,.aimp *::after{{box-sizing:border-box}}
.aimp-wrap{{max-width:1140px;margin:0 auto;padding:clamp(26px,5vw,54px) clamp(18px,5vw,32px) 88px}}
.aimp-grid{{display:grid;grid-template-columns:minmax(0,1fr) 312px;gap:clamp(30px,4.4vw,58px);align-items:start}}
.aimp-main{{min-width:0;max-width:720px}}
.aimp-aside{{position:sticky;top:24px;display:flex;flex-direction:column;gap:22px}}
@media(max-width:940px){{.aimp-grid{{grid-template-columns:1fr;gap:40px}}.aimp-aside{{position:static}}.aimp-main{{max-width:none}}}}

/* header */
.aimp-chip{{display:inline-flex;align-items:center;gap:8px;font-family:{hf};font-size:11.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:{lime};background:rgba(167,176,107,.08);border:1px solid rgba(167,176,107,.28);padding:6px 13px;border-radius:999px;margin:0 0 18px}}
.aimp-chip::before{{content:"";width:6px;height:6px;border-radius:50%;background:{lime};box-shadow:0 0 8px {lime}}}
.aimp-h1{{font-family:{hf};font-size:clamp(28px,4.6vw,44px);font-weight:700;line-height:1.1;letter-spacing:-.025em;color:{ink};margin:0 0 18px;text-wrap:balance}}
.aimp-dek{{font-family:{bf};font-weight:400;font-size:clamp(17px,2vw,20px);line-height:1.55;color:{sub};margin:0 0 26px;text-wrap:pretty;max-width:62ch}}
.aimp-byline{{display:flex;align-items:center;gap:12px;padding:0 0 26px;margin:0 0 30px;border-bottom:1px solid {brd}}}
.aimp-byline-av{{width:40px;height:40px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:14px;color:{bg};background:{acc};position:relative;overflow:hidden}}
.aimp-byline-av img,.aimp-author-av img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:50%}}
.aimp-byline-txt{{display:flex;flex-direction:column;gap:2px;min-width:0}}
.aimp-byline-n{{font-family:{hf};font-weight:600;font-size:14px;color:{ink}}}
.aimp-byline-m{{font-size:12px;color:{dim};letter-spacing:.02em}}
.aimp-byline-m b{{color:{lime};font-weight:600}}

/* hero */
.aimp-hero{{margin:0 0 36px}}
.aimp-hero img{{width:100%;border-radius:18px;border:1px solid {brd};display:block;box-shadow:0 16px 40px -28px rgba(0,0,0,.5)}}
.aimp-hero figcaption{{font-size:11px;letter-spacing:.06em;color:{dim};margin-top:10px;text-align:right}}

/* body */
.aimp-body{{font-size:18px;line-height:1.78;color:{sub}}}
.aimp-body p{{margin:0 0 22px;text-wrap:pretty}}
.aimp-intro{{font-size:20px;line-height:1.62;font-weight:500;color:{ink};margin:0 0 28px}}
.aimp-body a{{color:{lime};text-decoration:underline;text-underline-offset:3px;text-decoration-color:rgba(167,176,107,.4)}}
.aimp-body a:hover{{text-decoration-color:{lime}}}
.aimp-body strong{{color:{ink};font-weight:700}}
.aimp-h2{{font-family:{hf};font-size:clamp(21px,2.9vw,29px);font-weight:700;line-height:1.18;letter-spacing:-.015em;color:{ink};margin:46px 0 16px;padding-left:16px;border-left:3px solid {acc}}}
.aimp-body h3{{font-family:{hf};font-size:18px;font-weight:600;color:{ink};margin:28px 0 10px}}
.aimp-body ul,.aimp-body ol{{margin:0 0 22px;padding-left:22px}}
.aimp-body li{{margin:0 0 9px}}
.aimp-concl{{margin:44px 0 0;padding:24px 26px;background:linear-gradient(160deg,rgba(168,85,247,.10),rgba(167,176,107,.05));border:1px solid {brd};border-radius:16px;font-size:17px;line-height:1.66;color:{ink}}}
.aimp-concl::before{{content:"The takeaway";display:block;font-family:{hf};font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{lime};margin-bottom:11px}}

/* sidebar: author */
.aimp-author{{border:1px solid {brd};border-radius:18px;background:{bg2};padding:22px;position:relative;overflow:hidden}}
.aimp-author::before{{content:"";position:absolute;inset:0 0 auto 0;height:54px;background:linear-gradient(135deg,rgba(168,85,247,.22),rgba(167,176,107,.10))}}
.aimp-author-av{{position:relative;width:60px;height:60px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:20px;color:{bg};background:{acc};box-shadow:0 0 0 4px {bg2};margin-bottom:13px;overflow:hidden}}
.aimp-author-k{{font-family:{hf};font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:{dim};margin:0 0 5px}}
.aimp-author-n{{font-family:{hf};font-size:17px;font-weight:700;color:{ink};margin:0 0 2px}}
.aimp-author-r{{font-size:12.5px;color:{lime};margin:0 0 11px;font-weight:500}}
.aimp-author-b{{font-size:13.5px;line-height:1.6;color:{sub};margin:0}}

/* sidebar: latest */
.aimp-latest{{border:1px solid {brd};border-radius:18px;background:{bg2};padding:20px}}
.aimp-latest-k{{font-family:{hf};font-size:11px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:{acc};margin:0 0 14px;display:flex;align-items:center;gap:8px}}
.aimp-latest-k::after{{content:"";flex:1;height:1px;background:{brd}}}
.aimp-lat{{display:grid;grid-template-columns:56px 1fr;gap:12px;padding:11px 0;border-top:1px solid {brd};text-decoration:none;color:inherit}}
.aimp-lat:hover .aimp-lat-t{{color:{lime}}}
.aimp-lat-img{{width:56px;height:48px;object-fit:cover;border-radius:10px;background:{surface};display:block}}
.aimp-lat-t{{font-family:{hf};font-size:13px;font-weight:600;line-height:1.32;color:{ink};margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;transition:color .15s}}
.aimp-lat-d{{font-size:10.5px;color:{dim};margin-top:4px;letter-spacing:.02em}}
.aimp-viewall{{display:block;text-align:center;margin-top:16px;background:{acc};color:{bg};font-family:{hf};font-weight:700;font-size:13px;padding:12px;border-radius:11px;text-decoration:none;transition:opacity .15s}}
.aimp-viewall:hover{{opacity:.9}}

/* discussion */
.aimp-disc{{margin:58px 0 0;padding-top:30px;border-top:1px solid {brd}}}
.aimp-reply{{margin:12px 0 0;padding:12px 15px;background:{bg};border-left:2px solid {acc};border-radius:0 12px 12px 0}}
.aimp-reply-top{{display:flex;align-items:center;gap:8px;margin-bottom:5px;flex-wrap:wrap}}
.aimp-reply-n{{font-family:{hf};font-weight:700;font-size:13px;color:{ink}}}
.aimp-reply-badge{{font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{bg};background:{acc};padding:2px 8px;border-radius:999px}}
.aimp-disc-head{{display:flex;align-items:center;gap:10px;margin:0 0 20px}}
.aimp-disc-k{{font-family:{hf};font-size:20px;font-weight:700;color:{ink}}}
.aimp-disc-c{{font-size:12px;font-weight:600;color:{lime};background:rgba(167,176,107,.10);border:1px solid rgba(167,176,107,.26);padding:3px 10px;border-radius:999px}}
.aimp-cm{{display:grid;grid-template-columns:38px 1fr;gap:13px;padding:16px 0;border-bottom:1px solid {brd}}}
.aimp-cm-av{{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:{hf};font-weight:700;font-size:13px;color:{bg};background:{acc}}}
.aimp-cm-top{{display:flex;align-items:baseline;justify-content:space-between;gap:10px;margin-bottom:5px}}
.aimp-cm-n{{font-family:{hf};font-weight:600;font-size:13.5px;color:{ink}}}
.aimp-cm-d{{font-size:10.5px;color:{dim}}}
.aimp-cm-t{{font-size:14px;line-height:1.6;color:{sub};margin:0}}
.aimp-empty{{font-size:13.5px;color:{dim};padding:12px 0}}
.aimp-form{{margin-top:22px;background:{bg2};border:1px solid {brd};border-radius:16px;padding:18px;display:flex;flex-direction:column;gap:11px}}
.aimp-in,.aimp-ta{{background:{bg};border:1px solid {brd};border-radius:11px;padding:12px 14px;font-family:{bf};font-size:14px;color:{ink};outline:none;transition:border-color .15s}}
.aimp-in:focus,.aimp-ta:focus{{border-color:{acc}}}
.aimp-ta{{min-height:92px;resize:vertical}}
.aimp-btn{{align-self:flex-start;background:{acc};color:{bg};border:0;border-radius:11px;padding:11px 24px;font-family:{hf};font-weight:700;font-size:13.5px;cursor:pointer;transition:opacity .15s}}
.aimp-btn:hover{{opacity:.9}}
"""

    author_card = (
        f'<aside class="aimp-author"><div class="aimp-author-av">{initials}<img src="{av}" alt="{author}" loading="lazy"></div>'
        f'<div class="aimp-author-k">Written by</div>'
        f'<div class="aimp-author-n">{author}</div>'
        f'<div class="aimp-author-r">{ai.get("title","Contributor")}</div>'
        f'<p class="aimp-author-b">{ai.get("bio","")}</p></aside>')

    latest = r'''<div class="aimp-latest"><div class="aimp-latest-k">Latest</div>
<div id="aimp-latest-list"></div>
<a class="aimp-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('aimp-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1677442136019-21780ecad995?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="aimp-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="aimp-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="aimp-lat-t">'+esc(p.title||'Untitled')+'</p><div class="aimp-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    disc = (
        '<section class="aimp-disc" id="aimp-discussion">'
        '<div class="aimp-disc-head"><span class="aimp-disc-k">Join the conversation</span>'
        '<span class="aimp-disc-c" id="aimp-cc">0</span></div>'
        '<div id="aimp-list"></div>'
        '<form class="aimp-form" id="aimp-form">'
        '<input class="aimp-in" id="aimp-name" placeholder="Your name" maxlength="40">'
        '<textarea class="aimp-ta" id="aimp-msg" placeholder="Share your thoughts" maxlength="800"></textarea>'
        '<button class="aimp-btn" type="submit">Post comment</button></form></section>'
        "<script>(function(){"
        "var L=document.getElementById('aimp-list'),CC=document.getElementById('aimp-cc'),F=document.getElementById('aimp-form');if(!L)return;"
        "var KEY='aimpc:'+location.pathname;"
        "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
        "function ini(n){n=(n||'Reader').trim().split(/\\s+/);return((n[0]||' ')[0]+((n[1]||'')[0]||'')).toUpperCase();}"
        "function row(c){var h='<div class=\"aimp-cm\"><div class=\"aimp-cm-av\">'+esc(ini(c.name))+'</div><div style=\"min-width:0\"><div class=\"aimp-cm-top\"><span class=\"aimp-cm-n\">'+esc(c.name||'Reader')+'</span><span class=\"aimp-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"aimp-cm-t\">'+esc(c.text||'')+'</p>';if(c.reply){h+='<div class=\"aimp-reply\"><div class=\"aimp-reply-top\"><span class=\"aimp-reply-n\">'+esc(c.reply.name||'Author')+'</span><span class=\"aimp-reply-badge\">Author</span><span class=\"aimp-cm-d\">'+esc(c.reply.date_display||'')+'</span></div><p class=\"aimp-cm-t\">'+esc(c.reply.text||'')+'</p></div>';}return h+'</div></div>';}"
        "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"aimp-empty\">No comments yet. Start the discussion.</div>';if(CC)CC.textContent=a.length;}"
        "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
        "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
        "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('aimp-name').value.trim(),m=document.getElementById('aimp-msg').value.trim();if(!m)return;mine.push({name:n||'Reader',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
        "})();</script>")

    body = f"""<div class="aimp"><div class="aimp-wrap"><div class="aimp-grid">
  <main class="aimp-main">
  <span class="aimp-chip">{cat}</span>
  <h1 class="aimp-h1">{article["title"]}</h1>
  <p class="aimp-dek">{article.get("meta_description","")}</p>
  <div class="aimp-byline"><div class="aimp-byline-av">{initials}<img src="{av}" alt="" loading="lazy"></div>
    <div class="aimp-byline-txt"><span class="aimp-byline-n">{author}</span>
    <span class="aimp-byline-m">{article.get("date","")} &middot; <b>{read_min} min read</b></span></div>
  </div>
  {hero}
  <div class="aimp-body">
    {_wrap_block(article["intro"], "p", "aimp-intro")}
    {_wrap_block(article.get("intro2",""), "p")}
    {sections}
    <div class="aimp-concl">{article["conclusion"]}</div>
    {_sources_block(article, t)}
  </div>
  {disc}
  </main>
  <aside class="aimp-aside">
  {author_card}
  {latest}
  </aside>
</div></div></div>""" + _giscus(site)

    return css, body
