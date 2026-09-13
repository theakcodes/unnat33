"""Idempotent seed script for populating normalized scheme metadata:
- sectors reference table (5 standard sectors)
- scheme_sectors junction table (25 directly source-supported mappings)
- scheme_eligibility table (12 rows with strict source-supported social category rules)

Safety Guarantees:
- The schemes table is 100% UNTOUCHED (zero INSERTs, zero UPDATEs, zero DELETEs).
- Atomic transaction: rolls back immediately if any step or assertion fails.
- Completely idempotent: safe to run multiple times without duplicating rows.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Ensure backend root is on Python module path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from app.db.database import engine


# 1. Canonical Sectors (5 sectors approved by user)
SECTORS_DATA = [
    ("MFG", "Manufacturing", "Enterprises engaged in the manufacture or production of goods"),
    ("SRV", "Services", "Enterprises engaged in providing or rendering of services"),
    ("TRD", "Trading / Retail", "Wholesale, retail, and commercial trading activities"),
    ("AGR", "Agriculture and Allied Activities", "Agricultural, allied farm, dairy, poultry, and agro-processing activities"),
    ("ART", "Artisans and Traditional Crafts", "Traditional craftspeople and artisans working with hand tools across identified trades"),
]

# 2. Directly Source-Supported Sector Mappings (25 mappings)
# Strict source-supported mappings only (Decision 3 Option A):
# - Schemes 1-4 (MUDRA): Manufacturing, Services, Trading (4 x 3 = 12)
# - Schemes 5-6 (PMEGP): Manufacturing, Services (2 x 2 = 4)
# - Scheme 7 (PM Vishwakarma): Artisans and Traditional Crafts (1)
# - Schemes 9, 11 (NSFDC MFS & Term Loan): Agriculture/Allied, Manufacturing, Services, Trading (2 x 4 = 8)
# - Schemes 8, 10, 12: Left unmapped (no direct economic sector specified in source)
SCHEME_SECTOR_MAPPINGS = [
    # MUDRA Shishu, Kishore, Tarun, Tarun Plus -> MFG, SRV, TRD
    (1, "MFG"), (1, "SRV"), (1, "TRD"),
    (2, "MFG"), (2, "SRV"), (2, "TRD"),
    (3, "MFG"), (3, "SRV"), (3, "TRD"),
    (4, "MFG"), (4, "SRV"), (4, "TRD"),
    # PMEGP & PMEGP 2nd Loan -> MFG, SRV
    (5, "MFG"), (5, "SRV"),
    (6, "MFG"), (6, "SRV"),
    # PM Vishwakarma -> ART
    (7, "ART"),
    # NSFDC MFS & NSFDC Term Loan -> AGR, MFG, SRV, TRD
    (9, "AGR"), (9, "MFG"), (9, "SRV"), (9, "TRD"),
    (11, "AGR"), (11, "MFG"), (11, "SRV"), (11, "TRD"),
]

# 3. Scheme Eligibility Criteria (12 rows, Decision 1 Option A)
# Social category fields: NULL for universal schemes with no caste restriction.
# Only set TRUE/FALSE where explicitly established by statutory source.
ELIGIBILITY_DATA = [
    # 1. PM MUDRA Shishu
    {
        "scheme_id": 1,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Collateral-free micro loans up to Rs. 50,000 for income-generating micro enterprises",
    },
    # 2. PM MUDRA Kishore
    {
        "scheme_id": 2,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Collateral-free micro loans above Rs. 50,000 up to Rs. 5 lakh",
    },
    # 3. PM MUDRA Tarun
    {
        "scheme_id": 3,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Collateral-free credit above Rs. 5 lakh up to Rs. 10 lakh",
    },
    # 4. PM MUDRA Tarun Plus
    {
        "scheme_id": 4,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Requires prior availing and successful repayment of a Tarun category loan",
    },
    # 5. PMEGP (Explicitly supports category-based subsidy 15-35%)
    {
        "scheme_id": 5,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
        "minority_eligible": True, "pwd_eligible": True, "ex_servicemen_eligible": True,
        "min_age": 18, "max_age": None, "max_annual_income": None,
        "notes": "Credit-linked margin money subsidy 15% to 35% depending on applicant category and location",
    },
    # 6. PMEGP 2nd Loan for Upgradation
    {
        "scheme_id": 6,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Financial assistance for upgradation of performing existing PMEGP units",
    },
    # 7. PM Vishwakarma (Artisan trades, min_age 18)
    {
        "scheme_id": 7,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": 18, "max_age": None, "max_annual_income": None,
        "notes": "Exclusively for traditional artisans and craftspeople across 18 identified trades",
    },
    # 8. PM SVANidhi (Urban street vendors)
    {
        "scheme_id": 8,
        "rural_eligible": False, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": None, "sc_eligible": None, "st_eligible": None, "obc_eligible": None,
        "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
        "min_age": None, "max_age": None, "max_annual_income": None,
        "notes": "Collateral-free working capital loan for urban street vendors and hawkers",
    },
    # 9. NSFDC Micro Finance Scheme (Scheduled Caste only, income ceiling 5L)
    {
        "scheme_id": 9,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": False, "sc_eligible": True, "st_eligible": False, "obc_eligible": False,
        "minority_eligible": False, "pwd_eligible": False, "ex_servicemen_eligible": False,
        "min_age": None, "max_age": None, "max_annual_income": Decimal("500000.00"),
        "notes": "Concessional micro-credit for Scheduled Caste beneficiaries with annual family income up to Rs. 5 lakh",
    },
    # 10. NSFDC Aajeevika Micro-Finance Yojana (Scheduled Caste only, income ceiling 5L)
    {
        "scheme_id": 10,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": False, "sc_eligible": True, "st_eligible": False, "obc_eligible": False,
        "minority_eligible": False, "pwd_eligible": False, "ex_servicemen_eligible": False,
        "min_age": None, "max_age": None, "max_annual_income": Decimal("500000.00"),
        "notes": "Micro-finance via NBFC-MFIs for Scheduled Caste beneficiaries with family income up to Rs. 5 lakh",
    },
    # 11. NSFDC Term Loan Scheme (Scheduled Caste only, income ceiling 5L)
    {
        "scheme_id": 11,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": False, "sc_eligible": True, "st_eligible": False, "obc_eligible": False,
        "minority_eligible": False, "pwd_eligible": False, "ex_servicemen_eligible": False,
        "min_age": None, "max_age": None, "max_annual_income": Decimal("500000.00"),
        "notes": "Concessional term finance for projects costing up to Rs. 50 lakh for Scheduled Caste beneficiaries",
    },
    # 12. NSFDC Udyam Nidhi Yojana (Scheduled Caste only, income ceiling 5L)
    {
        "scheme_id": 12,
        "rural_eligible": True, "urban_eligible": True,
        "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
        "general_eligible": False, "sc_eligible": True, "st_eligible": False, "obc_eligible": False,
        "minority_eligible": False, "pwd_eligible": False, "ex_servicemen_eligible": False,
        "min_age": None, "max_age": None, "max_annual_income": Decimal("500000.00"),
        "notes": "Financing through cooperative institutions and small finance banks for Scheduled Caste beneficiaries",
    },
]


def run_seed():
    print("=" * 65)
    print("STARTING NORMALIZED ELIGIBILITY & SECTORS DATA SEEDING")
    print("=" * 65)

    with engine.begin() as conn:
        # Step 0: Pre-condition check on schemes table
        initial_scheme_count = conn.execute(text("SELECT COUNT(*) FROM schemes;")).scalar()
        print(f"[CHECK] Current schemes row count: {initial_scheme_count}")
        if initial_scheme_count != 12:
            raise RuntimeError(
                f"Expected exactly 12 schemes in database, found {initial_scheme_count}. Aborting."
            )

        # Record checksum / row identities to verify schemes remains 100% untouched
        initial_schemes = conn.execute(text("SELECT id, name FROM schemes ORDER BY id;")).fetchall()

        # Step 1: Seed Sectors (5 standard sectors)
        print("\n[STEP 1] Seeding sectors reference table...")
        for code, name, desc in SECTORS_DATA:
            conn.execute(
                text("""
                    INSERT INTO sectors (sector_code, sector_name, description)
                    VALUES (:code, :name, :desc)
                    ON CONFLICT (sector_name) DO UPDATE SET
                        sector_code = EXCLUDED.sector_code,
                        description = EXCLUDED.description;
                """),
                {"code": code, "name": name, "desc": desc},
            )
        sectors_count = conn.execute(text("SELECT COUNT(*) FROM sectors;")).scalar()
        print(f" -> Sectors populated: {sectors_count} rows.")

        # Build sector code -> id mapping
        sector_rows = conn.execute(text("SELECT id, sector_code FROM sectors;")).fetchall()
        sector_id_map = {row.sector_code: row.id for row in sector_rows}

        # Step 2: Seed Scheme-Sector Mappings (25 source-supported mappings)
        print("\n[STEP 2] Seeding scheme_sectors junction records...")
        for scheme_id, sector_code in SCHEME_SECTOR_MAPPINGS:
            sector_id = sector_id_map.get(sector_code)
            if not sector_id:
                raise ValueError(f"Unknown sector code: {sector_code}")
            conn.execute(
                text("""
                    INSERT INTO scheme_sectors (scheme_id, sector_id)
                    VALUES (:scheme_id, :sector_id)
                    ON CONFLICT (scheme_id, sector_id) DO NOTHING;
                """),
                {"scheme_id": scheme_id, "sector_id": sector_id},
            )
        ss_count = conn.execute(text("SELECT COUNT(*) FROM scheme_sectors;")).scalar()
        print(f" -> Scheme-Sectors populated: {ss_count} mappings.")

        # Step 3: Seed Scheme Eligibility Criteria (12 rows)
        print("\n[STEP 3] Seeding scheme_eligibility records...")
        for elig in ELIGIBILITY_DATA:
            conn.execute(
                text("""
                    INSERT INTO scheme_eligibility (
                        scheme_id, rural_eligible, urban_eligible,
                        male_eligible, female_eligible, other_gender_eligible,
                        general_eligible, sc_eligible, st_eligible, obc_eligible,
                        minority_eligible, pwd_eligible, ex_servicemen_eligible,
                        min_age, max_age, max_annual_income, notes
                    ) VALUES (
                        :scheme_id, :rural_eligible, :urban_eligible,
                        :male_eligible, :female_eligible, :other_gender_eligible,
                        :general_eligible, :sc_eligible, :st_eligible, :obc_eligible,
                        :minority_eligible, :pwd_eligible, :ex_servicemen_eligible,
                        :min_age, :max_age, :max_annual_income, :notes
                    )
                    ON CONFLICT (scheme_id) DO UPDATE SET
                        rural_eligible = EXCLUDED.rural_eligible,
                        urban_eligible = EXCLUDED.urban_eligible,
                        male_eligible = EXCLUDED.male_eligible,
                        female_eligible = EXCLUDED.female_eligible,
                        other_gender_eligible = EXCLUDED.other_gender_eligible,
                        general_eligible = EXCLUDED.general_eligible,
                        sc_eligible = EXCLUDED.sc_eligible,
                        st_eligible = EXCLUDED.st_eligible,
                        obc_eligible = EXCLUDED.obc_eligible,
                        minority_eligible = EXCLUDED.minority_eligible,
                        pwd_eligible = EXCLUDED.pwd_eligible,
                        ex_servicemen_eligible = EXCLUDED.ex_servicemen_eligible,
                        min_age = EXCLUDED.min_age,
                        max_age = EXCLUDED.max_age,
                        max_annual_income = EXCLUDED.max_annual_income,
                        notes = EXCLUDED.notes;
                """),
                elig,
            )
        elig_count = conn.execute(text("SELECT COUNT(*) FROM scheme_eligibility;")).scalar()
        print(f" -> Scheme Eligibility populated: {elig_count} rows.")

        # Step 4: Strict Post-Condition Verifications
        print("\n[STEP 4] Executing strict post-condition assertions...")

        # 4.1 Schemes table must remain exactly 12 and untouched
        final_scheme_count = conn.execute(text("SELECT COUNT(*) FROM schemes;")).scalar()
        if final_scheme_count != 12:
            raise RuntimeError(f"Schemes count altered! Expected 12, got {final_scheme_count}")

        final_schemes = conn.execute(text("SELECT id, name FROM schemes ORDER BY id;")).fetchall()
        if initial_schemes != final_schemes:
            raise RuntimeError("Schemes identity altered! Aborting transaction.")
        print(" [PASS] schemes table is 100% UNTOUCHED (12 rows identical).")

        # 4.2 Sectors count must be exactly 5
        if sectors_count != 5:
            raise RuntimeError(f"Expected 5 sectors, got {sectors_count}")
        print(" [PASS] sectors table has exactly 5 canonical sectors.")

        # 4.3 Scheme_sectors count must be exactly 25
        if ss_count != 25:
            raise RuntimeError(f"Expected 25 scheme_sectors mappings, got {ss_count}")
        print(" [PASS] scheme_sectors table has exactly 25 source-supported mappings.")

        # 4.4 Scheme_eligibility count must be exactly 12
        if elig_count != 12:
            raise RuntimeError(f"Expected 12 eligibility records, got {elig_count}")
        print(" [PASS] scheme_eligibility table has exactly 12 records.")

        # 4.5 Foreign key integrity / orphan check
        orphan_elig = conn.execute(text("""
            SELECT COUNT(*) FROM scheme_eligibility e
            LEFT JOIN schemes s ON e.scheme_id = s.id
            WHERE s.id IS NULL;
        """)).scalar()
        orphan_ss = conn.execute(text("""
            SELECT COUNT(*) FROM scheme_sectors ss
            LEFT JOIN schemes s ON ss.scheme_id = s.id
            LEFT JOIN sectors sec ON ss.sector_id = sec.id
            WHERE s.id IS NULL OR sec.id IS NULL;
        """)).scalar()
        if orphan_elig != 0 or orphan_ss != 0:
            raise RuntimeError("Orphaned foreign key records detected!")
        print(" [PASS] Zero orphaned records in relational foreign keys.")

        # 4.6 Verification of NSFDC Social Category Criteria
        nsfdc_check = conn.execute(text("""
            SELECT COUNT(*) FROM scheme_eligibility
            WHERE scheme_id IN (9, 10, 11, 12)
              AND sc_eligible = TRUE
              AND general_eligible = FALSE
              AND max_annual_income = 500000.00;
        """)).scalar()
        if nsfdc_check != 4:
            raise RuntimeError(f"NSFDC social category check failed (count={nsfdc_check})")
        print(" [PASS] NSFDC schemes verified: SC-only affirmative action, income limit Rs. 5L.")

        # 4.7 Verification of Universal Schemes (social category is NULL)
        universal_check = conn.execute(text("""
            SELECT COUNT(*) FROM scheme_eligibility
            WHERE scheme_id IN (1, 2, 3, 4, 6, 7, 8)
              AND general_eligible IS NULL
              AND sc_eligible IS NULL;
        """)).scalar()
        if universal_check != 7:
            raise RuntimeError(f"Universal schemes category check failed (count={universal_check})")
        print(" [PASS] Universal schemes verified: social category eligibility fields are NULL.")

    print("\n" + "=" * 65)
    print("SUCCESS: Database transaction committed cleanly.")
    print("=" * 65)


if __name__ == "__main__":
    run_seed()
