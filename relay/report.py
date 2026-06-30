#!/usr/bin/env python3
"""Generuje samodzielny raport HTML obok zdjęć (photos/report.html).

Otwierasz dwuklikiem w przeglądarce — bez serwera, bez internetu. Obrazy ładowane
lokalnie (względne ścieżki), dane analizy wstrzyknięte wprost do pliku.
"""
from __future__ import annotations

import json
from pathlib import Path


def build(photos_dir) -> Path:
    d = Path(photos_dir)
    items = []
    for jpg in sorted(d.glob("growkit_*.jpg")):
        sidecar = d / (jpg.stem + ".json")
        meta = {}
        if sidecar.exists():
            try:
                meta = json.loads(sidecar.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                meta = {}
        items.append({
            "img": jpg.name,
            "capturedAt": meta.get("capturedAt"),
            "analysis": meta.get("analysis"),
        })
    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(items, ensure_ascii=False))
    out = d / "report.html"
    out.write_text(html, encoding="utf-8")
    return out


TEMPLATE = r"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mushroom Growth Monitor</title>
<style>
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#faf8f6;color:#3e2723}
.app{max-width:1100px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:25px;margin:0 0 4px}.sub{color:#8d6e63;font-size:12px;margin-bottom:16px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}
.stat{background:#fff;border:1px solid #efe8e3;border-radius:12px;padding:14px;text-align:center}
.stat .v{font-size:22px;font-weight:700}.stat .l{font-size:12px;color:#8d6e63;margin-top:4px}
.alert{background:#fff8e1;border:1px solid #ffe082;border-radius:12px;padding:14px;margin:12px 0}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}
.box{background:#fff;border:1px solid #efe8e3;border-radius:12px;padding:14px}
.box h3{margin:0 0 8px;font-size:14px}.legend{font-size:12px;display:flex;gap:14px;margin-top:4px}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
.card{background:#fff;border:1px solid #efe8e3;border-radius:12px;overflow:hidden}
.card img{width:100%;height:190px;object-fit:cover;display:block}
.cb{padding:12px}.date{font-size:12px;color:#8d6e63;margin-bottom:8px}
.badge{display:inline-block;color:#fff;font-size:12px;font-weight:600;padding:3px 9px;border-radius:999px;margin:0 6px 6px 0}
.kv{display:flex;align-items:center;gap:8px;margin:8px 0;font-size:13px}
.bar{flex:1;height:8px;background:#eee;border-radius:999px;overflow:hidden}.bar>div{height:100%;background:#26a69a}
.meta{display:flex;flex-wrap:wrap;gap:10px;font-size:12px;color:#8d6e63}
.issues{margin:8px 0 0;padding-left:0;list-style:none;font-size:12px;color:#c62828}
.rec{font-size:12px;background:#f1f8e9;padding:8px;border-radius:8px;margin:8px 0 0}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}.charts{grid-template-columns:1fr}}
</style></head>
<body><div class="app">
<h1>🍄 Mushroom Growth Monitor</h1>
<div class="sub">raport lokalny — wygenerowany z folderu ze zdjęciami</div>
<div id="root"></div>
</div>
<script>
const DATA = /*__DATA__*/null;
const SL={inoculation:"Inokulacja",colonization:"Kolonizacja",fully_colonized:"Zarośnięte",pinning:"Pinning (zawiązki)",fruiting:"Owocowanie",harvest_ready:"Do zbioru",contamination:"Kontaminacja",unknown:"Nieznane"};
const SC={inoculation:"#9e9e9e",colonization:"#42a5f5",fully_colonized:"#26a69a",pinning:"#ffa726",fruiting:"#66bb6a",harvest_ready:"#8bc34a",contamination:"#ef5350",unknown:"#bdbdbd"};
const MO={none:"—",normal:"prawidłowa",long_stems:"długie nóżki ⚠️",large_caps:"duże kapelusze",leggy_thin:"wątłe/wyciągnięte ⚠️",aborts:"poronienia ⚠️"};
const CO={none:"brak",light:"lekka",heavy:"duża ⚠️",standing_water:"stojąca woda ⚠️"};
const fmt=ms=>ms?new Date(ms).toLocaleString("pl-PL"):"";
const esc=s=>String(s==null?"":s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function chart(series,yMin,yMax,unit){
  const W=760,H=200,pL=42,pB=24,pT=10,pR=10,pw=W-pL-pR,ph=H-pT-pB;
  const xs=[].concat(...series.map(s=>s.pts.map(p=>p.x)));
  if(!xs.length)return"";
  const xMin=Math.min(...xs),xMax=Math.max(...xs),sx=(xMax-xMin)||1;
  const X=x=>pL+((x-xMin)/sx)*pw,Y=y=>pT+ph-((y-yMin)/((yMax-yMin)||1))*ph;
  let g="";
  for(let i=0;i<=4;i++){const t=yMin+(yMax-yMin)*i/4;g+='<line x1="'+pL+'" y1="'+Y(t)+'" x2="'+(W-pR)+'" y2="'+Y(t)+'" stroke="#eee"/><text x="'+(pL-6)+'" y="'+(Y(t)+4)+'" text-anchor="end" font-size="11" fill="#888">'+Math.round(t)+unit+'</text>';}
  let paths="";
  for(const s of series){
    const v=s.pts.filter(p=>p.y!=null);
    if(!v.length)continue;
    const d=v.map((p,i)=>(i?"L":"M")+" "+X(p.x)+" "+Y(p.y)).join(" ");
    paths+='<path d="'+d+'" fill="none" stroke="'+s.color+'" stroke-width="2"/>';
    paths+=v.map(p=>'<circle cx="'+X(p.x)+'" cy="'+Y(p.y)+'" r="2.5" fill="'+s.color+'"/>').join("");
  }
  return '<svg viewBox="0 0 '+W+' '+H+'" width="100%">'+g+paths+'</svg>';
}
const root=document.getElementById("root");
if(!DATA||!DATA.length){root.innerHTML='<p style="color:#8d6e63">Brak zdjęć. Uruchom bt_receiver.py i poczekaj na zdjęcia z telefonu.</p>';}
else{
  const S=[...DATA].sort((a,b)=>(a.capturedAt||0)-(b.capturedAt||0));
  const last=S[S.length-1],la=last.analysis;
  const pin=S.find(p=>p.analysis&&p.analysis.pins_detected);
  let h='';
  h+='<div class="stats">';
  h+='<div class="stat"><div class="v">'+S.length+'</div><div class="l">Zdjęć</div></div>';
  h+='<div class="stat"><div class="v">'+(la?SL[la.stage]:"—")+'</div><div class="l">Etap</div></div>';
  h+='<div class="stat"><div class="v">'+(la?la.colonization_pct+"%":"—")+'</div><div class="l">Kolonizacja</div></div>';
  h+='<div class="stat"><div class="v">'+(la?((la.temperature_c==null?"?":la.temperature_c)+"°C / "+(la.humidity_pct==null?"?":la.humidity_pct)+"%"):"—")+'</div><div class="l">Temp / Wilg.</div></div>';
  h+='</div>';
  if(pin){h+='<div class="alert">🌱 <b>Pinning wykryty!</b> Pierwsze zawiązki: '+fmt(pin.capturedAt)+' — grzybnia zaczęła wychodzić na zewnątrz (start owocowania).</div>';}
  const col=[{color:"#26a69a",pts:S.map(p=>({x:p.capturedAt,y:p.analysis?p.analysis.colonization_pct:null}))}];
  const clim=[{color:"#ef5350",pts:S.map(p=>({x:p.capturedAt,y:p.analysis?p.analysis.temperature_c:null}))},{color:"#42a5f5",pts:S.map(p=>({x:p.capturedAt,y:p.analysis?p.analysis.humidity_pct:null}))}];
  h+='<div class="charts"><div class="box"><h3>Postęp kolonizacji</h3>'+chart(col,0,100,"%")+'</div>';
  h+='<div class="box"><h3>Klimat w boxie</h3>'+chart(clim,0,100,"")+'<div class="legend"><span style="color:#ef5350">● Temperatura °C</span><span style="color:#42a5f5">● Wilgotność %</span></div></div></div>';
  h+='<h2 style="font-size:18px">Galeria ('+S.length+')</h2><div class="gallery">';
  for(const p of [...S].reverse()){
    const a=p.analysis;
    h+='<div class="card"><a href="'+esc(p.img)+'" target="_blank"><img loading="lazy" src="'+esc(p.img)+'"></a><div class="cb"><div class="date">'+fmt(p.capturedAt)+'</div>';
    if(a){
      h+='<span class="badge" style="background:'+(SC[a.stage]||"#bdbdbd")+'">'+SL[a.stage]+'</span>';
      if(a.pins_detected)h+='<span class="badge" style="background:#ff9800">🌱 piny: '+a.pin_count_estimate+'</span>';
      h+='<div class="kv"><span>Kolonizacja</span><div class="bar"><div style="width:'+a.colonization_pct+'%"></div></div><b>'+a.colonization_pct+'%</b></div>';
      h+='<div class="meta">';
      if(a.temperature_c!=null)h+='<span>🌡️ '+a.temperature_c+'°C</span>';
      if(a.humidity_pct!=null)h+='<span>💧 '+a.humidity_pct+'%</span>';
      h+='<span>🍄 '+(MO[a.morphology]||a.morphology)+'</span><span>💦 '+(CO[a.condensation]||a.condensation)+'</span></div>';
      if(a.issues&&a.issues.length)h+='<ul class="issues">'+a.issues.map(i=>'<li>⚠️ '+esc(i)+'</li>').join("")+'</ul>';
      if(a.recommendation)h+='<p class="rec">💡 '+esc(a.recommendation)+'</p>';
    }else{h+='<div class="date">Bez analizy AI</div>';}
    h+='</div></div>';
  }
  h+='</div>';
  root.innerHTML=h;
}
</script>
</body></html>
"""


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    print(build(os.environ.get("LOCAL_PHOTOS_DIR", "./photos")))
