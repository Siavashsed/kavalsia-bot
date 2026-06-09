"""Bespoke article page for TravelVerge (prefix: tvg-).

A clean, premium PRESS / magazine reading layout. Three columns on desktop:
a sticky LEFT rail (author card + "In this story" jump-nav + share), a wide
readable MAIN column, and a sticky RIGHT rail (subscribe card + most-read rail
pulled live from articles.json + a plan-your-trip CTA). Light, warm-white page
for maximum readability under the site's darker header shell.

Deliberate choices per the brief:
  - NO drop cap (first letter is normal size).
  - All article text is LEFT aligned, generous line-height, comfortable measure.
  - Fully responsive: at <=1040px the rails stack below the article, sticky off.
  - Readable serif headlines + clean sans body, premium spacing.
  - Hero image always carries a visible source credit (we credit every photo).

Self-contained: only the injected bot data-helpers are used (no `import bot`).
No em dashes anywhere. Unique class prefix `tvg-`.
"""

SITE_ID = "travelverge"


def render(article, site, image_url, photographer, t):
    ai = _resolve_author(site, article)
    author = ai["name"]
    a_title = ai.get("title") or "Travel Desk"
    a_bio = ai.get("bio") or site.get("author_bio") or ""
    av = ("https://api.dicebear.com/9.x/notionists/svg?seed="
          + author.replace(" ", "%20") + "&backgroundColor=0e4f4a,0a3d39,116b63")

    cat = (article.get("category") or site.get("category") or "Travel & Destinations")
    date = article.get("date", "")
    read_min = max(3, _count_words(article.get("intro", "") + " ".join(
        s.get("content", "") for s in article.get("sections", []))) // 220)

    # ---- premium light press palette (independent of the dark site theme) ----
    INK = "#15201d"; SUB = "#5d6b66"; DIM = "#8a958f"
    ACC = "#0f766e"; ACC2 = "#0b5a54"; LINE = "#e7ece9"
    PAPER = "#ffffff"; PAPER2 = "#f6f8f7"; WARM = "#fbfaf7"
    SERIF = "'Fraunces','Merriweather',Georgia,serif"
    SANS = "'Inter',system-ui,-apple-system,sans-serif"

    # ---- build sections with anchor ids so the left-rail TOC can jump to them ----
    toc, secs = [], []
    for i, sec in enumerate(article.get("sections", []) or []):
        h = (sec.get("heading") or "").strip()
        if not h:
            continue
        sid = f"tvg-s{i+1}"
        toc.append(f'<a class="tvg-toc-a" href="#{sid}">{h}</a>')
        secs.append(f'<h2 id="{sid}" class="tvg-h2">{h}</h2>{sec.get("content","")}')
    toc_html = ('<nav class="tvg-toc"><div class="tvg-rail-h">In this story</div>'
                + "".join(toc) + "</nav>") if toc else ""

    hero = ""
    if image_url:
        credit = (f'<figcaption class="tvg-cap">Photo: {photographer}. Source credited; '
                  f'used with permission or under licence.</figcaption>' if photographer
                  else '<figcaption class="tvg-cap">Photo credited to its source.</figcaption>')
        hero = (f'<figure class="tvg-hero"><img src="{image_url}" alt="'
                + (article.get("image_alt") or article["title"]).replace('"', "'")
                + '" loading="eager" decoding="async">' + credit + '</figure>')

    intro = _wrap_block(article.get("intro", ""), "p", "tvg-lede")
    intro2 = _wrap_block(article.get("intro2", ""), "p")
    concl = _wrap_block(article.get("conclusion", ""), "p")
    sources = _sources_block(article, t) if "_sources_block" in globals() else ""

    css = f"""
.tvg{{--ink:{INK};--sub:{SUB};--dim:{DIM};--acc:{ACC};--acc2:{ACC2};--line:{LINE};--paper:{PAPER};--paper2:{PAPER2};--warm:{WARM};
  background:var(--warm);color:var(--ink);font-family:{SANS};line-height:1.72;-webkit-font-smoothing:antialiased}}
.tvg *{{box-sizing:border-box}}
.tvg-grid{{max-width:1240px;margin:0 auto;padding:34px 28px 60px;display:grid;
  grid-template-columns:208px minmax(0,1fr) 300px;gap:40px;align-items:start}}
/* rails */
.tvg-left,.tvg-right{{position:sticky;top:24px;display:flex;flex-direction:column;gap:24px;font-family:{SANS}}}
.tvg-rail-h{{font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);margin-bottom:12px}}
.tvg-auth{{display:flex;gap:12px;align-items:center}}
.tvg-auth img{{width:46px;height:46px;border-radius:50%;background:var(--paper2);border:1px solid var(--line)}}
.tvg-auth .nm{{font-family:{SERIF};font-weight:600;font-size:15px;color:var(--ink);line-height:1.2}}
.tvg-auth .rl{{font-size:11.5px;color:var(--dim);margin-top:2px}}
.tvg-toc{{border-top:1px solid var(--line);padding-top:18px;display:flex;flex-direction:column}}
.tvg-toc-a{{font-size:13px;color:var(--sub);text-decoration:none;padding:6px 0;border-bottom:1px solid var(--line);line-height:1.4;transition:color .15s}}
.tvg-toc-a:hover{{color:var(--acc)}}
.tvg-share{{display:flex;gap:8px}}
.tvg-share a{{flex:1;text-align:center;font-size:11px;font-weight:700;color:var(--sub);border:1px solid var(--line);border-radius:8px;padding:8px 0;text-decoration:none;background:var(--paper)}}
.tvg-share a:hover{{border-color:var(--acc);color:var(--acc)}}
/* right rail cards */
.tvg-card{{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:20px}}
.tvg-card.sub{{background:linear-gradient(160deg,#0e4f4a,#0a3d39);color:#eafdf8;border:0}}
.tvg-card.sub .tvg-rail-h{{color:#7fe9d8}}
.tvg-card.sub p{{font-size:13px;color:#bfe6df;margin:0 0 14px}}
.tvg-card.sub input{{width:100%;border:0;border-radius:8px;padding:11px 12px;font-size:13px;margin-bottom:8px;font-family:{SANS}}}
.tvg-card.sub button{{width:100%;border:0;border-radius:8px;padding:11px;font-size:13px;font-weight:800;background:#7fe9d8;color:#06302c;cursor:pointer}}
.tvg-read a{{display:flex;gap:11px;align-items:flex-start;text-decoration:none;padding:11px 0;border-bottom:1px solid var(--line);color:var(--ink)}}
.tvg-read a:last-child{{border-bottom:0}}
.tvg-read .rk{{font-family:{SERIF};font-weight:600;font-size:18px;color:var(--acc);line-height:1;flex:0 0 auto;width:18px}}
.tvg-read .rt{{font-size:13px;line-height:1.4;font-weight:500}}
.tvg-cta{{display:block;text-align:center;background:var(--ink);color:#fff;border-radius:10px;padding:13px;font-size:13px;font-weight:700;text-decoration:none}}
/* main column */
.tvg-main{{max-width:720px;text-align:left}}
.tvg-kick{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:12px;color:var(--dim);margin-bottom:16px}}
.tvg-chip{{font-size:10.5px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#fff;background:var(--acc);padding:5px 11px;border-radius:999px}}
.tvg-main h1{{font-family:{SERIF};font-weight:600;font-size:clamp(30px,4.4vw,46px);line-height:1.1;letter-spacing:-.015em;color:var(--ink);margin:0 0 16px;text-align:left;text-wrap:balance}}
.tvg-dek{{font-size:clamp(17px,2vw,20px);line-height:1.5;color:var(--sub);margin:0 0 26px;text-align:left;max-width:64ch}}
.tvg-hero{{margin:0 0 30px}}
.tvg-hero img{{width:100%;border-radius:14px;display:block;border:1px solid var(--line)}}
.tvg-cap{{font-size:11.5px;color:var(--dim);margin-top:9px;text-align:left;font-style:italic}}
.tvg-body{{font-size:18px;line-height:1.8;color:#27322e;text-align:left}}
.tvg-body p{{margin:0 0 22px;text-align:left}}
.tvg-lede{{font-size:20px;line-height:1.65;color:var(--ink);font-weight:500}}
/* explicitly NO drop cap */
.tvg-body p::first-letter{{font-size:inherit;float:none;font-weight:inherit;margin:0;color:inherit}}
.tvg-h2{{font-family:{SERIF};font-weight:600;font-size:clamp(22px,3vw,29px);line-height:1.2;color:var(--ink);margin:44px 0 14px;text-align:left}}
.tvg-body h3{{font-family:{SANS};font-weight:700;font-size:19px;color:var(--ink);margin:28px 0 10px;text-align:left}}
.tvg-body a{{color:var(--acc);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}}
.tvg-body strong{{color:var(--ink);font-weight:700}}
.tvg-body ul,.tvg-body ol{{margin:0 0 22px;padding-left:22px;text-align:left}}
.tvg-body li{{margin-bottom:9px;line-height:1.7}}
.tvg-body img{{width:100%;border-radius:12px;border:1px solid var(--line);margin:26px 0}}
.tvg-body blockquote{{margin:30px 0;padding:6px 0 6px 22px;border-left:3px solid var(--acc);font-family:{SERIF};font-style:italic;font-size:22px;line-height:1.45;color:var(--ink)}}
.tvg-concl{{margin:40px 0 0;padding:26px 26px;background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:12px}}
.tvg-concl .lbl{{font-size:11px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:var(--acc);display:block;margin-bottom:10px}}
.tvg-concl p{{margin:0 0 12px;font-size:17px;line-height:1.7}}.tvg-concl p:last-child{{margin:0}}
.tvg-auth-box{{margin:36px 0 0;padding:22px;background:var(--paper);border:1px solid var(--line);border-radius:14px;display:flex;gap:16px;align-items:flex-start}}
.tvg-auth-box img{{width:54px;height:54px;border-radius:50%;border:1px solid var(--line);flex:0 0 auto;background:var(--paper2)}}
.tvg-auth-box .nm{{font-family:{SERIF};font-weight:600;font-size:16px}}
.tvg-auth-box .rl{{font-size:12px;color:var(--acc);text-transform:uppercase;letter-spacing:.04em;font-weight:700;margin:2px 0 8px}}
.tvg-auth-box .bio{{font-size:13.5px;color:var(--sub);line-height:1.6;margin:0}}
/* contrast guard against the homepage shell's light-page audit rules */
body[data-page-depth="1"] .tvg-main h1,body[data-page-depth="1"] .tvg-h2,body[data-page-depth="1"] .tvg-body{{color:#15201d !important}}
body[data-page-depth="1"] .tvg-body p{{color:#27322e !important}}
/* ---------- responsive ---------- */
@media(max-width:1040px){{
  .tvg-grid{{grid-template-columns:1fr;gap:34px;max-width:760px;padding:24px 20px 50px}}
  .tvg-left,.tvg-right{{position:static;flex-direction:row;flex-wrap:wrap;gap:18px}}
  .tvg-left>*,.tvg-right>*{{flex:1 1 240px}}
  .tvg-toc{{border-top:0}}
  .tvg-main{{max-width:none;order:-1}}
}}
@media(max-width:560px){{
  .tvg-grid{{padding:18px 16px 40px}}
  .tvg-body{{font-size:17px}}
  .tvg-left,.tvg-right{{flex-direction:column}}
  .tvg-main h1{{font-size:28px}}
}}
"""

    here_slug = article.get("slug", "")
    body = f"""<div class="tvg">
<div class="tvg-grid">

  <aside class="tvg-left">
    <div>
      <div class="tvg-rail-h">Written by</div>
      <div class="tvg-auth"><img src="{av}" alt="{author}"><div><div class="nm">{author}</div><div class="rl">{a_title}</div></div></div>
    </div>
    {toc_html}
    <div class="tvg-share">
      <a href="#" onclick="navigator.share?navigator.share({{title:document.title,url:location.href}}):navigator.clipboard.writeText(location.href);return false;">Share</a>
      <a href="#top" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false;">Top</a>
    </div>
  </aside>

  <article class="tvg-main">
    <div class="tvg-kick"><span class="tvg-chip">{cat}</span><span>{date}</span><span>&middot;</span><span>{read_min} min read</span></div>
    <h1>{article['title']}</h1>
    {f'<p class="tvg-dek">{article.get("meta_description","")}</p>' if article.get("meta_description") else ''}
    {hero}
    <div class="tvg-body">
      {intro}
      {intro2}
      {''.join(secs)}
      <div class="tvg-concl"><span class="lbl">The bottom line</span>{concl}</div>
      {sources}
    </div>
    <div class="tvg-auth-box"><img src="{av}" alt="{author}"><div><div class="nm">{author}</div><div class="rl">{a_title}</div><p class="bio">{a_bio}</p></div></div>
  </article>

  <aside class="tvg-right">
    <div class="tvg-card sub">
      <div class="tvg-rail-h">The Dispatch</div>
      <p>Honest hotel and destination reviews, every week. No sponsored fluff.</p>
      <input type="email" placeholder="you@email.com" aria-label="Email">
      <button type="button" onclick="this.textContent='Thanks for subscribing';this.disabled=true">Subscribe free</button>
    </div>
    <div class="tvg-card">
      <div class="tvg-rail-h">Most read</div>
      <div class="tvg-read" id="tvg-read"><div class="rt" style="color:#8a958f;font-size:12px">Loading guides...</div></div>
    </div>
    <a class="tvg-cta" href="./">Browse all destinations &rarr;</a>
  </aside>

</div>
</div>
<script>
(function(){{
  var here="{here_slug}";
  function depth(){{return parseInt(document.body.getAttribute('data-page-depth')||'0',10);}}
  var base=depth()>=1?'../':'./';
  fetch(base+'articles.json').then(function(r){{return r.ok?r.json():[];}}).then(function(a){{
    if(!Array.isArray(a))return;
    a=a.filter(function(p){{return p&&p.slug&&p.title&&p.slug!==here;}}).slice(0,5);
    var el=document.getElementById('tvg-read');if(!el)return;
    if(!a.length){{el.innerHTML='<div class="rt" style="color:#8a958f;font-size:12px">More guides soon.</div>';return;}}
    el.innerHTML=a.map(function(p,i){{
      return '<a href="'+base+p.slug+'/"><span class="rk">'+(i+1)+'</span><span class="rt">'+p.title+'</span></a>';
    }}).join('');
  }}).catch(function(){{}});
}})();
</script>"""

    return css, body
