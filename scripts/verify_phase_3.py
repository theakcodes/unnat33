"""
scripts/verify_phase_3.py

Comprehensive verification script for Phase 3:
1. Legacy invariants (Schemes 1-12 untouched, exactly 12 legacy links, IDs 1-12, no duplicates)
2. Programme integrity (60 total, unique codes, zero orphan FKs, zero duplicates)
3. Views functionality (v_unified_program_sectors & v_unified_program_eligibility)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def run_verification():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(f"DATABASE_URL not found in {env_path}")
    engine = create_engine(db_url)

    print("=" * 70)
    print("PHASE 3: COMPREHENSIVE SYSTEM VERIFICATION")
    print("=" * 70)

    with engine.connect() as conn:
        # --- 1. LEGACY INVARIANTS ---
        print("\n--- 1. LEGACY INVARIANTS ---")
        schemes_count = conn.execute(text("SELECT COUNT(*) FROM schemes;")).scalar()
        scheme_ids = conn.execute(text("SELECT id FROM schemes ORDER BY id;")).scalars().all()
        print(f"schemes row count: {schemes_count} (Expected: 12)")
        print(f"schemes IDs: {scheme_ids}")
        assert schemes_count == 12, f"schemes count mismatch: {schemes_count}"
        assert scheme_ids == list(range(1, 13)), f"schemes IDs mismatch: {scheme_ids}"

        legacy_links = conn.execute(text(
            "SELECT id, program_code, legacy_scheme_id FROM government_programs WHERE legacy_scheme_id IS NOT NULL ORDER BY legacy_scheme_id;"
        )).fetchall()
        print(f"government_programs legacy links count: {len(legacy_links)} (Expected: 12)")
        linked_ids = [r[2] for r in legacy_links]
        print(f"Linked legacy scheme IDs: {linked_ids}")
        assert len(legacy_links) == 12, f"Legacy link count mismatch: {len(legacy_links)}"
        assert linked_ids == list(range(1, 13)), f"Linked legacy IDs mismatch: {linked_ids}"

        # Confirm scheme_eligibility and scheme_sectors are untouched
        se_count = conn.execute(text("SELECT COUNT(*) FROM scheme_eligibility;")).scalar()
        ss_count = conn.execute(text("SELECT COUNT(*) FROM scheme_sectors;")).scalar()
        sec_count = conn.execute(text("SELECT COUNT(*) FROM sectors;")).scalar()
        print(f"scheme_eligibility count: {se_count} (Expected: 12)")
        print(f"scheme_sectors count:     {ss_count} (Expected: 25)")
        print(f"sectors count:            {sec_count} (Expected: 5)")
        assert se_count == 12, f"scheme_eligibility altered: {se_count}"
        assert ss_count == 25, f"scheme_sectors altered: {ss_count}"
        assert sec_count == 5, f"sectors altered: {sec_count}"

        # --- 2. PROGRAMME INTEGRITY ---
        print("\n--- 2. PROGRAMME INTEGRITY ---")
        total_programs = conn.execute(text("SELECT COUNT(*) FROM government_programs;")).scalar()
        unique_codes = conn.execute(text("SELECT COUNT(DISTINCT program_code) FROM government_programs;")).scalar()
        print(f"Total government_programs:  {total_programs} (Expected: 60)")
        print(f"Unique program codes:       {unique_codes} (Expected: 60)")
        assert total_programs == 60, f"Total programs mismatch: {total_programs}"
        assert unique_codes == 60, f"Non-unique program codes found: {unique_codes}"

        # Child table counts
        ps_count = conn.execute(text("SELECT COUNT(*) FROM program_sectors;")).scalar()
        pe_count = conn.execute(text("SELECT COUNT(*) FROM program_eligibility;")).scalar()
        p_credit_count = conn.execute(text("SELECT COUNT(*) FROM program_credit_details;")).scalar()
        p_guarantee_count = conn.execute(text("SELECT COUNT(*) FROM program_guarantee_details;")).scalar()
        p_subsidy_count = conn.execute(text("SELECT COUNT(*) FROM program_subsidy_details;")).scalar()

        print(f"program_sectors rows:        {ps_count} (Expected: 93)")
        print(f"program_eligibility rows:    {pe_count} (Expected: 48)")
        print(f"program_credit_details rows: {p_credit_count} (Expected: 5)")
        print(f"program_guarantee_details:   {p_guarantee_count} (Expected: 3)")
        print(f"program_subsidy_details:     {p_subsidy_count} (Expected: 8)")

        assert ps_count == 93, f"program_sectors count mismatch: {ps_count}"
        assert pe_count == 48, f"program_eligibility count mismatch: {pe_count}"
        assert p_credit_count == 5, f"program_credit_details count mismatch: {p_credit_count}"
        assert p_guarantee_count == 3, f"program_guarantee_details count mismatch: {p_guarantee_count}"
        assert p_subsidy_count == 8, f"program_subsidy_details count mismatch: {p_subsidy_count}"

        # Orphan checks
        orphan_ps = conn.execute(text("""
            SELECT COUNT(*) FROM program_sectors ps
            LEFT JOIN government_programs gp ON ps.program_id = gp.id
            LEFT JOIN sectors s ON ps.sector_id = s.id
            WHERE gp.id IS NULL OR s.id IS NULL;
        """)).scalar()
        orphan_pe = conn.execute(text("""
            SELECT COUNT(*) FROM program_eligibility pe
            LEFT JOIN government_programs gp ON pe.program_id = gp.id
            WHERE gp.id IS NULL;
        """)).scalar()
        orphan_credit = conn.execute(text("""
            SELECT COUNT(*) FROM program_credit_details c
            LEFT JOIN government_programs gp ON c.program_id = gp.id
            WHERE gp.id IS NULL;
        """)).scalar()
        orphan_guarantee = conn.execute(text("""
            SELECT COUNT(*) FROM program_guarantee_details g
            LEFT JOIN government_programs gp ON g.program_id = gp.id
            WHERE gp.id IS NULL;
        """)).scalar()
        orphan_subsidy = conn.execute(text("""
            SELECT COUNT(*) FROM program_subsidy_details s
            LEFT JOIN government_programs gp ON s.program_id = gp.id
            WHERE gp.id IS NULL;
        """)).scalar()

        print(f"Orphan checks:")
        print(f"  program_sectors orphans:        {orphan_ps} (Expected: 0)")
        print(f"  program_eligibility orphans:    {orphan_pe} (Expected: 0)")
        print(f"  credit details orphans:         {orphan_credit} (Expected: 0)")
        print(f"  guarantee details orphans:      {orphan_guarantee} (Expected: 0)")
        print(f"  subsidy details orphans:        {orphan_subsidy} (Expected: 0)")

        assert orphan_ps == 0 and orphan_pe == 0 and orphan_credit == 0 and orphan_guarantee == 0 and orphan_subsidy == 0, "Orphan foreign keys found!"

        # Duplicate check on program_sectors
        dup_ps = conn.execute(text("""
            SELECT program_id, sector_id, COUNT(*)
            FROM program_sectors
            GROUP BY program_id, sector_id
            HAVING COUNT(*) > 1;
        """)).fetchall()
        print(f"Duplicate (program_id, sector_id) mappings: {len(dup_ps)} (Expected: 0)")
        assert len(dup_ps) == 0, f"Duplicate sector mappings found: {dup_ps}"

        # --- 3. VIEWS VERIFICATION ---
        print("\n--- 3. VIEWS VERIFICATION ---")
        
        # A. v_unified_program_sectors
        unified_sec_rows = conn.execute(text("SELECT COUNT(*) FROM v_unified_program_sectors;")).scalar()
        distinct_sec_progs = conn.execute(text("SELECT COUNT(DISTINCT program_id) FROM v_unified_program_sectors;")).scalar()
        print(f"v_unified_program_sectors total rows: {unified_sec_rows} (Expected: 25 legacy + 93 new = 118)")
        print(f"v_unified_program_sectors distinct programmes: {distinct_sec_progs} (Expected: 9 legacy + 47 new = 56)")
        assert unified_sec_rows == 118, f"v_unified_program_sectors count mismatch: {unified_sec_rows}"
        assert distinct_sec_progs == 56, f"Distinct programmes in sector view mismatch: {distinct_sec_progs}"

        # Sample check legacy scheme in view
        pmegp_sec = conn.execute(text(
            "SELECT sector_code, sector_name FROM v_unified_program_sectors WHERE program_code = 'PMEGP_NEW' ORDER BY sector_code;"
        )).fetchall()
        print(f"Sample legacy view check (PMEGP_NEW sectors): {pmegp_sec}")
        assert [r[0] for r in pmegp_sec] == ["MFG", "SRV"], f"PMEGP sectors mismatch: {pmegp_sec}"

        # Sample check new programme in view
        standup_sec = conn.execute(text(
            "SELECT sector_code, sector_name FROM v_unified_program_sectors WHERE program_code = 'STANDUP_INDIA' ORDER BY sector_code;"
        )).fetchall()
        print(f"Sample new programme view check (STANDUP_INDIA sectors): {standup_sec}")
        assert [r[0] for r in standup_sec] == ["AGR", "MFG", "SRV", "TRD"], f"Stand-Up India sectors mismatch: {standup_sec}"

        # Sample check artisan traditional programme in view
        sfurti_sec = conn.execute(text(
            "SELECT sector_code, sector_name FROM v_unified_program_sectors WHERE program_code = 'SFURTI_CLUSTERS' ORDER BY sector_code;"
        )).fetchall()
        print(f"Sample traditional artisan view check (SFURTI_CLUSTERS sectors): {sfurti_sec}")
        assert [r[0] for r in sfurti_sec] == ["ART", "MFG"], f"SFURTI sectors mismatch: {sfurti_sec}"

        # B. v_unified_program_eligibility
        unified_elig_rows = conn.execute(text("SELECT COUNT(*) FROM v_unified_program_eligibility;")).scalar()
        distinct_elig_progs = conn.execute(text("SELECT COUNT(DISTINCT program_id) FROM v_unified_program_eligibility;")).scalar()
        print(f"v_unified_program_eligibility total rows: {unified_elig_rows} (Expected: 12 legacy + 48 new = 60)")
        print(f"v_unified_program_eligibility distinct programmes: {distinct_elig_progs} (Expected: 60)")
        assert unified_elig_rows == 60, f"v_unified_program_eligibility count mismatch: {unified_elig_rows}"
        assert distinct_elig_progs == 60, f"Distinct programmes in eligibility view mismatch: {distinct_elig_progs}"

        # Sample check legacy scheme eligibility in view
        nsfdc_elig = conn.execute(text(
            "SELECT program_code, sc_eligible, general_eligible, max_annual_income FROM v_unified_program_eligibility WHERE program_code = 'NSFDC_MFS';"
        )).fetchone()
        print(f"Sample legacy view check (NSFDC_MFS eligibility): {dict(nsfdc_elig._mapping)}")
        assert nsfdc_elig[1] is True and nsfdc_elig[2] is False, "NSFDC eligibility criteria mismatch in view!"

        # Sample check new programme eligibility in view
        swarnima_elig = conn.execute(text(
            "SELECT program_code, female_eligible, male_eligible, obc_eligible, general_eligible, max_annual_income FROM v_unified_program_eligibility WHERE program_code = 'NBCFDC_NEW_SWARNIMA';"
        )).fetchone()
        print(f"Sample new programme view check (NBCFDC_NEW_SWARNIMA eligibility): {dict(swarnima_elig._mapping)}")
        assert swarnima_elig[1] is True and swarnima_elig[2] is False and swarnima_elig[3] is True and swarnima_elig[4] is False, "NBCFDC eligibility criteria mismatch in view!"

        print("\nALL VERIFICATION INVARIANTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_verification()
