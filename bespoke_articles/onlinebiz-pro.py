"""Bespoke article page for OnlineBiz Pro (id: onlinebiz-pro).

A premium "operator dossier" / business-intelligence brief on a dark canvas
with purple + lime accents. Distinct from the trading-tech tech-editorial
sibling: a framed dossier card with a dotted-grid header band, monospace
file-tab metadata, numbered "FILE" section markers, a lime "key takeaway"
brief block, and a right-rail intel panel (author dossier + Latest desk +
view-all). Discussion is a "FIELD NOTES" log. Self-contained CSS, prefix obz-.
No em dashes anywhere.
"""

SITE_ID = "onlinebiz-pro"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    initials = "".join(w[0] for w in author.split()[:2]).upper() or "OB"
    hf = t["heading_font"]
    bf = t.get("body_font") or t.get("font") or "'Inter',system-ui,sans-serif"
    bg, bg2 = t["bg"], t["bg2"]
    surf = t.get("bg3") or t.get("surface") or bg2
    ink, dim, brd = t["text"], t["meta"], t["border"]
    sub = t.get("text2", dim)
    acc = t["accent"]          # purple
    acc2 = t.get("accent2", acc)
    lime = "#c8f135"           # business-intelligence signal accent
    mono = "ui-monospace,'JetBrains Mono','SFMono-Regular',Menlo,monospace"
    cat = (article.get("category") or site.get("category") or "Briefing")

    # Local word-count (bot._count_words is defined after the bespoke loader
    # runs, so it is not reliably injected into this module namespace).
    import re as _re
    _txt = _wrap_block(article.get("intro", "")) + _article_sections(article["sections"], t)
    _words = len(_re.findall(r"\w+", _re.sub(r"<[^>]+>", " ", _txt)))
    read_min = max(3, _words // 220)

    hero = ""
    if image_url:
        hero = (f'<figure class="obz-hero"><img src="{image_url}" '
                f'alt="{article.get("image_alt","")}" loading="lazy">'
                f'<figcaption>Exhibit / {photographer} via Pexels</figcaption></figure>')

    sections = _inject_section_breaks(_article_sections(article["sections"], t), 'obz-h2')

    css = f"""
.obz{{background:{bg};color:{ink};font-family:{bf};
  background-image:radial-gradient(circle at 1px 1px,rgba(255,255,255,.035) 1px,transparent 0);
  background-size:22px 22px}}
.obz *,.obz *::before,.obz *::after{{box-sizing:border-box}}
.obz-wrap{{max-width:1160px;margin:0 auto;padding:clamp(26px,5vw,54px) clamp(16px,5vw,28px) 88px}}

/* file-tab top band */
.obz-tab{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;
  font-family:{mono};font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;
  color:{dim};padding:0 0 14px;margin:0 0 clamp(20px,3vw,30px);
  border-bottom:1px dashed {brd}}}
.obz-tab b{{color:{lime};font-weight:700;letter-spacing:.18em}}
.obz-tab .obz-dot{{width:6px;height:6px;border-radius:50%;background:{acc};display:inline-block}}

.obz-grid{{display:grid;grid-template-columns:minmax(0,1fr) 320px;
  gap:clamp(28px,4vw,56px);align-items:start}}
.obz-main{{min-width:0;max-width:760px}}
.obz-aside{{position:sticky;top:22px;display:flex;flex-direction:column;gap:18px}}

/* dossier header card */
.obz-card{{position:relative;border:1px solid {brd};border-radius:16px;
  background:linear-gradient(180deg,{surf},{bg2});
  padding:clamp(22px,3.5vw,34px);margin:0 0 clamp(26px,3vw,34px);overflow:hidden}}
.obz-card::before{{content:'';position:absolute;inset:0;
  background-image:linear-gradient(90deg,{acc},{acc2});height:3px;border-radius:16px 16px 0 0}}
.obz-kicker{{display:inline-flex;align-items:center;gap:8px;font-family:{mono};
  font-size:10.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
  color:{acc2};margin:0 0 16px}}
.obz-kicker::before{{content:'';width:18px;height:1px;background:{acc2};display:inline-block}}
.obz-h1{{font-family:{hf};font-size:clamp(30px,4.3vw,44px);font-weight:800;
  line-height:1.1;letter-spacing:-.025em;color:{ink};margin:0 0 16px;text-wrap:balance}}
.obz-dek{{font-family:{bf};font-size:clamp(16px,1.9vw,19px);font-weight:400;
  line-height:1.55;color:{sub};margin:0 0 22px;text-wrap:pretty}}
.obz-meta{{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;
  padding-top:18px;border-top:1px dashed {brd}}}
.obz-av{{width:38px;height:38px;border-radius:9px;flex:0 0 auto;display:flex;
  align-items:center;justify-content:center;font-family:{hf};font-weight:800;
  font-size:13px;color:{bg};background:linear-gradient(135deg,{acc2},{lime})}}
.obz-meta-n{{font-family:{hf};font-weight:700;font-size:13.5px;color:{ink}}}
.obz-meta-s{{font-family:{mono};font-size:10.5px;letter-spacing:.06em;color:{dim};margin-top:2px}}
.obz-meta-r{{margin-left:auto;font-family:{mono};font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:{lime};border:1px solid {brd};padding:6px 11px;border-radius:999px}}

.obz-hero{{margin:0 0 clamp(26px,3vw,34px)}}
.obz-hero img{{width:100%;border-radius:14px;border:1px solid {brd};display:block}}
.obz-hero figcaption{{font-family:{mono};font-size:10px;letter-spacing:.14em;
  text-transform:uppercase;color:{dim};margin-top:9px}}

.obz-body{{font-size:18px;line-height:1.78;color:{ink}}}
.obz-body p{{margin:0 0 22px;text-wrap:pretty}}
.obz-body a{{color:{acc2};text-decoration:underline;text-underline-offset:3px}}
.obz-body strong{{color:{ink};font-weight:700}}
.obz-body h3{{font-family:{hf};font-size:18px;font-weight:700;color:{ink};margin:28px 0 10px}}

/* lime brief / key-takeaway intro */
.obz-brief{{position:relative;font-size:18px;line-height:1.62;font-weight:500;
  color:{ink};background:{bg2};border:1px solid {brd};border-left:3px solid {lime};
  border-radius:0 12px 12px 0;padding:18px 20px 18px 22px;margin:0 0 26px}}
.obz-brief::before{{content:'KEY TAKEAWAY';display:block;font-family:{mono};font-size:10px;
  font-weight:700;letter-spacing:.22em;color:{lime};margin-bottom:9px}}

/* numbered FILE section markers */
.obz-h2{{counter-increment:obzsec;font-family:{hf};font-size:clamp(21px,2.8vw,27px);
  font-weight:700;line-height:1.22;letter-spacing:-.01em;color:{ink};
  margin:44px 0 14px;padding-top:22px;border-top:1px solid {brd}}}
.obz-h2::before{{content:'FILE ' counter(obzsec,decimal-leading-zero);display:block;
  font-family:{mono};font-size:10px;font-weight:700;letter-spacing:.22em;
  color:{acc2};margin-bottom:8px}}
.obz-body{{counter-reset:obzsec}}

.obz-concl{{margin:42px 0 0;padding:24px 26px;border:1px solid {brd};border-radius:14px;
  background:linear-gradient(180deg,{surf},{bg2});font-size:17px;line-height:1.66;color:{ink}}}
.obz-concl::before{{content:'OPERATOR VERDICT';display:block;font-family:{mono};font-size:10px;
  font-weight:700;letter-spacing:.22em;color:{lime};margin-bottom:11px}}

/* aside panels */
.obz-panel{{border:1px solid {brd};border-radius:14px;background:{bg2};padding:18px}}
.obz-panel-k{{display:flex;align-items:center;gap:8px;font-family:{mono};font-size:10px;
  font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:{acc2};margin:0 0 14px}}
.obz-panel-k::before{{content:'';width:5px;height:5px;background:{lime};border-radius:50%;display:inline-block}}

/* author dossier */
.obz-author .obz-au-top{{display:flex;align-items:center;gap:12px;margin-bottom:12px}}
.obz-au-av{{width:48px;height:48px;border-radius:11px;flex:0 0 auto;display:flex;
  align-items:center;justify-content:center;font-family:{hf};font-weight:800;font-size:16px;
  color:{bg};background:linear-gradient(135deg,{acc},{lime})}}
.obz-au-n{{font-family:{hf};font-size:15px;font-weight:700;color:{ink};margin:0}}
.obz-au-r{{font-family:{mono};font-size:10.5px;letter-spacing:.04em;color:{acc2};margin:2px 0 0}}
.obz-au-b{{font-size:13px;line-height:1.6;color:{sub};margin:0}}

/* latest desk */
.obz-lat{{display:grid;grid-template-columns:52px 1fr;gap:11px;padding:11px 0;
  border-top:1px solid {brd};text-decoration:none;color:inherit}}
.obz-lat:first-of-type{{border-top:0;padding-top:2px}}
.obz-lat:hover .obz-lat-t{{color:{lime}}}
.obz-lat-img{{width:52px;height:46px;object-fit:cover;border-radius:8px;background:{surf};display:block}}
.obz-lat-t{{font-family:{hf};font-size:12.5px;font-weight:600;line-height:1.3;color:{ink};
  margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
  overflow:hidden;transition:color .15s}}
.obz-lat-d{{font-family:{mono};font-size:9.5px;letter-spacing:.04em;color:{dim};margin-top:4px}}
.obz-viewall{{display:block;text-align:center;margin-top:15px;
  background:linear-gradient(135deg,{acc},{acc2});color:#fff;font-family:{hf};font-weight:700;
  font-size:12.5px;padding:12px;border-radius:10px;text-decoration:none;letter-spacing:.01em}}
.obz-viewall:hover{{filter:brightness(1.08)}}

@media(max-width:940px){{.obz-grid{{grid-template-columns:1fr;gap:34px}}
  .obz-aside{{position:static}}.obz-main{{max-width:none}}}}

/* discussion = FIELD NOTES log */
.obz-disc{{margin:54px 0 0;padding-top:28px;border-top:2px solid {acc}}}
.obz-disc-head{{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:0 0 18px}}
.obz-disc-k{{font-family:{hf};font-size:19px;font-weight:800;color:{ink};letter-spacing:-.01em}}
.obz-disc-k small{{display:block;font-family:{mono};font-size:10px;font-weight:700;
  letter-spacing:.2em;color:{acc2};margin-top:4px}}
.obz-disc-c{{font-family:{mono};font-size:10.5px;letter-spacing:.08em;color:{dim}}}
.obz-cm{{position:relative;padding:14px 0 14px 18px;border-bottom:1px solid {brd}}}
.obz-cm::before{{content:'';position:absolute;left:0;top:18px;width:6px;height:6px;
  border-radius:50%;background:{lime}}}
.obz-cm-top{{display:flex;justify-content:space-between;gap:10px;margin-bottom:5px}}
.obz-cm-n{{font-family:{hf};font-weight:700;font-size:13.5px;color:{ink}}}
.obz-cm-d{{font-family:{mono};font-size:10px;letter-spacing:.04em;color:{dim}}}
.obz-cm-t{{font-size:14px;line-height:1.6;color:{sub};margin:0}}
.obz-empty{{font-family:{mono};font-size:12px;letter-spacing:.04em;color:{dim};padding:10px 0}}
.obz-form{{margin-top:22px;display:flex;flex-direction:column;gap:10px;
  border:1px solid {brd};border-radius:14px;background:{bg2};padding:18px}}
.obz-form-k{{font-family:{mono};font-size:10px;font-weight:700;letter-spacing:.2em;
  text-transform:uppercase;color:{acc2};margin:0 0 2px}}
.obz-in,.obz-ta{{background:{bg};border:1px solid {brd};border-radius:9px;padding:11px 13px;
  font-family:{bf};font-size:14px;color:{ink};outline:none;width:100%}}
.obz-in:focus,.obz-ta:focus{{border-color:{lime}}}
.obz-ta{{min-height:92px;resize:vertical}}
.obz-btn{{align-self:flex-start;background:{lime};color:#0a0a0b;border:0;border-radius:9px;
  padding:11px 24px;font-family:{hf};font-weight:800;font-size:13px;letter-spacing:.02em;cursor:pointer}}
.obz-btn:hover{{filter:brightness(1.05)}}
@media(max-width:560px){{.obz-meta-r{{margin-left:0}}}}
"""

    disc = ('<section class="obz-disc" id="obz-discussion">'
            '<div class="obz-disc-head"><div class="obz-disc-k">Field Notes'
            '<small>READER LOG</small></div>'
            '<span class="obz-disc-c" id="obz-cc"></span></div>'
            '<div id="obz-list"></div>'
            '<form class="obz-form" id="obz-form">'
            '<div class="obz-form-k">Log an entry</div>'
            '<input class="obz-in" id="obz-name" placeholder="Your name / handle" maxlength="40">'
            '<textarea class="obz-ta" id="obz-msg" placeholder="Add a field note to the dossier" maxlength="800"></textarea>'
            '<button class="obz-btn" type="submit">Submit note</button></form></section>'
            "<script>(function(){"
            "var L=document.getElementById('obz-list'),CC=document.getElementById('obz-cc'),F=document.getElementById('obz-form');if(!L)return;"
            "var KEY='obzc:'+location.pathname;"
            "function esc(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',\"'\":'&#39;'})[c];});}"
            "function row(c){return '<div class=\"obz-cm\"><div class=\"obz-cm-top\"><span class=\"obz-cm-n\">'+esc(c.name||'Operator')+'</span><span class=\"obz-cm-d\">'+esc(c.date_display||c.date_iso||'')+'</span></div><p class=\"obz-cm-t\">'+esc(c.text||'')+'</p></div>';}"
            "function render(a){L.innerHTML=a.length?a.map(row).join(''):'<div class=\"obz-empty\">No field notes filed yet. Be first on the record.</div>';if(CC)CC.textContent=a.length+(a.length===1?' note':' notes')+' on file';}"
            "var mine=[];try{mine=JSON.parse(localStorage.getItem(KEY))||[];}catch(e){}var seed=[];"
            "fetch('./comments.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():[];}).then(function(j){seed=Array.isArray(j)?j:[];render(seed.concat(mine));}).catch(function(){render(mine);});"
            "if(F)F.addEventListener('submit',function(e){e.preventDefault();var n=document.getElementById('obz-name').value.trim(),m=document.getElementById('obz-msg').value.trim();if(!m)return;mine.push({name:n||'Operator',text:m,date_display:'just now'});try{localStorage.setItem(KEY,JSON.stringify(mine));}catch(e){}render(seed.concat(mine));F.reset();});"
            "})();</script>")

    author_card = (f'<aside class="obz-panel obz-author">'
                   f'<div class="obz-panel-k">Compiled by</div>'
                   f'<div class="obz-au-top"><div class="obz-au-av">{initials}</div>'
                   f'<div><p class="obz-au-n">{author}</p>'
                   f'<p class="obz-au-r">{ai.get("title","Contributor")}</p></div></div>'
                   f'<p class="obz-au-b">{ai.get("bio","")}</p></aside>')

    latest = r'''<div class="obz-panel"><div class="obz-panel-k">Latest off the desk</div>
<div id="obz-latest-list"></div>
<a class="obz-viewall" href="../articles/">View all articles &rarr;</a></div>
<script>(function(){
var L=document.getElementById('obz-latest-list');if(!L)return;
var here=location.pathname.replace(/\/$/,'').split('/').pop();
var FB='https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=200&q=70';
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];});}
function load(){return fetch('../articles.json',{cache:'no-store'}).then(function(r){if(r.ok)return r.json();return fetch('./articles.json',{cache:'no-store'}).then(function(r2){return r2.ok?r2.json():[];});});}
load().then(function(d){var a=(Array.isArray(d)?d:[]).slice();a.sort(function(x,y){return(''+(y.date_iso||'')).localeCompare(''+(x.date_iso||''));});a=a.filter(function(p){return (p.slug||'')!==here;}).slice(0,5);
L.innerHTML=a.map(function(p){return '<a class="obz-lat" href="../'+encodeURIComponent(p.slug||'')+'/"><img class="obz-lat-img" loading="lazy" alt="" src="'+esc(p.image||FB)+'"><div><p class="obz-lat-t">'+esc(p.title||'Untitled')+'</p><div class="obz-lat-d">'+esc(p.date_iso||'')+'</div></div></a>';}).join('');
}).catch(function(){});
})();</script>'''

    body = f"""<div class="obz"><div class="obz-wrap">
  <div class="obz-tab"><b>OnlineBiz Pro</b><span class="obz-dot"></span>
    <span>Operator Dossier</span><span class="obz-dot"></span>
    <span>Ref {article.get("date_iso","")}</span><span class="obz-dot"></span>
    <span>{read_min} min read</span></div>
  <div class="obz-grid">
  <main class="obz-main">
    <div class="obz-card">
      <div class="obz-kicker">{cat}</div>
      <h1 class="obz-h1">{article["title"]}</h1>
      <p class="obz-dek">{article.get("meta_description","")}</p>
      <div class="obz-meta"><div class="obz-av">{initials}</div>
        <div><div class="obz-meta-n">{author}</div>
        <div class="obz-meta-s">{article.get("date","")}</div></div>
        <span class="obz-meta-r">Briefing</span>
      </div>
    </div>
    {hero}
    <div class="obz-body">
      {_wrap_block(article["intro"], "p", "obz-brief")}
      {_wrap_block(article.get("intro2",""), "p")}
      {sections}
      <div class="obz-concl">{article["conclusion"]}</div>
      {_sources_block(article, t)}
    </div>
    {disc}
  </main>
  <aside class="obz-aside">
    {author_card}
    {latest}
  </aside>
  </div>
</div></div>""" + _giscus(site)

    return css, body
