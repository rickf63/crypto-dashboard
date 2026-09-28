# -*- coding: utf-8 -*-
"""
Dashboard de Criptomonedas en Tiempo Real
==========================================
Top 10 criptos, dominancia de mercado, comparativa
de rendimiento y gráfica histórica de precio.

API: CoinGecko (gratis, sin registro)

Requisitos:
  pip install flask requests

Uso:
  python app.py
  Abre http://localhost:5002
"""

import requests
from flask import Flask, render_template_string, jsonify
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

COINGECKO = "https://api.coingecko.com/api/v3"

# ----------------------------------------------------------------------
# API COINGECKO
# ----------------------------------------------------------------------
def get_top10():
    try:
        r = requests.get(f"{COINGECKO}/coins/markets", params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "price_change_percentage": "1h,24h,7d,30d",
            "sparkline": True
        }, timeout=10)
        return r.json()
    except:
        return []


def get_global():
    try:
        r = requests.get(f"{COINGECKO}/global", timeout=10)
        return r.json().get("data", {})
    except:
        return {}


def get_historico(coin_id, dias=30):
    try:
        r = requests.get(f"{COINGECKO}/coins/{coin_id}/market_chart", params={
            "vs_currency": "usd",
            "days": dias,
            "interval": "daily" if dias >= 30 else "hourly"
        }, timeout=10)
        data = r.json()
        precios = data.get("prices", [])
        return {
            "fechas": [p[0] for p in precios],
            "precios": [round(p[1], 6) for p in precios]
        }
    except:
        return {"fechas": [], "precios": []}


# ----------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crypto Dashboard</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:#0a0a0f;color:#fff;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;padding:16px}
    h1{font-size:1.4rem;margin-bottom:2px}
    .sub{color:#555;font-size:.8rem;margin-bottom:20px}
    .accent{color:#f7931a}
    .grid-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:20px}
    .stat{background:#111;border-radius:10px;padding:14px;border:1px solid #1f1f1f}
    .stat .lbl{color:#555;font-size:.7rem;text-transform:uppercase;letter-spacing:.5px}
    .stat .val{font-size:1.3rem;font-weight:700;margin-top:4px}
    .card{background:#111;border-radius:10px;padding:16px;margin-bottom:16px;border:1px solid #1f1f1f}
    .card h2{color:#555;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px;margin-bottom:14px}
    table{width:100%;border-collapse:collapse;font-size:.85rem}
    th{color:#555;font-weight:500;padding:8px;text-align:left;border-bottom:1px solid #1f1f1f;white-space:nowrap}
    td{padding:8px;border-bottom:1px solid #111;vertical-align:middle}
    tr:hover td{background:#151515}
    .coin-name{display:flex;align-items:center;gap:8px;cursor:pointer}
    .coin-name img{width:24px;height:24px;border-radius:50%}
    .coin-name:hover .sym{color:#f7931a}
    .sym{font-weight:700;font-size:.9rem}
    .rank{color:#333;font-size:.75rem;width:24px}
    .pos{color:#00d4aa}
    .neg{color:#ff4444}
    .neu{color:#888}
    canvas{max-height:200px}
    .tabs{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap}
    .tab{background:#1a1a1a;border:1px solid #2a2a2a;color:#888;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:.8rem}
    .tab.active{background:#f7931a22;border-color:#f7931a66;color:#f7931a}
    .sparkline{width:80px;height:30px}
    .loading-msg{color:#333;text-align:center;padding:40px;font-size:.9rem}
    .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
    .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    @media(max-width:700px){.grid2{grid-template-columns:1fr}.hide-mob{display:none}}
    .refresh-info{color:#333;font-size:.7rem;text-align:right;margin-top:8px}
    #selected-name{color:#f7931a;font-weight:700}
  </style>
</head>
<body>
  <h1>🪙 <span class="accent">Crypto</span> Dashboard</h1>
  <p class="sub">Top 10 · Dominancia · Rendimiento · Histórico — datos en tiempo real via CoinGecko</p>

  <div class="grid-stats" id="stats-globales">
    <div class="stat"><div class="lbl">Cargando...</div><div class="val">—</div></div>
  </div>

  <div class="grid2">
    <div class="card">
      <h2>Dominancia de mercado</h2>
      <canvas id="cDom"></canvas>
    </div>
    <div class="card">
      <h2>Rendimiento 7 días</h2>
      <canvas id="cRend"></canvas>
    </div>
  </div>

  <div class="card">
    <h2>Top 10 Criptomonedas</h2>
    <div style="overflow-x:auto">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Moneda</th>
            <th>Precio</th>
            <th>1h</th>
            <th>24h</th>
            <th>7d</th>
            <th class="hide-mob">Market Cap</th>
            <th class="hide-mob">Vol 24h</th>
            <th class="hide-mob">7 días</th>
          </tr>
        </thead>
        <tbody id="tabla"></tbody>
      </table>
    </div>
    <p style="color:#333;font-size:.7rem;margin-top:8px">Clic en cualquier moneda para ver su historial</p>
  </div>

  <div class="card">
    <h2>Historial de precio — <span id="selected-name">Bitcoin</span></h2>
    <div class="tabs">
      <div class="tab active" onclick="cargarHistorico(selectedCoin, 7, this)">7D</div>
      <div class="tab" onclick="cargarHistorico(selectedCoin, 30, this)">30D</div>
      <div class="tab" onclick="cargarHistorico(selectedCoin, 90, this)">90D</div>
      <div class="tab" onclick="cargarHistorico(selectedCoin, 365, this)">1A</div>
    </div>
    <canvas id="cHistorico"></canvas>
  </div>

  <p class="refresh-info">Actualiza cada 60 segundos · Datos: CoinGecko</p>

<script>
let cDom=null, cRend=null, cHist=null;
let selectedCoin = 'bitcoin';
let selectedDias = 7;

function fmt(n){
  if(!n&&n!==0)return'—';
  if(Math.abs(n)>=1e9)return'$'+(n/1e9).toFixed(2)+'B';
  if(Math.abs(n)>=1e6)return'$'+(n/1e6).toFixed(2)+'M';
  if(Math.abs(n)>=1000)return'$'+n.toLocaleString('en-US',{maximumFractionDigits:2});
  return'$'+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:6});
}
function pct(n){
  if(!n&&n!==0)return'<span class="neu">—</span>';
  const c=n>0?'pos':n<0?'neg':'neu';
  return`<span class="${c}">${n>0?'▲':n<0?'▼':''}${Math.abs(n).toFixed(2)}%</span>`;
}
function mktfmt(n){
  if(!n)return'—';
  if(n>=1e12)return'$'+(n/1e12).toFixed(2)+'T';
  if(n>=1e9)return'$'+(n/1e9).toFixed(2)+'B';
  return'$'+(n/1e6).toFixed(0)+'M';
}

function kill(c){if(c){c.destroy();return null;}return null;}

async function cargarTodo(){
  const r = await fetch('/api/mercado');
  const d = await r.json();

  // Stats globales
  const g = d.global;
  document.getElementById('stats-globales').innerHTML=`
    <div class="stat"><div class="lbl">Market Cap Total</div>
      <div class="val">${mktfmt(g.total_market_cap?.usd)}</div></div>
    <div class="stat"><div class="lbl">Volumen 24h</div>
      <div class="val">${mktfmt(g.total_volume?.usd)}</div></div>
    <div class="stat"><div class="lbl">Dominancia BTC</div>
      <div class="val accent">${g.market_cap_percentage?.btc?.toFixed(1)}%</div></div>
    <div class="stat"><div class="lbl">Dominancia ETH</div>
      <div class="val" style="color:#627eea">${g.market_cap_percentage?.eth?.toFixed(1)}%</div></div>
    <div class="stat"><div class="lbl">Criptos activas</div>
      <div class="val">${g.active_cryptocurrencies?.toLocaleString()}</div></div>
  `;

  // Dominancia
  const dom = g.market_cap_percentage || {};
  const domKeys = Object.keys(dom).slice(0,8);
  const domVals = domKeys.map(k=>dom[k]);
  const otros   = 100 - domVals.reduce((a,b)=>a+b,0);
  const domColors=['#f7931a','#627eea','#26a17b','#e84142','#2775ca','#9945ff','#00ffa3','#e6007a','#888'];
  cDom=kill(cDom);
  cDom=new Chart(document.getElementById('cDom').getContext('2d'),{
    type:'doughnut',
    data:{labels:[...domKeys.map(k=>k.toUpperCase()),'Otros'],
          datasets:[{data:[...domVals,otros>0?otros:0],backgroundColor:domColors,borderWidth:0}]},
    options:{responsive:true,cutout:'65%',
      plugins:{legend:{position:'right',labels:{color:'#888',font:{size:10},boxWidth:10}}}}
  });

  // Rendimiento 7d
  const coins = d.coins;
  const rend7  = coins.map(c=>({name:c.symbol.toUpperCase(),val:c.price_change_percentage_7d_in_currency||0}))
                      .sort((a,b)=>b.val-a.val);
  cRend=kill(cRend);
  cRend=new Chart(document.getElementById('cRend').getContext('2d'),{
    type:'bar',
    data:{labels:rend7.map(c=>c.name),
          datasets:[{label:'Cambio 7d %',data:rend7.map(c=>c.val.toFixed(2)),
            backgroundColor:rend7.map(c=>c.val>=0?'rgba(0,212,170,.7)':'rgba(255,68,68,.7)'),
            borderRadius:4}]},
    options:{responsive:true,
      plugins:{legend:{display:false}},
      scales:{x:{ticks:{color:'#666'},grid:{display:false}},
              y:{ticks:{color:'#666',callback:v=>v+'%'},grid:{color:'#1a1a1a'}}}}
  });

  // Tabla
  let html='';
  coins.forEach(c=>{
    const sp=c.sparkline_in_7d?.price||[];
    html+=`<tr onclick="seleccionar('${c.id}','${c.name}')" style="cursor:pointer">
      <td><span class="rank">${c.market_cap_rank}</span></td>
      <td><div class="coin-name">
        <img src="${c.image}" alt="${c.symbol}" loading="lazy">
        <div><div class="sym">${c.symbol.toUpperCase()}</div>
        <div style="color:#444;font-size:.7rem">${c.name}</div></div>
      </div></td>
      <td><strong>${fmt(c.current_price)}</strong></td>
      <td>${pct(c.price_change_percentage_1h_in_currency)}</td>
      <td>${pct(c.price_change_percentage_24h_in_currency)}</td>
      <td>${pct(c.price_change_percentage_7d_in_currency)}</td>
      <td class="hide-mob">${mktfmt(c.market_cap)}</td>
      <td class="hide-mob">${mktfmt(c.total_volume)}</td>
      <td class="hide-mob">
        <canvas class="sparkline" id="sp-${c.id}"></canvas>
      </td>
    </tr>`;
  });
  document.getElementById('tabla').innerHTML=html;

  // Sparklines
  coins.forEach(c=>{
    const sp=c.sparkline_in_7d?.price||[];
    if(!sp.length)return;
    const el=document.getElementById('sp-'+c.id);
    if(!el)return;
    const color=sp[sp.length-1]>=sp[0]?'#00d4aa':'#ff4444';
    new Chart(el.getContext('2d'),{
      type:'line',
      data:{labels:sp.map((_,i)=>i),datasets:[{data:sp,borderColor:color,borderWidth:1.5,
        pointRadius:0,fill:false,tension:.3}]},
      options:{responsive:false,plugins:{legend:{display:false}},
        scales:{x:{display:false},y:{display:false}}}
    });
  });
}

function seleccionar(id, nombre){
  selectedCoin = id;
  document.getElementById('selected-name').textContent = nombre;
  // reset tabs
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab')[0].classList.add('active');
  cargarHistorico(id, 7, document.querySelectorAll('.tab')[0]);
}

async function cargarHistorico(coinId, dias, tabEl){
  selectedDias = dias;
  if(tabEl){
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    tabEl.classList.add('active');
  }
  const r = await fetch(`/api/historico?coin=${coinId}&dias=${dias}`);
  const d = await r.json();
  if(!d.precios.length)return;

  const fechas = d.fechas.map(ts=>{
    const dt=new Date(ts);
    return dias<=7
      ? dt.toLocaleDateString('es-MX',{weekday:'short',hour:'2-digit',minute:'2-digit'})
      : dt.toLocaleDateString('es-MX',{day:'2-digit',month:'short'});
  });

  const color = d.precios[d.precios.length-1]>=d.precios[0]?'#00d4aa':'#ff4444';
  cHist=kill(cHist);
  cHist=new Chart(document.getElementById('cHistorico').getContext('2d'),{
    type:'line',
    data:{labels:fechas,datasets:[{
      label:'Precio USD',data:d.precios,borderColor:color,borderWidth:2,
      backgroundColor:color.replace(')',',0.08)').replace('rgb','rgba'),
      pointRadius:0,fill:true,tension:.3
    }]},
    options:{responsive:true,
      plugins:{legend:{display:false},
        tooltip:{callbacks:{label:ctx=>'$'+ctx.raw.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:6})}}},
      scales:{
        x:{ticks:{color:'#555',maxTicksLimit:8},grid:{color:'#151515'}},
        y:{ticks:{color:'#555',callback:v=>'$'+v.toLocaleString('en-US',{maximumFractionDigits:4})},grid:{color:'#151515'}}
      }
    }
  });
}

// Arrancar
cargarTodo();
cargarHistorico('bitcoin', 7, null);
setInterval(cargarTodo, 60000);
</script>
</body>
</html>
"""

# ----------------------------------------------------------------------
# RUTAS
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/mercado")
def mercado():
    return jsonify({
        "coins":  get_top10(),
        "global": get_global()
    })

@app.route("/api/historico")
def historico():
    from flask import request
    coin = request.args.get("coin", "bitcoin")
    dias = int(request.args.get("dias", 30))
    return jsonify(get_historico(coin, dias))

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import socket
    try: ip = socket.gethostbyname(socket.gethostname())
    except: ip = "127.0.0.1"
    print("="*55)
    print("  CRYPTO DASHBOARD")
    print("="*55)
    print(f"\n  PC:  http://localhost:5002")
    print(f"  CEL: http://{ip}:5002")
    print("\n  Ctrl+C para detener")
    print("="*55)
    app.run(host="0.0.0.0", port=5002, debug=False)
