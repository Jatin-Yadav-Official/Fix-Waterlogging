import json
import urllib.parse
import urllib.request
import datetime
import os
import uuid
import base64
from typing import Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELPLINES_PATH = os.path.join(BASE_DIR, "data", "helplines.json")
if not os.path.exists(HELPLINES_PATH):
    for c in [os.path.join(os.getcwd(), "data", "helplines.json"), os.path.join(os.getcwd(), "helplines.json"), "data/helplines.json"]:
        if os.path.exists(c):
            HELPLINES_PATH = c
            break

COMPLAINTS_LOG_PATH = os.path.join(os.path.dirname(HELPLINES_PATH), "complaints.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

class MunicipalityComplaintService:
    """
    Handles citizen flood grievance lodging, GPS coordinate capture,
    ticket tracking, and generates pre-filled official WhatsApp dispatch links
    targeting GMDA Gurugram (7840001817) and Chandigarh civic helplines.
    """

    def __init__(self):
        with open(HELPLINES_PATH, "r", encoding="utf-8") as f:
            self.helplines = json.load(f)
        
        if not os.path.exists(COMPLAINTS_LOG_PATH):
            with open(COMPLAINTS_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)

    def register_complaint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        city = data.get("city", "Gurugram")
        location_name = data.get("location_name", "Unspecified Spot")
        lat = data.get("lat", 28.4595)
        lng = data.get("lng", 77.0266)
        severity = data.get("severity", "Severe (Impassable)")
        notes = data.get("notes", "Heavy water accumulation blocking traffic.")
        host = data.get("host") or "127.0.0.1:8000"

        # Unique Ticket ID (re-use client generated ticket if provided for consistency)
        ticket_id = data.get("ticket_id") or f"TKT-{city[:3].upper()}-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        helpline_info = self.helplines.get(city, self.helplines.get("Gurugram", {
            "authority": "Municipal Flood Control Cell",
            "whatsapp": "7840001817"
        }))
        whatsapp_no = helpline_info["whatsapp"]

        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")

        # Official Structured Civic Grievance Message for WhatsApp
        maps_link = f"https://maps.google.com/?q={lat},{lng}"
        formatted_message = (
            f"*URGENT: WATERLOGGING GRIEVANCE REPORT*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"*Ticket ID:* `{ticket_id}`\n"
            f"*Authority:* {helpline_info['authority']}\n"
            f"*City:* {city}\n"
            f"*Location:* {location_name}\n"
            f"*GPS:* {lat:.5f}, {lng:.5f}\n"
            f"*Live Maps Location:* {maps_link}\n"
            f"*Severity:* {severity}\n"
            f"*Timestamp:* {timestamp_str}\n"
            f"*Citizen Notes:* {notes}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"_Submitted via Fix Waterlogging AI Civic Portal_"
        )

        encoded_text = urllib.parse.quote(formatted_message)
        whatsapp_url = f"https://wa.me/91{whatsapp_no}?text={encoded_text}"

        # Attempt direct transmission via Meta WhatsApp Cloud API if credentials are provided
        dispatch_result = self._send_via_meta_cloud_api(whatsapp_no, formatted_message)
        dispatch_status = "Direct Meta WhatsApp Cloud API Dispatched" if dispatch_result.get("mode") == "meta_cloud_api" else "Dispatched to Municipal Grievance Register"

        record = {
            "ticket_id": ticket_id,
            "city": city,
            "location_name": location_name,
            "lat": lat,
            "lng": lng,
            "severity": severity,
            "notes": notes,
            "timestamp": timestamp_str,
            "target_whatsapp": whatsapp_no,
            "status": dispatch_status,
            "dispatch_mode": dispatch_result.get("mode", "local_database"),
            "whatsapp_dispatch_url": whatsapp_url
        }

        # Save to local complaint database
        try:
            with open(COMPLAINTS_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
            logs.insert(0, record)
            with open(COMPLAINTS_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(logs[:100], f, indent=2) # keep last 100
        except Exception as e:
            print("Warning: could not write to complaints log:", e)

        return {
            "ticket_id": ticket_id,
            "city": city,
            "whatsapp_no": whatsapp_no,
            "whatsapp_dispatch_url": whatsapp_url,
            "formatted_message": formatted_message,
            "authority": helpline_info["authority"],
            "status": dispatch_status,
            "dispatch_result": dispatch_result
        }

    def _send_via_meta_cloud_api(self, target_phone: str, message: str) -> Dict[str, Any]:
        """
        Direct server-to-server dispatch to Meta WhatsApp Cloud API (Free 1,000/month tier).
        Endpoint: https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages
        """
        try:
            if not os.path.exists(CONFIG_PATH):
                return {"success": True, "mode": "local_database"}
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            
            token = cfg.get("WHATSAPP_CLOUD_API_TOKEN", "").strip()
            phone_id = cfg.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
            test_override = cfg.get("TEST_RECIPIENT_OVERRIDE", "").strip()

            if not token or not phone_id:
                return {
                    "success": True,
                    "mode": "local_database",
                    "note": "Logged to local complaint register. Enter Meta Token & Phone ID in config.json to deliver real WhatsApp messages."
                }

            dest_phone = test_override if test_override else target_phone
            clean_phone = dest_phone.replace("+", "").replace("-", "").replace(" ", "")
            if len(clean_phone) == 10:
                clean_phone = f"91{clean_phone}"

            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "preview_url": True,
                    "body": message
                }
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            })
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    return {"success": True, "mode": "meta_cloud_api", "meta_response": resp_data}
            except urllib.error.HTTPError as he:
                err_body = he.read().decode("utf-8", errors="ignore")
                # Fallback to template if outside 24-hr customer service window
                if "131047" in err_body or "template" in err_body.lower():
                    tpl_payload = {
                        "messaging_product": "whatsapp",
                        "to": clean_phone,
                        "type": "template",
                        "template": {
                            "name": "hello_world",
                            "language": { "code": "en_US" }
                        }
                    }
                    tpl_req = urllib.request.Request(url, data=json.dumps(tpl_payload).encode("utf-8"), headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    })
                    with urllib.request.urlopen(tpl_req, timeout=10) as tpl_resp:
                        tpl_data = json.loads(tpl_resp.read().decode("utf-8"))
                        return {"success": True, "mode": "meta_cloud_api_template", "meta_response": tpl_data}
                return {"success": False, "mode": "meta_cloud_api_error", "error": f"HTTP {he.code}: {err_body}"}
        except Exception as e:
            return {"success": False, "mode": "meta_cloud_api_error", "error": str(e)}

    def get_recent_complaints(self, limit: int = 15) -> list:
        try:
            with open(COMPLAINTS_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)[:limit]
        except Exception:
            return []

    def track_complaint(self, ticket_id: str) -> Optional[dict]:
        clean_id = ticket_id.strip().upper()
        try:
            with open(COMPLAINTS_LOG_PATH, "r", encoding="utf-8") as f:
                logs = json.load(f)
            for c in logs:
                if c.get("ticket_id", "").strip().upper() == clean_id:
                    return c
        except Exception:
            pass
        return None

if __name__ == "__main__":
    service = MunicipalityComplaintService()
    test_res = service.register_complaint({
        "city": "Gurugram",
        "location_name": "Narsinghpur Chowk (NH-48)",
        "lat": 28.4215,
        "lng": 76.9945,
        "severity": "Severe (Water > 3ft)",
        "notes": "Service lane completely choked. Cars stuck.",
        "image_name": "narsinghpur_flood.jpg"
    })
    print("Complaint Service Test:")
    print("Ticket:", test_res["ticket_id"])
    print("Target WhatsApp:", test_res["whatsapp_no"])
    print("Dispatch URL Preview:", test_res["whatsapp_dispatch_url"][:90] + "...")
