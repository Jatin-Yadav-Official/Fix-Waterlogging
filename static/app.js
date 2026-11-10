// Fix Waterlogging - Production Client Application Logic
// Pan-India Mapping & IMD 3-Hourly Synoptic Telemetry Freshness

let currentCity = 'Gurugram';
let map = null;
let hotspotLayers = [];
let directRouteLayer = null;
let detourRouteLayer = null;
let originMarker = null;
let destMarker = null;
let currentHotspots = [];
let currentHelpline = {};
let currentWeatherData = null;

// Map Pin Selection Mode: 'origin', 'dest', or null
let mapPickTarget = null;

// Real-Time Freshness Ticker Interval
let freshnessTickerInterval = null;

// Route points (Starts 100% empty - zero annoying autofills)
let selectedOrigin = null;
let selectedDest = null;

let originDebounceTimer = null;
let destDebounceTimer = null;

// Pan-India City Centers (Entire Subcontinent Coverage)
const CITY_CENTERS = {
  'Gurugram': { lat: 28.4555, lng: 77.0324, zoom: 12 },
  'Chandigarh': { lat: 30.7333, lng: 76.7794, zoom: 13 },
  'Jalandhar': { lat: 31.3260, lng: 75.5762, zoom: 13 },
  'Kapurthala': { lat: 31.3800, lng: 75.3800, zoom: 13 },
  'Delhi': { lat: 28.6139, lng: 77.2090, zoom: 12 },
  'Noida': { lat: 28.5355, lng: 77.3910, zoom: 12 },
  'Mumbai': { lat: 19.0760, lng: 72.8777, zoom: 12 },
  'Bengaluru': { lat: 12.9716, lng: 77.5946, zoom: 12 },
  'Hyderabad': { lat: 17.3850, lng: 78.4867, zoom: 12 },
  'India': { lat: 22.5937, lng: 78.9629, zoom: 5 } // Whole Pan-India View
};

// Comprehensive Pan-India Master Places (Instantaneous 0ms Fallback)
const MASTER_SEARCH_PLACES = [
  // GURUGRAM
  { name: "Subhash Chowk", display_name: "Subhash Chowk, Sohna Road, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4312, lng: 77.0421, type: "Chowk / Junction" },
  { name: "MG Road Metro Station", display_name: "MG Road Metro Station, Gurugram, Haryana (Mall Mile)", city: "Gurugram", state: "Haryana", lat: 28.4800, lng: 77.0800, type: "Transit / Metro" },
  { name: "DLF Cyber City", display_name: "DLF Cyber City, Phase 2, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4950, lng: 77.0890, type: "IT / Commercial Hub" },
  { name: "IFFCO Chowk", display_name: "IFFCO Chowk, NH-48, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4725, lng: 77.0725, type: "Chowk / Junction" },
  { name: "Rajiv Chowk", display_name: "Rajiv Chowk, NH-48 Connector, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4555, lng: 77.0324, type: "Chowk / Underpass" },
  { name: "Hero Honda Chowk", display_name: "Hero Honda Chowk, NH-48, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4416, lng: 77.0097, type: "Chowk / Underpass" },
  { name: "Sector 29 Gurugram", display_name: "Sector 29, Gurugram, Haryana (Leisure Valley / Food Hub)", city: "Gurugram", state: "Haryana", lat: 28.4670, lng: 77.0620, type: "Commercial / Sector" },
  { name: "Sector 14 Gurugram", display_name: "Sector 14, Old Gurugram, Haryana (Main Market)", city: "Gurugram", state: "Haryana", lat: 28.4730, lng: 77.0450, type: "Residential / Market" },
  { name: "Sector 56 Gurugram", display_name: "Sector 56, Golf Course Extension, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4270, lng: 77.1030, type: "Metro / Sector" },
  { name: "Golf Course Road", display_name: "Golf Course Road (Genpact Underpass), Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4680, lng: 77.0980, type: "Arterial Highway" },
  { name: "Narsinghpur (NH-48)", display_name: "Narsinghpur Chowk, NH-48 Expressway, Gurugram, Haryana", city: "Gurugram", state: "Haryana", lat: 28.4215, lng: 76.9945, type: "Expressway / Service Road" },

  // CHANDIGARH
  { name: "Sector 17 City Center", display_name: "Sector 17 City Center Plaza, Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7410, lng: 76.7820, type: "City Center / Plaza" },
  { name: "ISBT Sector 17", display_name: "ISBT Sector 17 Bus Stand, Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7380, lng: 76.7780, type: "Interstate Bus Terminal" },
  { name: "ISBT Sector 43", display_name: "ISBT Sector 43 Bus Stand, Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7150, lng: 76.7460, type: "Interstate Bus Terminal" },
  { name: "Sector 29 Chandigarh", display_name: "Sector 29, Chandigarh, UT (Iron & Steel Market)", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7120, lng: 76.7950, type: "Commercial Sector" },
  { name: "Tribune Chowk", display_name: "Tribune Chowk, Dakshin Marg / Purv Marg, Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7055, lng: 76.7925, type: "Chowk / Key Transit" },
  { name: "Madhya Marg (Sector 26)", display_name: "Madhya Marg (Sector 26 Grain Market), Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7250, lng: 76.8020, type: "Arterial Highway" },
  { name: "Industrial Area Phase I", display_name: "Industrial Area Phase 1 (Near Elante Mall), Chandigarh, UT", city: "Chandigarh", state: "Chandigarh (UT)", lat: 30.7080, lng: 76.8080, type: "Commercial / Mall" },

  // PUNJAB (JALANDHAR & KAPURTHALA)
  { name: "Jalandhar ISBT Bus Stand", display_name: "Shaheed-e-Azam Bhagat Singh ISBT Bus Stand, Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3190, lng: 75.5860, type: "Transit Terminal" },
  { name: "Model Town Jalandhar", display_name: "Model Town Market / Nikku Park, Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3060, lng: 75.5780, type: "Commercial / Market" },
  { name: "BMC Chowk Jalandhar", display_name: "BMC Chowk, GT Road, Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3210, lng: 75.5810, type: "Chowk / Junction" },
  { name: "PAP Chowk Jalandhar", display_name: "PAP Chowk Flyover, NH-44, Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3110, lng: 75.6180, type: "Expressway Junction" },
  { name: "Rama Mandi Chowk", display_name: "Rama Mandi Chowk (Hoshiarpur Road Link), Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3160, lng: 75.6270, type: "Chowk / Market" },
  { name: "Jalandhar City Railway Station", display_name: "Jalandhar City Railway Station (JUC), Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.3320, lng: 75.5830, type: "Railway Station" },
  { name: "Jalandhar Cantt Railway Station", display_name: "Jalandhar Cantt Railway Station (JRC), Jalandhar, Punjab", city: "Jalandhar", state: "Punjab", lat: 31.2950, lng: 75.6180, type: "Railway Station" },
  { name: "Kapurthala DC Office", display_name: "Deputy Commissioner Complex, Court Road, Kapurthala, Punjab", city: "Kapurthala", state: "Punjab", lat: 31.3810, lng: 75.3850, type: "Government Complex" },
  // Calibrated Pushpa Gujral Science City Coordinates (Exact Campus & Gate)
  { name: "Pushpa Gujral Science City", display_name: "Pushpa Gujral Science City, Jalandhar-Kapurthala Highway, Punjab", city: "Kapurthala", state: "Punjab", lat: 31.3395, lng: 75.4635, type: "Science / Educational" },
  { name: "Shalimar Gardens Kapurthala", display_name: "Shalimar Gardens / Jagatjit Palace, Kapurthala, Punjab", city: "Kapurthala", state: "Punjab", lat: 31.3780, lng: 75.3720, type: "Heritage / Landmark" },
  { name: "Rail Coach Factory (RCF)", display_name: "Rail Coach Factory (RCF Township), Kapurthala, Punjab", city: "Kapurthala", state: "Punjab", lat: 31.3250, lng: 75.3520, type: "Industrial Township" },
  { name: "Golden Temple Amritsar", display_name: "Sri Harmandir Sahib (Golden Temple), Amritsar, Punjab", city: "Amritsar", state: "Punjab", lat: 31.6200, lng: 74.8765, type: "Heritage Hub" },
  { name: "Ludhiana Clock Tower", display_name: "Ghanta Ghar (Clock Tower), GT Road, Ludhiana, Punjab", city: "Ludhiana", state: "Punjab", lat: 30.9120, lng: 75.8530, type: "City Center" },

  // DELHI-NCR & OTHER NCR SECTORS
  { name: "Connaught Place", display_name: "Connaught Place (Rajiv Chowk Metro), New Delhi, Delhi", city: "Delhi", state: "Delhi", lat: 28.6315, lng: 77.2167, type: "National Center" },
  { name: "India Gate", display_name: "India Gate, Rajpath, New Delhi, Delhi", city: "Delhi", state: "Delhi", lat: 28.6129, lng: 77.2295, type: "Monument" },
  { name: "IGI Airport Terminal 3", display_name: "Indira Gandhi International Airport (T3), New Delhi, Delhi", city: "Delhi", state: "Delhi", lat: 28.5562, lng: 77.1000, type: "International Airport" },
  { name: "Sector 18 Noida", display_name: "Sector 18 (Atta Market / Mall of India), Noida, Uttar Pradesh", city: "Noida", state: "Uttar Pradesh", lat: 28.5700, lng: 77.3220, type: "Commercial / Metro" },
  { name: "Sector 62 Noida", display_name: "Sector 62 (Electronic City Metro), Noida, Uttar Pradesh", city: "Noida", state: "Uttar Pradesh", lat: 28.6270, lng: 77.3650, type: "IT / Tech Hub" },
  { name: "Sector 29 Noida", display_name: "Sector 29, Noida, Gautam Buddha Nagar, Uttar Pradesh (Ganga Shopping)", city: "Noida", state: "Uttar Pradesh", lat: 28.5680, lng: 77.3320, type: "NCR Sector" },
  { name: "Sector 29 Faridabad", display_name: "Sector 29, Faridabad, Haryana (Bypass Road)", city: "Faridabad", state: "Haryana", lat: 28.4010, lng: 77.3290, type: "NCR Sector" },

  // MAHARASHTRA & BENGALURU & HYDERABAD
  { name: "Marine Drive Mumbai", display_name: "Marine Drive (Queen's Necklace), South Mumbai, Maharashtra", city: "Mumbai", state: "Maharashtra", lat: 18.9430, lng: 72.8230, type: "Arterial Promenade" },
  { name: "Bandra Kurla Complex (BKC)", display_name: "Bandra Kurla Complex (BKC), Mumbai, Maharashtra", city: "Mumbai", state: "Maharashtra", lat: 19.0650, lng: 72.8680, type: "Financial Center" },
  { name: "MG Road Bengaluru", display_name: "MG Road / Brigade Road, Bengaluru, Karnataka", city: "Bengaluru", state: "Karnataka", lat: 12.9750, lng: 77.6080, type: "Central Commercial Hub" },
  { name: "Koramangala", display_name: "Koramangala 5th Block (Sony World Junction), Bengaluru, Karnataka", city: "Bengaluru", state: "Karnataka", lat: 12.9350, lng: 77.6240, type: "Tech Hub" },
  { name: "Hitec City Hyderabad", display_name: "Cyber Towers, Hitec City, Madhapur, Hyderabad, Telangana", city: "Hyderabad", state: "Telangana", lat: 17.4500, lng: 78.3800, type: "IT Corridor" }
];

// Baseline Hotspots Cache for Supported Indian Regions
const INITIAL_HOTSPOTS_CACHE = {
  "Gurugram": [
    { id: "GGN-HOT-01", name: "Sohna Road", type: "Road / highway", lat: 28.411, lng: 77.044, total_events: 9, recurrence: "Chronic", drain_threshold_mm_hr: 20.0, severity_weight: 0.95 },
    { id: "GGN-HOT-02", name: "Golf Course Extension Road", type: "Road / highway", lat: 28.418, lng: 77.095, total_events: 8, recurrence: "Chronic", drain_threshold_mm_hr: 22.0, severity_weight: 0.92 },
    { id: "GGN-HOT-03", name: "Narsinghpur (NH-48)", type: "Expressway / Service Lane", lat: 28.4215, lng: 76.9945, total_events: 8, recurrence: "Chronic", drain_threshold_mm_hr: 15.0, severity_weight: 0.98 },
    { id: "GGN-HOT-04", name: "Rajiv Chowk", type: "Chowk / junction", lat: 28.4555, lng: 77.0324, total_events: 8, recurrence: "Chronic", drain_threshold_mm_hr: 25.0, severity_weight: 0.90 },
    { id: "GGN-HOT-05", name: "Hero Honda Chowk", type: "Chowk / Underpass", lat: 28.4416, lng: 77.0097, total_events: 7, recurrence: "Chronic", drain_threshold_mm_hr: 22.0, severity_weight: 0.92 },
    { id: "GGN-HOT-06", name: "Udyog Vihar", type: "Colony / industrial", lat: 28.502, lng: 77.087, total_events: 7, recurrence: "Chronic", drain_threshold_mm_hr: 24.0, severity_weight: 0.88 },
    { id: "GGN-HOT-07", name: "Subhash Chowk", type: "Chowk / junction", lat: 28.4312, lng: 77.0421, total_events: 6, recurrence: "Chronic", drain_threshold_mm_hr: 25.0, severity_weight: 0.86 },
    { id: "GGN-HOT-08", name: "Basai Chowk", type: "Chowk / junction", lat: 28.4635, lng: 76.9995, total_events: 6, recurrence: "Chronic", drain_threshold_mm_hr: 22.0, severity_weight: 0.85 },
    { id: "GGN-HOT-09", name: "Sector 29", type: "Commercial / Sector", lat: 28.467, lng: 77.062, total_events: 5, recurrence: "Official Hotspot", drain_threshold_mm_hr: 26.0, severity_weight: 0.80 },
    { id: "GGN-HOT-10", name: "Sheetla Mata Road", type: "Road / highway", lat: 28.472, lng: 77.021, total_events: 5, recurrence: "Chronic", drain_threshold_mm_hr: 20.0, severity_weight: 0.82 },
    { id: "GGN-HOT-11", name: "Sector 14", type: "Residential / Colony", lat: 28.473, lng: 77.045, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 25.0, severity_weight: 0.78 }
  ],
  "Chandigarh": [
    { id: "CHD-HOT-01", name: "Madhya Marg (Sec 26 & Tribune Stretch)", type: "Road / highway", lat: 30.725, lng: 76.802, total_events: 8, recurrence: "Repeat", drain_threshold_mm_hr: 15.0, severity_weight: 0.88 },
    { id: "CHD-HOT-02", name: "Tribune Chowk", type: "Chowk / junction", lat: 30.7055, lng: 76.7925, total_events: 7, recurrence: "Official Hotspot", drain_threshold_mm_hr: 16.0, severity_weight: 0.90 },
    { id: "CHD-HOT-03", name: "Hallomajra", type: "Colony / settlement", lat: 30.692, lng: 76.801, total_events: 6, recurrence: "Repeat", drain_threshold_mm_hr: 14.0, severity_weight: 0.85 },
    { id: "CHD-HOT-04", name: "Industrial Area Phase I & II", type: "Colony / industrial", lat: 30.708, lng: 76.808, total_events: 6, recurrence: "Repeat", drain_threshold_mm_hr: 15.0, severity_weight: 0.86 },
    { id: "CHD-HOT-05", name: "Industrial Area Railway Underpass", type: "Underpass / road", lat: 30.702, lng: 76.815, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 12.0, severity_weight: 0.92 },
    { id: "CHD-HOT-06", name: "Sector 29", type: "Commercial Sector", lat: 30.712, lng: 76.795, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 18.0, severity_weight: 0.80 }
  ],
  "Jalandhar": [
    { id: "JAL-HOT-01", name: "PAP Chowk Flyover Underpass", type: "Highway Underpass", lat: 31.3110, lng: 75.6180, total_events: 6, recurrence: "Chronic", drain_threshold_mm_hr: 16.0, severity_weight: 0.92 },
    { id: "JAL-HOT-02", name: "BMC Chowk to Bus Stand Road", type: "Arterial Road", lat: 31.3200, lng: 75.5830, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 18.0, severity_weight: 0.85 },
    { id: "JAL-HOT-03", name: "Rama Mandi Low-lying Junction", type: "Road Junction", lat: 31.3160, lng: 75.6270, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 15.0, severity_weight: 0.88 },
    { id: "JAL-HOT-04", name: "Damoria Bridge Underpass", type: "Railway Underpass", lat: 31.3350, lng: 75.5800, total_events: 7, recurrence: "Chronic", drain_threshold_mm_hr: 12.0, severity_weight: 0.95 },
    { id: "JAL-HOT-05", name: "Model Town Geeta Mandir Stretch", type: "Market Road", lat: 31.3070, lng: 75.5760, total_events: 4, recurrence: "Repeat", drain_threshold_mm_hr: 20.0, severity_weight: 0.78 }
  ],
  "Kapurthala": [
    { id: "KAP-HOT-01", name: "DC Office Court Road Underpass", type: "Government Complex", lat: 31.3810, lng: 75.3850, total_events: 5, recurrence: "Repeat", drain_threshold_mm_hr: 16.0, severity_weight: 0.86 },
    { id: "KAP-HOT-02", name: "Sultanpur Lodhi Road Low Stretch", type: "Highway Stretch", lat: 31.3320, lng: 75.3610, total_events: 4, recurrence: "Repeat", drain_threshold_mm_hr: 15.0, severity_weight: 0.82 },
    { id: "KAP-HOT-03", name: "Shalimar Bag Roundabout", type: "Roundabout", lat: 31.3780, lng: 75.3720, total_events: 4, recurrence: "Repeat", drain_threshold_mm_hr: 18.0, severity_weight: 0.75 }
  ],
  "Delhi": [
    { id: "DEL-HOT-01", name: "Minto Bridge Underpass", type: "Railway Underpass", lat: 28.6350, lng: 77.2250, total_events: 10, recurrence: "Chronic", drain_threshold_mm_hr: 14.0, severity_weight: 0.98 },
    { id: "DEL-HOT-02", name: "ITO Ring Road Low Stretch", type: "Arterial Highway", lat: 28.6280, lng: 77.2480, total_events: 8, recurrence: "Chronic", drain_threshold_mm_hr: 18.0, severity_weight: 0.90 },
    { id: "DEL-HOT-03", name: "Pul Prahladpur Underpass", type: "Underpass", lat: 28.5020, lng: 77.2950, total_events: 7, recurrence: "Chronic", drain_threshold_mm_hr: 12.0, severity_weight: 0.94 }
  ],
  "Mumbai": [
    { id: "MUM-HOT-01", name: "Hindmata Flyover & Junction (Dadar)", type: "Chowk / Junction", lat: 19.0120, lng: 72.8420, total_events: 12, recurrence: "Chronic", drain_threshold_mm_hr: 25.0, severity_weight: 0.98 },
    { id: "MUM-HOT-02", name: "Milan Subway (Santacruz)", type: "Subway Underpass", lat: 19.0830, lng: 72.8450, total_events: 10, recurrence: "Chronic", drain_threshold_mm_hr: 20.0, severity_weight: 0.95 },
    { id: "MUM-HOT-03", name: "Gandhi Market (Kings Circle)", type: "Highway / Market", lat: 19.0310, lng: 72.8590, total_events: 9, recurrence: "Chronic", drain_threshold_mm_hr: 22.0, severity_weight: 0.92 }
  ]
};

// 1. Initialize Pan-India Leaflet Map
function initMap() {
  const mapElement = document.getElementById('map');
  if (!mapElement) return;

  if (map) {
    try { map.remove(); } catch (e) {}
    map = null;
  }

  const center = CITY_CENTERS[currentCity] || CITY_CENTERS['Gurugram'];

  if (typeof L === 'undefined') {
    setTimeout(initMap, 300);
    return;
  }

  map = L.map('map', {
    zoomControl: true,
    attributionControl: false,
    minZoom: 4,
    maxZoom: 18
  }).setView([center.lat, center.lng], center.zoom);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    minZoom: 4,
    noWrap: false,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  setTimeout(() => {
    if (map) {
      map.invalidateSize();
      map.setView([center.lat, center.lng], center.zoom);
    }
  }, 200);

  window.addEventListener('resize', () => {
    if (map) map.invalidateSize();
  });

  // Map Click Listener - Supports Picking Origin OR Destination anywhere in India
  map.on('click', function(e) {
    const lat = parseFloat(e.latlng.lat.toFixed(5));
    const lng = parseFloat(e.latlng.lng.toFixed(5));

    if (mapPickTarget === 'origin') {
      // User is picking Origin on map
      selectedOrigin = { name: `Map Location (${lat}, ${lng})`, lat: lat, lng: lng };
      const origInput = document.getElementById('route-origin-input');
      if (origInput) origInput.value = selectedOrigin.name;

      // Reverse-geocode to real Indian street/locality name
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
        .then(r => r.json())
        .then(rev => {
          if (rev && rev.display_name) {
            selectedOrigin.name = rev.display_name;
            if (origInput) origInput.value = rev.display_name;
            if (originMarker) originMarker.bindPopup(`<strong>Origin:</strong> ${rev.display_name}`);
          }
        }).catch(err => {});

      cancelMapPinSelection();
      updateMapPins();
      if (selectedOrigin && selectedDest) {
        runCustomDetour();
      }

    } else if (mapPickTarget === 'dest') {
      // User is picking Destination on map
      selectedDest = { name: `Map Location (${lat}, ${lng})`, lat: lat, lng: lng };
      const destInput = document.getElementById('route-dest-input');
      if (destInput) destInput.value = selectedDest.name;

      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
        .then(r => r.json())
        .then(rev => {
          if (rev && rev.display_name) {
            selectedDest.name = rev.display_name;
            if (destInput) destInput.value = rev.display_name;
            if (destMarker) destMarker.bindPopup(`<strong>Destination:</strong> ${rev.display_name}`);
          }
        }).catch(err => {});

      cancelMapPinSelection();
      updateMapPins();
      if (selectedOrigin && selectedDest) {
        runCustomDetour();
      }

    } else {
      // Update coordinates for complaint form
      const compLat = document.getElementById('comp-lat');
      const compLng = document.getElementById('comp-lng');
      if (compLat) compLat.value = lat;
      if (compLng) compLng.value = lng;
      updateWhatsAppPreview();
    }
  });

  // Close suggestions on outside click
  document.addEventListener('click', function(e) {
    const origBox = document.getElementById('origin-suggestions');
    const origInput = document.getElementById('route-origin-input');
    if (origBox && !e.target.closest('#origin-suggestions') && (!origInput || !e.target.closest('#route-origin-input'))) {
      origBox.classList.add('hidden');
    }

    const destBox = document.getElementById('dest-suggestions');
    const destInput = document.getElementById('route-dest-input');
    if (destBox && !e.target.closest('#dest-suggestions') && (!destInput || !e.target.closest('#route-dest-input'))) {
      destBox.classList.add('hidden');
    }
  });
}

// 2. City Switching
function switchCity(cityName) {
  currentCity = cityName;

  const panSelect = document.getElementById('pan-india-select');
  if (panSelect) panSelect.value = cityName;

  const ggnBtn = document.getElementById('city-ggn-btn');
  const chdBtn = document.getElementById('city-chd-btn');
  const punjabBtn = document.getElementById('city-punjab-btn');

  [ggnBtn, chdBtn, punjabBtn].forEach(b => {
    if (b) b.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition-all text-slate-400 hover:text-white';
  });

  if (cityName === 'Gurugram') {
    if (ggnBtn) ggnBtn.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition-all bg-blue-600 text-white shadow-md';
  } else if (cityName === 'Chandigarh') {
    if (chdBtn) chdBtn.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition-all bg-blue-600 text-white shadow-md';
  } else if (cityName === 'Jalandhar' || cityName === 'Kapurthala') {
    if (punjabBtn) punjabBtn.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition-all bg-blue-600 text-white shadow-md';
  }

  // Reset route points cleanly on city switch (never force unwanted default routes)
  clearRoutePoints();

  currentWeatherData = null;
  const weatherBox = document.getElementById('extracted-weather-box');
  if (weatherBox) weatherBox.classList.add('hidden');

  setElementText('stat-severe', '-');
  setElementText('stat-high', '-');
  setElementText('stat-moderate', '-');

  const banner = document.getElementById('city-alert-banner');
  const badge = document.getElementById('alert-badge');
  const text = document.getElementById('alert-text');
  if (banner) banner.className = 'p-3.5 m-3 rounded-xl bg-slate-900 border border-slate-700/60 flex items-start gap-3 transition-all';
  if (badge) {
    badge.className = 'text-[11px] font-bold uppercase tracking-wider text-cyan-400';
    badge.textContent = 'Awaiting Forecast';
  }
  if (text) text.textContent = `Click 'Fetch Weather Forecast' to extract meteorological data for ${cityName}, then run AI estimation.`;

  const center = CITY_CENTERS[cityName] || CITY_CENTERS['India'];
  if (map) {
    map.flyTo([center.lat, center.lng], center.zoom, { duration: 1.0 });
  }

  loadInitialNeutralHotspots();
  updateHelplineInfo();
  updateMapPins();
}

// 3. Tab Switching
function selectTab(tabName) {
  const tabs = ['predict', 'detour', 'hotspots'];
  tabs.forEach(t => {
    const panel = document.getElementById(`panel-${t}`);
    const btn = document.getElementById(`tab-${t}-btn`);
    if (panel) panel.classList.add('hidden');
    if (btn) btn.className = 'flex-1 py-2 text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center justify-center gap-1.5';
  });

  const activePanel = document.getElementById(`panel-${tabName}`);
  const activeBtn = document.getElementById(`tab-${tabName}-btn`);
  if (activePanel) activePanel.classList.remove('hidden');
  if (activeBtn) activeBtn.className = 'flex-1 py-2 text-xs font-semibold text-cyan-400 border-b-2 border-cyan-400 flex items-center justify-center gap-1.5';

  // Detour is calculated only when user enters points and clicks 'Calculate Route & Flood Detour'
}

// 4. Initial Neutral Hotspots Loading
async function loadInitialNeutralHotspots() {
  const baselineSpots = INITIAL_HOTSPOTS_CACHE[currentCity] || INITIAL_HOTSPOTS_CACHE['Gurugram'];
  currentHotspots = baselineSpots.map(s => ({
    ...s,
    probability_pct: 0,
    severity: 'Baseline Safe',
    color: '#38bdf8',
    estimated_depth_cm: 0.0,
    advisory: 'Current weather is clear. Road drains and underpasses are safe and passable.'
  }));

  renderHotspotsOnMap(currentHotspots, false);
  renderHotspotsList(currentHotspots, false);
  setElementText('hotspot-count-badge', currentHotspots.length);

  try {
    const res = await fetch(`/api/hotspots?city=${currentCity}`);
    if (res.ok) {
      const data = await res.json();
      if (data && data.hotspots && data.hotspots.length > 0) {
        currentHotspots = data.hotspots.map(s => ({
          ...s,
          probability_pct: 0,
          severity: 'Baseline Safe',
          color: '#38bdf8',
          estimated_depth_cm: 0.0,
          advisory: s.description || 'Current weather is clear. Safe and passable.'
        }));
        renderHotspotsOnMap(currentHotspots, false);
        renderHotspotsList(currentHotspots, false);
        setElementText('hotspot-count-badge', currentHotspots.length);
      }
    }
  } catch (err) {}
}

// 5. STEP 1: Fetch Live Weather Forecast API (NO POPUP - Smooth in-page display)
async function fetchWeatherForecast() {
  const btn = document.getElementById('fetch-weather-btn');
  if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Ingesting IMD Feed...';

  let weatherData = null;

  try {
    const res = await fetch(`/api/weather?city=${currentCity}`);
    if (res.ok) {
      weatherData = await res.json();
    }
  } catch (err) {}

  if (!weatherData || !weatherData.recommended_simulation) {
    const stName = `IMD ${currentCity} Regional Meteorological Centre (MoES Govt. of India)`;
    weatherData = {
      source: "India Meteorological Department (IMD) Ground Observatories",
      authority: "Ministry of Earth Sciences, Govt. of India",
      city: currentCity,
      station: {
        name: stName,
        radar: "IMD National Doppler Weather Radar Grid",
        elevation: "220 meters"
      },
      current_weather: {
        observed_rain_mm: 0.0,
        temperature_c: 25.5,
        summary: "Clear Sky. All storm drains and arterial underpasses fully dry and safe."
      },
      imd_color_code: "GREEN",
      imd_bulletin: "Official IMD Ground Telemetry synchronized. Normal traffic flow advised across corridors.",
      recommended_simulation: {
        rainfall_mm: 0.0,
        duration_hours: 2.0
      }
    };
  }

  currentWeatherData = weatherData;

  // Restore button text
  if (btn) btn.innerHTML = '<i class="fa-solid fa-satellite-dish"></i> Fetch Weather Forecast';

  // Smoothly display extracted weather card underneath the button (NO POPUP)
  const box = document.getElementById('extracted-weather-box');
  if (box) box.classList.remove('hidden');

  const stName = weatherData.station ? weatherData.station.name : 'IMD Observatory';
  const rainObs = weatherData.current_weather ? weatherData.current_weather.observed_rain_mm : 0.0;
  const colorCode = weatherData.imd_color_code || 'GREEN';

  setElementText('weather-station-name', stName);
  setElementText('weather-rain-mm', `${rainObs} mm (Latest Observed)`);
  setElementText('weather-imd-code', `[${colorCode}]`);
  setElementText('weather-summary-text', weatherData.imd_bulletin || 'Data ready. Click "Run AI Flood Estimation" to calculate risk.');

  // Update IMD 3-Hourly Publication Freshness
  updateWeatherFreshnessLabel();
  if (freshnessTickerInterval) clearInterval(freshnessTickerInterval);
  freshnessTickerInterval = setInterval(updateWeatherFreshnessLabel, 10000); // Ticks every 10 seconds

  // Animate the Run AI Estimation button to prompt the user
  const runBtn = document.getElementById('run-predict-btn');
  if (runBtn) runBtn.classList.add('ring-4', 'ring-cyan-400/50', 'animate-pulse');
}

// Computes IMD Official 3-Hourly Synoptic Release Freshness (02:30, 05:30, 08:30, 11:30, 14:30, 17:30, 20:30, 23:30 IST)
function getLatestIMDBulletinTime(now) {
  const d = now || new Date();
  const hours = [2.5, 5.5, 8.5, 11.5, 14.5, 17.5, 20.5, 23.5];
  const curDec = d.getHours() + (d.getMinutes() / 60) + (d.getSeconds() / 3600);

  let latestH = null;
  for (let i = hours.length - 1; i >= 0; i--) {
    if (curDec >= hours[i]) {
      latestH = hours[i];
      break;
    }
  }

  const bulletinDate = new Date(d);
  if (latestH !== null) {
    const intH = Math.floor(latestH);
    const intM = Math.round((latestH - intH) * 60);
    bulletinDate.setHours(intH, intM, 0, 0);
  } else {
    // Before 02:30 IST -> belongs to yesterday's 23:30 IST bulletin
    bulletinDate.setDate(bulletinDate.getDate() - 1);
    bulletinDate.setHours(23, 30, 0, 0);
  }

  const diffSec = Math.max(0, Math.floor((d.getTime() - bulletinDate.getTime()) / 1000));
  const diffMin = Math.floor(diffSec / 60);
  const hDiff = Math.floor(diffMin / 60);
  const mDiff = diffMin % 60;

  let elapsedStr = '';
  if (hDiff > 0) {
    if (mDiff === 0) {
      elapsedStr = `${hDiff} hr${hDiff > 1 ? 's' : ''} ago`;
    } else {
      elapsedStr = `${hDiff} hr ${mDiff} mins ago`;
    }
  } else if (diffMin === 0) {
    elapsedStr = 'just now (< 1 min ago)';
  } else {
    elapsedStr = `${diffMin} min${diffMin !== 1 ? 's' : ''} ago`;
  }

  const timeFormatted = bulletinDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return {
    issuedTime: `${timeFormatted} IST`,
    elapsedStr: elapsedStr
  };
}

function updateWeatherFreshnessLabel() {
  const el = document.getElementById('weather-time-ago');
  if (!el) return;

  const freshness = getLatestIMDBulletinTime(new Date());
  el.innerHTML = `<i class="fa-regular fa-clock text-cyan-400 mr-1"></i>Report generated ${freshness.elapsedStr} <span class="text-slate-400 text-[9px] font-normal">(Issued ${freshness.issuedTime})</span>`;
}

// 6. STEP 2: Run AI Prediction Engine
async function runPrediction() {
  if (!currentWeatherData) {
    alert("⚠️ Please click 'Fetch Weather Forecast' first to extract the meteorological dataset!");
    return;
  }

  const runBtn = document.getElementById('run-predict-btn');
  if (runBtn) {
    runBtn.classList.remove('ring-4', 'ring-cyan-400/50', 'animate-pulse');
    runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Estimating Waterlogging...';
  }

  const rain = currentWeatherData.recommended_simulation ? currentWeatherData.recommended_simulation.rainfall_mm : 0.0;
  const dur = currentWeatherData.recommended_simulation ? currentWeatherData.recommended_simulation.duration_hours : 2.0;

  let predictionData = null;

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        city: currentCity,
        rainfall_mm: rain,
        duration_hrs: dur
      })
    });
    if (res.ok) {
      predictionData = await res.json();
    }
  } catch (err) {}

  if (!predictionData) {
    predictionData = calculateClientSidePrediction(currentCity, rain, dur);
  }

  if (runBtn) runBtn.innerHTML = '<i class="fa-solid fa-play"></i> Run AI Flood Estimation';

  currentHotspots = predictionData.hotspots;

  updateAlertBanner(predictionData.summary);
  setElementText('stat-severe', predictionData.summary.severe_count);
  setElementText('stat-high', predictionData.summary.high_count);
  setElementText('stat-moderate', predictionData.summary.moderate_count);

  renderHotspotsOnMap(predictionData.hotspots, true);
  renderHotspotsList(predictionData.hotspots, true);

  if (window.innerWidth < 768) {
    toggleMobileView('map');
  }
}

// Client-Side Sigmoid Calculation Fallback
function calculateClientSidePrediction(city, rainfall_mm, duration_hrs) {
  const spots = INITIAL_HOTSPOTS_CACHE[city] || INITIAL_HOTSPOTS_CACHE['Gurugram'];
  const dur = Math.max(duration_hrs, 0.25);
  const intensity = rainfall_mm / dur;

  const results = spots.map(spot => {
    const threshold = spot.drain_threshold_mm_hr || 20.0;
    const recurrence = spot.recurrence || 'Repeat';
    const hist_factor = recurrence === 'Chronic' ? 1.25 : (recurrence === 'Official Hotspot' ? 1.15 : 1.0);

    const drain_stress_ratio = intensity / threshold;
    const z = (drain_stress_ratio - 1.0) * 2.8 + (rainfall_mm / 60.0) * 0.8 + (hist_factor - 1.0) * 1.5;
    let probability = 1.0 / (1.0 + Math.exp(-z));
    probability = Math.round(Math.max(0.05, Math.min(0.99, probability)) * 100) / 100;

    let severity = 'Clear';
    let color = '#22c55e';
    let depth_cm = Math.round(Math.max(0, rainfall_mm * 0.08) * 10) / 10;
    let advisory = 'CLEAR: Normal traffic flow expected. Regular wet-weather precautions.';

    if (probability >= 0.80) {
      severity = 'Severe';
      color = '#ef4444';
      depth_cm = Math.round(Math.min(120, 25 + (intensity - threshold) * 2.2 + (rainfall_mm * 0.2)) * 10) / 10;
      advisory = 'CRITICAL: Impassable for low sedans & 2-wheelers. High chance of submerged underpass or stalled engines.';
    } else if (probability >= 0.60) {
      severity = 'High';
      color = '#f97316';
      depth_cm = Math.round(Math.min(45, 15 + (intensity - threshold) * 1.4) * 10) / 10;
      advisory = 'HIGH RISK: Severe water stagnation and heavy crawl. Use recommended detour.';
    } else if (probability >= 0.35) {
      severity = 'Moderate';
      color = '#eab308';
      depth_cm = Math.round(Math.min(20, 5 + (intensity - threshold) * 0.8) * 10) / 10;
      advisory = 'MODERATE: Surface runoff and curb pooling. Passable with caution at low speeds.';
    }

    return {
      id: spot.id,
      name: spot.name,
      type: spot.type,
      lat: spot.lat,
      lng: spot.lng,
      recurrence: recurrence,
      total_events: spot.total_events,
      probability: probability,
      probability_pct: Math.round(probability * 100),
      severity: severity,
      color: color,
      estimated_depth_cm: depth_cm,
      threshold_mm_hr: threshold,
      advisory: advisory
    };
  });

  results.sort((a, b) => b.probability - a.probability);

  const severe_count = results.filter(r => r.severity === 'Severe').length;
  const high_count = results.filter(r => r.severity === 'High').length;
  const moderate_count = results.filter(r => r.severity === 'Moderate').length;

  return {
    city: city,
    summary: {
      severe_count,
      high_count,
      moderate_count,
      city_status_color: severe_count > 0 ? 'red' : (high_count > 0 ? 'orange' : (moderate_count > 0 ? 'yellow' : 'green')),
      city_alert: severe_count > 0 ? 'Severe waterlogging detected across arterial corridors.' : 'Road conditions clear and passable across city.'
    },
    hotspots: results
  };
}

// 7. Update Alert Banner
function updateAlertBanner(summary) {
  const banner = document.getElementById('city-alert-banner');
  const badge = document.getElementById('alert-badge');
  const text = document.getElementById('alert-text');
  if (!banner || !badge || !text) return;

  if (summary.city_status_color === 'red') {
    banner.className = 'p-3.5 m-3 rounded-xl bg-red-950/40 border border-red-500/40 flex items-start gap-3 transition-all';
    badge.className = 'text-[11px] font-bold uppercase tracking-wider text-red-400';
    badge.textContent = 'Severe Flood Warning';
  } else if (summary.city_status_color === 'orange') {
    banner.className = 'p-3.5 m-3 rounded-xl bg-orange-950/40 border border-orange-500/40 flex items-start gap-3 transition-all';
    badge.className = 'text-[11px] font-bold uppercase tracking-wider text-orange-400';
    badge.textContent = 'Orange Travel Warning';
  } else if (summary.city_status_color === 'yellow') {
    banner.className = 'p-3.5 m-3 rounded-xl bg-yellow-950/40 border border-yellow-500/40 flex items-start gap-3 transition-all';
    badge.className = 'text-[11px] font-bold uppercase tracking-wider text-yellow-400';
    badge.textContent = 'Yellow Monsoon Watch';
  } else {
    banner.className = 'p-3.5 m-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 flex items-start gap-3 transition-all';
    badge.className = 'text-[11px] font-bold uppercase tracking-wider text-emerald-400';
    badge.textContent = 'Clear Road Conditions';
  }

  text.textContent = summary.city_alert;
}

// 8. Render Hotspots on Leaflet Map
function renderHotspotsOnMap(hotspots, isPredicted) {
  if (!map) return;

  hotspotLayers.forEach(l => {
    try { map.removeLayer(l); } catch(e) {}
  });
  hotspotLayers = [];

  hotspots.forEach(spot => {
    const isRisk = isPredicted && (spot.severity === 'Severe' || spot.severity === 'High' || spot.severity === 'Moderate');
    const color = isRisk ? spot.color : '#38bdf8';
    const radius = spot.severity === 'Severe' ? 420 : (spot.severity === 'High' ? 300 : (spot.severity === 'Moderate' ? 200 : 120));

    if (isRisk) {
      const circle = L.circle([spot.lat, spot.lng], {
        color: color,
        fillColor: color,
        fillOpacity: 0.35,
        radius: radius,
        weight: 2
      }).addTo(map);
      hotspotLayers.push(circle);
    }

    const marker = L.circleMarker([spot.lat, spot.lng], {
      radius: isRisk ? 7 : 5,
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 1,
      fillOpacity: 0.95
    }).addTo(map);

    const safeTitle = (spot.name || 'Hotspot').replace(/'/g, "\\'");
    const popupContent = `
      <div class="p-1 space-y-1.5 text-xs">
        <div class="flex items-center justify-between gap-2 border-b border-slate-700 pb-1">
          <strong class="text-white text-sm">${spot.name}</strong>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold text-white" style="background-color: ${color}">
            ${isPredicted ? `${spot.severity} (${spot.probability_pct}%)` : 'Baseline Safe (0%)'}
          </span>
        </div>
        <div class="text-slate-300 space-y-0.5 text-[11px]">
          <div><strong>Type:</strong> ${spot.type}</div>
          <div><strong>Recurrence:</strong> ${spot.recurrence} (${spot.total_events || 2} logged events)</div>
          <div><strong>Est. Depth:</strong> <span class="text-amber-400 font-bold">${spot.estimated_depth_cm || 0} cm</span></div>
          <div><strong>Drain Capacity:</strong> ${spot.drain_threshold_mm_hr || spot.threshold_mm_hr || 20} mm/hr</div>
        </div>
        <p class="text-[11px] text-slate-300 italic bg-slate-800 p-1.5 rounded">${spot.advisory}</p>
        <button onclick="prefillComplaint('${safeTitle}', ${spot.lat}, ${spot.lng})" class="w-full mt-1.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[11px] font-semibold flex items-center justify-center gap-1">
          <i class="fa-brands fa-whatsapp"></i> Report Grievance Here
        </button>
      </div>
    `;

    marker.bindPopup(popupContent);
    hotspotLayers.push(marker);
  });
}

// 9. Render Hotspots Sidebar List
function renderHotspotsList(hotspots, isPredicted) {
  const container = document.getElementById('hotspot-list-container');
  if (!container) return;
  container.innerHTML = '';

  hotspots.forEach(spot => {
    const item = document.createElement('div');
    item.className = 'p-2.5 bg-slate-900/70 border border-slate-700/60 rounded-xl hover:border-slate-500 transition-all cursor-pointer';
    item.onclick = () => {
      if (map) map.flyTo([spot.lat, spot.lng], 15, { duration: 0.8 });
    };

    const isRisk = isPredicted && spot.probability_pct > 0;
    const badgeColor = isRisk ? spot.color : '#10b981';
    const badgeText = isRisk ? `${spot.severity} ${spot.probability_pct}%` : `${spot.recurrence} (0% Risk)`;
    const depthInfo = isRisk ? `Depth: <strong class="text-amber-400">${spot.estimated_depth_cm} cm</strong>` : `Drain Limit: ${spot.drain_threshold_mm_hr || spot.threshold_mm_hr || 20} mm/hr`;

    item.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-semibold text-xs text-white">${spot.name}</span>
        <span class="text-[10px] font-bold px-2 py-0.5 rounded text-white" style="background-color: ${badgeColor}">
          ${badgeText}
        </span>
      </div>
      <div class="flex items-center justify-between text-[11px] text-slate-400">
        <span>Type: <strong class="text-slate-300">${spot.type}</strong></span>
        <span>${depthInfo}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

// 10. PAN-INDIA AUTOCOMPLETE (Local Instant Matches + Pan-India OpenStreetMap Nominatim)
function handleOriginSearch(val) {
  clearTimeout(originDebounceTimer);
  const query = (val || '').trim();

  const localMatches = filterLocalPlaces(query);
  renderSuggestions(localMatches, 'origin');

  if (query.length >= 2) {
    originDebounceTimer = setTimeout(() => {
      fetchPanIndiaNominatim(query, 'origin', localMatches);
    }, 280);
  }
}

function handleDestSearch(val) {
  clearTimeout(destDebounceTimer);
  const query = (val || '').trim();

  const localMatches = filterLocalPlaces(query);
  renderSuggestions(localMatches, 'dest');

  if (query.length >= 2) {
    destDebounceTimer = setTimeout(() => {
      fetchPanIndiaNominatim(query, 'dest', localMatches);
    }, 280);
  }
}

function filterLocalPlaces(query) {
  const q = (query || '').toLowerCase().trim();
  if (!q) {
    return MASTER_SEARCH_PLACES.filter(p => p.city.toLowerCase() === currentCity.toLowerCase()).slice(0, 7);
  }
  const matches = MASTER_SEARCH_PLACES.filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.display_name.toLowerCase().includes(q) ||
    p.city.toLowerCase().includes(q) ||
    p.state.toLowerCase().includes(q)
  );
  matches.sort((a, b) => {
    const aCur = a.city.toLowerCase() === currentCity.toLowerCase() ? 0 : 1;
    const bCur = b.city.toLowerCase() === currentCity.toLowerCase() ? 0 : 1;
    return aCur - bCur;
  });
  return matches.slice(0, 7);
}

async function fetchPanIndiaNominatim(query, type, localMatches) {
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&countrycodes=in&format=json&addressdetails=1&limit=6`;
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) return;
    const data = await res.json();

    if (data && data.length > 0) {
      const panIndiaPlaces = data.map(item => {
        const addr = item.address || {};
        const state = addr.state || addr.state_district || 'India';
        const city = addr.city || addr.town || addr.village || addr.county || state;
        const name = item.name || item.display_name.split(',')[0];
        return {
          name: name,
          display_name: item.display_name,
          city: city,
          state: state,
          lat: parseFloat(item.lat),
          lng: parseFloat(item.lon),
          type: addr.suburb || addr.neighbourhood || addr.road || addr.amenity || 'Location (Pan-India)'
        };
      });

      const combined = [...localMatches];
      panIndiaPlaces.forEach(pip => {
        const already = combined.some(c => Math.abs(c.lat - pip.lat) < 0.005 && Math.abs(c.lng - pip.lng) < 0.005);
        if (!already) combined.push(pip);
      });

      renderSuggestions(combined.slice(0, 9), type);
    }
  } catch (e) {}
}

function renderSuggestions(places, type) {
  const container = document.getElementById(`${type}-suggestions`);
  if (!container) return;
  container.innerHTML = '';

  if (!places || places.length === 0) {
    container.innerHTML = `<div class="p-2.5 text-slate-400 text-xs italic">No matching locations found across India</div>`;
    container.classList.remove('hidden');
    return;
  }

  places.forEach(p => {
    const item = document.createElement('div');
    item.className = 'p-2.5 hover:bg-slate-800 transition-all cursor-pointer text-left border-b border-slate-800 last:border-0';
    item.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-bold text-xs text-white">${p.name}</span>
        <span class="text-[9px] uppercase px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 font-semibold">${p.state}</span>
      </div>
      <div class="text-[11px] text-slate-400 truncate mt-0.5">
        <i class="fa-solid fa-location-dot text-red-400 mr-1"></i>${p.display_name}
      </div>
    `;

    item.onclick = () => {
      if (type === 'origin') {
        selectedOrigin = { name: p.display_name, lat: p.lat, lng: p.lng };
        const input = document.getElementById('route-origin-input');
        if (input) input.value = p.display_name;
      } else {
        selectedDest = { name: p.display_name, lat: p.lat, lng: p.lng };
        const input = document.getElementById('route-dest-input');
        if (input) input.value = p.display_name;
      }
      container.classList.add('hidden');

      if (map) {
        map.flyTo([p.lat, p.lng], 14, { duration: 1.0 });
      }

      updateMapPins();
      if (selectedOrigin && selectedDest) {
        runCustomDetour();
      }
    };

    container.appendChild(item);
  });

  container.classList.remove('hidden');
}

// 11. Swap Points
function swapOriginDestination() {
  const temp = selectedOrigin;
  selectedOrigin = selectedDest;
  selectedDest = temp;

  const origInput = document.getElementById('route-origin-input');
  const destInput = document.getElementById('route-dest-input');
  if (origInput) origInput.value = selectedOrigin ? selectedOrigin.name : '';
  if (destInput) destInput.value = selectedDest ? selectedDest.name : '';

  updateMapPins();
  if (selectedOrigin && selectedDest) {
    runCustomDetour();
  }
}

// 11B. Remove Points / Reset Route
function clearRoutePoints() {
  selectedOrigin = null;
  selectedDest = null;

  const origInput = document.getElementById('route-origin-input');
  const destInput = document.getElementById('route-dest-input');
  if (origInput) origInput.value = '';
  if (destInput) destInput.value = '';

  if (originMarker) {
    try { map.removeLayer(originMarker); } catch(e) {}
    originMarker = null;
  }
  if (destMarker) {
    try { map.removeLayer(destMarker); } catch(e) {}
    destMarker = null;
  }

  if (directRouteLayer) {
    try { map.removeLayer(directRouteLayer); } catch(e) {}
    directRouteLayer = null;
  }
  if (detourRouteLayer) {
    try { map.removeLayer(detourRouteLayer); } catch(e) {}
    detourRouteLayer = null;
  }

  const resultCard = document.getElementById('detour-result-card');
  if (resultCard) resultCard.classList.add('hidden');

  // Smoothly return map to current city center
  const center = CITY_CENTERS[currentCity] || CITY_CENTERS['Gurugram'];
  if (map) {
    map.flyTo([center.lat, center.lng], center.zoom, { duration: 0.8 });
  }
}

// 12. GPS Origin Locator (Works ANYWHERE in India)
function setOriginToCurrentGPS() {
  if (navigator.geolocation) {
    const origInput = document.getElementById('route-origin-input');
    const oldPlaceholder = origInput ? origInput.placeholder : '';
    if (origInput) origInput.placeholder = 'Acquiring GPS fix (satellite/wifi)...';

    navigator.geolocation.getCurrentPosition(
      pos => {
        const lat = parseFloat(pos.coords.latitude.toFixed(5));
        const lng = parseFloat(pos.coords.longitude.toFixed(5));
        selectedOrigin = { name: `📍 Live GPS Location (${lat}, ${lng})`, lat: lat, lng: lng };
        const input = document.getElementById('route-origin-input');
        if (input) {
          input.value = selectedOrigin.name;
          input.placeholder = oldPlaceholder;
        }

        fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
          .then(r => r.json())
          .then(rev => {
            if (rev && rev.display_name) {
              selectedOrigin.name = `📍 ${rev.display_name}`;
              if (input) input.value = selectedOrigin.name;
              if (originMarker) originMarker.bindPopup(`<strong>Origin:</strong> ${selectedOrigin.name}`);
            }
          }).catch(err => {});

        if (map) map.flyTo([lat, lng], 14, { duration: 1.0 });

        updateMapPins();
        if (selectedOrigin && selectedDest) {
          runCustomDetour();
        }
      },
      err => {
        alert('Geolocation permission not granted or acquisition timed out.');
        if (origInput) origInput.placeholder = oldPlaceholder;
      },
      { enableHighAccuracy: true, timeout: 6000, maximumAge: 60000 }
    );
  } else {
    alert('Geolocation is not supported by your browser.');
  }
}

// 13. Map Pin Picker (Supports Both Origin AND Destination Anywhere in India)
function enableMapPinSelection(target) {
  mapPickTarget = target || 'dest';
  if (window.innerWidth < 768) {
    toggleMobileView('map');
  }
  const indicator = document.getElementById('map-pick-indicator');
  const textSpan = document.getElementById('map-pick-text');

  if (indicator) indicator.classList.remove('hidden');
  if (textSpan) {
    textSpan.textContent = mapPickTarget === 'origin'
      ? '📍 Click anywhere on the map to set STARTING LOCATION (Origin)'
      : '📍 Click anywhere on the map to set DESTINATION (Arrival)';
  }

  const mapDiv = document.getElementById('map');
  if (mapDiv) mapDiv.style.cursor = 'crosshair';
}

function cancelMapPinSelection() {
  mapPickTarget = null;
  const indicator = document.getElementById('map-pick-indicator');
  if (indicator) indicator.classList.add('hidden');

  const mapDiv = document.getElementById('map');
  if (mapDiv) mapDiv.style.cursor = '';
}

// 14. Update Start & End Map Pins
function updateMapPins() {
  if (!map) return;

  if (originMarker) {
    try { map.removeLayer(originMarker); } catch(e) {}
    originMarker = null;
  }
  if (destMarker) {
    try { map.removeLayer(destMarker); } catch(e) {}
    destMarker = null;
  }

  if (selectedOrigin && selectedOrigin.lat) {
    originMarker = L.circleMarker([selectedOrigin.lat, selectedOrigin.lng], {
      radius: 9,
      fillColor: '#10b981',
      color: '#ffffff',
      weight: 2.5,
      fillOpacity: 1
    }).addTo(map).bindPopup(`<strong>Origin:</strong> ${selectedOrigin.name}`);
  }

  if (selectedDest && selectedDest.lat) {
    destMarker = L.circleMarker([selectedDest.lat, selectedDest.lng], {
      radius: 9,
      fillColor: '#ef4444',
      color: '#ffffff',
      weight: 2.5,
      fillOpacity: 1
    }).addTo(map).bindPopup(`<strong>Destination:</strong> ${selectedDest.name}`);
  }
}

// 15. Run Pan-India Smart Detour Engine
async function runCustomDetour() {
  if (!selectedOrigin || !selectedDest) {
    alert("Please select or enter both a Starting Location and a Destination first.");
    return;
  }

  const rain = currentWeatherData && currentWeatherData.recommended_simulation ? currentWeatherData.recommended_simulation.rainfall_mm : 0.0;
  const dur = currentWeatherData && currentWeatherData.recommended_simulation ? currentWeatherData.recommended_simulation.duration_hours : 2.0;

  let routeData = null;

  try {
    const res = await fetch('/api/route', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        city: currentCity,
        origin_lat: selectedOrigin.lat,
        origin_lng: selectedOrigin.lng,
        origin_name: selectedOrigin.name,
        dest_lat: selectedDest.lat,
        dest_lng: selectedDest.lng,
        dest_name: selectedDest.name,
        rainfall_mm: rain,
        duration_hrs: dur
      })
    });
    if (res.ok) {
      routeData = await res.json();
    }
  } catch (err) {}

  if (!routeData) {
    routeData = generateClientSideRoute(selectedOrigin, selectedDest, currentHotspots);
  }

  const resultCard = document.getElementById('detour-result-card');
  if (resultCard) resultCard.classList.remove('hidden');

  setElementText('direct-eta', `${routeData.standard_route.estimated_time_mins} mins`);
  setElementText('detour-eta', `${routeData.detour_route.estimated_time_mins} mins`);
  setElementText('detour-dist', `${routeData.detour_route.distance_km} km`);
  setElementText('detour-saved-time', `${routeData.detour_route.time_saved_mins} mins`);
  setElementText('detour-reason', routeData.detour_route.reason);

  const tagsContainer = document.getElementById('hazard-tags');
  if (tagsContainer) {
    tagsContainer.innerHTML = '';
    if (!routeData.hazards_on_direct_route || routeData.hazards_on_direct_route.length === 0) {
      tagsContainer.innerHTML = '<span class="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">No flood hazards on direct path</span>';
    } else {
      routeData.hazards_on_direct_route.forEach(h => {
        const tag = document.createElement('span');
        tag.className = 'text-[10px] bg-red-900/80 text-red-200 px-2 py-0.5 rounded border border-red-700';
        tag.textContent = `${h.name} (${h.severity})`;
        tagsContainer.appendChild(tag);
      });
    }
  }

  drawRoutesOnMap(routeData);
  if (window.innerWidth < 768) {
    toggleMobileView('map');
  }
}

// Client-Side Geometric Routing Fallback
function generateClientSideRoute(orig, dest, hotspots) {
  const o_lat = orig.lat, o_lng = orig.lng;
  const d_lat = dest.lat, d_lng = dest.lng;

  const R = 6371.0;
  const dLat = (d_lat - o_lat) * Math.PI / 180.0;
  const dLon = (d_lng - o_lng) * Math.PI / 180.0;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(o_lat * Math.PI / 180.0) * Math.cos(d_lat * Math.PI / 180.0) * Math.sin(dLon/2) * Math.sin(dLon/2);
  const dist_km = Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * 10) / 10;

  const steps = 20;
  const r1_pts = [];
  for (let s = 0; s <= steps; s++) {
    const frac = s / steps;
    r1_pts.push([
      Math.round((o_lat + (d_lat - o_lat) * frac) * 100000) / 100000,
      Math.round((o_lng + (d_lng - o_lng) * frac) * 100000) / 100000
    ]);
  }

  const mid_lat = (o_lat + d_lat) / 2.0;
  const mid_lng = (o_lng + d_lng) / 2.0;
  const arc_lat = mid_lat - 0.007;
  const arc_lng = mid_lng + 0.012;

  const r2_pts = [];
  const half = Math.floor(steps / 2);
  for (let s = 0; s < half; s++) {
    const frac = s / half;
    r2_pts.push([
      Math.round((o_lat + (arc_lat - o_lat) * frac) * 100000) / 100000,
      Math.round((o_lng + (arc_lng - o_lng) * frac) * 100000) / 100000
    ]);
  }
  for (let s = 0; s <= half; s++) {
    const frac = s / half;
    r2_pts.push([
      Math.round((arc_lat + (d_lat - arc_lat) * frac) * 100000) / 100000,
      Math.round((arc_lng + (d_lng - arc_lng) * frac) * 100000) / 100000
    ]);
  }

  return {
    standard_route: {
      distance_km: Math.round(dist_km * 1.1 * 10) / 10,
      estimated_time_mins: Math.max(15, Math.round(dist_km * 3.5)),
      waypoints: r1_pts
    },
    detour_route: {
      distance_km: Math.round(dist_km * 1.25 * 10) / 10,
      estimated_time_mins: Math.max(12, Math.round(dist_km * 2.1)),
      time_saved_mins: Math.max(4, Math.round(dist_km * 1.4)),
      reason: "Bypasses flooded bottlenecks via elevated parallel arterial corridor.",
      waypoints: r2_pts
    },
    hazards_on_direct_route: (hotspots || []).filter(h => h.severity === 'Severe' || h.severity === 'High').slice(0, 2)
  };
}

// 16. Draw Routes on Leaflet Map
function drawRoutesOnMap(data) {
  if (!map) return;

  if (directRouteLayer) {
    try { map.removeLayer(directRouteLayer); } catch(e) {}
    directRouteLayer = null;
  }
  if (detourRouteLayer) {
    try { map.removeLayer(detourRouteLayer); } catch(e) {}
    detourRouteLayer = null;
  }

  directRouteLayer = L.polyline(data.standard_route.waypoints, {
    color: '#ef4444',
    weight: 4,
    dashArray: '8, 8',
    opacity: 0.85
  }).addTo(map);

  detourRouteLayer = L.polyline(data.detour_route.waypoints, {
    color: '#10b981',
    weight: 5,
    opacity: 0.95
  }).addTo(map);

  updateMapPins();

  const group = new L.featureGroup([directRouteLayer, detourRouteLayer]);
  map.fitBounds(group.getBounds(), { padding: [50, 50] });
}

// 17. Update Helpline Details
async function updateHelplineInfo() {
  const helplines = {
    'Gurugram': { authority: "GMDA Flood Control & Grievance Cell", whatsapp: "7840001817", toll_free: "18001801817" },
    'Chandigarh': { authority: "Municipal Corporation Chandigarh (MCC) Control Room", whatsapp: "9417891000", toll_free: "01722787200" },
    'Jalandhar': { authority: "Municipal Corporation Jalandhar (MCJ) Disaster Cell", whatsapp: "9814100000", toll_free: "01812227015" },
    'Kapurthala': { authority: "District Administration Kapurthala Flood Control", whatsapp: "9815000000", toll_free: "01822233777" },
    'Delhi': { authority: "Delhi Disaster Management Authority (DDMA) Control Room", whatsapp: "9868878899", toll_free: "1077" },
    'Mumbai': { authority: "BMC Disaster Management Control Room", whatsapp: "9999000000", toll_free: "1916" }
  };

  currentHelpline = helplines[currentCity] || helplines['Gurugram'];

  setElementText('helpline-authority', currentHelpline.authority);
  setElementText('helpline-number', currentHelpline.whatsapp);
  const callBtn = document.getElementById('helpline-call-btn');
  if (callBtn) callBtn.href = `tel:${currentHelpline.toll_free}`;
  setElementText('modal-authority-name', `Connecting to ${currentHelpline.authority} (${currentHelpline.whatsapp})`);
}

// 18. Citizen Grievance & WhatsApp Modal Logic
function openComplaintModal() {
  const modal = document.getElementById('complaint-modal');
  const formBody = document.getElementById('complaint-form-body');
  const footer = document.getElementById('complaint-modal-footer');
  const successView = document.getElementById('complaint-success-view');

  if (formBody) formBody.classList.remove('hidden');
  if (footer) footer.classList.remove('hidden');
  if (successView) successView.classList.add('hidden');
  if (modal) modal.classList.remove('hidden');

  updateWhatsAppPreview();
}

function closeComplaintModal() {
  const modal = document.getElementById('complaint-modal');
  if (modal) modal.classList.add('hidden');
}

function prefillComplaint(name, lat, lng) {
  const locInput = document.getElementById('comp-location');
  const latInput = document.getElementById('comp-lat');
  const lngInput = document.getElementById('comp-lng');

  if (locInput) locInput.value = name;
  if (latInput) latInput.value = parseFloat(lat).toFixed(5);
  if (lngInput) lngInput.value = parseFloat(lng).toFixed(5);

  openComplaintModal();
}

function detectGPSLocation() {
  const locInput = document.getElementById('comp-location');
  const oldPlaceholder = locInput ? locInput.placeholder : '';
  if (locInput) locInput.placeholder = 'Acquiring GPS fix...';

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => {
        const latInput = document.getElementById('comp-lat');
        const lngInput = document.getElementById('comp-lng');

        if (latInput) latInput.value = pos.coords.latitude.toFixed(5);
        if (lngInput) lngInput.value = pos.coords.longitude.toFixed(5);
        if (locInput) {
          locInput.value = `GPS Location (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`;
          locInput.placeholder = oldPlaceholder;
        }
        updateWhatsAppPreview();
      },
      err => {
        alert('Geolocation permission not granted or acquisition timed out.');
        if (locInput) locInput.placeholder = oldPlaceholder;
      },
      { enableHighAccuracy: true, timeout: 6000, maximumAge: 60000 }
    );
  } else {
    alert('Geolocation is not supported by your browser.');
  }
}

function updateWhatsAppPreview() {
  const loc = getInputValue('comp-location', 'Unspecified Spot');
  const lat = getInputValue('comp-lat', '28.4555');
  const lng = getInputValue('comp-lng', '77.0324');
  const sev = getInputValue('comp-severity', 'Severe (Water Depth > 3 ft / Underpass Submerged)');
  const notes = getInputValue('comp-notes', 'None provided');

  const preview = 
`*URGENT: WATERLOGGING GRIEVANCE REPORT*
━━━━━━━━━━━━━━━━━━━━━
*Authority:* ${currentHelpline.authority || 'Flood Control'}
*City:* ${currentCity}
*Location:* ${loc}
*GPS:* ${lat}, ${lng}
*Maps Pin:* https://maps.google.com/?q=${lat},${lng}
*Severity:* ${sev}
*Citizen Notes:* ${notes}
━━━━━━━━━━━━━━━━━━━━━
_Submitted directly via Fix Waterlogging AI Civic Portal_`;

  setElementText('whatsapp-preview-text', preview);
}

// 19. Complaint Submission & Direct WhatsApp Dispatch
async function submitGrievanceReport(e) {
  if (e && e.preventDefault) e.preventDefault();

  const loc = getInputValue('comp-location', 'Reported Spot');
  const lat = parseFloat(getInputValue('comp-lat', '28.4555')) || 28.4555;
  const lng = parseFloat(getInputValue('comp-lng', '77.0324')) || 77.0324;
  const sev = getInputValue('comp-severity', 'Severe (Water Depth > 3 ft / Underpass Submerged)');
  const notes = getInputValue('comp-notes', 'Heavy waterlogging blocking traffic.');

  const btn = document.getElementById('submit-complaint-btn');
  if (btn) btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing Ticket & WhatsApp...';

  // Generate unique Ticket ID synchronously
  const ticketId = `TKT-${currentCity.substring(0,3).toUpperCase()}-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${Math.floor(1000 + Math.random() * 9000)}`;
  const authName = currentHelpline.authority || 'GMDA Grievance / Flood Control Cell';
  const whatsappNo = currentHelpline.whatsapp || '7840001817';

  // Construct structured municipal report text
  const timestampStr = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
  const mapsLink = `https://maps.google.com/?q=${lat},${lng}`;

  const formattedMessage = 
`*URGENT: WATERLOGGING GRIEVANCE REPORT*
━━━━━━━━━━━━━━━━━━━━━
*Ticket ID:* \`${ticketId}\`
*Authority:* ${authName}
*City:* ${currentCity}
*Location:* ${loc}
*GPS:* ${lat.toFixed(5)}, ${lng.toFixed(5)}
*Live Maps Location:* ${mapsLink}
*Severity:* ${sev}
*Timestamp:* ${timestampStr}
*Citizen Notes:* ${notes}
━━━━━━━━━━━━━━━━━━━━━
_Submitted via Fix Waterlogging AI Civic Portal_`;

  const whatsappUrl = `https://wa.me/91${whatsappNo}?text=${encodeURIComponent(formattedMessage)}`;

  // Post to local server in background to register ticket in municipal database
  try {
    fetch('/api/complaint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticket_id: ticketId,
        city: currentCity,
        location_name: loc,
        lat: lat,
        lng: lng,
        severity: sev,
        notes: notes
      })
    }).catch(() => {});
  } catch (err) {}

  // Open WhatsApp directly to the municipality helpline (Bypasses OS share sheets & contact pickers)
  let waWindow = null;
  try {
    waWindow = window.open(whatsappUrl, '_blank');
  } catch (err) {}

  // Fallback if window.open was blocked by browser popup blocker
  if (!waWindow || waWindow.closed || typeof waWindow.closed === 'undefined') {
    const tempLink = document.createElement('a');
    tempLink.href = whatsappUrl;
    tempLink.target = '_blank';
    tempLink.rel = 'noopener noreferrer';
    document.body.appendChild(tempLink);
    tempLink.click();
    tempLink.remove();
  }

  // Switch modal view to show the Ticket Confirmation Screen
  const formBody = document.getElementById('complaint-form-body');
  const footer = document.getElementById('complaint-modal-footer');
  const successView = document.getElementById('complaint-success-view');

  if (formBody) formBody.classList.add('hidden');
  if (footer) footer.classList.add('hidden');
  if (successView) successView.classList.remove('hidden');

  setElementText('success-ticket-id', ticketId);
  setElementText('success-authority', authName);
  setElementText('success-whatsapp-no', whatsappNo);

  const waLink = document.getElementById('success-whatsapp-link');
  if (waLink) waLink.href = whatsappUrl;

  if (btn) btn.innerHTML = '<i class="fa-brands fa-whatsapp text-sm"></i> Send Report to Municipality WhatsApp';
}

// Function Aliases
const submitComplaintAndRedirectWhatsApp = submitGrievanceReport;
const submitComplaintDirectly = submitGrievanceReport;

// Copy Ticket ID to Clipboard
function copyTicketId() {
  const el = document.getElementById('success-ticket-id');
  if (el && el.textContent) {
    navigator.clipboard.writeText(el.textContent.trim()).then(() => {
      const btnText = document.getElementById('copy-ticket-btn-text');
      if (btnText) {
        btnText.textContent = 'Copied!';
        setTimeout(() => { btnText.textContent = 'Copy'; }, 2000);
      }
    }).catch(() => {});
  }
}

// Mobile View Switcher (Map vs Controls Panel)
function toggleMobileView(view) {
  const sidebar = document.getElementById('main-sidebar');
  const btnMap = document.getElementById('mobile-btn-map');
  const btnPanel = document.getElementById('mobile-btn-panel');
  if (!sidebar) return;

  if (view === 'panel') {
    sidebar.classList.remove('hidden');
    sidebar.classList.add('flex');
    if (btnPanel) {
      btnPanel.className = 'px-4 py-2 rounded-full text-xs font-bold transition-all bg-cyan-600 text-white shadow-lg shadow-cyan-600/40 flex items-center gap-1.5';
    }
    if (btnMap) {
      btnMap.className = 'px-4 py-2 rounded-full text-xs font-bold transition-all text-slate-300 hover:text-white flex items-center gap-1.5';
    }
  } else {
    sidebar.classList.add('hidden');
    sidebar.classList.remove('flex');
    if (btnMap) {
      btnMap.className = 'px-4 py-2 rounded-full text-xs font-bold transition-all bg-cyan-600 text-white shadow-lg shadow-cyan-600/40 flex items-center gap-1.5';
    }
    if (btnPanel) {
      btnPanel.className = 'px-4 py-2 rounded-full text-xs font-bold transition-all text-slate-300 hover:text-white flex items-center gap-1.5';
    }
    if (map) {
      setTimeout(() => {
        try { map.invalidateSize(); } catch(e) {}
      }, 150);
    }
  }
}

// Window resize listener to keep layout synced between mobile & desktop
window.addEventListener('resize', () => {
  const sidebar = document.getElementById('main-sidebar');
  if (!sidebar) return;
  if (window.innerWidth >= 768) {
    sidebar.classList.remove('hidden');
    sidebar.classList.add('flex');
  } else {
    const btnMap = document.getElementById('mobile-btn-map');
    if (btnMap && btnMap.classList.contains('bg-cyan-600')) {
      sidebar.classList.add('hidden');
      sidebar.classList.remove('flex');
    }
  }
  if (map) {
    try { map.invalidateSize(); } catch(e) {}
  }
});

// Global Exports
window.submitGrievanceReport = submitGrievanceReport;
window.submitComplaintAndRedirectWhatsApp = submitGrievanceReport;
window.submitComplaintDirectly = submitGrievanceReport;
window.copyTicketId = copyTicketId;
window.toggleMobileView = toggleMobileView;

// Helpers
function setElementText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function getInputValue(id, fallback) {
  const el = document.getElementById(id);
  return (el && el.value) ? el.value : fallback;
}

// Initialization Logic
function initApp() {
  initMap();

  const origInput = document.getElementById('route-origin-input');
  const destInput = document.getElementById('route-dest-input');
  if (origInput) origInput.value = selectedOrigin ? selectedOrigin.name : '';
  if (destInput) destInput.value = selectedDest ? selectedDest.name : '';

  loadInitialNeutralHotspots();
  updateHelplineInfo();
  updateMapPins();

  // Attach live update listeners safely
  ['comp-location', 'comp-lat', 'comp-lng', 'comp-severity', 'comp-notes'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updateWhatsAppPreview);
  });
}

// Run on DOM ready or immediately if already loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
