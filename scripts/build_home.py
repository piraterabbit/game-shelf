import json, html, sys
root = sys.argv[1]
games = json.load(open(f"{root}/games.json", encoding="utf8"))
games.sort(key=lambda g: g["title"].lower())
n3 = sum(g["tag"] == "3D" for g in games)
n2 = len(games) - n3
e = html.escape

cards = "\n".join(
    f'''      <a class="shot" href="{g["slug"]}/" data-tag="{g["tag"]}" data-title="{e(g["title"].lower())}">
        <span class="thumb"><img src="thumbs/{g["slug"]}.jpg" alt="" loading="lazy" width="960" height="600"><span class="tag">{g["tag"]}</span></span>
        <span class="name">{e(g["title"])}</span>
      </a>'''
    for g in games
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
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(28px,4vw,56px) clamp(20px,3vw,48px);padding-bottom:72px}}
.shot{{display:block}}
.thumb{{position:relative;display:block;aspect-ratio:8/5;border-radius:var(--r-card);overflow:hidden;background:#eef0f5;box-shadow:0 0 0 1px rgba(14,19,48,.06)}}
.thumb img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s}}
.shot:hover .thumb img,.shot:focus-visible .thumb img{{transform:scale(1.045)}}
.shot:focus-visible{{outline:3px solid var(--acc);outline-offset:6px;border-radius:22px}}
.tag{{position:absolute;top:12px;right:12px;font-size:.68rem;font-weight:800;letter-spacing:.08em;padding:4px 9px;border-radius:99px;background:rgba(255,255,255,.92);color:var(--fg)}}
.shot[data-tag="3D"] .tag{{background:var(--acc);color:#2a1c00}}
.name{{display:block;margin-top:12px;font-weight:600;font-size:1.02rem}}
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
      <div class="who"><h1>Game Shelf</h1><span class="badge">by Remi</span></div>
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
  <footer>by Remi</footer>
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
