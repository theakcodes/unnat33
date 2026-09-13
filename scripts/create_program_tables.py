"""
create_program_tables.py

Non-destructive DDL migration to create:
1. government_programs
2. program_sectors
3. program_eligibility
4. program_credit_details
5. program_guarantee_details
6. program_subsidy_details
7. v_unified_program_sectors
8. v_unified_program_eligibility

Guarantees:
- Zero modifications to existing tables (schemes, sectors, scheme_sectors, scheme_eligibility).
- Idempotent (uses IF NOT EXISTS / CREATE OR REPLACE).
- Fully transactional.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def run_ddl():
    from app.db.database import engine

    ddl_statements = [
        # 1. Master government_programs table
        """
        CREATE TABLE IF NOT EXISTS government_programs (
            id SERIAL PRIMARY KEY,
            program_code VARCHAR(50) UNIQUE NOT NULL,
            program_name VARCHAR(255) NOT NULL,
            owning_ministry VARCHAR(255) NOT NULL,
            nodal_agency VARCHAR(255),
            official_portal_url TEXT NOT NULL,
            primary_type VARCHAR(50) NOT NULL,
            secondary_types VARCHAR(50)[],
            actionability_type VARCHAR(50) NOT NULL,
            hierarchy_level VARCHAR(50) NOT NULL,
            parent_program_id INT REFERENCES government_programs(id) ON DELETE SET NULL,
            description TEXT,
            benefit_summary TEXT NOT NULL,
            benefit_type VARCHAR(50) NOT NULL,
            benefit_headline_numeric NUMERIC(14,2),
            benefit_headline_percentage NUMERIC(5,2),
            target_beneficiary_summary TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'active',
            legacy_scheme_id INT UNIQUE REFERENCES schemes(id) ON DELETE RESTRICT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_gov_prog_primary_type ON government_programs(primary_type);",
        "CREATE INDEX IF NOT EXISTS idx_gov_prog_actionability ON government_programs(actionability_type);",
        "CREATE INDEX IF NOT EXISTS idx_gov_prog_status ON government_programs(status);",
        "CREATE INDEX IF NOT EXISTS idx_gov_prog_legacy_id ON government_programs(legacy_scheme_id);",

        # 2. program_sectors table
        """
        CREATE TABLE IF NOT EXISTS program_sectors (
            program_id INT NOT NULL REFERENCES government_programs(id) ON DELETE CASCADE,
            sector_id INT NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (program_id, sector_id)
        );
        """,

        # 3. program_eligibility table (Exact live column mirror of scheme_eligibility)
        """
        CREATE TABLE IF NOT EXISTS program_eligibility (
            id SERIAL PRIMARY KEY,
            program_id INT UNIQUE NOT NULL REFERENCES government_programs(id) ON DELETE CASCADE,
            rural_eligible BOOLEAN,
            urban_eligible BOOLEAN,
            male_eligible BOOLEAN,
            female_eligible BOOLEAN,
            other_gender_eligible BOOLEAN,
            general_eligible BOOLEAN,
            sc_eligible BOOLEAN,
            st_eligible BOOLEAN,
            obc_eligible BOOLEAN,
            minority_eligible BOOLEAN,
            pwd_eligible BOOLEAN,
            ex_servicemen_eligible BOOLEAN,
            min_age INT,
            max_age INT,
            max_annual_income NUMERIC(14,2),
            target_gender VARCHAR(50),
            target_social_categories VARCHAR(100),
            artisan_mandate BOOLEAN DEFAULT FALSE,
            street_vendor_mandate BOOLEAN DEFAULT FALSE,
            startup_mandate BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 4. program_credit_details table
        """
        CREATE TABLE IF NOT EXISTS program_credit_details (
            id SERIAL PRIMARY KEY,
            program_id INT UNIQUE NOT NULL REFERENCES government_programs(id) ON DELETE CASCADE,
            min_loan_amount NUMERIC(14,2),
            max_loan_amount NUMERIC(14,2),
            interest_rate_min NUMERIC(5,2),
            interest_rate_max NUMERIC(5,2),
            tenure_years NUMERIC(5,2),
            moratorium_months INT,
            collateral_required BOOLEAN DEFAULT FALSE,
            promoter_contribution_pct NUMERIC(5,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 5. program_guarantee_details table
        """
        CREATE TABLE IF NOT EXISTS program_guarantee_details (
            id SERIAL PRIMARY KEY,
            program_id INT UNIQUE NOT NULL REFERENCES government_programs(id) ON DELETE CASCADE,
            max_credit_limit NUMERIC(14,2) NOT NULL,
            guarantee_coverage_pct NUMERIC(5,2) NOT NULL,
            annual_guarantee_fee_pct NUMERIC(5,2),
            hybrid_security_allowed BOOLEAN DEFAULT FALSE,
            eligible_lending_institutions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 6. program_subsidy_details table
        """
        CREATE TABLE IF NOT EXISTS program_subsidy_details (
            id SERIAL PRIMARY KEY,
            program_id INT UNIQUE NOT NULL REFERENCES government_programs(id) ON DELETE CASCADE,
            subsidy_pct NUMERIC(5,2),
            max_subsidy_amount NUMERIC(14,2),
            min_project_cost NUMERIC(14,2),
            max_project_cost NUMERIC(14,2),
            beneficiary_contribution_pct NUMERIC(5,2),
            disbursement_type VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 7. Unified sector view
        """
        CREATE OR REPLACE VIEW v_unified_program_sectors AS
        SELECT 
            gp.id AS program_id,
            gp.program_code,
            ss.sector_id,
            s.sector_code,
            s.sector_name
        FROM government_programs gp
        JOIN scheme_sectors ss ON gp.legacy_scheme_id = ss.scheme_id
        JOIN sectors s ON ss.sector_id = s.id
        WHERE gp.legacy_scheme_id IS NOT NULL

        UNION ALL

        SELECT 
            gp.id AS program_id,
            gp.program_code,
            ps.sector_id,
            s.sector_code,
            s.sector_name
        FROM government_programs gp
        JOIN program_sectors ps ON gp.id = ps.program_id
        JOIN sectors s ON ps.sector_id = s.id
        WHERE gp.legacy_scheme_id IS NULL;
        """,

        # 8. Unified eligibility view
        """
        CREATE OR REPLACE VIEW v_unified_program_eligibility AS
        SELECT 
            gp.id AS program_id,
            gp.program_code,
            se.rural_eligible,
            se.urban_eligible,
            se.male_eligible,
            se.female_eligible,
            se.other_gender_eligible,
            se.general_eligible,
            se.sc_eligible,
            se.st_eligible,
            se.obc_eligible,
            se.minority_eligible,
            se.pwd_eligible,
            se.ex_servicemen_eligible,
            se.min_age,
            se.max_age,
            se.max_annual_income,
            se.notes
        FROM government_programs gp
        JOIN scheme_eligibility se ON gp.legacy_scheme_id = se.scheme_id
        WHERE gp.legacy_scheme_id IS NOT NULL

        UNION ALL

        SELECT 
            gp.id AS program_id,
            gp.program_code,
            pe.rural_eligible,
            pe.urban_eligible,
            pe.male_eligible,
            pe.female_eligible,
            pe.other_gender_eligible,
            pe.general_eligible,
            pe.sc_eligible,
            pe.st_eligible,
            pe.obc_eligible,
            pe.minority_eligible,
            pe.pwd_eligible,
            pe.ex_servicemen_eligible,
            pe.min_age,
            pe.max_age,
            pe.max_annual_income,
            pe.notes
        FROM government_programs gp
        JOIN program_eligibility pe ON gp.id = pe.program_id
        WHERE gp.legacy_scheme_id IS NULL;
        """
    ]

    print("Executing Phase 1 DDL non-destructively in a single transaction...")
    with engine.begin() as conn:
        for stmt in ddl_statements:
            conn.execute(text(stmt))

    print("Phase 1 DDL executed successfully.")

if __name__ == "__main__":
    run_ddl()
