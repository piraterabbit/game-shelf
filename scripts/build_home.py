import json, html, sys
root = sys.argv[1]
games = json.load(open(f"{root}/games.json", encoding="utf8"))
games.sort(key=lambda g: g["title"].lower())
n3 = sum(g["tag"] == "3D" for g in games)
n2 = len(games) - n3
e = html.escape

COLORS = ["#ff9f1c", "#ffd60a", "#7bd63a", "#3fa9f5", "#c06cf2", "#ff5a4f"]   # classic cartridge-label colours
cards = "\n".join(
    f'''      <a class="shot" href="{g["slug"]}/" data-tag="{g["tag"]}" data-title="{e(g["title"].lower())}" style="--c:{COLORS[i % len(COLORS)]}">
        <span class="lab"><span>Game Shelf</span><span>GS-26{i + 1:02d}</span></span>
        <span class="name">{e(g["title"])}</span>
        <span class="stripes" aria-hidden="true"><i></i><i></i><i></i><i></i></span>
        <span class="thumb"><img src="thumbs/{g["slug"]}.jpg" alt="" loading="lazy" width="960" height="600"></span>
        <span class="foot"><span>Game Program</span><span class="tag">{g["tag"]}</span></span>
      </a>'''
    for i, g in enumerate(games)
)

page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Game Shelf</title>
<style>
:root{{--r-card:20px;--bg:#fff;--fg:#0e1330;--mut:#6b7085;--line:#e7e8ee;--chip:#f3f3f6;--ink:#0e1330;--ink-fg:#fff;--acc:#ffb84d;color-scheme:light}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.45 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}}
a{{color:inherit;text-decoration:none}}
.wrap{{width:100%;margin:0;padding:0 clamp(16px,4vw,64px)}}
header.top{{display:grid;grid-template-columns:1fr;gap:clamp(24px,5vw,72px);padding:clamp(24px,4vw,40px) 0 clamp(28px,4vw,48px)}}
.avatar{{width:64px;height:64px;border-radius:50%;background:var(--ink);color:var(--ink-fg);display:grid;place-items:center;font-weight:800;font-size:1.35rem;letter-spacing:-.02em}}
.who{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:18px 0 10px}}
.who h1{{margin:0;font-size:1.9rem;letter-spacing:-.02em}}
.badge{{background:#1d2a3a;color:#fff;font-size:.7rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:5px 9px;border-radius:6px}}
.headline{{margin:0;font-size:clamp(2.1rem,5.2vw,3.6rem);line-height:1.04;letter-spacing:-.035em;font-weight:800;text-wrap:balance}}
.stats{{display:flex;gap:22px;flex-wrap:wrap;color:var(--mut);margin:22px 0 24px}}
.stats b{{color:var(--fg);font-weight:600}}
.actions{{display:flex;gap:12px;flex-wrap:wrap}}
.btn{{display:inline-flex;align-items:center;height:48px;padding:0 24px;border-radius:999px;font-weight:600;border:1px solid var(--line);background:#fff;cursor:pointer;font:inherit;font-weight:600;transition:background .15s,transform .15s}}
.btn:hover{{background:var(--chip)}}
.btn.pri{{background:var(--ink);color:var(--ink-fg);border-color:var(--ink)}}
.btn.pri:hover{{background:#1d2347}}
nav.bar{{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:14px 0;border-bottom:1px solid var(--line);margin-bottom:clamp(24px,4vw,40px)}}
.tabs{{display:flex;gap:4px;flex-wrap:wrap}}
.tab{{font:inherit;font-weight:600;background:none;border:0;padding:10px 18px;border-radius:999px;cursor:pointer;color:var(--fg)}}
.tab:hover{{background:var(--chip)}}
.tab[aria-selected=true]{{background:var(--chip)}}
.tab span{{color:var(--mut);font-weight:500;margin-left:4px}}
select{{font:inherit;font-weight:500;height:46px;padding:0 14px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--fg);cursor:pointer}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(20px,2.6vw,36px);padding-bottom:72px}}
.shot{{display:flex;flex-direction:column;gap:10px;background:#0b0b0d;color:#fff;border-radius:10px;padding:14px 14px 12px;font-family:"Arial Black","Helvetica Neue",Impact,system-ui,sans-serif;box-shadow:0 1px 0 #2a2a30 inset,0 10px 24px rgba(14,19,48,.18);transition:transform .2s,box-shadow .2s}}
.shot:hover,.shot:focus-visible{{transform:translateY(-4px);box-shadow:0 1px 0 #2a2a30 inset,0 18px 34px rgba(14,19,48,.28)}}
.shot:focus-visible{{outline:3px solid var(--c);outline-offset:4px}}
.lab,.foot{{display:flex;justify-content:space-between;align-items:center;gap:8px;font:700 .62rem/1 ui-monospace,"SF Mono",Menlo,Consolas,monospace;letter-spacing:.16em;text-transform:uppercase;color:#9a9aa3}}
.lab span:first-child{{color:var(--c)}}
.name{{display:flex;align-items:flex-end;min-height:2.1em;font-weight:900;font-size:clamp(1.05rem,1.55vw,1.5rem);line-height:1.05;letter-spacing:.01em;text-transform:uppercase;color:var(--c);overflow-wrap:anywhere}}
.stripes{{display:grid;gap:3px}}
.stripes i{{display:block;height:3px;background:var(--c)}}
.stripes i:nth-child(2){{opacity:.75}}.stripes i:nth-child(3){{opacity:.5}}.stripes i:nth-child(4){{opacity:.28}}
.thumb{{position:relative;display:block;aspect-ratio:8/5;border-radius:4px;overflow:hidden;background:#1a1a1f;border:2px solid #f4f1e8}}
.thumb img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s}}
.shot:hover .thumb img,.shot:focus-visible .thumb img{{transform:scale(1.045)}}
.tag{{color:#0b0b0d;background:var(--c);padding:3px 7px;border-radius:2px;letter-spacing:.1em}}
.empty{{grid-column:1/-1;color:var(--mut)}}
footer{{border-top:1px solid var(--line);padding:24px 0 40px;color:var(--mut);font-size:.9rem}}
@media (max-width:1200px){{.grid{{grid-template-columns:repeat(3,1fr)}}}}
@media (max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media (max-width:560px){{.grid{{grid-template-columns:1fr}}nav.bar{{flex-direction:column;align-items:stretch}}select{{width:100%}}}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;scroll-behavior:auto!important}}}}
</style></head><body>
<div class="wrap">
  <header class="top">
    <div>
      <div class="avatar" aria-hidden="true">R</div>
      <div class="who"><h1>Game Shelf</h1><span class="badge">by Remi Alexander</span></div>
      <p class="headline">Browser games you can play right now.</p>
      <div class="stats"><span><b>{len(games)}</b> games</span><span><b>{n3}</b> in 3D</span><span><b>{n2}</b> in 2D</span></div>
      <div class="actions">
        <button class="btn pri" id="rand" type="button">Play a random game</button>
      </div>
    </div>
  </header>
  <nav class="bar" aria-label="Filter games">
    <div class="tabs" role="tablist">
      <button class="tab" role="tab" aria-selected="true" data-f="all" type="button">All<span>{len(games)}</span></button>
    </div>
    <select id="sort" aria-label="Sort games"><option value="az">A to Z</option><option value="za">Z to A</option></select>
  </nav>
  <main>
    <div class="grid" id="grid">
{cards}
    </div>
  </main>
  <footer>by Remi Alexander</footer>
</div>
<script>
(function(){{
  var grid=document.getElementById("grid"),shots=[].slice.call(grid.children),tabs=[].slice.call(document.querySelectorAll(".tab")),f="all";
  function apply(){{shots.forEach(function(s){{s.hidden=!(f==="all"||s.dataset.tag===f)}})}}
  tabs.forEach(function(t){{t.onclick=function(){{f=t.dataset.f;tabs.forEach(function(x){{x.setAttribute("aria-selected",x===t)}});apply()}}}});
  document.getElementById("sort").onchange=function(){{
    var dir=this.value==="za"?-1:1;
    shots.sort(function(a,b){{return dir*a.dataset.title.localeCompare(b.dataset.title)}}).forEach(function(s){{grid.appendChild(s)}});
  }};
  document.getElementById("rand").onclick=function(){{
    var v=shots.filter(function(s){{return !s.hidden}});if(v.length)location.href=v[Math.floor(Math.random()*v.length)].getAttribute("href");
  }};
}})();
</script>
</body></html>
'''
open(f"{root}/index.html", "w", encoding="utf8").write(page)
print(len(games), "games;", n3, "3D;", n2, "2D")
