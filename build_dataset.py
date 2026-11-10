import json

# Master locations with historical occurrences from the Excel sheet,
# recurrence levels, coordinates, and flooding sensitivity profiles.

GEOCODED_HOTSPOTS = {
    "Gurugram": [
        {
            "id": "GGN-HOT-01",
            "name": "Sohna Road",
            "type": "Road / highway",
            "lat": 28.4110,
            "lng": 77.0440,
            "total_events": 9,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 20.0,
            "severity_weight": 0.95,
            "description": "Chronic bottleneck between Subhash Chowk and Badshahpur; severe water buildup on both carriageways."
        },
        {
            "id": "GGN-HOT-02",
            "name": "Golf Course Extension Road",
            "type": "Road / highway",
            "lat": 28.4180,
            "lng": 77.0950,
            "total_events": 8,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 22.0,
            "severity_weight": 0.92,
            "description": "Repeated flooding at key junctions and service lanes, heavy traffic paralysis during monsoon."
        },
        {
            "id": "GGN-HOT-03",
            "name": "Narsinghpur (NH-48)",
            "type": "Expressway / Service Lane",
            "lat": 28.4215,
            "lng": 76.9945,
            "total_events": 8,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 15.0,
            "severity_weight": 0.98,
            "description": "Notorious 3-4 feet water accumulation on NH-48 main carriage and service lanes; halts Delhi-Jaipur traffic."
        },
        {
            "id": "GGN-HOT-04",
            "name": "Rajiv Chowk",
            "type": "Chowk / junction",
            "lat": 28.4555,
            "lng": 77.0324,
            "total_events": 8,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 25.0,
            "severity_weight": 0.90,
            "description": "Major intersection connecting Old Gurugram, NH-48 and Sohna road. Underpass and slip roads submerge."
        },
        {
            "id": "GGN-HOT-05",
            "name": "Hero Honda Chowk",
            "type": "Chowk / Underpass",
            "lat": 28.4416,
            "lng": 77.0097,
            "total_events": 7,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 22.0,
            "severity_weight": 0.92,
            "description": "Badshahpur drain overflow spot. Historic site of Gurujam; underpasses prone to prompt closure."
        },
        {
            "id": "GGN-HOT-06",
            "name": "Udyog Vihar",
            "type": "Colony / industrial",
            "lat": 28.5020,
            "lng": 77.0870,
            "total_events": 7,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 24.0,
            "severity_weight": 0.88,
            "description": "Critical IT / Industrial cluster near Delhi border; internal roads face severe knee-deep flooding."
        },
        {
            "id": "GGN-HOT-07",
            "name": "Subhash Chowk",
            "type": "Chowk / junction",
            "lat": 28.4312,
            "lng": 77.0421,
            "total_events": 6,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 25.0,
            "severity_weight": 0.86,
            "description": "Sohna Road connector. Underpass flooded for hours during moderate to heavy rain."
        },
        {
            "id": "GGN-HOT-08",
            "name": "Basai Chowk",
            "type": "Chowk / junction",
            "lat": 28.4635,
            "lng": 76.9995,
            "total_events": 6,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 22.0,
            "severity_weight": 0.85,
            "description": "Low-lying junction connecting Old Gurugram and Dwarka Expressway sectors; poor natural drainage."
        },
        {
            "id": "GGN-HOT-09",
            "name": "IFFCO Chowk",
            "type": "Chowk / junction",
            "lat": 28.4725,
            "lng": 77.0725,
            "total_events": 4,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 28.0,
            "severity_weight": 0.78,
            "description": "Key transit hub for buses & metro commuters. Slip lanes and pedestrian underpasses waterlog."
        },
        {
            "id": "GGN-HOT-10",
            "name": "Golf Course Road",
            "type": "Road / highway",
            "lat": 28.4680,
            "lng": 77.0980,
            "total_events": 3,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 30.0,
            "severity_weight": 0.75,
            "description": "Rapid Metro corridor and underpasses (Genpact, DLF Phase 1) vulnerable during intense cloudbursts."
        },
        {
            "id": "GGN-HOT-11",
            "name": "Khandsa Road",
            "type": "Road / highway",
            "lat": 28.4460,
            "lng": 77.0010,
            "total_events": 3,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 20.0,
            "severity_weight": 0.76,
            "description": "Near NH-48 culverts; dense traffic with heavy backflow from clogged storm channels."
        },
        {
            "id": "GGN-HOT-12",
            "name": "Sector 14 Gurugram",
            "type": "Sector / Market",
            "lat": 28.4730,
            "lng": 77.0450,
            "total_events": 3,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 25.0,
            "severity_weight": 0.72,
            "description": "Commercial heart of Old Gurugram; market parking and main road experience steady pooling."
        },
        {
            "id": "GGN-HOT-13",
            "name": "Vatika Chowk",
            "type": "Chowk / junction",
            "lat": 28.4025,
            "lng": 77.0435,
            "total_events": 3,
            "recurrence": "Chronic",
            "drain_threshold_mm_hr": 28.0,
            "severity_weight": 0.74,
            "description": "Intersection of Sohna Road and Southern Peripheral Road (SPR); heavy run-off from Aravalli foothills."
        },
        {
            "id": "GGN-HOT-14",
            "name": "Sheetla Mata Road",
            "type": "Road / highway",
            "lat": 28.4790,
            "lng": 77.0210,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 25.0,
            "severity_weight": 0.65,
            "description": "High footfall religious and commuter corridor; water enters adjoining residential colonies."
        },
        {
            "id": "GGN-HOT-15",
            "name": "Palam Vihar",
            "type": "Colony / area",
            "lat": 28.5100,
            "lng": 77.0340,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 26.0,
            "severity_weight": 0.62,
            "description": "Low-lying blocks C & D suffer prolonged water retention after heavy spells."
        },
        {
            "id": "GGN-HOT-16",
            "name": "Cyber City / Shankar Chowk",
            "type": "Commercial Corridor",
            "lat": 28.4950,
            "lng": 77.0890,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 32.0,
            "severity_weight": 0.68,
            "description": "Entry point to DLF Cyber City; slow discharge leads to rapid traffic tailbacks onto NH-48."
        },
        {
            "id": "GGN-HOT-17",
            "name": "Dwarka Expressway (Sector 100-104)",
            "type": "Road / highway",
            "lat": 28.4850,
            "lng": 76.9800,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 30.0,
            "severity_weight": 0.60,
            "description": "New developing sectors; incomplete roadside drainage creates large temporary lakes on service lanes."
        }
    ],
    "Chandigarh": [
        {
            "id": "CHD-HOT-01",
            "name": "Madhya Marg (Sec 26 & Tribune Chowk Stretch)",
            "type": "Arterial Highway",
            "lat": 30.7250,
            "lng": 76.8020,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 15.0,
            "severity_weight": 0.88,
            "description": "Primary east-west arterial; drain capacity designed for only 15 mm/hr, collapses during intense bursts."
        },
        {
            "id": "CHD-HOT-02",
            "name": "Tribune Chowk",
            "type": "Chowk / junction",
            "lat": 30.7055,
            "lng": 76.7925,
            "total_events": 2,
            "recurrence": "Official Hotspot",
            "drain_threshold_mm_hr": 16.0,
            "severity_weight": 0.86,
            "description": "Official MC 2025 hotspot list; primary Tricity gateway with knee-deep water disrupting Panchkula-Zirakpur movement."
        },
        {
            "id": "CHD-HOT-03",
            "name": "Hallomajra",
            "type": "Colony / area",
            "lat": 30.6920,
            "lng": 76.8010,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 14.0,
            "severity_weight": 0.84,
            "description": "Low-lying area near airport road; water enters ground-floor houses and interior links."
        },
        {
            "id": "CHD-HOT-04",
            "name": "Industrial Area Phase I & II",
            "type": "Colony / area",
            "lat": 30.7080,
            "lng": 76.8080,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 15.0,
            "severity_weight": 0.82,
            "description": "Underpasses and internal commercial roads flood quickly; CTU workshop and railway approaches affected."
        },
        {
            "id": "CHD-HOT-05",
            "name": "Industrial Area Underpass (Railway Station)",
            "type": "Underpass / bridge",
            "lat": 30.7020,
            "lng": 76.8150,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 12.0,
            "severity_weight": 0.94,
            "description": "Submerged underpass; fire brigade rescues required for stranded cars during peak rains."
        },
        {
            "id": "CHD-HOT-06",
            "name": "Manimajra (Shastri Nagar)",
            "type": "Colony / area",
            "lat": 30.7230,
            "lng": 76.8450,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 15.0,
            "severity_weight": 0.80,
            "description": "Adjacent to seasonal rivulet; runoff overwhelms storm sewers causing prolonged stagnation."
        },
        {
            "id": "CHD-HOT-07",
            "name": "Sukhna Choe Low-Level Bridges & Kishangarh",
            "type": "Underpass / bridge",
            "lat": 30.7350,
            "lng": 76.8180,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 18.0,
            "severity_weight": 0.90,
            "description": "Low bridges submerged whenever Sukhna lake floodgates open; police enforce mandatory diversions."
        },
        {
            "id": "CHD-HOT-08",
            "name": "Southern Sectors (33, 34, 35, 45)",
            "type": "Sector / Residential",
            "lat": 30.7180,
            "lng": 76.7650,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 20.0,
            "severity_weight": 0.78,
            "description": "Sectors 33, 34, 35 and 45 show repeat road cave-ins and flooded roundabouts (GMCH-32 & JW Marriott)."
        },
        {
            "id": "CHD-HOT-09",
            "name": "ISBT-17 & Sector 22 Mobile Market",
            "type": "Commercial / Transit",
            "lat": 30.7350,
            "lng": 76.7750,
            "total_events": 2,
            "recurrence": "Repeat",
            "drain_threshold_mm_hr": 18.0,
            "severity_weight": 0.76,
            "description": "Basements and showroom entries submerge in Sector 22 market; bus terminals slow down."
        },
        {
            "id": "CHD-HOT-10",
            "name": "Toga Bridge (New Chandigarh Link)",
            "type": "Underpass / bridge",
            "lat": 30.7850,
            "lng": 76.7320,
            "total_events": 1,
            "recurrence": "Single (Severe)",
            "drain_threshold_mm_hr": 20.0,
            "severity_weight": 0.85,
            "description": "Seasonal torrent bridge on periphery; recorded vehicle washaway during June deluge."
        }
    ]
}

HELPLINES = {
    "Gurugram": {
        "whatsapp": "7840001817",
        "toll_free": "1800-180-1817",
        "landline": "0124-4753555",
        "emergency": "112",
        "authority": "GMDA Grievance / Flood Control Cell",
        "note": "GMDA grievance WhatsApp handles GMDA, MCG and Manesar MC. Photo submission supported."
    },
    "Chandigarh": {
        "whatsapp": "7840001817", # Fallback grievance channel
        "toll_free": "0172-2540200",
        "landline": "0172-2738082",
        "emergency": "112",
        "authority": "Chandigarh Municipal Corporation (MC) Flood Control Room",
        "note": "Primary control room: 0172-2540200 (Sector 15) & 112 for emergency waterlogging assistance."
    }
}

if __name__ == "__main__":
    with open("C:/Users/Jatin/.gemini/antigravity/scratch/urban-flood-guard/data/geocoded_locations.json", "w", encoding="utf-8") as f:
        json.dump(GEOCODED_HOTSPOTS, f, indent=2)
    with open("C:/Users/Jatin/.gemini/antigravity/scratch/urban-flood-guard/data/helplines.json", "w", encoding="utf-8") as f:
        json.dump(HELPLINES, f, indent=2)
    print("Geocoded hotspots and helpline databases successfully created!")
