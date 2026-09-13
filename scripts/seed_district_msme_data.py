"""
scripts/seed_district_msme_data.py

Transactional, idempotent ingestion script for District MSME market sizing data.
Ingests MSME.csv into PostgreSQL:
1. states (36 States and Union Territories)
2. districts (785 districts with unique LGD code stored in district_code)
3. msme_district_data (785 records with micro, small, medium enterprise metrics)

Invariants verified:
- Exactly 36 States/UTs
- Exactly 785 Districts
- Exactly 785 MSME district data records
- 100% Unique LGD codes in district_code
- 100% Mathematical consistency: micro + small + medium == total
- Idempotent and repeatable (uses ON CONFLICT DO UPDATE)
- Leaves all 12 legacy schemes, 60 government programs, and user tables 100% untouched.
"""

import os
import csv
import sys
from pathlib import Path
from datetime import date
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Canonical ISO / standard abbreviations for Indian States and UTs
STATE_CODE_MAP = {
    1: "JK",   # Jammu and Kashmir
    2: "HP",   # Himachal Pradesh
    3: "PB",   # Punjab
    4: "CH",   # Chandigarh
    5: "UK",   # Uttarakhand
    6: "HR",   # Haryana
    7: "DL",   # Delhi
    8: "RJ",   # Rajasthan
    9: "UP",   # Uttar Pradesh
    10: "BR",  # Bihar
    11: "SK",  # Sikkim
    12: "AR",  # Arunachal Pradesh
    13: "NL",  # Nagaland
    14: "MN",  # Manipur
    15: "MZ",  # Mizoram
    16: "TR",  # Tripura
    17: "ML",  # Meghalaya
    18: "AS",  # Assam
    19: "WB",  # West Bengal
    20: "JH",  # Jharkhand
    21: "OD",  # Odisha
    22: "CG",  # Chhattisgarh
    23: "MP",  # Madhya Pradesh
    24: "GJ",  # Gujarat
    27: "MH",  # Maharashtra
    28: "AP",  # Andhra Pradesh
    29: "KA",  # Karnataka
    30: "GA",  # Goa
    31: "LD",  # Lakshadweep
    32: "KL",  # Kerala
    33: "TN",  # Tamil Nadu
    34: "PY",  # Puducherry
    35: "AN",  # Andaman and Nicobar Islands
    36: "TG",  # Telangana
    37: "LA",  # Ladakh
    38: "DH",  # Dadra and Nagar Haveli and Daman and Diu
}

def get_engine():
    from app.db.database import engine
    return engine

def seed_district_data(csv_path: Path = None):
    if csv_path is None:
        csv_path = Path(r"C:\Users\Aadi Jain\Desktop\dataset\MSME.csv")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"MSME.csv not found at {csv_path}")

    print("=" * 70)
    print("PHASE 3A: SEEDING DISTRICT MSME DATA")
    print(f"Source: {csv_path}")
    print("=" * 70)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    header = reader[0]
    data = reader[1:]
    print(f"Read {len(data)} data rows from {csv_path.name}")

    engine = get_engine()
    reporting_date = date(2024, 3, 31)

    with engine.begin() as conn:
        # 1. Extract and Upsert States
        states_dict = {}
        for r in data:
            sid = int(r[1])
            sname = r[0].strip().upper()
            if sid not in states_dict:
                states_dict[sid] = sname

        print(f"Upserting {len(states_dict)} States/UTs...")
        for sid, sname in states_dict.items():
            scode = STATE_CODE_MAP.get(sid, f"ST{sid:02d}")
            conn.execute(
                text("""
                    INSERT INTO states (id, state_code, state_name, created_at)
                    VALUES (:id, :state_code, :state_name, NOW())
                    ON CONFLICT (id) DO UPDATE 
                    SET state_name = EXCLUDED.state_name,
                        state_code = EXCLUDED.state_code;
                """),
                {"id": sid, "state_code": scode, "state_name": sname}
            )

        # 2. Extract and Upsert Districts
        print(f"Upserting {len(data)} Districts...")
        for r in data:
            sname = r[0].strip().upper()
            sid = int(r[1])
            dname = r[2].strip()
            lgd = str(r[3]).strip()

            conn.execute(
                text("""
                    INSERT INTO districts (district_code, district_name, state_id, created_at)
                    VALUES (:district_code, :district_name, :state_id, NOW())
                    ON CONFLICT (district_code) DO UPDATE
                    SET district_name = EXCLUDED.district_name,
                        state_id = EXCLUDED.state_id;
                """),
                {"district_code": lgd, "district_name": dname, "state_id": sid}
            )

        # Fetch district primary key mapping (lg_dt_code -> district_id)
        d_rows = conn.execute(text("SELECT id, district_code FROM districts;")).fetchall()
        lgd_to_id = {r[1]: r[0] for r in d_rows}

        # 3. Upsert MSME District Data
        print(f"Upserting {len(data)} MSME District Data records...")
        for r in data:
            lgd = str(r[3]).strip()
            district_id = lgd_to_id[lgd]
            medium = int(r[4])
            micro = int(r[5])
            small = int(r[6])
            tot = int(r[7])

            assert micro + small + medium == tot, f"Math mismatch in {r}"

            conn.execute(
                text("""
                    INSERT INTO msme_district_data (
                        district_id, reporting_date,
                        micro_enterprises, small_enterprises, medium_enterprises,
                        source_name, source_url, created_at
                    )
                    VALUES (
                        :district_id, :reporting_date,
                        :micro_enterprises, :small_enterprises, :medium_enterprises,
                        :source_name, :source_url, NOW()
                    )
                    ON CONFLICT (district_id, reporting_date) DO UPDATE
                    SET micro_enterprises = EXCLUDED.micro_enterprises,
                        small_enterprises = EXCLUDED.small_enterprises,
                        medium_enterprises = EXCLUDED.medium_enterprises,
                        source_name = EXCLUDED.source_name,
                        source_url = EXCLUDED.source_url;
                """),
                {
                    "district_id": district_id,
                    "reporting_date": reporting_date,
                    "micro_enterprises": micro,
                    "small_enterprises": small,
                    "medium_enterprises": medium,
                    "source_name": "Udyam Registration Portal (Kaggle MSME.csv)",
                    "source_url": "https://udyamregistration.gov.in/",
                }
            )

    # 4. Validation
    with engine.connect() as conn:
        st_count = conn.execute(text("SELECT COUNT(*) FROM states;")).scalar()
        dt_count = conn.execute(text("SELECT COUNT(*) FROM districts;")).scalar()
        m_count = conn.execute(text("SELECT COUNT(*) FROM msme_district_data;")).scalar()

        total_micro = conn.execute(text("SELECT SUM(micro_enterprises) FROM msme_district_data;")).scalar()
        total_small = conn.execute(text("SELECT SUM(small_enterprises) FROM msme_district_data;")).scalar()
        total_medium = conn.execute(text("SELECT SUM(medium_enterprises) FROM msme_district_data;")).scalar()

        print("\n--- INGESTION VALIDATION ---")
        print(f"States Count:             {st_count} (Expected: 36)")
        print(f"Districts Count:          {dt_count} (Expected: 785)")
        print(f"MSME District Data Count: {m_count} (Expected: 785)")
        print(f"Total Micro Enterprises:  {total_micro:,}")
        print(f"Total Small Enterprises:  {total_small:,}")
        print(f"Total Medium Enterprises: {total_medium:,}")
        print(f"Total MSMEs:              {(total_micro + total_small + total_medium):,}")

        assert st_count == 36, f"Expected 36 states, found {st_count}"
        assert dt_count == 785, f"Expected 785 districts, found {dt_count}"
        assert m_count == 785, f"Expected 785 msme_district_data records, found {m_count}"

    print("\nSUCCESS: Phase 3A District MSME Data Ingestion Complete!")

if __name__ == "__main__":
    seed_district_data()
