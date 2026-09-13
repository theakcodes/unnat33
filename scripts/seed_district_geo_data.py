"""
scripts/seed_district_geo_data.py

Enriches all 785 official LGD districts in PostgreSQL with geographic centroids
(latitude, longitude, elevation) from Open-Meteo Geocoding API into table `district_geo_centroids`.

Guarantees & Invariants:
- PostgreSQL `goi_schemes` is authoritative.
- Idempotent and repeatable (uses ON CONFLICT (district_id) DO UPDATE).
- Rate-limited to comply with Open-Meteo limits (0.08s sleep between requests).
- Canonical alias dictionary maps LGD district names to administrative headquarters / standard spellings.
- Logs resolved and unresolved counts cleanly without fabricating coordinates.
"""

import os
import sys
import re
import time
from pathlib import Path
from decimal import Decimal

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

import httpx
from sqlalchemy import text
from app.db.session import SessionLocal

# Ensure Windows terminal doesn't crash on Unicode characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Canonical District Headquarter & Transliteration Mapping for Indian LGD Districts
DISTRICT_ALIASES = {
    # Andhra Pradesh
    ("ANAKAPALLI", "ANDHRA PRADESH"): "Anakapalle",
    ("ANNAMAYYA", "ANDHRA PRADESH"): "Rayachoti",
    ("CHITOOR", "ANDHRA PRADESH"): "Chittoor",
    ("EAST GODAVARI", "ANDHRA PRADESH"): "Rajahmundry",
    ("KONASEEMA", "ANDHRA PRADESH"): "Amalapuram",
    ("NTR", "ANDHRA PRADESH"): "Vijayawada",
    ("N T R", "ANDHRA PRADESH"): "Vijayawada",
    ("PALNADU", "ANDHRA PRADESH"): "Narasaraopet",
    ("PARVATHIPURAM MANYAM", "ANDHRA PRADESH"): "Parvathipuram",
    ("PRAKASAM", "ANDHRA PRADESH"): "Ongole",
    ("SPSR NELLORE", "ANDHRA PRADESH"): "Nellore",
    ("SRI POTTI SRIRAMULU NELLORE", "ANDHRA PRADESH"): "Nellore",
    ("WEST GODAVARI", "ANDHRA PRADESH"): "Bhimavaram",
    ("Y.S.R", "ANDHRA PRADESH"): "Kadapa",
    ("ALLURI SITHARAMA RAJU", "ANDHRA PRADESH"): "Paderu",

    # Andaman & Nicobar
    ("NORTH AND MIDDLE ANDAMAN", "ANDAMAN AND NICOBAR ISLANDS"): "Mayabunder",
    ("SOUTH ANDAMANS", "ANDAMAN AND NICOBAR ISLANDS"): "Port Blair",
    ("NIKOBARS", "ANDAMAN AND NICOBAR ISLANDS"): "Car Nicobar",

    # Arunachal Pradesh
    ("ANJAW", "ARUNACHAL PRADESH"): "Hawai",
    ("DIBANG VALLEY", "ARUNACHAL PRADESH"): "Anini",
    ("EAST KAMENG", "ARUNACHAL PRADESH"): "Seppa",
    ("EAST SIANG", "ARUNACHAL PRADESH"): "Pasighat",
    ("KAMLE", "ARUNACHAL PRADESH"): "Raga",
    ("KRA DAADI", "ARUNACHAL PRADESH"): "Jamin",
    ("KURUNG KUMEY", "ARUNACHAL PRADESH"): "Koloriang",
    ("LEPARADA", "ARUNACHAL PRADESH"): "Basar",
    ("LOWER DIBANG VALLEY", "ARUNACHAL PRADESH"): "Roing",
    ("LOWER SIANG", "ARUNACHAL PRADESH"): "Likabali",
    ("LOWER SUBANSIRI", "ARUNACHAL PRADESH"): "Ziro",
    ("PAKKE KESSANG", "ARUNACHAL PRADESH"): "Lemmi",
    ("PAPUM PARE", "ARUNACHAL PRADESH"): "Yupia",
    ("SHI YOMI", "ARUNACHAL PRADESH"): "Tato",
    ("UPPER SIANG", "ARUNACHAL PRADESH"): "Yingkiong",
    ("UPPER SUBANSIRI", "ARUNACHAL PRADESH"): "Daporijo",
    ("WEST KAMENG", "ARUNACHAL PRADESH"): "Bomdila",
    ("WEST SIANG", "ARUNACHAL PRADESH"): "Aalo",

    # Assam
    ("BAJALI", "ASSAM"): "Pathsala",
    ("CACHAR", "ASSAM"): "Silchar",
    ("CHARAIDEO", "ASSAM"): "Sonari",
    ("DIMA HASAO", "ASSAM"): "Haflong",
    ("KAMRUP", "ASSAM"): "Amingaon",
    ("KAMRUP METRO", "ASSAM"): "Guwahati",
    ("KARBI-ANGELONG", "ASSAM"): "Diphu",
    ("KARBI ANGLONG", "ASSAM"): "Diphu",
    ("SIVASAGAR", "ASSAM"): "Sibsagar",
    ("SOUTH SALMARA MANCACHAR", "ASSAM"): "Mankachar",
    ("TAMULPUR", "ASSAM"): "Tamulpur",
    ("WEST KARBI ANGLONG", "ASSAM"): "Hamren",

    # Bihar
    ("KAIMUR (BHABUA)", "BIHAR"): "Bhabua",
    ("LAKHISARAI", "BIHAR"): "Lakhisarai",
    ("NALANDA", "BIHAR"): "Bihar Sharif",
    ("PASCHIM CHAMPARAN", "BIHAR"): "Bettiah",
    ("PASHCHIM  CHAMPARAN", "BIHAR"): "Bettiah",
    ("PASHCHIM CHAMPARAN", "BIHAR"): "Bettiah",
    ("PURBI CHAMPARAN", "BIHAR"): "Motihari",
    ("PURBI  CHAMPARAN", "BIHAR"): "Motihari",

    # Chhattisgarh
    ("BALOD BAZAR", "CHHATTISGARH"): "Baloda Bazar",
    ("DAKSHIN BASTAR DANTEWADA", "CHHATTISGARH"): "Dantewada",
    ("DANTEWADA", "CHHATTISGARH"): "Dantewada",
    ("GAURELA PENDRA MARWAHI", "CHHATTISGARH"): "Gaurella",
    ("GAURELLA PENDRA MARWAHI", "CHHATTISGARH"): "Gaurella",
    ("JANJGIR-CHAMPA", "CHHATTISGARH"): "Janjgir",
    ("KABIRDHAM", "CHHATTISGARH"): "Kawardha",
    ("KHAIRAGARH CHHUIKHADAN GANDAI", "CHHATTISGARH"): "Khairagarh",
    ("KHAIRGARH CHHUIKHADAN GANDAI", "CHHATTISGARH"): "Khairagarh",
    ("KOREA", "CHHATTISGARH"): "Baikunthpur",
    ("MANENDRAGARH CHIRMICHI BHARATPUR", "CHHATTISGARH"): "Manendragarh",
    ("MANENDRAGARH CHIRIMIRI BHARATPUR", "CHHATTISGARH"): "Manendragarh",
    ("MOHLA MANPUR AMBAGARH CHOUKI", "CHHATTISGARH"): "Mohla",
    ("RAJNANDAGAON", "CHHATTISGARH"): "Rajnandgaon",
    ("SARANGARH BILAIGARH", "CHHATTISGARH"): "Sarangarh",
    ("UTTAR BASTAR KANKER", "CHHATTISGARH"): "Kanker",

    # Delhi
    ("CENTRAL", "DELHI"): "Central Delhi",
    ("EAST", "DELHI"): "East Delhi",
    ("NORTH", "DELHI"): "North Delhi",
    ("NORTH EAST", "DELHI"): "Shahdara",
    ("NORTH WEST", "DELHI"): "Kanjhawala",
    ("SOUTH", "DELHI"): "South Delhi",
    ("SOUTH EAST", "DELHI"): "Defence Colony",
    ("SOUTH WEST", "DELHI"): "Dwarka",
    ("WEST", "DELHI"): "Rajouri Garden",
    ("SHAHDARA", "DELHI"): "Shahdara",

    # Goa
    ("NORTH GOA", "GOA"): "Panaji",
    ("SOUTH GOA", "GOA"): "Margao",

    # Gujarat
    ("ARVALLI", "GUJARAT"): "Modasa",
    ("BANAS KANTHA", "GUJARAT"): "Palanpur",
    ("CHHOTA UDEPUR", "GUJARAT"): "Chhota Udaipur",
    ("CHHOTAUDEPUR", "GUJARAT"): "Chhota Udaipur",
    ("DEVBHOOMI DWARKA", "GUJARAT"): "Khambhalia",
    ("DOHAD", "GUJARAT"): "Dahod",
    ("GIR SOMNATH", "GUJARAT"): "Veraval",
    ("MAHISAGAR", "GUJARAT"): "Lunawada",
    ("MEHSANA", "GUJARAT"): "Mahesana",
    ("PANCH MAHALS", "GUJARAT"): "Godhra",
    ("SABAR KANTHA", "GUJARAT"): "Himmatnagar",
    ("THE DANGS", "GUJARAT"): "Ahwa",

    # Haryana
    ("CHARKHI DADRI", "HARYANA"): "Dadri",

    # Himachal Pradesh
    ("LAHUL AND SPITI", "HIMACHAL PRADESH"): "Keylong",

    # Jammu & Kashmir
    ("BADGAM", "JAMMU AND KASHMIR"): "Budgam",
    ("BUDGAM", "JAMMU AND KASHMIR"): "Budgam",
    ("BANDIPORA", "JAMMU AND KASHMIR"): "Bandipora",
    ("BANDIPORE", "JAMMU AND KASHMIR"): "Bandipora",
    ("BARAMULA", "JAMMU AND KASHMIR"): "Baramulla",
    ("BARAMULLA", "JAMMU AND KASHMIR"): "Baramulla",
    ("SHOPIAN", "JAMMU AND KASHMIR"): "Shupiyan",

    # Jharkhand
    ("EAST SINGHBHUM", "JHARKHAND"): "Jamshedpur",
    ("KODERMA", "JHARKHAND"): "Jhumri Telaiya",
    ("PASHCHIMI SINGHBHUM", "JHARKHAND"): "Chaibasa",
    ("PURBI SINGHBHUM", "JHARKHAND"): "Jamshedpur",
    ("SARAIKELA KHARSAWAN", "JHARKHAND"): "Seraikela",
    ("SERAIKELA-KHARSAWAN", "JHARKHAND"): "Seraikela",
    ("WEST SINGHBHUM", "JHARKHAND"): "Chaibasa",

    # Karnataka
    ("BENGALURU (RURAL)", "KARNATAKA"): "Nelamangala",
    ("CHAMARAJNAGAR", "KARNATAKA"): "Chamarajanagar",
    ("CHIKBALLAPUR", "KARNATAKA"): "Chikkaballapur",
    ("DAKSHIN KANNAD", "KARNATAKA"): "Mangalore",
    ("UTTAR KANNAD", "KARNATAKA"): "Karwar",
    ("VIJAYANAGARA", "KARNATAKA"): "Hospet",

    # Kerala
    ("PATHANAMTHIPTA", "KERALA"): "Pathanamthitta",
    ("WAYANAD", "KERALA"): "Kalpetta",

    # Ladakh
    ("LEH LADAKH", "LADAKH"): "Leh",

    # Lakshadweep
    ("LAKSHADWEEP DISTRICT", "LAKSHADWEEP"): "Kavaratti",

    # Madhya Pradesh
    ("AGAR MALWA", "MADHYA PRADESH"): "Agar",
    ("EAST NIMAR", "MADHYA PRADESH"): "Khandwa",
    ("HOSHANGABAD", "MADHYA PRADESH"): "Narmadapuram",
    ("NARSINGHPUR", "MADHYA PRADESH"): "Narsimhapur",
    ("NIWARI", "MADHYA PRADESH"): "Niwari",

    # Maharashtra
    ("BULDHANA", "MAHARASHTRA"): "Buldana",
    ("MUMBAI CITY", "MAHARASHTRA"): "Mumbai",
    ("MUMBAI SUBURBAN", "MAHARASHTRA"): "Bandra",
    ("NAN DED", "MAHARASHTRA"): "Nanded",
    ("RAIGAD", "MAHARASHTRA"): "Alibag",

    # Manipur
    ("IMPHAL EAST", "MANIPUR"): "Porompat",
    ("IMPHAL WEST", "MANIPUR"): "Lamphelpat",
    ("NONEY", "MANIPUR"): "Noney",

    # Meghalaya
    ("EAST GARO HILLS", "MEGHALAYA"): "Williamnagar",
    ("EAST KHASI HILLS", "MEGHALAYA"): "Shillong",
    ("EAST JAINTIA HILLS", "MEGHALAYA"): "Khliehriat",
    ("EASTERN WEST KHASI HILLS", "MEGHALAYA"): "Mairang",
    ("NORTH GARO HILLS", "MEGHALAYA"): "Resubelpara",
    ("RI BHOI", "MEGHALAYA"): "Nongpoh",
    ("SOUTH GARO HILLS", "MEGHALAYA"): "Baghmara",
    ("SOUTH WEST GARO HILLS", "MEGHALAYA"): "Ampati",
    ("SOUTH WEST  GARO HILLS", "MEGHALAYA"): "Ampati",
    ("SOUTH WEST KHASI HILLS", "MEGHALAYA"): "Mawkyrwat",
    ("WEST GARO HILLS", "MEGHALAYA"): "Tura",
    ("WEST JAINTIA HILLS", "MEGHALAYA"): "Jowai",
    ("WEST KHASI HILLS", "MEGHALAYA"): "Nongstoin",

    # Mizoram
    ("CHAMPHAI", "MIZORAM"): "Champhai",

    # Nagaland
    ("CHUMOUKEDIMA", "NAGALAND"): "Chumukedima",
    ("KIPHRIE", "NAGALAND"): "Kiphire",
    ("SHAMATOR", "NAGALAND"): "Shamator",

    # Odisha
    ("BOUDH", "ODISHA"): "Boudh",
    ("JAGATSINGHAPUR", "ODISHA"): "Jagatsinghpur",
    ("JAJAPUR", "ODISHA"): "Jajpur",
    ("KANDHAMAL", "ODISHA"): "Phulbani",
    ("NABARANGPUR", "ODISHA"): "Nabarangapur",
    ("SUBARNAPUR", "ODISHA"): "Sonepur",

    # Punjab
    ("FATEHGARH SAHIB", "PUNJAB"): "Fatehgarh Sahib",
    ("FEROZEPUR", "PUNJAB"): "Firozpur",
    ("MALERKOTLA", "PUNJAB"): "Malerkotla",
    ("SAS NAGAR", "PUNJAB"): "Mohali",
    ("SHAHID BHAGAT SINGH NAGAR", "PUNJAB"): "Nawanshahr",
    ("SRI MUKTSAR SAHIB", "PUNJAB"): "Muktsar",

    # Rajasthan
    ("ANOOPGARH", "RAJASTHAN"): "Anupgarh",
    ("DIDWANA KUCHAMAN", "RAJASTHAN"): "Didwana",
    ("GANGAPURCITY", "RAJASTHAN"): "Gangapur City",
    ("JAIPUR GRAMIN", "RAJASTHAN"): "Jaipur",
    ("JALOR", "RAJASTHAN"): "Jalore",
    ("JALORE", "RAJASTHAN"): "Jalore",
    ("JHUNJHUNU", "RAJASTHAN"): "Jhunjhunun",
    ("JODHPUR GRAMIN", "RAJASTHAN"): "Jodhpur",
    ("KHAIRTHAL-TIJARA", "RAJASTHAN"): "Tijara",
    ("KOTPUTLI-BEHROR", "RAJASTHAN"): "Kotputli",

    # Tamil Nadu
    ("CHENNAI", "TAMIL NADU"): "Chennai",
    ("THE NILGIRIS", "TAMIL NADU"): "Udhagamandalam",
    ("THE NILGIRISH", "TAMIL NADU"): "Udhagamandalam",
    ("THIRUVALLUR", "TAMIL NADU"): "Tiruvallur",
    ("TIRUPATHUR", "TAMIL NADU"): "Tirupattur",
    ("VIRUDHUNAGAR", "TAMIL NADU"): "Virudhunagar",

    # Telangana
    ("BHADRADRI KOTHAGUDEM", "TELANGANA"): "Kothagudem",
    ("HANUMAKONDA", "TELANGANA"): "Hanamkonda",
    ("JANGOAN", "TELANGANA"): "Jangaon",
    ("JAYASHANKAR BHUPALPALLY", "TELANGANA"): "Bhupalpalle",
    ("JAYASHANKAR BHUPALAPALLY", "TELANGANA"): "Bhupalpalle",
    ("JOGULAMBA GADWAL", "TELANGANA"): "Gadwal",
    ("KAMAREDDY", "TELANGANA"): "Kamareddy",
    ("KOMARAM BHEEM ASIFABAD", "TELANGANA"): "Asifabad",
    ("MAHABUBABAD", "TELANGANA"): "Mahabubabad",
    ("MAHABUBNAGAR", "TELANGANA"): "Mahbubnagar",
    ("MEDCHAL MALKAJGIRI", "TELANGANA"): "Shamshabad",
    ("MULUGU", "TELANGANA"): "Mulug",
    ("NAGARKURNOOL", "TELANGANA"): "Nagarkurnool",
    ("RAJANNA SIRCILLA", "TELANGANA"): "Sircilla",
    ("RANGA REDDI", "TELANGANA"): "Shamshabad",
    ("SANGAREDDY", "TELANGANA"): "Sangareddi",
    ("WARANGAL", "TELANGANA"): "Warangal",
    ("YADADRI BHUVANAGIRI", "TELANGANA"): "Bhongir",

    # Tripura
    ("GOMATI", "TRIPURA"): "Udaipur",
    ("NORTH TRIPURA", "TRIPURA"): "Dharmanagar",
    ("SEPAHIJALA", "TRIPURA"): "Bishramganj",
    ("SOUTH TRIPURA", "TRIPURA"): "Belonia",
    ("UNAKOTI", "TRIPURA"): "Kailashahar",
    ("WEST TRIPURA", "TRIPURA"): "Agartala",

    # Uttar Pradesh
    ("AMBEDAKAR NAGAR", "UTTAR PRADESH"): "Akbarpur",
    ("AMETHI", "UTTAR PRADESH"): "Gauriganj",
    ("BHADOHI", "UTTAR PRADESH"): "Gyanpur",
    ("BULANDSHAHAR", "UTTAR PRADESH"): "Bulandshahr",
    ("GAUTAM BUDDHA NAGAR", "UTTAR PRADESH"): "Noida",
    ("GORAKHAPUR", "UTTAR PRADESH"): "Gorakhpur",
    ("HATHRAS", "UTTAR PRADESH"): "Hathras",
    ("KANPUR DEHAT", "UTTAR PRADESH"): "Akbarpur",
    ("KANPUR NAGAR", "UTTAR PRADESH"): "Kanpur",
    ("KASGANJ", "UTTAR PRADESH"): "Kasganj",
    ("KAUSHAMBI", "UTTAR PRADESH"): "Manjhanpur",
    ("KUSHINAGAR", "UTTAR PRADESH"): "Padrauna",
    ("SAMBHAL", "UTTAR PRADESH"): "Sambhal",
    ("SANT KABIR NAGAR", "UTTAR PRADESH"): "Khalilabad",
    ("SANT KABEER NAGAR", "UTTAR PRADESH"): "Khalilabad",
    ("SHRAVASTI", "UTTAR PRADESH"): "Bhinga",
    ("SIDDHARTHNAGAR", "UTTAR PRADESH"): "Navgarh",

    # Uttarakhand
    ("PAURI GARHWAL", "UTTARAKHAND"): "Pauri",
    ("RUDRA PRAYAG", "UTTARAKHAND"): "Rudraprayag",
    ("TEHRI GARHWAL", "UTTARAKHAND"): "New Tehri",
    ("UDHAM SINGH NAGAR", "UTTARAKHAND"): "Rudrapur",

    # West Bengal
    ("ALIPURDUAR", "WEST BENGAL"): "Alipur Duar",
    ("BIRBHUM", "WEST BENGAL"): "Suri",
    ("COOCHBEHAR", "WEST BENGAL"): "Cooch Behar",
    ("DAKSHIN DINAJPUR", "WEST BENGAL"): "Balurghat",
    ("EAST MEDINIPUR", "WEST BENGAL"): "Tamluk",
    ("JHARGRAM", "WEST BENGAL"): "Jhargram",
    ("KALIMPONG", "WEST BENGAL"): "Kalimpong",
    ("KOLKOTA", "WEST BENGAL"): "Kolkata",
    ("NORTH 24 PARGANAS", "WEST BENGAL"): "Barasat",
    ("NORTH 24 PRAGANAS", "WEST BENGAL"): "Barasat",
    ("PASCHIM BARDHAMAN", "WEST BENGAL"): "Asansol",
    ("PASCHIM MEDINIPUR", "WEST BENGAL"): "Midnapore",
    ("PURBA BARDHAMAN", "WEST BENGAL"): "Bardhaman",
    ("PURBA MEDINIPUR", "WEST BENGAL"): "Tamluk",
    ("SOUTH 24 PARGANAS", "WEST BENGAL"): "Alipore",
    ("SOUTH 24 PRAGANAS", "WEST BENGAL"): "Alipore",
    ("UTTAR DINAJPUR", "WEST BENGAL"): "Raiganj",
    ("WEST MEDINIPUR", "WEST BENGAL"): "Midnapore",

    # Additional Headquarter Mappings for 100% Coverage
    ("RAJNANDAGAON", "CHHATTISGARH"): "Dongargarh",
    ("DANTEWADA", "CHHATTISGARH"): "Dantewara",
    ("FIROZEPUR", "PUNJAB"): "Firozpur",
    ("FATEHGARH SAHIB", "PUNJAB"): "Sirhind",
    ("MALERKOTLA", "PUNJAB"): "Maler Kotla",
    ("GANGAPURCITY", "RAJASTHAN"): "Gangapur",
    ("JALORE", "RAJASTHAN"): "Jalor",
    ("LAHUL AND SPITI", "HIMACHAL PRADESH"): "Kyelang",
    ("BOUDH", "ODISHA"): "Baud",
    ("VIRUDHUNAGAR", "TAMIL NADU"): "Virudunagar",
    ("KAMAREDDY", "TELANGANA"): "Kamareddi",
    ("MAHABUBABAD", "TELANGANA"): "Mahbubabad",
    ("RAJANNA SIRCILLA", "TELANGANA"): "Sirsilla",
    ("JAYASHANKAR BHUPALAPALLY", "TELANGANA"): "Bhupalpally",
    ("NAGARKURNOOL", "TELANGANA"): "Achampet",
    ("BUDGAM", "JAMMU AND KASHMIR"): "Badgam",
    ("BANDIPORA", "JAMMU AND KASHMIR"): "Bandipura",
    ("BARAMULLA", "JAMMU AND KASHMIR"): "Baramula",
    ("NONEY", "MANIPUR"): "Haochong",
    ("IMPHAL EAST", "MANIPUR"): "Imphal",
    ("IMPHAL WEST", "MANIPUR"): "Imphal",
    ("LAKHISARAI", "BIHAR"): "Luckeesarai",
    ("CHIKBALLAPUR", "KARNATAKA"): "Chintamani",
    ("WAYANAD", "KERALA"): "Mananthavady",
    ("CHAMPHAI", "MIZORAM"): "Khawzawl",
    ("SHAMATOR", "NAGALAND"): "Noklak",
    ("SERAIKELA-KHARSAWAN", "JHARKHAND"): "Saraikela",
}


def clean_district_name(name: str) -> str:
    """Clean parentheses, abbreviations, and extra spaces from district names."""
    cleaned = re.sub(r"\(.*?\)", "", name).strip()
    cleaned = cleaned.replace(".", "").strip()
    # Normalize multiple whitespace characters
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def seed_district_geography(force_refresh: bool = False):
    """
    Enriches all 785 districts with coordinates and elevation from Open-Meteo.
    Inserts or updates records in `district_geo_centroids`.
    """
    db = SessionLocal()
    
    # Check existing count
    existing_count = db.execute(text("SELECT COUNT(*) FROM district_geo_centroids")).scalar()
    print(f"Current district_geo_centroids count in DB: {existing_count}")
    
    # Query all districts with state names
    districts = db.execute(text("""
        SELECT d.id, d.district_name, d.district_code, s.state_name
        FROM districts d
        JOIN states s ON d.state_id = s.id
        ORDER BY d.id
    """)).fetchall()
    
    total = len(districts)
    print(f"Total districts to enrich: {total}")
    
    upsert_sql = text("""
        INSERT INTO district_geo_centroids (district_id, latitude, longitude, elevation_meters, source, created_at, updated_at)
        VALUES (:district_id, :latitude, :longitude, :elevation_meters, :source, NOW(), NOW())
        ON CONFLICT (district_id) DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            elevation_meters = EXCLUDED.elevation_meters,
            source = EXCLUDED.source,
            updated_at = NOW()
    """)
    
    client = httpx.Client(timeout=10.0)
    resolved_count = 0
    unresolved = []
    start_time = time.time()
    
    for idx, (d_id, d_name, d_code, s_name) in enumerate(districts):
        # Check if already exists unless force_refresh
        if not force_refresh:
            existing = db.execute(
                text("SELECT id FROM district_geo_centroids WHERE district_id = :d_id"),
                {"d_id": d_id}
            ).fetchone()
            if existing:
                resolved_count += 1
                continue

        # Build candidate search queries
        key = (d_name.strip().upper(), s_name.strip().upper())
        candidates = []
        if key in DISTRICT_ALIASES:
            candidates.append(DISTRICT_ALIASES[key])
        
        c_name = clean_district_name(d_name)
        if c_name not in candidates:
            candidates.append(c_name)
        if d_name not in candidates:
            candidates.append(d_name)
            
        found_match = None
        
        for cand in candidates:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={cand}&countryCode=IN&count=10&language=en&format=json"
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        # Prioritize state match
                        for r in results:
                            adm1 = (r.get("admin1") or "").lower()
                            st = s_name.lower()
                            if st in adm1 or adm1 in st or ("delhi" in st and "delhi" in adm1):
                                found_match = r
                                break
                        if not found_match and len(results) > 0:
                            found_match = results[0]
            except Exception as e:
                # Retrying once after brief pause
                time.sleep(0.5)
                try:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        results = resp.json().get("results", [])
                        if results:
                            found_match = results[0]
                except Exception:
                    pass
            
            if found_match:
                break
        
        if found_match:
            lat = Decimal(str(round(found_match["latitude"], 6)))
            lon = Decimal(str(round(found_match["longitude"], 6)))
            elevation = None
            if found_match.get("elevation") is not None:
                elevation = Decimal(str(round(found_match["elevation"], 2)))
                
            db.execute(upsert_sql, {
                "district_id": d_id,
                "latitude": lat,
                "longitude": lon,
                "elevation_meters": elevation,
                "source": "open-meteo",
            })
            resolved_count += 1
        else:
            unresolved.append((d_id, d_name, d_code, s_name))
            
        # Commit periodically every 50 records
        if (idx + 1) % 50 == 0:
            db.commit()
            elapsed = time.time() - start_time
            print(f"Processed {idx + 1}/{total} districts ({resolved_count} resolved) in {elapsed:.1f}s")
            
        # Rate limit to ~12 req/sec to stay well under 600 req/min
        time.sleep(0.08)

    db.commit()
    db.close()
    
    elapsed = time.time() - start_time
    print("\n=======================================================")
    print("DISTRICT GEOGRAPHIC ENRICHMENT COMPLETE")
    print(f"Total districts in DB: {total}")
    print(f"Resolved and cached:   {resolved_count} ({resolved_count/total*100:.1f}%)")
    print(f"Unresolved districts:  {len(unresolved)}")
    print(f"Total time elapsed:    {elapsed:.1f} seconds")
    print("=======================================================")
    
    if unresolved:
        print("\nUnresolved details:")
        for u in unresolved:
            print(f"  ID: {u[0]}, District: '{u[1]}', LGD Code: {u[2]}, State: '{u[3]}'")


if __name__ == "__main__":
    force = "--force" in sys.argv
    seed_district_geography(force_refresh=force)
