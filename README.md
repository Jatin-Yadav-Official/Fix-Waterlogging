# 🌊 Fix Waterlogging (Jal Sachet)
### *AI-Powered Urban Waterlogging Prediction, Smart Commuter Detours & Municipal Grievance Automation*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://fix-waterlogging.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Leaflet](https://img.shields.io/badge/Leaflet-Interactive%20Maps-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-Responsive%20UI-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![IMD](https://img.shields.io/badge/IMD-Weather%20Data-orange?style=for-the-badge&logo=open-street-map&logoColor=white)](https://mausam.imd.gov.in)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

---

## 🌐 Live Demonstration
> 🔗 **Website URL:** **[https://fix-waterlogging.onrender.com/](https://fix-waterlogging.onrender.com/)**
> 
> *Click above to explore live meteorological forecast ingestion, flood risk simulations, dark Leaflet maps, dynamic detour navigation, and 1-click WhatsApp municipal grievance dispatch live on desktop or mobile.*

---

## 🎯 Project Motto & Vision

> **"From Reactive Pumping to Proactive Civic Resilience"**

During intense monsoon spells, major urban corridors—such as Gurugram's **NH-48, Subhash Chowk, Rajiv Chowk, and Hero Honda Chowk**, as well as **Chandigarh's vulnerable underpasses**—paralyze within 30 to 45 minutes of heavy rain. Commuters get stranded, emergency vehicles face massive gridlocks, and municipal departments struggle to respond after water levels rise.

**Fix Waterlogging** transforms urban flood defense by shifting civic intervention from *reactive post-flood recovery* to *predictive pre-storm prevention*:
1. **Predict Before Deluge**: Accurately estimates flood probability and water depth hours before clouds burst using real-time meteorological models and infrastructure drainage thresholds.
2. **Protect Commuters**: Calculates safe, elevated bypass routes around submerged choke points, saving up to 25 minutes of crawl time.
3. **Bridge Citizens & Government**: Automates instant, verified grievance dispatch directly into official municipal control rooms with GPS pins and ticket IDs.

---

## ✨ Key Features

### 1. 🧠 AI Waterlogging Prediction Engine
- **Learns from Historical Ground Deluges**: Trained on verified 2022–2026 waterlogging event registries across Gurugram and Chandigarh.
- **Physics-Informed Risk Modeling**: Evaluates storm rainfall intensity ($\text{mm/hr}$) against physical stormwater drainage capacities (e.g., Chandigarh's design limit of $15\text{--}20\text{ mm/hr}$ vs. Gurugram's chronic bottleneck thresholds).
- **Multi-Class Hazard Categorization**:
  - 🔴 **Severe (>80% Risk / Depth >45 cm)**: Underpass submerged, engine stall danger for low sedans & 2-wheelers.
  - 🟠 **High (60–80% Risk / Depth 20–45 cm)**: Heavy stagnation, severe traffic crawl.
  - 🟡 **Moderate (35–60% Risk / Depth 5–20 cm)**: Surface runoff, curb pooling.
  - 🟢 **Clear (<35% Risk)**: Passable roads.

### 2. 🌦️ Live Meteorological Forecast Ingestion
- **Automated Weather Model**: Integrates real-time weather forecasting for Gurugram, Chandigarh, and Pan-India cities.
- **Rolling 12-Hour Early Warning**: Analyzes upcoming storm duration, total rainfall volume ($\text{mm}$), and peak cloudburst intensity.
- **Interactive "What-If" DELUGE Simulator**: Commuters and city planners can drag rain volume and duration sliders to stress-test road networks under extreme 100 mm cloudburst scenarios.

### 3. 🗺️ Smart Dynamic Detour Routing
- **Hazard Interception**: Commuters enter any starting point and destination (e.g., *Cyber City ➔ Subhash Chowk* or *Sector 14 ➔ Kherki Daula*).
- **Real-Time Risk Scanning**: The routing engine intercepts the direct path against predicted flooded hotspots.
- **Elevated Bypass Generation**: Automatically computes an alternate safe route skirted around choked underpasses, providing real-time time savings (e.g., *Saves 24 mins*) and clear navigation advisories.

### 4. 📢 1-Click WhatsApp Municipal Grievance Dispatch
- **Direct Official Helplines**: Pre-configured to reach official civic control rooms:
  - **Gurugram GMDA Flood Control Room**: `7840001817`
  - **Chandigarh Municipal Corporation**: Official flood control cell
- **Zero Suspicious Links**: Pure structured civic grievance payload with:
  - Unique Official Ticket ID (`TKT-GUR-2026...`)
  - Live Google Maps GPS pin
  - Severity classification and citizen notes
- **Auto-GPS Capture**: 1-click HTML5 geolocation autofills coordinates accurately.

### 5. 📱 Mobile-First Responsive Design
- **Full-Screen Interactive Map Canvas**: Custom Dark Leaflet map with animated pulsating risk rings.
- **1-Thumb Switcher Bar**: Seamlessly toggle between `[ 🗺️ Map View ]` and `[ ⚙️ AI Controls ]` on any phone without clutter.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend UI** | HTML5, Tailwind CSS, JavaScript (ES6+), FontAwesome 6 |
| **Mapping & Geospatial** | Leaflet.js, OpenStreetMap CartoDB Dark Matter, Nominatim Geocoding |
| **Backend API** | Python 3 Standard Library (`http.server`, `urllib`, `json`, `ssl`) |
| **Meteorological Data** | Open-Meteo Weather API & IMD Observatories |
| **Civic Dispatch** | WhatsApp Universal Click-to-Chat (`wa.me`) Protocol |
| **Dependencies** | **Zero heavy pip packages required!** Runs out-of-the-box on standard Python 3.8+ |

---

## 📂 Project Architecture

```
Fix Waterlogging/
├── server.py               # REST API & static file HTTP server
├── Procfile                # Cloud deployment entrypoint (Render/Railway)
├── requirements.txt        # Runtime environment configuration
├── run_app.bat             # 1-Click Windows desktop launcher
│
├── static/                 # Client-side web application
│   ├── index.html          # Responsive dashboard with mobile view-switcher
│   ├── app.js              # Map rendering, detour routing & prediction logic
│   └── style.css           # Custom animations, dark maps & mobile styling
│
├── model/
│   ├── __init__.py         # Package initialization
│   └── predictor.py        # Machine learning & sigmoid flood risk estimator
│
├── services/
│   ├── __init__.py         # Package initialization
│   ├── weather_service.py  # Forecast ingestion & rolling storm analysis
│   ├── routing_service.py  # Direct hazard detection & detour generation
│   ├── complaint_service.py# WhatsApp dispatch formatting & ticket logger
│   └── imd_service.py      # Pan-India station & alert mapping
│
└── data/
    ├── historical_events.json # 2022-2026 master ground waterlogging records
    ├── geocoded_locations.json# Drain capacities, coordinates & recurrence tags
    └── helplines.json         # GMDA & Chandigarh MC contact registers
```

---

## 🚀 Quickstart: Run Locally

### Method 1: Using the 1-Click Desktop Launcher (Windows)
Double-click `run_app.bat` inside the folder. The server will start automatically!

### Method 2: Using the Command Line
```bash
# 1. Navigate to the folder
cd "C:\Users\Jatin\Desktop\Fix Waterlogging"

# 2. Start the Python server
python server.py
```
Open your browser at:
👉 **`http://127.0.0.1:8000`**

---

## ☁️ How to Deploy Online (Free 24/7 Hosting)

Deploy your own live copy to **Render.com** in 2 minutes:
1. Push this folder to a GitHub repository.
2. Sign in to [Render.com](https://render.com) and click **New +** ➔ **Web Service**.
3. Select your GitHub repository.
4. Settings:
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt` (or leave empty)
   - **Start Command:** `python server.py`
5. Click **Deploy Web Service**. You will get an instant public URL:
   👉 **`https://fix-waterlogging.onrender.com/`**

---

## 👥 Civic Impact & Attribution
Developed as an open civic-tech resilience solution to mitigate urban monsoon disruptions in Indian metropolitan cities. 

*Stay safe, avoid submerged underpasses, and help cities drain faster!* 🌧️🛡️
