# 🪙 Crypto Dashboard

Dashboard de criptomonedas en tiempo real construido con Flask y Chart.js. Datos en vivo via CoinGecko API (gratis, sin registro).

---

## ✨ ¿Qué muestra?

- **Stats globales** — Market cap total, volumen 24h, dominancia BTC y ETH, criptos activas
- **Dominancia de mercado** — Gráfica donut con el peso de cada cripto
- **Rendimiento 7 días** — Barras comparativas de las top 10
- **Top 10 criptomonedas** — Precio, cambio 1h/24h/7d, market cap, volumen y sparkline
- **Historial de precio** — Gráfica interactiva 7D/30D/90D/1A para cualquier cripto
- **Auto-actualización** cada 60 segundos

---

## 🚀 Instalación y uso

```bash
git clone https://github.com/rickf63/crypto-dashboard.git
cd crypto-dashboard
pip install flask requests
python app.py
```

Abre **http://localhost:5002** en tu navegador.

---

## 🛠 Stack

- **Backend:** Python, Flask, requests
- **Frontend:** HTML/CSS, JavaScript, Chart.js 4.4
- **API:** CoinGecko (gratis, sin API key)

---

## 📄 Licencia

MIT
