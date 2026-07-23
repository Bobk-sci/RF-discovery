"""Gabarit HTML autonome du dashboard (M10).

HTML/CSS/JS en ligne, aucune dépendance externe (coût nul, déployable sur GitHub Pages).
Le graphe de force est écrit en JavaScript pur. Injection par jetons ``__…__`` côté Python
(pas de ``str.format`` : le JS contient des accolades).
"""
from __future__ import annotations

TEMPLATE = r"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RF-Discovery — dashboard</title>
<style>
  :root{--bg:#f7f8fa;--fg:#1a1d24;--muted:#5c6672;--card:#fff;--border:#e2e6ea;--accent:#2191fb}
  @media (prefers-color-scheme:dark){
    :root{--bg:#12151b;--fg:#e6e9ee;--muted:#9aa4b2;--card:#1b1f27;--border:#2a2f3a;--accent:#4c9f70}
  }
  *{box-sizing:border-box}
  body{margin:0;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}
  header{padding:24px 20px 8px}
  h1{margin:0;font-size:22px}
  .sub{color:var(--muted);font-size:13px;margin-top:4px}
  main{max-width:1080px;margin:0 auto;padding:16px 20px 60px}
  section{margin-top:28px}
  h2{font-size:16px;border-bottom:1px solid var(--border);padding-bottom:6px}
  .cards{display:flex;flex-wrap:wrap;gap:12px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px 16px;min-width:120px;color:var(--muted);font-size:13px}
  .card .num{display:block;font-size:24px;font-weight:700;color:var(--fg)}
  .scroll{overflow-x:auto}
  table{border-collapse:collapse;width:100%;font-size:13px;background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden}
  th,td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
  th{background:rgba(127,127,127,.08);position:sticky;top:0}
  td.mp{white-space:normal;color:var(--muted);font-size:12px}
  .graphwrap{position:relative;background:var(--card);border:1px solid var(--border);border-radius:10px}
  svg{width:100%;height:560px;display:block}
  .link{stroke:var(--muted);stroke-opacity:.35}
  .link.candidate{stroke:#e4572e;stroke-width:2;stroke-dasharray:5 4;stroke-opacity:.9}
  .node{cursor:grab}
  .node circle{stroke-width:1.5}
  .legend{display:flex;flex-wrap:wrap;gap:10px;padding:10px 14px;font-size:12px;color:var(--muted)}
  .legend span{display:inline-flex;align-items:center;gap:5px}
  .dot{width:10px;height:10px;border-radius:50%}
  .controls{display:flex;gap:16px;align-items:center;padding:8px 14px;font-size:13px;color:var(--muted);border-top:1px solid var(--border)}
  #tip{position:fixed;display:none;background:var(--card);border:1px solid var(--border);border-radius:6px;padding:6px 9px;font-size:12px;pointer-events:none;box-shadow:0 4px 14px rgba(0,0,0,.15);z-index:9}
  footer{max-width:1080px;margin:0 auto;padding:0 20px 40px;color:var(--muted);font-size:12px}
  a{color:var(--accent)}
</style>
</head>
<body>
<header>
  <h1>RF-Discovery — dashboard</h1>
  <div class="sub">Dernier run : <b>__LATEST__</b> · généré le __GENERATED__ · moteur déterministe, le LLM n'entre jamais dans le scoring.</div>
</header>
<main>
  <section>
    <h2>Verdicts</h2>
    <div class="cards">__VERDICT_CARDS__</div>
  </section>

  <section>
    <h2>Graphe des candidats (top 30)</h2>
    <div class="graphwrap">
      <svg id="graph" viewBox="0 0 900 560" preserveAspectRatio="xMidYMid meet"></svg>
      <div class="legend" id="legend"></div>
      <div class="controls">
        <label><input type="checkbox" id="toggle-known" checked> arêtes connues (contexte)</label>
        <span>— liens candidats en <b style="color:#e4572e">rouge pointillé</b> (proposés, sans arête directe)</span>
      </div>
    </div>
  </section>

  <section>
    <h2>Candidats classés — run __LATEST__</h2>
    <div class="scroll"><table>
      <thead><tr><th>#</th><th>source</th><th>cible</th><th>z</th><th>p</th><th>novelty_z</th><th>burst</th><th>verdict</th><th>métachemin</th></tr></thead>
      <tbody>__CANDS_ROWS__</tbody>
    </table></div>
  </section>

  <section>
    <h2>Historique des verdicts</h2>
    <div class="scroll"><table>
      <thead><tr><th>run</th><th>source</th><th>cible</th><th>verdict</th></tr></thead>
      <tbody>__ADJ_ROWS__</tbody>
    </table></div>
  </section>

  <section>
    <h2>Historique des runs</h2>
    <div class="scroll"><table>
      <thead><tr><th>date</th><th>arêtes</th><th>candidats</th><th>statut</th><th>durée</th></tr></thead>
      <tbody>__RUNS_ROWS__</tbody>
    </table></div>
  </section>
</main>
<footer>RF-Discovery · DWPC + null par permutation + gate time-slice · dashboard statique GitHub Pages.</footer>
<div id="tip"></div>
<script>
const DATA = __GRAPH_JSON__;
(function(){
  const W=900,H=560,ns="http://www.w3.org/2000/svg";
  const svg=document.getElementById("graph");
  const colors=DATA.colors||{};
  const n=DATA.nodes.length||1;
  const nodes=DATA.nodes.map((d,i)=>({...d,x:W/2+240*Math.cos(2*Math.PI*i/n),y:H/2+240*Math.sin(2*Math.PI*i/n),vx:0,vy:0}));
  const idx={};nodes.forEach(o=>idx[o.id]=o);
  const links=DATA.links.filter(l=>idx[l.source]&&idx[l.target]).map(l=>({...l,s:idx[l.source],t:idx[l.target]}));
  const gL=document.createElementNS(ns,"g"),gN=document.createElementNS(ns,"g");
  svg.appendChild(gL);svg.appendChild(gN);
  const lineEls=links.map(l=>{const e=document.createElementNS(ns,"line");e.setAttribute("class","link "+l.kind);gL.appendChild(e);return e;});
  const nodeEls=nodes.map(o=>{const g=document.createElementNS(ns,"g");g.setAttribute("class","node");
    const c=document.createElementNS(ns,"circle");const r=4+Math.min(8,Math.sqrt((o.degree||1)));
    c.setAttribute("r",o.seed?r+2:r);c.setAttribute("fill",colors[o.type]||"#8a8f98");
    if(o.seed)c.setAttribute("stroke","#111");gN.appendChild(g);g.appendChild(c);drag(g,o);tip(g,o);return g;});
  function step(){
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const a=nodes[i],b=nodes[j];let dx=a.x-b.x,dy=a.y-b.y;let d2=dx*dx+dy*dy+0.01;
      let d=Math.sqrt(d2),f=900/d2;dx/=d;dy/=d;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f;}
    links.forEach(l=>{let dx=l.t.x-l.s.x,dy=l.t.y-l.s.y;let d=Math.sqrt(dx*dx+dy*dy)+0.01;
      let f=(d-95)*0.02;dx/=d;dy/=d;l.s.vx+=dx*f;l.s.vy+=dy*f;l.t.vx-=dx*f;l.t.vy-=dy*f;});
    nodes.forEach(o=>{o.vx+=(W/2-o.x)*0.002;o.vy+=(H/2-o.y)*0.002;o.vx*=0.85;o.vy*=0.85;
      if(!o.fixed){o.x+=o.vx;o.y+=o.vy;}o.x=Math.max(12,Math.min(W-12,o.x));o.y=Math.max(12,Math.min(H-12,o.y));});
    paint();
  }
  function paint(){
    links.forEach((l,i)=>{lineEls[i].setAttribute("x1",l.s.x);lineEls[i].setAttribute("y1",l.s.y);
      lineEls[i].setAttribute("x2",l.t.x);lineEls[i].setAttribute("y2",l.t.y);});
    nodes.forEach((o,i)=>nodeEls[i].setAttribute("transform","translate("+o.x+","+o.y+")"));
  }
  let k=0;function loop(){step();if(++k<420)requestAnimationFrame(loop);}loop();
  function pt(ev){const r=svg.getBoundingClientRect();return{x:(ev.clientX-r.left)*(W/r.width),y:(ev.clientY-r.top)*(H/r.height)};}
  function drag(el,o){el.addEventListener("mousedown",e=>{o.fixed=true;
    const mv=ev=>{const p=pt(ev);o.x=p.x;o.y=p.y;paint();};
    const up=()=>{o.fixed=false;removeEventListener("mousemove",mv);removeEventListener("mouseup",up);k=0;loop();};
    addEventListener("mousemove",mv);addEventListener("mouseup",up);e.preventDefault();});}
  const tipEl=document.getElementById("tip");
  function tip(el,o){el.addEventListener("mouseenter",()=>{tipEl.innerHTML="<b>"+o.id+"</b><br>"+(o.type||"?")+" · degré "+o.degree;tipEl.style.display="block";});
    el.addEventListener("mousemove",e=>{tipEl.style.left=(e.clientX+12)+"px";tipEl.style.top=(e.clientY+12)+"px";});
    el.addEventListener("mouseleave",()=>{tipEl.style.display="none";});}
  document.getElementById("toggle-known").addEventListener("change",e=>{
    gL.querySelectorAll(".link.known").forEach(l=>l.style.display=e.target.checked?"":"none");});
  const used=[...new Set(nodes.map(o=>o.type).filter(Boolean))];
  document.getElementById("legend").innerHTML=used.map(t=>'<span><i class="dot" style="background:'+(colors[t]||"#888")+'"></i>'+t+'</span>').join("");
})();
</script>
</body>
</html>
"""
