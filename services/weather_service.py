import urllib.request
import json
import os
import datetime
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

CITY_COORDINATES = {
    "Gurugram": {"lat": 28.4595, "lng": 77.0266, "query": "Gurgaon"},
    "Chandigarh": {"lat": 30.7333, "lng": 76.7794, "query": "Chandigarh"}
}

class WeatherForecastService:
    """
    Connects to your chosen weather API:
    1. WeatherAPI.com (when you paste your key in config.json)
    2. OpenWeatherMap (when provider is openweathermap)
    3. Open-Meteo (automatic zero-key fallback)
    """

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"WEATHER_API_PROVIDER": "open-meteo", "WEATHER_API_KEY": ""}

    def fetch_live_forecast(self, city: str) -> Dict[str, Any]:
        # Reload config in case user just saved their key
        self.config = self._load_config()
        provider = self.config.get("WEATHER_API_PROVIDER", "weatherapi").lower()
        api_key = self.config.get("WEATHER_API_KEY", "").strip()

        coords = CITY_COORDINATES.get(city, CITY_COORDINATES["Gurugram"])
        lat = coords["lat"]
        lng = coords["lng"]
        q_name = coords["query"]

        # CASE 1: User pasted a WeatherAPI.com key
        if api_key and api_key != "YOUR_API_KEY_HERE" and "weatherapi" in provider:
            return self._fetch_weatherapi(q_name, api_key, city)

        # CASE 2: User pasted an OpenWeatherMap key
        elif api_key and api_key != "YOUR_API_KEY_HERE" and "openweathermap" in provider:
            return self._fetch_openweathermap(lat, lng, api_key, city)

        # CASE 3: Default Free Open-Meteo API (No key required)
        else:
            return self._fetch_open_meteo(lat, lng, city)

    def _fetch_weatherapi(self, query: str, api_key: str, city: str) -> Dict[str, Any]:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={query}&days=2&aqi=no&alerts=no"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UrbanFloodGuard/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                forecastday = data.get("forecast", {}).get("forecastday", [])
                
                hourly_list = []
                total_rain_mm = 0.0
                peak_hourly_mm = 0.0
                heavy_hours = 0

                if forecastday:
                    hours = forecastday[0].get("hour", [])
                    for h in hours[:12]:
                        precip_mm = float(h.get("precip_mm", 0.0))
                        time_str = h.get("time", "")[-5:]
                        hourly_list.append({"time": time_str, "rain_mm": precip_mm})
                        total_rain_mm += precip_mm
                        if precip_mm > peak_hourly_mm:
                            peak_hourly_mm = precip_mm
                        if precip_mm >= 3.0:
                            heavy_hours += 1

                spell_dur = max(1.0, float(heavy_hours)) if heavy_hours > 0 else 2.0

                return {
                    "source": "WeatherAPI.com (Custom Key Connected)",
                    "status": "online",
                    "city": city,
                    "hourly_forecast": hourly_list,
                    "recommended_simulation": {
                        "rainfall_mm": round(max(15.0, total_rain_mm), 1),
                        "duration_hours": spell_dur,
                        "peak_intensity_mm_hr": peak_hourly_mm
                    }
                }
        except Exception as e:
            return self._generate_simulated_fallback(city, f"WeatherAPI error: {str(e)}")

    def _fetch_openweathermap(self, lat: float, lng: float, api_key: str, city: str) -> Dict[str, Any]:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&appid={api_key}&units=metric"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UrbanFloodGuard/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                forecast_list = data.get("list", [])[:8]
                
                hourly_list = []
                total_rain_mm = 0.0
                for item in forecast_list:
                    rain_obj = item.get("rain", {})
                    rain_3h = float(rain_obj.get("3h", 0.0))
                    time_str = item.get("dt_txt", "")[-8:-3]
                    hourly_list.append({"time": time_str, "rain_mm": rain_3h})
                    total_rain_mm += rain_3h

                return {
                    "source": "OpenWeatherMap (Custom Key Connected)",
                    "status": "online",
                    "city": city,
                    "hourly_forecast": hourly_list,
                    "recommended_simulation": {
                        "rainfall_mm": round(max(15.0, total_rain_mm), 1),
                        "duration_hours": 3.0,
                        "peak_intensity_mm_hr": round(total_rain_mm / 3.0, 1)
                    }
                }
        except Exception as e:
            return self._generate_simulated_fallback(city, f"OpenWeatherMap error: {str(e)}")

    def _fetch_open_meteo(self, lat: float, lng: float, city: str) -> Dict[str, Any]:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lng}&current=temperature_2m,precipitation,rain"
            f"&hourly=temperature_2m,precipitation,rain"
            f"&forecast_days=2&timezone=Asia%2FKolkata"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UrbanFloodGuard/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current_time = data.get("current", {}).get("time", "")
                hourly = data.get("hourly", {})
                times = hourly.get("time", [])
                precip = hourly.get("precipitation", [])
                temps = hourly.get("temperature_2m", [])

                # Find starting index matching the current hour (e.g. 16:00 today)
                start_idx = 0
                if current_time:
                    hour_prefix = current_time[:13] # e.g. '2026-11-03T16'
                    for i, t in enumerate(times):
                        if t.startswith(hour_prefix):
                            start_idx = i
                            break

                # Slice forward 12 hours from right now
                slice_times = times[start_idx : start_idx + 13]
                slice_precip = precip[start_idx : start_idx + 13]
                slice_temps = temps[start_idx : start_idx + 13]

                peak_hourly_mm = max(slice_precip) if slice_precip else 0.0
                total_12h_mm = round(sum(slice_precip), 1)
                heavy_hours = sum(1 for p in slice_precip if p >= 5.0)
                spell_dur = max(1.0, float(heavy_hours)) if heavy_hours > 0 else 2.0
                is_dry = total_12h_mm < 1.0

                formatted_forecast = []
                for t, p, tm in zip(slice_times, slice_precip, slice_temps):
                    try:
                        dt = datetime.datetime.fromisoformat(t)
                        t_label = dt.strftime("%I:%M %p")
                    except Exception:
                        t_label = t[-5:]
                    formatted_forecast.append({"time": t_label, "rain_mm": p, "temp_c": tm})

                return {
                    "source": "Open-Meteo Free API (Zero-Key Live)",
                    "status": "online",
                    "city": city,
                    "hourly_forecast": formatted_forecast,
                    "actual_live_rain_mm": total_12h_mm,
                    "is_dry_season": is_dry,
                    "recommended_simulation": {
                        "rainfall_mm": total_12h_mm if not is_dry else 0.0,
                        "duration_hours": spell_dur,
                        "peak_intensity_mm_hr": peak_hourly_mm
                    },
                    "message": f"Rolling 12-hour forecast from current time ({formatted_forecast[0]['time']} to {formatted_forecast[-1]['time']}) loaded."
                }
        except Exception as e:
            return self._generate_simulated_fallback(city, str(e))

    def _generate_simulated_fallback(self, city: str, err_reason: str) -> Dict[str, Any]:
        now = datetime.datetime.now()
        # Realistic monsoon scenarios from the Excel sheet (2022-2026 data pack)
        presets = {
            "Gurugram": {"rain": 66.0, "dur": 1.33, "profile": [2.0, 15.0, 32.0, 14.0, 3.0, 0.0, 0.0, 0.0]},
            "Chandigarh": {"rain": 72.7, "dur": 2.0, "profile": [1.0, 12.0, 38.0, 18.0, 3.7, 0.0, 0.0, 0.0]}
        }
        cfg = presets.get(city, presets["Gurugram"])
        return {
            "source": "Monsoon Scenario Simulator (Offline Fallback)",
            "status": "simulated",
            "city": city,
            "note": f"Live network notice: {err_reason}. Loaded authentic monsoon deluge scenario from Excel data pack.",
            "hourly_forecast": [{"time": (now + datetime.timedelta(hours=i)).strftime("%H:00"), "rain_mm": v} for i, v in enumerate(cfg["profile"])],
            "actual_live_rain_mm": cfg["rain"],
            "is_dry_season": False,
            "recommended_simulation": {
                "rainfall_mm": cfg["rain"],
                "duration_hours": cfg["dur"],
                "peak_intensity_mm_hr": max(cfg["profile"])
            },
            "message": f"Monsoon test scenario loaded: {cfg['rain']} mm in {cfg['dur']} hrs."
        }
