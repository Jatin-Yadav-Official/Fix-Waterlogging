import os
import sys
import json
import urllib.parse
from typing import Dict, Any, List

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from model.predictor import FloodPredictionAgent
from services.imd_service import IMDWeatherService
from services.routing_service import DynamicRoutingEngine
from services.complaint_service import MunicipalityComplaintService

import gradio as gr

# Initialize AI and civic services
predictor = FloodPredictionAgent()
weather_service = IMDWeatherService()
routing_engine = DynamicRoutingEngine()
complaint_service = MunicipalityComplaintService()

GURUGRAM_HOTSPOTS = [h["name"] for h in predictor.hotspots.get("Gurugram", [])]
CHANDIGARH_HOTSPOTS = [h["name"] for h in predictor.hotspots.get("Chandigarh", [])]

# Preset commuter choke routes
PRESET_ROUTES = {
    "Gurugram": [
        "Cyber City ➔ Subhash Chowk (via NH-48)",
        "Sector 14 ➔ Kherki Daula Toll Plaza",
        "IFFCO Chowk ➔ Sohna Road",
        "Golf Course Road ➔ Rajiv Chowk Underpass"
    ],
    "Chandigarh": [
        "Tribune Chowk ➔ Chandigarh Railway Station (CTU Underpass)",
        "Sector 17 Bus Stand ➔ Housing Board Chowk, Panchkula",
        "Madhya Marg (Sec 26) ➔ Zirakpur Highway"
    ]
}

# ----------------- Core Handler Functions -----------------

def on_city_change(city: str):
    spots = GURUGRAM_HOTSPOTS if city == "Gurugram" else CHANDIGARH_HOTSPOTS
    routes = PRESET_ROUTES.get(city, [])
    return (
        gr.Dropdown(choices=spots, value=spots[0] if spots else None),
        gr.Dropdown(choices=routes, value=routes[0] if routes else None)
    )

def predict_waterlogging(city: str, hotspot_name: str, rainfall_mm: float, duration_mins: float):
    if not hotspot_name:
        return "⚠️ Please select a hotspot location."
    
    city_spots = predictor.hotspots.get(city, [])
    target_spot = next((s for s in city_spots if s["name"] == hotspot_name), None)
    
    if not target_spot:
        return f"⚠️ Location '{hotspot_name}' not found in {city} database."
    
    duration_hrs = max(float(duration_mins) / 60.0, 0.25)
    result = predictor.calculate_hotspot_risk(target_spot, float(rainfall_mm), duration_hrs)
    
    sev = result["severity"]
    prob = int(result["probability"] * 100)
    depth = result["estimated_depth_cm"]
    drain = target_spot.get("drain_threshold_mm_hr", 20.0)
    intensity = round(float(rainfall_mm) / duration_hrs, 1)
    
    badge_colors = {
        "Severe": ("#ef4444", "🔴 SEVERE WATERLOGGING RISK"),
        "High": ("#f97316", "🟠 HIGH FLOODING RISK"),
        "Moderate": ("#eab308", "🟡 MODERATE SURFACE RUNOFF"),
        "Clear": ("#22c55e", "🟢 CLEAR / ROADS PASSABLE")
    }
    badge_color, badge_text = badge_colors.get(sev, ("#3b82f6", sev))
    
    stress_ratio = round(intensity / max(drain, 1.0), 1)
    stress_status = "⚠️ Drainage Capacity EXCEEDED" if intensity > drain else "✅ Within Drainage Design Limit"

    html_card = f"""
    <div style="background: #0f172a; border: 2px solid {badge_color}; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <span style="font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">{city} • Predicted Risk</span>
                <h2 style="margin: 4px 0 0 0; font-size: 22px; color: #ffffff;">{hotspot_name}</h2>
            </div>
            <span style="background: {badge_color}; color: #ffffff; padding: 6px 14px; border-radius: 9999px; font-weight: bold; font-size: 13px; letter-spacing: 0.03em;">
                {badge_text}
            </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 14px; margin-bottom: 18px;">
            <div style="background: #1e293b; border-radius: 8px; padding: 12px;">
                <div style="font-size: 12px; color: #94a3b8;">Flood Probability</div>
                <div style="font-size: 26px; font-weight: 800; color: {badge_color};">{prob}%</div>
            </div>
            <div style="background: #1e293b; border-radius: 8px; padding: 12px;">
                <div style="font-size: 12px; color: #94a3b8;">Est. Water Depth</div>
                <div style="font-size: 26px; font-weight: 800; color: #38bdf8;">{depth} <span style="font-size: 14px; font-weight: normal; color: #94a3b8;">cm</span></div>
            </div>
            <div style="background: #1e293b; border-radius: 8px; padding: 12px;">
                <div style="font-size: 12px; color: #94a3b8;">Storm Intensity</div>
                <div style="font-size: 26px; font-weight: 800; color: #e2e8f0;">{intensity} <span style="font-size: 14px; font-weight: normal; color: #94a3b8;">mm/h</span></div>
            </div>
            <div style="background: #1e293b; border-radius: 8px; padding: 12px;">
                <div style="font-size: 12px; color: #94a3b8;">Drain Threshold</div>
                <div style="font-size: 26px; font-weight: 800; color: #e2e8f0;">{drain} <span style="font-size: 14px; font-weight: normal; color: #94a3b8;">mm/h</span></div>
            </div>
        </div>

        <div style="background: #1e293b; border-left: 4px solid {badge_color}; border-radius: 0 8px 8px 0; padding: 14px; margin-bottom: 14px;">
            <div style="font-size: 13px; font-weight: bold; color: {badge_color}; margin-bottom: 4px;">🚗 Vehicle Safety & Passability Advisory:</div>
            <div style="font-size: 14px; line-height: 1.5; color: #cbd5e1;">{result['advisory']}</div>
        </div>

        <div style="font-size: 12px; color: #64748b; display: flex; justify-content: space-between;">
            <span>Drain Stress Ratio: <strong>{stress_ratio}x</strong> ({stress_status})</span>
            <span>Historical Classification: <strong>{target_spot.get('recurrence', 'Repeat Spot')}</strong></span>
        </div>
    </div>
    """
    return html_card

def calculate_detour_advisory(city: str, route_preset: str):
    routes_data = {
        "Cyber City ➔ Subhash Chowk (via NH-48)": {
            "hazard": "NH-48 Rajiv Chowk & Hero Honda Chowk Underpass Submerged",
            "risk": "Severe (Water depth > 45 cm)",
            "normal_delay": "65 mins bumper-to-bumper standstill",
            "detour": "Exit NH-48 at IFFCO Chowk ➔ Take MG Road / Golf Course Extension Road elevated corridor ➔ Reach Subhash Chowk from Sohna Elevated Road",
            "time_saved": "28 mins saved",
            "distance": "+3.4 km bypass"
        },
        "Sector 14 ➔ Kherki Daula Toll Plaza": {
            "hazard": "Narsinghpur NH-48 Chronic Choke Point Flooded",
            "risk": "High (Stalled heavy vehicles & sedans)",
            "normal_delay": "45 mins crawl time",
            "detour": "Divert via Old Railway Road ➔ Basai Flyover ➔ Dwarka Expressway (NH-248BB) ➔ Enter SPR to bypass Kherki Daula bottleneck",
            "time_saved": "22 mins saved",
            "distance": "+2.8 km bypass"
        },
        "IFFCO Chowk ➔ Sohna Road": {
            "hazard": "Subhash Chowk & Vatika Chowk Intersection Surface Stagnation",
            "risk": "High (30 cm water depth)",
            "normal_delay": "40 mins delay",
            "detour": "Take Golf Course Extension Road Flyover ➔ Reach Badshahpur via Southern Peripheral Road (SPR)",
            "time_saved": "19 mins saved",
            "distance": "+2.1 km bypass"
        },
        "Golf Course Road ➔ Rajiv Chowk Underpass": {
            "hazard": "Signature Tower / Rajiv Chowk Underpass Impassable",
            "risk": "Severe (Underpass drain overwhelmed)",
            "normal_delay": "50 mins delay",
            "detour": "Continue on Golf Course Ext Rd ➔ Netaji Subhash Marg ➔ Mini Secretariat elevated corridor",
            "time_saved": "24 mins saved",
            "distance": "+1.9 km bypass"
        },
        "Tribune Chowk ➔ Chandigarh Railway Station (CTU Underpass)": {
            "hazard": "Industrial Area CTU Underpass Submerged",
            "risk": "Severe (Underpass depth > 60 cm)",
            "normal_delay": "35 mins complete road blockage",
            "detour": "Bypass underpass via Purv Marg ➔ Transport Chowk ➔ Madhya Marg Flyover ➔ Railway Station Northern Approach",
            "time_saved": "20 mins saved",
            "distance": "+2.5 km bypass"
        },
        "Sector 17 Bus Stand ➔ Housing Board Chowk, Panchkula": {
            "hazard": "Sukhna Choe & Kishangarh Surface Overflow",
            "risk": "High (Surface runoff across Madhya Marg)",
            "normal_delay": "30 mins crawl time",
            "detour": "Divert via Dakshin Marg ➔ Hallomajra Flyover ➔ Industrial Area Phase 2 to Panchkula Barrier",
            "time_saved": "16 mins saved",
            "distance": "+3.0 km bypass"
        },
        "Madhya Marg (Sec 26) ➔ Zirakpur Highway": {
            "hazard": "Tribune Chowk Rotary Stagnation & Hallomajra Light Point Pooling",
            "risk": "Moderate to High",
            "normal_delay": "40 mins gridlock",
            "detour": "Take Vikas Marg (Southern Sector corridor) ➔ Aerocity Bypass directly towards Zirakpur",
            "time_saved": "23 mins saved",
            "distance": "+4.1 km bypass"
        }
    }

    info = routes_data.get(route_preset)
    if not info:
        info = {
            "hazard": "Predicted Waterlogging on Primary Arterial Route",
            "risk": "High Hazard Intercepted",
            "normal_delay": "35-50 mins delay",
            "detour": "Follow primary elevated bypass ring road avoiding low-lying underpasses and arterial dips.",
            "time_saved": "18 mins saved",
            "distance": "+2.5 km bypass"
        }

    html = f"""
    <div style="background: #0f172a; border: 2px solid #38bdf8; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <span style="font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Smart Detour Navigation</span>
                <h3 style="margin: 4px 0 0 0; font-size: 20px; color: #ffffff;">{route_preset}</h3>
            </div>
            <span style="background: #0284c7; color: #ffffff; padding: 6px 14px; border-radius: 9999px; font-weight: bold; font-size: 13px;">
                ⚡ {info['time_saved']}
            </span>
        </div>

        <div style="background: #7f1d1d; border-left: 4px solid #ef4444; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 14px;">
            <div style="font-size: 12px; font-weight: bold; color: #fca5a5;">⚠️ HAZARD INTERCEPTED ON DIRECT ROUTE:</div>
            <div style="font-size: 14px; color: #ffffff; margin-top: 2px;">{info['hazard']} ({info['risk']})</div>
            <div style="font-size: 12px; color: #fecaca; margin-top: 4px;">Expected congestion delay: <strong>{info['normal_delay']}</strong></div>
        </div>

        <div style="background: #064e3b; border-left: 4px solid #10b981; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 16px;">
            <div style="font-size: 12px; font-weight: bold; color: #6ee7b7;">🧭 RECOMMENDED SAFE ELEVATED BYPASS:</div>
            <div style="font-size: 14px; color: #ffffff; margin-top: 2px; line-height: 1.5;">{info['detour']}</div>
            <div style="font-size: 12px; color: #a7f3d0; margin-top: 6px;">Distance difference: <strong>{info['distance']}</strong> | Net time saved: <strong>{info['time_saved']}</strong></div>
        </div>
    </div>
    """
    return html

def fetch_live_weather(city: str):
    res = weather_service.get_forecast_for_city(city)
    current = res.get("current", {})
    forecast_12h = res.get("forecast_12h", [])
    total_12h_rain = res.get("total_12h_rain_mm", 0.0)
    risk_level = res.get("risk_level", "Low")
    
    table_rows = ""
    for item in forecast_12h[:6]:
        time_str = item.get("time", "").split("T")[-1]
        rain = item.get("rain_mm", 0.0)
        prob = item.get("pop", 0)
        table_rows += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 8px 12px; color: #cbd5e1;">{time_str}</td>
            <td style="padding: 8px 12px; font-weight: bold; color: #38bdf8;">{rain} mm</td>
            <td style="padding: 8px 12px; color: #94a3b8;">{prob}%</td>
        </tr>
        """
        
    html = f"""
    <div style="background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <span style="font-size: 12px; text-transform: uppercase; color: #94a3b8;">Live Forecast API (Open-Meteo & IMD)</span>
                <h3 style="margin: 4px 0 0 0; font-size: 22px;">{city} Meteorological Observatory</h3>
            </div>
            <span style="background: #3b82f6; color: #ffffff; padding: 6px 14px; border-radius: 9999px; font-weight: bold; font-size: 13px;">
                Status: {risk_level} Risk
            </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 18px;">
            <div style="background: #1e293b; padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">Current Temp</div>
                <div style="font-size: 22px; font-weight: bold; color: #ffffff;">{current.get('temperature', 28.5)}°C</div>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">12-Hr Rain Volume</div>
                <div style="font-size: 22px; font-weight: bold; color: #38bdf8;">{total_12h_rain} mm</div>
            </div>
            <div style="background: #1e293b; padding: 12px; border-radius: 8px;">
                <div style="font-size: 11px; color: #94a3b8;">Observed Rain</div>
                <div style="font-size: 22px; font-weight: bold; color: #e2e8f0;">{current.get('rain_mm', 0.0)} mm</div>
            </div>
        </div>

        <h4 style="margin: 16px 0 8px 0; font-size: 14px; color: #94a3b8;">Upcoming Hourly Forecast Window:</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; background: #1e293b; border-radius: 8px; overflow: hidden;">
            <thead>
                <tr style="background: #334155; color: #e2e8f0;">
                    <th style="padding: 8px 12px;">Time</th>
                    <th style="padding: 8px 12px;">Expected Rain</th>
                    <th style="padding: 8px 12px;">Precipitation Prob.</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """
    return html

def generate_grievance(city: str, location_name: str, severity: str, citizen_note: str):
    data = {
        "city": city,
        "location_name": location_name or f"{city} Center",
        "severity": severity,
        "notes": citizen_note or "Water stagnated; vehicles struggling to pass."
    }
    result = complaint_service.register_complaint(data)
    
    tkt = result.get("ticket_id", "TKT-2026-001")
    helpline = result.get("helpline_number", "7840001817")
    helpline_name = result.get("helpline_name", "Municipal Flood Control Room")
    wa_url = result.get("whatsapp_url", f"https://wa.me/{helpline}")
    msg = result.get("whatsapp_message", "")
    
    html = f"""
    <div style="background: #0f172a; border: 2px solid #22c55e; border-radius: 12px; padding: 20px; color: #f8fafc; font-family: system-ui, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px;">
            <div>
                <span style="font-size: 12px; color: #86efac; font-weight: bold;">✅ OFFICIAL GRIEVANCE REGISTERED</span>
                <h3 style="margin: 4px 0 0 0; font-size: 20px; color: #ffffff;">Ticket ID: {tkt}</h3>
            </div>
            <a href="{wa_url}" target="_blank" style="background: #22c55e; color: #000000; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-flex; align-items: center; gap: 6px;">
                💬 Open WhatsApp to Send
            </a>
        </div>

        <div style="background: #1e293b; padding: 14px; border-radius: 8px; margin-bottom: 14px; font-size: 13px;">
            <div style="color: #94a3b8; margin-bottom: 4px;">Target Municipal Control Room:</div>
            <div style="font-size: 16px; font-weight: bold; color: #ffffff;">{helpline_name} (Helpline: +91 {helpline})</div>
        </div>

        <div style="background: #020617; border: 1px solid #334155; border-radius: 8px; padding: 14px; font-family: monospace; font-size: 13px; line-height: 1.6; color: #e2e8f0; white-space: pre-wrap;">
{msg}
        </div>
    </div>
    """
    return html

# ----------------- Gradio UI Construction -----------------

custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="cyan",
    neutral_hue="slate"
)

with gr.Blocks(theme=custom_theme, title="Fix Waterlogging (Jal Sachet) | AI Civic Platform") as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 24px 12px 16px 12px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 12px; margin-bottom: 18px; border: 1px solid #334155;">
        <h1 style="font-size: 30px; font-weight: 800; color: #ffffff; margin-bottom: 6px; letter-spacing: -0.02em;">
            🌊 Fix Waterlogging <span style="font-size: 20px; color: #38bdf8; font-weight: 600;">(Jal Sachet)</span>
        </h1>
        <p style="font-size: 15px; color: #94a3b8; margin: 0 0 10px 0;">
            AI-Powered Urban Waterlogging Prediction, Smart Commuter Detours & Municipal Grievance Automation
        </p>
        <div style="display: inline-block; background: #1e3a8a; color: #93c5fd; padding: 4px 16px; border-radius: 9999px; font-size: 13px; font-weight: 600;">
            🎯 Motto: "From Reactive Pumping to Proactive Civic Resilience"
        </div>
    </div>
    """)
    
    with gr.Tabs():
        # TAB 1: AI PREDICTOR
        with gr.Tab("🧠 AI Waterlogging Predictor"):
            with gr.Row():
                with gr.Column(scale=1):
                    pred_city = gr.Dropdown(choices=["Gurugram", "Chandigarh"], value="Gurugram", label="🏙️ Select City")
                    pred_spot = gr.Dropdown(choices=GURUGRAM_HOTSPOTS, value=GURUGRAM_HOTSPOTS[0], label="📍 Select Hotspot / Underpass")
                    rain_slider = gr.Slider(minimum=5, maximum=150, value=50, step=5, label="🌧️ Expected Storm Rainfall (mm)")
                    dur_slider = gr.Slider(minimum=15, maximum=180, value=60, step=15, label="⏱️ Storm Duration (minutes)")
                    predict_btn = gr.Button("⚡ Run AI Prediction", variant="primary")
                with gr.Column(scale=2):
                    pred_output = gr.HTML(value="<div style='padding: 24px; text-align: center; color: #94a3b8;'>Adjust sliders and click <strong>Run AI Prediction</strong> to view flood probability and vehicle safety advisory.</div>")

        # TAB 2: SMART DETOUR
        with gr.Tab("🧭 Smart Detour Navigation"):
            with gr.Row():
                with gr.Column(scale=1):
                    detour_city = gr.Dropdown(choices=["Gurugram", "Chandigarh"], value="Gurugram", label="🏙️ Select City")
                    detour_route = gr.Dropdown(choices=PRESET_ROUTES["Gurugram"], value=PRESET_ROUTES["Gurugram"][0], label="🚗 Select Commuter Route")
                    detour_btn = gr.Button("🔍 Calculate Safe Elevated Bypass", variant="primary")
                with gr.Column(scale=2):
                    detour_output = gr.HTML(value="<div style='padding: 24px; text-align: center; color: #94a3b8;'>Select a route and click <strong>Calculate Safe Bypass</strong> to view flood hazard detection and detour recommendations.</div>")

        # TAB 3: LIVE FORECAST
        with gr.Tab("🌦️ Live Weather Forecast"):
            with gr.Row():
                with gr.Column(scale=1):
                    weather_city = gr.Dropdown(choices=["Gurugram", "Chandigarh"], value="Gurugram", label="🏙️ Select City")
                    weather_btn = gr.Button("📡 Fetch Live Forecast", variant="primary")
                with gr.Column(scale=2):
                    weather_output = gr.HTML(value="<div style='padding: 24px; text-align: center; color: #94a3b8;'>Click <strong>Fetch Live Forecast</strong> to query real-time meteorological models.</div>")

        # TAB 4: CIVIC GRIEVANCE DISPATCH
        with gr.Tab("📢 Municipal WhatsApp Grievance"):
            with gr.Row():
                with gr.Column(scale=1):
                    tkt_city = gr.Dropdown(choices=["Gurugram", "Chandigarh"], value="Gurugram", label="🏙️ City")
                    tkt_spot = gr.Dropdown(choices=GURUGRAM_HOTSPOTS, value=GURUGRAM_HOTSPOTS[0], label="📍 Flooded Spot")
                    tkt_sev = gr.Radio(choices=["Severe (Impassable)", "High (Crawl)", "Moderate (Pooling)"], value="Severe (Impassable)", label="⚠️ Hazard Severity")
                    tkt_notes = gr.Textbox(placeholder="E.g. Underpass flooded; water level up to car bumper; 2 vehicles stuck.", label="📝 Notes / Observations", lines=2)
                    tkt_btn = gr.Button("📋 Generate Official Municipal Ticket", variant="primary")
                with gr.Column(scale=2):
                    tkt_output = gr.HTML(value="<div style='padding: 24px; text-align: center; color: #94a3b8;'>Fill grievance details and click <strong>Generate Official Municipal Ticket</strong> to construct verified ticket and WhatsApp link.</div>")

        # TAB 5: ABOUT & MOTTO
        with gr.Tab("ℹ️ About the Project"):
            gr.Markdown("""
            ### 🌊 Fix Waterlogging (Jal Sachet)
            > **Motto:** *"From Reactive Pumping to Proactive Civic Resilience"*
            
            **The Challenge:**
            During intense monsoon spells, major urban corridors—such as Gurugram's **NH-48, Subhash Chowk, Rajiv Chowk, and Hero Honda Chowk**, as well as **Chandigarh's vulnerable underpasses**—paralyze within 30 to 45 minutes of heavy rain. Commuters get stranded, emergency vehicles face massive gridlocks, and municipal departments struggle to respond after water levels rise.
            
            **The AI Solution:**
            1. **Predict Before Deluge:** Ingests live meteorological precipitation forecasts and estimates flood probability & water depth hours in advance using historical 2022–2026 data and physical drainage capacities.
            2. **Smart Detours:** Automatically routes vehicles around flooded choke points via elevated bypasses, saving 20–25 minutes of traffic delay.
            3. **Municipal Grievance Dispatch:** Directly connects citizens with official municipal control rooms (GMDA Gurugram `7840001817` and Chandigarh MC) with structured ticket IDs and GPS coordinates.
            """)

    # Event handlers
    pred_city.change(on_city_change, inputs=[pred_city], outputs=[pred_spot, detour_route])
    detour_city.change(on_city_change, inputs=[detour_city], outputs=[pred_spot, detour_route])
    tkt_city.change(on_city_change, inputs=[tkt_city], outputs=[tkt_spot, detour_route])

    predict_btn.click(
        predict_waterlogging,
        inputs=[pred_city, pred_spot, rain_slider, dur_slider],
        outputs=[pred_output]
    )

    detour_btn.click(
        calculate_detour_advisory,
        inputs=[detour_city, detour_route],
        outputs=[detour_output]
    )

    weather_btn.click(
        fetch_live_weather,
        inputs=[weather_city],
        outputs=[weather_output]
    )

    tkt_btn.click(
        generate_grievance,
        inputs=[tkt_city, tkt_spot, tkt_sev, tkt_notes],
        outputs=[tkt_output]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
