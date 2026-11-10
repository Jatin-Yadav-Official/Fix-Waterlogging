import urllib.request
import json
import sys
import datetime

def fetch_weather(city_name="Gurugram", lat=28.4595, lng=77.0266):
    print(f"\n[*] Requesting rolling 12-hour live forecast for {city_name}...")
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lng}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m"
        f"&hourly=temperature_2m,precipitation,rain,relative_humidity_2m"
        f"&forecast_days=2&timezone=Asia%2FKolkata"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "UrbanFloodGuard/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            current = data.get("current", {})
            hourly = data.get("hourly", {})
            current_time = current.get("time", "") # e.g. '2026-11-03T16:00'

            times = hourly.get("time", [])
            precip = hourly.get("precipitation", [])
            temps = hourly.get("temperature_2m", [])
            humidity = hourly.get("relative_humidity_2m", [])

            # Match starting index with current hour
            start_idx = 0
            if current_time:
                hour_prefix = current_time[:13]
                for i, t in enumerate(times):
                    if t.startswith(hour_prefix):
                        start_idx = i
                        break

            slice_indices = range(start_idx, min(start_idx + 13, len(times)))
            
            print(f"==========================================================================")
            print(f"LIVE ROLLING 12-HOUR FORECAST: {city_name.upper()}")
            print(f"==========================================================================")
            print(f"Request Time:       {current_time.replace('T', ' ')} IST")
            print(f"Current Temp:       {current.get('temperature_2m')} deg C")
            print(f"Current Humidity:   {current.get('relative_humidity_2m')} %")
            print(f"Current Wind Speed: {current.get('wind_speed_10m')} km/h")
            print(f"--------------------------------------------------------------------------")
            print(f"Hour                 | Temperature | Rainfall (mm) | Humidity | Sky Condition")
            print(f"---------------------+-------------+---------------+----------+---------------")
            
            total_rain = 0.0
            for idx in slice_indices:
                t_str = times[idx]
                dt = datetime.datetime.fromisoformat(t_str)
                time_formatted = dt.strftime("%I:%M %p (%a)")
                p = precip[idx]
                tm = temps[idx]
                h = humidity[idx] if idx < len(humidity) else 0
                total_rain += p
                cond = "Wet Rain" if p > 0 else "Clear / Dry"
                print(f"{time_formatted:20} |   {tm:4.1f} C    |    {p:4.1f} mm    |   {h:2d} %   | {cond}")

            print(f"--------------------------------------------------------------------------")
            print(f"Total Cumulative Rain in next 12 hours: {total_rain:.1f} mm")
            print(f"==========================================================================\n")
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    coords = {
        "chandigarh": ("Chandigarh, UT", 30.7333, 76.7794),
        "gurugram": ("Gurugram, Haryana", 28.4595, 77.0266),
        "gurgaon": ("Gurugram, Haryana", 28.4595, 77.0266),
        "jalandhar": ("Jalandhar, Punjab", 31.3260, 75.5762)
    }
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "gurugram"
    name, lat, lng = coords.get(target, ("Gurugram, Haryana", 28.4595, 77.0266))
    fetch_weather(name, lat, lng)
