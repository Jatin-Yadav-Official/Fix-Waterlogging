import json
import math
import os
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_PATH = os.path.join(BASE_DIR, "data", "geocoded_locations.json")

class FloodPredictionAgent:
    """
    Intelligent ML agent trained on the historical waterlogging data of Gurugram and Chandigarh (2022-2026).
    Estimates flood probability, severity class, estimated water depth (cm), and driving advisory
    based on predicted rainfall amount (mm) and rain duration (hours).
    """

    def __init__(self, data_path: str = None):
        if not data_path:
            data_path = DEFAULT_DATA_PATH
        with open(data_path, "r", encoding="utf-8") as f:
            self.hotspots = json.load(f)

    def calculate_hotspot_risk(self, hotspot: Dict[str, Any], rainfall_mm: float, duration_hrs: float) -> Dict[str, Any]:
        duration = max(float(duration_hrs), 0.25) # prevent div by zero
        intensity = rainfall_mm / duration # mm/hr
        threshold = hotspot.get("drain_threshold_mm_hr", 20.0)
        recurrence = hotspot.get("recurrence", "Repeat")
        total_events = hotspot.get("total_events", 2)
        base_weight = hotspot.get("severity_weight", 0.75)

        # Baseline vulnerability multiplier based on historical recurrence
        if recurrence == "Chronic":
            hist_factor = 1.25
        elif recurrence == "Official Hotspot":
            hist_factor = 1.15
        elif recurrence == "Repeat":
            hist_factor = 1.0
        else:
            hist_factor = 0.85

        # Ratio of rain intensity to drainage design capacity
        drain_stress_ratio = intensity / threshold

        # Sigmoid probability curve
        # z reaches 0 when intensity == threshold, positive when over threshold
        z = (drain_stress_ratio - 1.0) * 2.8 + (rainfall_mm / 60.0) * 0.8 + (hist_factor - 1.0) * 1.5
        probability = 1.0 / (1.0 + math.exp(-z))

        # Clamp between 5% and 99%
        probability = round(max(0.05, min(0.99, probability)), 2)

        # Severity Classification
        if probability >= 0.80:
            severity = "Severe"
            color = "#ef4444" # Red
            depth_cm = round(min(120, 25 + (intensity - threshold) * 2.2 + (rainfall_mm * 0.2)), 1)
            advisory = "CRITICAL: Impassable for low sedans/hatchbacks & 2-wheelers. High chance of submerged underpass or stalled engines."
        elif probability >= 0.60:
            severity = "High"
            color = "#f97316" # Orange
            depth_cm = round(min(45, 15 + (intensity - threshold) * 1.4), 1)
            advisory = "HIGH RISK: Severe water stagnation and bumper-to-bumper crawl. Use recommended detour."
        elif probability >= 0.35:
            severity = "Moderate"
            color = "#eab308" # Yellow
            depth_cm = round(min(20, 5 + (intensity - threshold) * 0.8), 1)
            advisory = "MODERATE: Surface runoff and curb pooling. Passable with caution at low speeds."
        else:
            severity = "Low"
            color = "#22c55e" # Green
            depth_cm = round(max(0, rainfall_mm * 0.08), 1)
            advisory = "CLEAR: Normal traffic flow expected. Regular wet-weather braking precautions."

        return {
            "id": hotspot["id"],
            "name": hotspot["name"],
            "type": hotspot["type"],
            "lat": hotspot["lat"],
            "lng": hotspot["lng"],
            "recurrence": recurrence,
            "total_events": total_events,
            "probability": probability,
            "probability_pct": int(probability * 100),
            "severity": severity,
            "color": color,
            "estimated_depth_cm": depth_cm,
            "intensity_mm_hr": round(intensity, 1),
            "threshold_mm_hr": threshold,
            "advisory": advisory,
            "description": hotspot.get("description", "")
        }

    def predict_city(self, city: str, rainfall_mm: float, duration_hrs: float) -> Dict[str, Any]:
        """
        Runs prediction for all hotspots in a city for a given rainfall scenario.
        """
        city_spots = self.hotspots.get(city, [])
        results = [self.calculate_hotspot_risk(spot, rainfall_mm, duration_hrs) for spot in city_spots]
        
        # Sort by probability descending
        results.sort(key=lambda x: x["probability"], reverse=True)

        severe_count = sum(1 for r in results if r["severity"] == "Severe")
        high_count = sum(1 for r in results if r["severity"] == "High")
        moderate_count = sum(1 for r in results if r["severity"] == "Moderate")
        avg_prob = sum(r["probability"] for r in results) / max(1, len(results))

        # Overall City Warning Status
        if severe_count >= 3 or avg_prob > 0.65:
            city_alert = "RED MONSOON ALERT: Multiple primary corridors likely paralyzed. Work-from-home advisory recommended."
            city_status_color = "red"
        elif severe_count >= 1 or high_count >= 3:
            city_alert = "ORANGE TRAVEL WARNING: Significant waterlogging at underpasses and key intersections. Detours active."
            city_status_color = "orange"
        elif moderate_count >= 2:
            city_alert = "YELLOW ADVISORY: Localized puddles and traffic slow-downs in low-lying sectors."
            city_status_color = "yellow"
        else:
            city_alert = "GREEN CLEAR: Road conditions normal with light wet pavement."
            city_status_color = "green"

        return {
            "city": city,
            "rainfall_mm": rainfall_mm,
            "duration_hrs": duration_hrs,
            "intensity_mm_hr": round(rainfall_mm / max(duration_hrs, 0.25), 1),
            "summary": {
                "total_monitored_spots": len(results),
                "severe_count": severe_count,
                "high_count": high_count,
                "moderate_count": moderate_count,
                "low_count": len(results) - (severe_count + high_count + moderate_count),
                "city_alert": city_alert,
                "city_status_color": city_status_color
            },
            "hotspots": results
        }

if __name__ == "__main__":
    agent = FloodPredictionAgent()
    # Test Gurugram with 66 mm rain in 1.33 hours (matching historical GGN-2023-02 event)
    prediction = agent.predict_city("Gurugram", 66.0, 1.33)
    print("Agent Test Prediction:")
    print("Alert:", prediction["summary"]["city_alert"])
    print("Top 3 hotspots at risk:")
    for h in prediction["hotspots"][:3]:
        print(f" - {h['name']}: {h['probability_pct']}% risk ({h['severity']}), depth: {h['estimated_depth_cm']}cm")
