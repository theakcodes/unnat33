"""
scripts/seed_government_programs.py

Transactional, idempotent seeding script for all 115 Government of India Programmes:
- 12 legacy programmes linked 1:1 to schemes.id (IDs 1-12)
- 48 baseline researched programmes (IDs 13-60)
- 55 expanded & verified GoI programmes (IDs 61-115) including all 5 data-correction passes.

Guarantees:
- Transactional: entire seed runs in a single transaction; rolls back on any error.
- Idempotent: safe to run multiple times without creating duplicates or altering baseline IDs.
- Cross-Database: fully compatible with both SQLite (local dev) and PostgreSQL (production).
- Strict Option A eligibility semantics (NULL = open, TRUE/FALSE = statutory constraint).
- Authoritative financial parameters in specialized child tables.
- Preserves baseline IDs 1-60 and parent-child hierarchy relationships.
"""

import os
import json
import sys
from pathlib import Path
from decimal import Decimal
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Ensure all SQLAlchemy declarative models are registered on Base
import app.models.master
import app.models.scheme
import app.models.program_models
import app.models.research_models
from app.db.database import Base, engine as default_engine

def get_engine():
    Base.metadata.create_all(bind=default_engine)
    return default_engine

def seed(custom_engine=None):
    engine = custom_engine or get_engine()
    # Ensure tables exist on the target engine
    Base.metadata.create_all(bind=engine)
    dialect = engine.dialect.name
    print(f"Starting seed process on database dialect: {dialect} ({engine.url})...")

    catalogue_path = Path(__file__).resolve().parent / "government_programs_catalogue.json"
    if not catalogue_path.exists():
        raise FileNotFoundError(f"Catalogue file not found at: {catalogue_path}")

    with open(catalogue_path, "r", encoding="utf-8") as f:
        catalogue = json.load(f)

    print(f"Loaded {len(catalogue)} programmes from catalogue.")
    assert len(catalogue) == 115, f"Expected 115 programmes in catalogue, found {len(catalogue)}"

    # Sector mapping: code -> ID
    sector_map = {
        "MFG": 1,
        "SRV": 2,
        "TRD": 3,
        "AGR": 4,
        "ART": 5,
    }

    with engine.begin() as conn:
        # Ensure sectors table is populated
        for code, sid in sector_map.items():
            sname = {
                "MFG": "Manufacturing",
                "SRV": "Services",
                "TRD": "Trading / Retail",
                "AGR": "Agriculture and Allied Activities",
                "ART": "Artisans and Traditional Crafts",
            }[code]
            if dialect == "sqlite":
                conn.execute(text("""
                    INSERT OR IGNORE INTO sectors (id, sector_code, sector_name)
                    VALUES (:id, :code, :name);
                """), {"id": sid, "code": code, "name": sname})
            else:
                conn.execute(text("""
                    INSERT INTO sectors (id, sector_code, sector_name)
                    VALUES (:id, :code, :name)
                    ON CONFLICT (id) DO UPDATE SET
                        sector_code = EXCLUDED.sector_code,
                        sector_name = EXCLUDED.sector_name;
                """), {"id": sid, "code": code, "name": sname})

        # 1. Upsert all government_programs records
        inserted_count = 0
        sectors_mapped_count = 0
        eligibility_count = 0
        credit_count = 0
        guarantee_count = 0
        subsidy_count = 0

        # Step 1: Insert/update programme rows
        for item in catalogue:
            p = item["program"].copy()
            prog_id_explicit = item.get("id")
            sec_types = p.get("secondary_types")
            if sec_types is not None and isinstance(sec_types, list):
                sec_types_json = json.dumps(sec_types) if dialect == "sqlite" else sec_types
            else:
                sec_types_json = None

            p_params = {
                "explicit_id": prog_id_explicit,
                "program_code": p["program_code"],
                "program_name": p["program_name"],
                "owning_ministry": p["owning_ministry"],
                "nodal_agency": p.get("nodal_agency"),
                "official_portal_url": p["official_portal_url"],
                "primary_type": p["primary_type"],
                "secondary_types": sec_types_json,
                "actionability_type": p["actionability_type"],
                "hierarchy_level": p["hierarchy_level"],
                "description": p.get("description"),
                "benefit_summary": p["benefit_summary"],
                "benefit_type": p["benefit_type"],
                "benefit_headline_numeric": p.get("benefit_headline_numeric"),
                "benefit_headline_percentage": p.get("benefit_headline_percentage"),
                "target_beneficiary_summary": p.get("target_beneficiary_summary"),
                "status": p.get("status", "active"),
                "legacy_scheme_id": p.get("legacy_scheme_id"),
            }

            if dialect == "sqlite":
                # For SQLite, check if exists by code
                existing = conn.execute(
                    text("SELECT id FROM government_programs WHERE program_code = :code;"),
                    {"code": p["program_code"]}
                ).fetchone()

                if existing:
                    prog_id = existing[0]
                    conn.execute(text("""
                        UPDATE government_programs
                        SET program_name = :program_name,
                            owning_ministry = :owning_ministry,
                            nodal_agency = :nodal_agency,
                            official_portal_url = :official_portal_url,
                            primary_type = :primary_type,
                            secondary_types = :secondary_types,
                            actionability_type = :actionability_type,
                            hierarchy_level = :hierarchy_level,
                            description = :description,
                            benefit_summary = :benefit_summary,
                            benefit_type = :benefit_type,
                            benefit_headline_numeric = :benefit_headline_numeric,
                            benefit_headline_percentage = :benefit_headline_percentage,
                            target_beneficiary_summary = :target_beneficiary_summary,
                            status = :status,
                            legacy_scheme_id = :legacy_scheme_id,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id;
                    """), {**p_params, "id": prog_id})
                else:
                    if prog_id_explicit:
                        conn.execute(text("""
                            INSERT INTO government_programs (
                                id, program_code, program_name, owning_ministry, nodal_agency,
                                official_portal_url, primary_type, secondary_types, actionability_type,
                                hierarchy_level, description, benefit_summary, benefit_type,
                                benefit_headline_numeric, benefit_headline_percentage,
                                target_beneficiary_summary, status, legacy_scheme_id, created_at, updated_at
                            ) VALUES (
                                :explicit_id, :program_code, :program_name, :owning_ministry, :nodal_agency,
                                :official_portal_url, :primary_type, :secondary_types, :actionability_type,
                                :hierarchy_level, :description, :benefit_summary, :benefit_type,
                                :benefit_headline_numeric, :benefit_headline_percentage,
                                :target_beneficiary_summary, :status, :legacy_scheme_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            );
                        """), p_params)
                        prog_id = prog_id_explicit
                    else:
                        conn.execute(text("""
                            INSERT INTO government_programs (
                                program_code, program_name, owning_ministry, nodal_agency,
                                official_portal_url, primary_type, secondary_types, actionability_type,
                                hierarchy_level, description, benefit_summary, benefit_type,
                                benefit_headline_numeric, benefit_headline_percentage,
                                target_beneficiary_summary, status, legacy_scheme_id, created_at, updated_at
                            ) VALUES (
                                :program_code, :program_name, :owning_ministry, :nodal_agency,
                                :official_portal_url, :primary_type, :secondary_types, :actionability_type,
                                :hierarchy_level, :description, :benefit_summary, :benefit_type,
                                :benefit_headline_numeric, :benefit_headline_percentage,
                                :target_beneficiary_summary, :status, :legacy_scheme_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            );
                        """), p_params)
                        prog_id = conn.execute(text("SELECT id FROM government_programs WHERE program_code = :code;"), {"code": p["program_code"]}).scalar()
            else:
                # PostgreSQL with explicit ID or ON CONFLICT
                if prog_id_explicit:
                    insert_sql = text("""
                        INSERT INTO government_programs (
                            id, program_code, program_name, owning_ministry, nodal_agency,
                            official_portal_url, primary_type, secondary_types, actionability_type,
                            hierarchy_level, description, benefit_summary, benefit_type,
                            benefit_headline_numeric, benefit_headline_percentage,
                            target_beneficiary_summary, status, legacy_scheme_id, created_at, updated_at
                        ) VALUES (
                            :explicit_id, :program_code, :program_name, :owning_ministry, :nodal_agency,
                            :official_portal_url, :primary_type, :secondary_types, :actionability_type,
                            :hierarchy_level, :description, :benefit_summary, :benefit_type,
                            :benefit_headline_numeric, :benefit_headline_percentage,
                            :target_beneficiary_summary, :status, :legacy_scheme_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (program_code) DO UPDATE SET
                            program_name = EXCLUDED.program_name,
                            owning_ministry = EXCLUDED.owning_ministry,
                            nodal_agency = EXCLUDED.nodal_agency,
                            official_portal_url = EXCLUDED.official_portal_url,
                            primary_type = EXCLUDED.primary_type,
                            secondary_types = EXCLUDED.secondary_types,
                            actionability_type = EXCLUDED.actionability_type,
                            hierarchy_level = EXCLUDED.hierarchy_level,
                            description = EXCLUDED.description,
                            benefit_summary = EXCLUDED.benefit_summary,
                            benefit_type = EXCLUDED.benefit_type,
                            benefit_headline_numeric = EXCLUDED.benefit_headline_numeric,
                            benefit_headline_percentage = EXCLUDED.benefit_headline_percentage,
                            target_beneficiary_summary = EXCLUDED.target_beneficiary_summary,
                            status = EXCLUDED.status,
                            legacy_scheme_id = EXCLUDED.legacy_scheme_id,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id;
                    """)
                else:
                    insert_sql = text("""
                        INSERT INTO government_programs (
                            program_code, program_name, owning_ministry, nodal_agency,
                            official_portal_url, primary_type, secondary_types, actionability_type,
                            hierarchy_level, description, benefit_summary, benefit_type,
                            benefit_headline_numeric, benefit_headline_percentage,
                            target_beneficiary_summary, status, legacy_scheme_id, created_at, updated_at
                        ) VALUES (
                            :program_code, :program_name, :owning_ministry, :nodal_agency,
                            :official_portal_url, :primary_type, :secondary_types, :actionability_type,
                            :hierarchy_level, :description, :benefit_summary, :benefit_type,
                            :benefit_headline_numeric, :benefit_headline_percentage,
                            :target_beneficiary_summary, :status, :legacy_scheme_id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (program_code) DO UPDATE SET
                            program_name = EXCLUDED.program_name,
                            owning_ministry = EXCLUDED.owning_ministry,
                            nodal_agency = EXCLUDED.nodal_agency,
                            official_portal_url = EXCLUDED.official_portal_url,
                            primary_type = EXCLUDED.primary_type,
                            secondary_types = EXCLUDED.secondary_types,
                            actionability_type = EXCLUDED.actionability_type,
                            hierarchy_level = EXCLUDED.hierarchy_level,
                            description = EXCLUDED.description,
                            benefit_summary = EXCLUDED.benefit_summary,
                            benefit_type = EXCLUDED.benefit_type,
                            benefit_headline_numeric = EXCLUDED.benefit_headline_numeric,
                            benefit_headline_percentage = EXCLUDED.benefit_headline_percentage,
                            target_beneficiary_summary = EXCLUDED.target_beneficiary_summary,
                            status = EXCLUDED.status,
                            legacy_scheme_id = EXCLUDED.legacy_scheme_id,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id;
                    """)
                prog_id = conn.execute(insert_sql, p_params).scalar()

            inserted_count += 1

            # Seed program_sectors
            conn.execute(text("DELETE FROM program_sectors WHERE program_id = :pid;"), {"pid": prog_id})
            for sec_code in item.get("sectors", []):
                sec_id = sector_map.get(sec_code)
                if sec_id:
                    if dialect == "sqlite":
                        conn.execute(text("""
                            INSERT OR IGNORE INTO program_sectors (program_id, sector_id, created_at)
                            VALUES (:pid, :sid, CURRENT_TIMESTAMP);
                        """), {"pid": prog_id, "sid": sec_id})
                    else:
                        conn.execute(text("""
                            INSERT INTO program_sectors (program_id, sector_id, created_at)
                            VALUES (:pid, :sid, CURRENT_TIMESTAMP)
                            ON CONFLICT (program_id, sector_id) DO NOTHING;
                        """), {"pid": prog_id, "sid": sec_id})
                    sectors_mapped_count += 1

            # Seed program_eligibility
            if "eligibility" in item and item["eligibility"]:
                e = item["eligibility"].copy()
                e["program_id"] = prog_id
                e.setdefault("artisan_mandate", False)
                e.setdefault("street_vendor_mandate", False)
                e.setdefault("startup_mandate", False)
                e.setdefault("notes", None)
                conn.execute(text("""
                    INSERT INTO program_eligibility (
                        program_id, rural_eligible, urban_eligible, male_eligible, female_eligible,
                        other_gender_eligible, general_eligible, sc_eligible, st_eligible, obc_eligible,
                        minority_eligible, pwd_eligible, ex_servicemen_eligible, min_age, max_age,
                        max_annual_income, target_gender, target_social_categories,
                        artisan_mandate, street_vendor_mandate, startup_mandate, notes
                    ) VALUES (
                        :program_id, :rural_eligible, :urban_eligible, :male_eligible, :female_eligible,
                        :other_gender_eligible, :general_eligible, :sc_eligible, :st_eligible, :obc_eligible,
                        :minority_eligible, :pwd_eligible, :ex_servicemen_eligible, :min_age, :max_age,
                        :max_annual_income, :target_gender, :target_social_categories,
                        :artisan_mandate, :street_vendor_mandate, :startup_mandate, :notes
                    )
                    ON CONFLICT (program_id) DO UPDATE SET
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
                        target_gender = EXCLUDED.target_gender,
                        target_social_categories = EXCLUDED.target_social_categories,
                        artisan_mandate = EXCLUDED.artisan_mandate,
                        street_vendor_mandate = EXCLUDED.street_vendor_mandate,
                        startup_mandate = EXCLUDED.startup_mandate,
                        notes = EXCLUDED.notes;
                """), e)
                eligibility_count += 1

            # Seed program_credit_details
            if "credit" in item and item["credit"]:
                c = item["credit"].copy()
                c["program_id"] = prog_id
                c.setdefault("collateral_required", False)
                conn.execute(text("""
                    INSERT INTO program_credit_details (
                        program_id, min_loan_amount, max_loan_amount, interest_rate_min,
                        interest_rate_max, tenure_years, moratorium_months, collateral_required,
                        promoter_contribution_pct
                    ) VALUES (
                        :program_id, :min_loan_amount, :max_loan_amount, :interest_rate_min,
                        :interest_rate_max, :tenure_years, :moratorium_months, :collateral_required,
                        :promoter_contribution_pct
                    )
                    ON CONFLICT (program_id) DO UPDATE SET
                        min_loan_amount = EXCLUDED.min_loan_amount,
                        max_loan_amount = EXCLUDED.max_loan_amount,
                        interest_rate_min = EXCLUDED.interest_rate_min,
                        interest_rate_max = EXCLUDED.interest_rate_max,
                        tenure_years = EXCLUDED.tenure_years,
                        moratorium_months = EXCLUDED.moratorium_months,
                        collateral_required = EXCLUDED.collateral_required,
                        promoter_contribution_pct = EXCLUDED.promoter_contribution_pct;
                """), c)
                credit_count += 1

            # Seed program_guarantee_details
            if "guarantee" in item and item["guarantee"]:
                g = item["guarantee"].copy()
                g["program_id"] = prog_id
                g.setdefault("hybrid_security_allowed", False)
                conn.execute(text("""
                    INSERT INTO program_guarantee_details (
                        program_id, max_credit_limit, guarantee_coverage_pct, annual_guarantee_fee_pct,
                        hybrid_security_allowed, eligible_lending_institutions
                    ) VALUES (
                        :program_id, :max_credit_limit, :guarantee_coverage_pct, :annual_guarantee_fee_pct,
                        :hybrid_security_allowed, :eligible_lending_institutions
                    )
                    ON CONFLICT (program_id) DO UPDATE SET
                        max_credit_limit = EXCLUDED.max_credit_limit,
                        guarantee_coverage_pct = EXCLUDED.guarantee_coverage_pct,
                        annual_guarantee_fee_pct = EXCLUDED.annual_guarantee_fee_pct,
                        hybrid_security_allowed = EXCLUDED.hybrid_security_allowed,
                        eligible_lending_institutions = EXCLUDED.eligible_lending_institutions;
                """), g)
                guarantee_count += 1

            # Seed program_subsidy_details
            if "subsidy" in item and item["subsidy"]:
                s = item["subsidy"].copy()
                s["program_id"] = prog_id
                conn.execute(text("""
                    INSERT INTO program_subsidy_details (
                        program_id, subsidy_pct, max_subsidy_amount, min_project_cost,
                        max_project_cost, beneficiary_contribution_pct, disbursement_type
                    ) VALUES (
                        :program_id, :subsidy_pct, :max_subsidy_amount, :min_project_cost,
                        :max_project_cost, :beneficiary_contribution_pct, :disbursement_type
                    )
                    ON CONFLICT (program_id) DO UPDATE SET
                        subsidy_pct = EXCLUDED.subsidy_pct,
                        max_subsidy_amount = EXCLUDED.max_subsidy_amount,
                        min_project_cost = EXCLUDED.min_project_cost,
                        max_project_cost = EXCLUDED.max_project_cost,
                        beneficiary_contribution_pct = EXCLUDED.beneficiary_contribution_pct,
                        disbursement_type = EXCLUDED.disbursement_type;
                """), s)
                subsidy_count += 1

        # Step 2: Resolve parent_program_id relationships
        resolved_parents = 0
        for item in catalogue:
            p = item["program"]
            parent_code = p.get("parent_program_code")
            if parent_code:
                conn.execute(text("""
                    UPDATE government_programs
                    SET parent_program_id = (SELECT id FROM government_programs WHERE program_code = :pcode)
                    WHERE program_code = :ccode;
                """), {"pcode": parent_code, "ccode": p["program_code"]})
                resolved_parents += 1

        # In PostgreSQL, update the sequence value for government_programs_id_seq if necessary
        if dialect == "postgresql":
            conn.execute(text("""
                SELECT setval(pg_get_serial_sequence('government_programs', 'id'), COALESCE(max(id), 1))
                FROM government_programs;
            """))

    print("\nSeeding transaction committed successfully.")
    print(f"Summary:")
    print(f"  Total Programmes Seeded:    {inserted_count}")
    print(f"  Sector Mappings Seeded:     {sectors_mapped_count}")
    print(f"  Eligibility Records Seeded: {eligibility_count}")
    print(f"  Credit Detail Records:      {credit_count}")
    print(f"  Guarantee Detail Records:   {guarantee_count}")
    print(f"  Subsidy Detail Records:     {subsidy_count}")
    print(f"  Parent Links Resolved:      {resolved_parents}")

if __name__ == "__main__":
    seed()
