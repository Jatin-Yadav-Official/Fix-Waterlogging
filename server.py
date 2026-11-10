import http.server
import json
import urllib.parse
import os
import sys
from typing import Dict, Any

# Robust root and sub-directory resolution for Linux, Windows, Docker & Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for sub in ["", "model", "services", "data"]:
    p = os.path.join(BASE_DIR, sub)
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from model.predictor import FloodPredictionAgent
except ImportError:
    from predictor import FloodPredictionAgent

try:
    from services.imd_service import IMDWeatherService
except ImportError:
    from imd_service import IMDWeatherService

try:
    from services.routing_service import DynamicRoutingEngine
except ImportError:
    from routing_service import DynamicRoutingEngine

try:
    from services.complaint_service import MunicipalityComplaintService
except ImportError:
    from complaint_service import MunicipalityComplaintService

predictor_agent = FloodPredictionAgent()
imd_weather_service = IMDWeatherService()
routing_engine = DynamicRoutingEngine()
complaint_service = MunicipalityComplaintService()

class FloodGuardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """REST API and Static Asset Handler for Fix Waterlogging"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(BASE_DIR, "static"), **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. API: Get Hotspots
        if path == "/api/hotspots":
            city = params.get("city", ["Gurugram"])[0]
            spots = predictor_agent.hotspots.get(city, [])
            return self._send_json({"city": city, "hotspots": spots})

        # 2. API: Get Weather Forecast (Official IMD Observatories)
        elif path == "/api/weather":
            city = params.get("city", ["Gurugram"])[0]
            result = imd_weather_service.fetch_imd_forecast(city)
            return self._send_json(result)

        # 3. API: Google Maps Style Autocomplete Geocoding
        elif path == "/api/geocode":
            query = params.get("q", [""])[0]
            city = params.get("city", [None])[0]
            suggestions = routing_engine.search_places(query, city)
            return self._send_json({"query": query, "suggestions": suggestions})

        # 4. API: Get Navigable Places / Landmarks for Autocomplete
        elif path == "/api/places":
            city = params.get("city", ["Gurugram"])[0]
            places = routing_engine.search_places("", city)
            return self._send_json({"city": city, "places": places})

        # 5. API: Get Historical Events
        elif path == "/api/history":
            city = params.get("city", [None])[0]
            history_file = os.path.join(BASE_DIR, "data", "historical_events.json")
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                if city:
                    events = [e for e in events if e["city"].lower() == city.lower()]
                return self._send_json({"events": events})
            return self._send_json({"events": []})

        # 4. API: Get Recent Complaints
        elif path == "/api/complaints":
            complaints = complaint_service.get_recent_complaints(20)
            return self._send_json({"complaints": complaints})

        # 4B. API: Track Complaint by Ticket ID
        elif path == "/api/track":
            tkt = params.get("ticket_id", [""])[0]
            record = complaint_service.track_complaint(tkt)
            if record:
                return self._send_json({"found": True, "complaint": record})
            return self._send_json({"found": False, "message": "Ticket ID not found in municipal register."})

        # 5. API: Helplines
        elif path == "/api/helplines":
            helpline_file = os.path.join(BASE_DIR, "data", "helplines.json")
            with open(helpline_file, "r", encoding="utf-8") as f:
                helplines = json.load(f)
            return self._send_json(helplines)

        # 6. API: Get Current Configuration
        elif path == "/api/config":
            config_file = os.path.join(BASE_DIR, "config.json")
            cfg = {"WEATHER_API_PROVIDER": "open-meteo", "WEATHER_API_KEY": ""}
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            key = cfg.get("WEATHER_API_KEY", "")
            masked_key = (key[:4] + "..." + key[-4:]) if len(key) > 8 else ("Configured" if key else "")
            return self._send_json({
                "provider": cfg.get("WEATHER_API_PROVIDER", "open-meteo"),
                "has_key": bool(key and key != "YOUR_KEY_HERE" and key != "YOUR_API_KEY_HERE"),
                "masked_key": masked_key
            })

        # 7. Default: Serve static files (HTML, JS, CSS, assets)
        else:
            if path == "/":
                self.path = "/index.html"
            return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        # 1. API: Predict Waterlogging Probability & Severity
        if path == "/api/predict":
            city = payload.get("city", "Gurugram")
            rainfall_mm = float(payload.get("rainfall_mm", 50.0))
            duration_hrs = float(payload.get("duration_hrs", 2.0))
            prediction = predictor_agent.predict_city(city, rainfall_mm, duration_hrs)
            return self._send_json(prediction)

        # 2. API: Plan Dynamic Route & Smart Detour
        elif path == "/api/route":
            city = payload.get("city", "Gurugram")
            rainfall_mm = float(payload.get("rainfall_mm", 50.0))
            duration_hrs = float(payload.get("duration_hrs", 2.0))
            
            # Run prediction first to know active flood risk hotspots
            prediction = predictor_agent.predict_city(city, rainfall_mm, duration_hrs)

            # Custom Origin and Destination coordinates
            origin_lat = float(payload.get("origin_lat", 28.4950 if city == "Gurugram" else 30.7380))
            origin_lng = float(payload.get("origin_lng", 77.0890 if city == "Gurugram" else 76.7780))
            dest_lat = float(payload.get("dest_lat", 28.4312 if city == "Gurugram" else 30.7080))
            dest_lng = float(payload.get("dest_lng", 77.0421 if city == "Gurugram" else 76.8080))
            origin_name = payload.get("origin_name", "Start Location")
            dest_name = payload.get("dest_name", "Destination Location")

            route_result = routing_engine.plan_custom_route(
                city, 
                (origin_lat, origin_lng), 
                (dest_lat, dest_lng), 
                origin_name, 
                dest_name, 
                prediction["hotspots"]
            )
            return self._send_json(route_result)

        # 3. API: Register Complaint & Generate WhatsApp Link
        elif path == "/api/complaint":
            result = complaint_service.register_complaint(payload)
            return self._send_json(result)

        # 4. API: Save API Key Configuration Locally
        elif path == "/api/config":
            provider = payload.get("provider", "weatherapi").strip()
            key = payload.get("api_key", "").strip()
            config_file = os.path.join(BASE_DIR, "config.json")
            cfg = {}
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["WEATHER_API_PROVIDER"] = provider
            cfg["WEATHER_API_KEY"] = key
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            return self._send_json({"success": True, "provider": provider, "message": "API key saved locally to config.json!"})

        else:
            return self._send_json({"error": "Endpoint not found"}, status=404)

def run_server(port: int = None):
    if port is None:
        port = int(os.environ.get("PORT", 8000))
    server_address = ("0.0.0.0", port)
    httpd = http.server.ThreadingHTTPServer(server_address, FloodGuardRequestHandler)
    print(f"===============================================================")
    print(f"Fix Waterlogging Server Running at http://127.0.0.1:{port}")
    print(f"Interactive Map, Detour Navigation, Weather Forecast & Civic Reporting")
    print(f"===============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
