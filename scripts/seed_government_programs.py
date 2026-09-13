"""
scripts/seed_government_programs.py

Transactional, idempotent seeding script for Government Programmes.
Seeds:
1. 12 legacy programmes linked 1:1 to schemes.id (IDs 1-12)
2. 48 newly researched programmes (IDs 13-60)

Guarantees:
- Transactional: entire seed runs in a single transaction; rolls back on any error.
- Idempotent: uses ON CONFLICT (program_code) DO UPDATE for government_programs and child tables.
- Zero modifications to schemes, scheme_sectors, scheme_eligibility, or sectors.
- Strict Option A eligibility semantics (NULL = open, TRUE/FALSE = statutory constraint).
- Authoritative financial data in specialized detail tables; display-only summaries in parent.
- Strictly verified official Government of India sources.
"""

import os
import json
import sys
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

def get_engine():
    import app.models
    from app.db.database import engine, Base
    Base.metadata.create_all(bind=engine)
    return engine

def seed():
    engine = get_engine()

    # -------------------------------------------------------------
    # 1. PROGRAMME DATA DEFINITIONS (60 Total: 12 Legacy + 48 New)
    # -------------------------------------------------------------
    
    # 12 Legacy Programmes (linked 1:1 to schemes 1-12)
    legacy_programs = [
        {
            "program_code": "PM_MUDRA_SHISHU",
            "program_name": "PM MUDRA - Shishu",
            "owning_ministry": "Ministry of Finance",
            "nodal_agency": "Department of Financial Services / MUDRA",
            "official_portal_url": "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Micro-credit for small income-generating businesses requiring loans up to Rs. 50,000.",
            "benefit_summary": "Collateral-free institutional credit up to Rs. 50,000.",
            "benefit_type": "TERM_LOAN",
            "benefit_headline_numeric": Decimal("50000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Micro entrepreneurs",
            "status": "active",
            "legacy_scheme_id": 1,
        },
        {
            "program_code": "PM_MUDRA_KISHORE",
            "program_name": "PM MUDRA - Kishore",
            "owning_ministry": "Ministry of Finance",
            "nodal_agency": "Department of Financial Services / MUDRA",
            "official_portal_url": "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Credit support for micro enterprises requiring more than Rs. 50,000 and up to Rs. 5 lakh.",
            "benefit_summary": "Collateral-free institutional credit above Rs. 50,000 and up to Rs. 5 lakh.",
            "benefit_type": "TERM_LOAN",
            "benefit_headline_numeric": Decimal("500000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Micro entrepreneurs",
            "status": "active",
            "legacy_scheme_id": 2,
        },
        {
            "program_code": "PM_MUDRA_TARUN",
            "program_name": "PM MUDRA - Tarun",
            "owning_ministry": "Ministry of Finance",
            "nodal_agency": "Department of Financial Services / MUDRA",
            "official_portal_url": "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Credit support for micro enterprises requiring more than Rs. 5 lakh and up to Rs. 10 lakh.",
            "benefit_summary": "Collateral-free institutional credit above Rs. 5 lakh and up to Rs. 10 lakh.",
            "benefit_type": "TERM_LOAN",
            "benefit_headline_numeric": Decimal("1000000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Micro entrepreneurs",
            "status": "active",
            "legacy_scheme_id": 3,
        },
        {
            "program_code": "PM_MUDRA_TARUN_PLUS",
            "program_name": "PM MUDRA - Tarun Plus",
            "owning_ministry": "Ministry of Finance",
            "nodal_agency": "Department of Financial Services / MUDRA",
            "official_portal_url": "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Credit support above Rs. 10 lakh and up to Rs. 20 lakh for entrepreneurs who have successfully repaid a previous Tarun loan.",
            "benefit_summary": "Collateral-free credit above Rs. 10 lakh and up to Rs. 20 lakh.",
            "benefit_type": "TERM_LOAN",
            "benefit_headline_numeric": Decimal("2000000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Existing micro entrepreneurs with repaid Tarun loan",
            "status": "active",
            "legacy_scheme_id": 4,
        },
        {
            "program_code": "PMEGP_NEW",
            "program_name": "Prime Minister Employment Generation Programme (PMEGP)",
            "owning_ministry": "Ministry of MSME",
            "nodal_agency": "Khadi and Village Industries Commission (KVIC)",
            "official_portal_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
            "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
            "secondary_types": ["CREDIT / LOAN"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Credit-linked subsidy programme for setting up new micro enterprises in non-farm sectors.",
            "benefit_summary": "Credit-linked subsidy of 15% to 35% on project cost up to Rs. 50 lakh for manufacturing and Rs. 20 lakh for services.",
            "benefit_type": "CAPITAL_SUBSIDY",
            "benefit_headline_numeric": Decimal("5000000.00"),
            "benefit_headline_percentage": Decimal("35.00"),
            "target_beneficiary_summary": "New individual entrepreneurs, SHGs, institutions",
            "status": "active",
            "legacy_scheme_id": 5,
        },
        {
            "program_code": "PMEGP_UPGRADATION",
            "program_name": "PMEGP 2nd Loan for Upgradation",
            "owning_ministry": "Ministry of MSME",
            "nodal_agency": "Khadi and Village Industries Commission (KVIC)",
            "official_portal_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
            "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
            "secondary_types": ["CREDIT / LOAN"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Financial assistance for upgrading existing, well-performing PMEGP/MUDRA units.",
            "benefit_summary": "Subsidy of 15% to 20% on project cost up to Rs. 1 crore for manufacturing and Rs. 25 lakh for services.",
            "benefit_type": "CAPITAL_SUBSIDY",
            "benefit_headline_numeric": Decimal("10000000.00"),
            "benefit_headline_percentage": Decimal("20.00"),
            "target_beneficiary_summary": "Existing performing PMEGP units",
            "status": "active",
            "legacy_scheme_id": 6,
        },
        {
            "program_code": "PM_VISHWAKARMA",
            "program_name": "PM Vishwakarma",
            "owning_ministry": "Ministry of MSME",
            "nodal_agency": "MoMSME / MoSD&E / DFS",
            "official_portal_url": "https://pmvishwakarma.gov.in",
            "primary_type": "TRADITIONAL INDUSTRY / ARTISANS",
            "secondary_types": ["CREDIT / LOAN", "SUBSIDY / CAPITAL ASSISTANCE"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "End-to-end holistic support for traditional artisans and craftspeople across 18 identified trades.",
            "benefit_summary": "Collateral-free enterprise credit up to Rs. 3 lakh (Rs. 1L first tranche + Rs. 2L second tranche) at 5% interest rate, plus Rs. 15,000 toolkit incentive.",
            "benefit_type": "CONCESSIONAL_CREDIT",
            "benefit_headline_numeric": Decimal("300000.00"),
            "benefit_headline_percentage": Decimal("5.00"),
            "target_beneficiary_summary": "Traditional artisans and craftspeople working with hands and tools",
            "status": "active",
            "legacy_scheme_id": 7,
        },
        {
            "program_code": "PM_SVANIDHI",
            "program_name": "PM SVANidhi",
            "owning_ministry": "Ministry of Housing and Urban Affairs",
            "nodal_agency": "MoHUA / SIDBI",
            "official_portal_url": "https://pmsvanidhi.mohua.gov.in",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Micro credit facility for urban street vendors to resume livelihoods.",
            "benefit_summary": "Working capital loan up to Rs. 10,000 (1st tranche), Rs. 20,000 (2nd tranche), and Rs. 50,000 (3rd tranche) with 7% interest subsidy on timely repayment.",
            "benefit_type": "WORKING_CAPITAL_LOAN",
            "benefit_headline_numeric": Decimal("50000.00"),
            "benefit_headline_percentage": Decimal("7.00"),
            "target_beneficiary_summary": "Urban street vendors and hawkers",
            "status": "active",
            "legacy_scheme_id": 8,
        },
        {
            "program_code": "NSFDC_MFS",
            "program_name": "NSFDC Micro Finance Scheme (MFS)",
            "owning_ministry": "Ministry of Social Justice and Empowerment",
            "nodal_agency": "National Scheduled Castes Finance and Development Corporation (NSFDC)",
            "official_portal_url": "https://nsfdc.nic.in",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Micro-finance through State Channelizing Agencies for small income-generating activities.",
            "benefit_summary": "Concessional micro credit up to Rs. 60,000 per beneficiary at 5% p.a. interest rate.",
            "benefit_type": "CONCESSIONAL_LOAN",
            "benefit_headline_numeric": Decimal("60000.00"),
            "benefit_headline_percentage": Decimal("5.00"),
            "target_beneficiary_summary": "Scheduled Caste individuals living below double the poverty line",
            "status": "active",
            "legacy_scheme_id": 9,
        },
        {
            "program_code": "NSFDC_AMY",
            "program_name": "NSFDC Aajeevika Micro-Finance Yojana (AMY)",
            "owning_ministry": "Ministry of Social Justice and Empowerment",
            "nodal_agency": "National Scheduled Castes Finance and Development Corporation (NSFDC)",
            "official_portal_url": "https://nsfdc.nic.in",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Micro-finance routed through NBFC-MFIs for income-generating micro activities.",
            "benefit_summary": "Concessional micro finance up to Rs. 60,000 per beneficiary at interest rates not exceeding NBFC-MFI caps.",
            "benefit_type": "CONCESSIONAL_LOAN",
            "benefit_headline_numeric": Decimal("60000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Scheduled Caste individuals living below double the poverty line",
            "status": "active",
            "legacy_scheme_id": 10,
        },
        {
            "program_code": "NSFDC_TERM_LOAN",
            "program_name": "NSFDC Term Loan Scheme",
            "owning_ministry": "Ministry of Social Justice and Empowerment",
            "nodal_agency": "National Scheduled Castes Finance and Development Corporation (NSFDC)",
            "official_portal_url": "https://nsfdc.nic.in",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Term credit finance for commercially viable income-generating projects.",
            "benefit_summary": "Term loan assistance up to 90% of project cost for projects costing up to Rs. 50 lakh at concessional interest rates.",
            "benefit_type": "TERM_LOAN",
            "benefit_headline_numeric": Decimal("5000000.00"),
            "benefit_headline_percentage": None,
            "target_beneficiary_summary": "Scheduled Caste individuals living below double the poverty line",
            "status": "active",
            "legacy_scheme_id": 11,
        },
        {
            "program_code": "NSFDC_UNY",
            "program_name": "NSFDC Udyam Nidhi Yojana (UNY)",
            "owning_ministry": "Ministry of Social Justice and Empowerment",
            "nodal_agency": "National Scheduled Castes Finance and Development Corporation (NSFDC)",
            "official_portal_url": "https://nsfdc.nic.in",
            "primary_type": "CREDIT / LOAN",
            "secondary_types": ["DIRECT_FINANCING"],
            "actionability_type": "DIRECTLY_RECOMMENDABLE",
            "hierarchy_level": "STANDALONE",
            "parent_program_code": None,
            "description": "Micro loans through cooperative societies and small finance entities for income generation.",
            "benefit_summary": "Micro loan assistance up to Rs. 44,000 per beneficiary at 4% p.a. interest rate.",
            "benefit_type": "CONCESSIONAL_LOAN",
            "benefit_headline_numeric": Decimal("44000.00"),
            "benefit_headline_percentage": Decimal("4.00"),
            "target_beneficiary_summary": "Scheduled Caste individuals living below double the poverty line",
            "status": "active",
            "legacy_scheme_id": 12,
        },
    ]

    # 48 New Programmes (IDs 13-60)
    new_programs = [
        # 1. Stand-Up India
        {
            "program": {
                "program_code": "STANDUP_INDIA",
                "program_name": "Stand-Up India Scheme",
                "owning_ministry": "Ministry of Finance",
                "nodal_agency": "Department of Financial Services / SIDBI",
                "official_portal_url": "https://www.standupmitra.in",
                "primary_type": "CREDIT / LOAN",
                "secondary_types": ["CREDIT GUARANTEE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Facilitates composite bank loans between Rs. 10 Lakh and Rs. 1 Crore to at least one SC/ST and one Woman borrower per bank branch for greenfield enterprises.",
                "benefit_summary": "Bank composite loan between Rs. 10 Lakh and Rs. 1 Crore with tenure up to 7 years and moratorium up to 18 months.",
                "benefit_type": "TERM_LOAN",
                "benefit_headline_numeric": Decimal("10000000.00"),
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "SC, ST, and Women entrepreneurs setting up greenfield ventures",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": None, "sc_eligible": True, "st_eligible": True, "obc_eligible": None,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Greenfield enterprise in manufacturing, services, agri-allied, or trading. In non-individual enterprises, 51% shareholding must be held by SC/ST or woman."
            },
            "credit": {
                "min_loan_amount": Decimal("1000000.00"), "max_loan_amount": Decimal("10000000.00"),
                "interest_rate_min": None, "interest_rate_max": None,
                "tenure_years": Decimal("7.0"), "moratorium_months": 18,
                "collateral_required": False, "promoter_contribution_pct": Decimal("15.00")
            }
        },

        # 2. SIDBI SMILE
        {
            "program": {
                "program_code": "SIDBI_SMILE",
                "program_name": "SIDBI Make in India Soft Loan Fund for MSMEs (SMILE)",
                "owning_ministry": "Ministry of MSME / Ministry of Finance",
                "nodal_agency": "SIDBI",
                "official_portal_url": "https://www.sidbi.in",
                "primary_type": "CREDIT / LOAN",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Provides quasi-equity and soft term loans to meet required debt-equity ratios for setting up new MSMEs and financing expansion/modernization.",
                "benefit_summary": "Soft term loan and quasi-equity assistance up to Rs. 25 Crore directly through SIDBI.",
                "benefit_type": "SOFT_LOAN",
                "benefit_headline_numeric": Decimal("250000000.00"),
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "New and existing MSMEs in 25 Make in India sectors",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Enterprises in 25 Make in India manufacturing and service sectors."
            },
            "credit": {
                "min_loan_amount": Decimal("1000000.00"), "max_loan_amount": Decimal("250000000.00"),
                "interest_rate_min": None, "interest_rate_max": None,
                "tenure_years": Decimal("10.0"), "moratorium_months": 36,
                "collateral_required": False, "promoter_contribution_pct": Decimal("15.00")
            }
        },

        # 3. NBCFDC New Swarnima for Women
        {
            "program": {
                "program_code": "NBCFDC_NEW_SWARNIMA",
                "program_name": "NBCFDC New Swarnima Scheme for Women",
                "owning_ministry": "Ministry of Social Justice & Empowerment",
                "nodal_agency": "NBCFDC",
                "official_portal_url": "https://nbcfdc.gov.in",
                "primary_type": "CREDIT / LOAN",
                "secondary_types": None,
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Term loan assistance at concessional interest rate of 5% p.a. to backward class women entrepreneurs for self-employment.",
                "benefit_summary": "Term loan up to Rs. 2,00,000 at a concessional interest rate of 5% p.a.",
                "benefit_type": "CONCESSIONAL_LOAN",
                "benefit_headline_numeric": Decimal("200000.00"),
                "benefit_headline_percentage": Decimal("5.00"),
                "target_beneficiary_summary": "Women entrepreneurs belonging to Backward Classes",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": False, "female_eligible": True, "other_gender_eligible": False,
                "general_eligible": False, "sc_eligible": False, "st_eligible": False, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": 55, "max_annual_income": Decimal("300000.00"),
                "notes": "Woman belonging to Backward Classes; family annual income ceiling up to Rs. 3 Lakh."
            },
            "credit": {
                "min_loan_amount": None, "max_loan_amount": Decimal("200000.00"),
                "interest_rate_min": Decimal("5.00"), "interest_rate_max": Decimal("5.00"),
                "tenure_years": Decimal("8.0"), "moratorium_months": 6,
                "collateral_required": False, "promoter_contribution_pct": Decimal("0.00")
            }
        },

        # 4. NSTFDC AMSY
        {
            "program": {
                "program_code": "NSTFDC_AMSY",
                "program_name": "NSTFDC Adivasi Mahila Sashaktikaran Yojana (AMSY)",
                "owning_ministry": "Ministry of Tribal Affairs",
                "nodal_agency": "NSTFDC",
                "official_portal_url": "https://nstfdc.tribal.gov.in",
                "primary_type": "CREDIT / LOAN",
                "secondary_types": None,
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Concessional loan assistance exclusively for Scheduled Tribe women entrepreneurs undertaking self-employment ventures.",
                "benefit_summary": "Loan assistance up to Rs. 2,00,000 at a subsidized interest rate of 4% p.a.",
                "benefit_type": "CONCESSIONAL_LOAN",
                "benefit_headline_numeric": Decimal("200000.00"),
                "benefit_headline_percentage": Decimal("4.00"),
                "target_beneficiary_summary": "Scheduled Tribe (ST) women entrepreneurs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": False, "female_eligible": True, "other_gender_eligible": False,
                "general_eligible": False, "sc_eligible": False, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": Decimal("300000.00"),
                "notes": "Scheduled Tribe (ST) woman; family income up to Rs. 3 Lakh."
            },
            "credit": {
                "min_loan_amount": None, "max_loan_amount": Decimal("200000.00"),
                "interest_rate_min": Decimal("4.00"), "interest_rate_max": Decimal("4.00"),
                "tenure_years": Decimal("5.0"), "moratorium_months": None,
                "collateral_required": False, "promoter_contribution_pct": Decimal("0.00")
            }
        },

        # 5. CGTMSE
        {
            "program": {
                "program_code": "CGTMSE",
                "program_name": "Credit Guarantee Scheme for Micro and Small Enterprises (CGTMSE)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "CGTMSE / SIDBI",
                "official_portal_url": "https://www.cgtmse.in",
                "primary_type": "CREDIT GUARANTEE",
                "secondary_types": None,
                "actionability_type": "FRAMEWORK",
                "hierarchy_level": "INSTITUTIONAL_FRAMEWORK",
                "parent_program_code": None,
                "description": "Provides third-party credit guarantee cover to Member Lending Institutions extending collateral-free loans to MSEs.",
                "benefit_summary": "Credit guarantee coverage between 75% and 85% for loans up to Rs. 10 Crore without third-party collateral.",
                "benefit_type": "CREDIT_GUARANTEE",
                "benefit_headline_numeric": Decimal("100000000.00"),
                "benefit_headline_percentage": Decimal("85.00"),
                "target_beneficiary_summary": "New and existing Micro and Small Enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Micro and Small enterprises; agriculture and educational institutions excluded."
            },
            "guarantee": {
                "max_credit_limit": Decimal("100000000.00"),
                "guarantee_coverage_pct": Decimal("85.00"),
                "annual_guarantee_fee_pct": Decimal("0.37"),
                "hybrid_security_allowed": True,
                "eligible_lending_institutions": "Scheduled Commercial Banks, RRBs, NBFCs, Small Finance Banks"
            }
        },

        # 6. CGSSD
        {
            "program": {
                "program_code": "CGSSD",
                "program_name": "Credit Guarantee Scheme for Subordinate Debt (CGSSD)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "CGTMSE / Ministry of MSME",
                "official_portal_url": "https://www.cgtmse.in",
                "primary_type": "CREDIT GUARANTEE",
                "secondary_types": ["CREDIT / LOAN"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Guarantee cover to banks for extending subordinate debt up to 15% of promoter equity or Rs. 75 Lakh to promoters of stressed/NPA MSME units.",
                "benefit_summary": "90% guarantee cover on subordinate debt up to Rs. 75 Lakh for stressed MSME revival.",
                "benefit_type": "CREDIT_GUARANTEE",
                "benefit_headline_numeric": Decimal("7500000.00"),
                "benefit_headline_percentage": Decimal("90.00"),
                "target_beneficiary_summary": "Promoters of stressed and NPA MSME units",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Operational MSME accounts classified as SMA-2 or NPA."
            },
            "guarantee": {
                "max_credit_limit": Decimal("7500000.00"),
                "guarantee_coverage_pct": Decimal("90.00"),
                "annual_guarantee_fee_pct": Decimal("1.50"),
                "hybrid_security_allowed": False,
                "eligible_lending_institutions": "All Member Lending Institutions"
            }
        },

        # 7. CGSS (Startups)
        {
            "program": {
                "program_code": "CGSS",
                "program_name": "Credit Guarantee Scheme for Startups (CGSS)",
                "owning_ministry": "Ministry of Commerce and Industry (DPIIT)",
                "nodal_agency": "NCGTC",
                "official_portal_url": "https://www.ncgtc.org.in",
                "primary_type": "CREDIT GUARANTEE",
                "secondary_types": ["INNOVATION / INCUBATION"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Credit guarantee coverage for loans and venture debt extended by financial institutions to DPIIT-recognized startups.",
                "benefit_summary": "Credit guarantee coverage up to Rs. 10 Crore per borrower for loans and venture debt.",
                "benefit_type": "CREDIT_GUARANTEE",
                "benefit_headline_numeric": Decimal("100000000.00"),
                "benefit_headline_percentage": Decimal("80.00"),
                "target_beneficiary_summary": "DPIIT-recognized innovative startups",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "DPIIT-recognized startup with stable revenue or proof of concept."
            },
            "guarantee": {
                "max_credit_limit": Decimal("100000000.00"),
                "guarantee_coverage_pct": Decimal("80.00"),
                "annual_guarantee_fee_pct": Decimal("2.00"),
                "hybrid_security_allowed": False,
                "eligible_lending_institutions": "Banks, NBFCs, AIFs (Venture Debt Funds)"
            }
        },

        # 8. PMFME
        {
            "program": {
                "program_code": "PMFME",
                "program_name": "Pradhan Mantri Formalisation of Micro food processing Enterprises (PMFME)",
                "owning_ministry": "Ministry of Food Processing Industries (MoFPI)",
                "nodal_agency": "State Nodal Agencies / MoFPI",
                "official_portal_url": "https://pmfme.mofpi.gov.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["CREDIT / LOAN"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Credit-linked capital subsidy for establishing or upgrading individual micro food processing enterprises under ODOP.",
                "benefit_summary": "35% credit-linked capital subsidy up to Rs. 10 Lakh per unit, with 10% minimum beneficiary contribution.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("1000000.00"),
                "benefit_headline_percentage": Decimal("35.00"),
                "target_beneficiary_summary": "Micro food processing entrepreneurs and SHGs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Existing or new micro food processing enterprise; proprietary or partnership."
            },
            "subsidy": {
                "subsidy_pct": Decimal("35.00"),
                "max_subsidy_amount": Decimal("1000000.00"),
                "min_project_cost": None, "max_project_cost": Decimal("10000000.00"),
                "beneficiary_contribution_pct": Decimal("10.00"),
                "disbursement_type": "Credit-Linked Back-Ended Subsidy"
            }
        },

        # 9. PMKSY - CEFPPC
        {
            "program": {
                "program_code": "PMKSY_CEFPPC",
                "program_name": "PMKSY - Creation / Expansion of Food Processing & Preservation Capacities (CEFPPC)",
                "owning_ministry": "Ministry of Food Processing Industries (MoFPI)",
                "nodal_agency": "MoFPI",
                "official_portal_url": "https://www.mofpi.gov.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["CLUSTER / INFRASTRUCTURE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Capital grant-in-aid for creating modern processing and preservation capacities and modernization of existing food processing units.",
                "benefit_summary": "Capital grant-in-aid of 35% in General areas (up to Rs. 5 Crore) and 50% in NER/Hilly areas.",
                "benefit_type": "CAPITAL_GRANT",
                "benefit_headline_numeric": Decimal("50000000.00"),
                "benefit_headline_percentage": Decimal("35.00"),
                "target_beneficiary_summary": "Food processing enterprises investing in modern processing plants",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Bank term loan required; minimum promoter net worth requirements per EOI guidelines."
            },
            "subsidy": {
                "subsidy_pct": Decimal("35.00"),
                "max_subsidy_amount": Decimal("50000000.00"),
                "min_project_cost": None, "max_project_cost": None,
                "beneficiary_contribution_pct": Decimal("20.00"),
                "disbursement_type": "Milestone-Based Grant-in-Aid"
            }
        },

        # 10. Agriculture Infrastructure Fund (AIF)
        {
            "program": {
                "program_code": "AIF",
                "program_name": "Agriculture Infrastructure Fund (AIF)",
                "owning_ministry": "Ministry of Agriculture & Farmers Welfare",
                "nodal_agency": "Department of Agriculture & Farmers Welfare",
                "official_portal_url": "https://agriinfra.dac.gov.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["CREDIT GUARANTEE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Medium-to-long term debt financing facility for post-harvest management infrastructure and community farming assets through interest subvention.",
                "benefit_summary": "3% per annum interest subvention on loans up to Rs. 2 Crore for up to 7 years, alongside CGTMSE guarantee fee coverage.",
                "benefit_type": "INTEREST_SUBVENTION",
                "benefit_headline_numeric": Decimal("20000000.00"),
                "benefit_headline_percentage": Decimal("3.00"),
                "target_beneficiary_summary": "Agri-entrepreneurs, startups, FPOs, PACS, and MSMEs creating post-harvest agri-assets",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Subvention available for up to 7 years on term loans up to Rs. 2 Crore."
            },
            "subsidy": {
                "subsidy_pct": Decimal("3.00"),
                "max_subsidy_amount": None,
                "min_project_cost": None, "max_project_cost": Decimal("20000000.00"),
                "beneficiary_contribution_pct": Decimal("10.00"),
                "disbursement_type": "Interest Subvention on Bank Loan"
            }
        },

        # 11. SCLCSS for SC/ST MSMEs
        {
            "program": {
                "program_code": "SCLCSS_SC_ST",
                "program_name": "Special Credit Linked Capital Subsidy Scheme (SCLCSS) for SC/ST MSMEs",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National SC-ST Hub / SIDBI",
                "official_portal_url": "https://www.scsthub.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["TECHNOLOGY / QUALITY"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "25% upfront capital subsidy on institutional finance availed by SC/ST MSMEs for purchasing modern plant and machinery.",
                "benefit_summary": "25% upfront capital subsidy (up to Rs. 25 Lakh on term loans up to Rs. 1 Crore) for acquiring modern plant and equipment.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("2500000.00"),
                "benefit_headline_percentage": Decimal("25.00"),
                "target_beneficiary_summary": "SC/ST-owned manufacturing and eligible service MSEs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": False, "sc_eligible": True, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Must be 100% owned by SC/ST entrepreneurs (or at least 51% in corporate entities)."
            },
            "subsidy": {
                "subsidy_pct": Decimal("25.00"),
                "max_subsidy_amount": Decimal("2500000.00"),
                "min_project_cost": None, "max_project_cost": Decimal("10000000.00"),
                "beneficiary_contribution_pct": None,
                "disbursement_type": "Upfront Capital Subsidy via Bank"
            }
        },

        # 12. AMI Storage
        {
            "program": {
                "program_code": "AMI_STORAGE",
                "program_name": "Agricultural Marketing Infrastructure (AMI) / Sub-scheme of ISAM",
                "owning_ministry": "Ministry of Agriculture & Farmers Welfare",
                "nodal_agency": "Directorate of Marketing & Inspection (DMI) / NABARD",
                "official_portal_url": "https://dmi.gov.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["CLUSTER / INFRASTRUCTURE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Back-ended capital subsidy scheme for creation of scientific storage infrastructure, cold storage, and rural godowns.",
                "benefit_summary": "25% capital subsidy (33.33% for women/SC/ST/NER) up to Rs. 50 Lakh to Rs. 87.5 Lakh on bank credit for storage infrastructure.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("8750000.00"),
                "benefit_headline_percentage": Decimal("33.33"),
                "target_beneficiary_summary": "Entrepreneurs, MSMEs, farmers, and cooperatives establishing storage infrastructure",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": False,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Infrastructure must be located in rural areas; institutional bank credit linked via NABARD."
            },
            "subsidy": {
                "subsidy_pct": Decimal("33.33"),
                "max_subsidy_amount": Decimal("8750000.00"),
                "min_project_cost": None, "max_project_cost": None,
                "beneficiary_contribution_pct": Decimal("20.00"),
                "disbursement_type": "Credit-Linked Back-Ended Subsidy via NABARD"
            }
        },

        # 13. SMAM CHC
        {
            "program": {
                "program_code": "SMAM_CHC",
                "program_name": "Sub-Mission on Agricultural Mechanization (SMAM) - Custom Hiring Centres (CHC)",
                "owning_ministry": "Ministry of Agriculture & Farmers Welfare",
                "nodal_agency": "Mechanization & Technology Division / State Agriculture Departments",
                "official_portal_url": "https://agrimachinery.nic.in",
                "primary_type": "SUBSIDY / CAPITAL ASSISTANCE",
                "secondary_types": ["OTHER MSME SUPPORT"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Provides 40% capital subsidy to rural youth and entrepreneurs to establish Custom Hiring Centres renting farm machinery.",
                "benefit_summary": "40% financial assistance (up to Rs. 10 Lakh on a Rs. 25 Lakh project) for agricultural machinery rental centres.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("1000000.00"),
                "benefit_headline_percentage": Decimal("40.00"),
                "target_beneficiary_summary": "Rural entrepreneurs and farmer groups establishing farm machinery rental businesses",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["SRV", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Applied online on agrimachinery.nic.in; equipment chosen from empaneled manufacturers."
            },
            "subsidy": {
                "subsidy_pct": Decimal("40.00"),
                "max_subsidy_amount": Decimal("1000000.00"),
                "min_project_cost": None, "max_project_cost": Decimal("2500000.00"),
                "beneficiary_contribution_pct": None,
                "disbursement_type": "Direct Capital Subsidy"
            }
        },

        # 14. PMS Trade Fairs
        {
            "program": {
                "program_code": "PMS_TRADE_FAIRS",
                "program_name": "Procurement and Marketing Support (PMS) Scheme - Trade Fair Participation",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Office of Development Commissioner (MSME)",
                "official_portal_url": "https://pms.dcmsme.gov.in",
                "primary_type": "MARKET ACCESS",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Subsidizes space rent for MSEs participating in national trade fairs, exhibitions, and expos to market manufactured goods.",
                "benefit_summary": "80% to 100% space rent subsidy (up to Rs. 1.5 Lakh for general micro enterprises and Rs. 3 Lakh for special categories).",
                "benefit_type": "SPACE_RENT_SUBSIDY",
                "benefit_headline_numeric": Decimal("300000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Udyam-registered Micro and Small Enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Valid Udyam Registration required; applied online on pms.dcmsme.gov.in before fair commencement."
            }
        },

        # 15. PMS VDP
        {
            "program": {
                "program_code": "PMS_VDP",
                "program_name": "PMS - Vendor Development Programmes (VDP) & Buyer-Seller Meets",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Office of Development Commissioner (MSME)",
                "official_portal_url": "https://pms.dcmsme.gov.in",
                "primary_type": "MARKET ACCESS",
                "secondary_types": None,
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "B2G buyer-seller meets connecting MSE suppliers directly to CPSEs, defense, and railways.",
                "benefit_summary": "Free/subsidized matchmaking platforms and vendor qualification with public sector buyers.",
                "benefit_type": "B2G_BUYER_MATCHMAKING",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Manufacturing and service MSEs supplying components to CPSEs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Udyam-registered MSEs; registration via PMS portal for VDP events."
            }
        },

        # 16. MSME Sambandh
        {
            "program": {
                "program_code": "MSME_SAMBANDH",
                "program_name": "MSME Sambandh (Public Procurement Monitoring Platform)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Ministry of MSME",
                "official_portal_url": "https://sambandh.msme.gov.in",
                "primary_type": "MARKET ACCESS",
                "secondary_types": ["OTHER MSME SUPPORT"],
                "actionability_type": "PLATFORM",
                "hierarchy_level": "PORTAL_PLATFORM",
                "parent_program_code": None,
                "description": "Statutory monitoring portal tracking CPSE compliance with the mandatory 25% annual MSE public procurement mandate.",
                "benefit_summary": "Tender intelligence, advance annual procurement forecasts, and tracking of CPSE procurement quotas for MSEs.",
                "benefit_type": "PROCUREMENT_INTELLIGENCE",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("25.00"),
                "target_beneficiary_summary": "MSE suppliers seeking institutional government and public sector contracts",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Open portal for public procurement data; MSEs register with Udyam."
            }
        },

        # 17. GeM MSME
        {
            "program": {
                "program_code": "GEM_MSME",
                "program_name": "Government e-Marketplace (GeM) - MSME Concessions & Fast-Track",
                "owning_ministry": "Ministry of Commerce and Industry",
                "nodal_agency": "GeM SPV",
                "official_portal_url": "https://gem.gov.in",
                "primary_type": "MARKET ACCESS",
                "secondary_types": ["OTHER MSME SUPPORT"],
                "actionability_type": "PLATFORM",
                "hierarchy_level": "PORTAL_PLATFORM",
                "parent_program_code": None,
                "description": "National public procurement portal providing statutory concessions to MSEs including EMD waiver and turnover exemptions.",
                "benefit_summary": "100% EMD waiver, prior turnover/experience exemptions, and access to all central/state government procurement tenders.",
                "benefit_type": "PUBLIC_PROCUREMENT_CONCESSION",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "All Udyam-registered Micro and Small Enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Requires PAN, Udyam Registration, and active bank account."
            }
        },

        # 18. NSSH SMAS
        {
            "program": {
                "program_code": "NSSH_SMAS",
                "program_name": "NSSH - Special Marketing Assistance Scheme (SMAS)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National SC-ST Hub (NSIC)",
                "official_portal_url": "https://www.scsthub.in",
                "primary_type": "MARKET ACCESS",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Reimbursement scheme covering marketing, stall rent, airfare, and freight for SC/ST MSEs participating in exhibitions.",
                "benefit_summary": "100% financial reimbursement of stall charges, economy airfare, and freight charges for SC/ST entrepreneurs.",
                "benefit_type": "MARKETING_REIMBURSEMENT",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "SC/ST-owned Micro and Small Enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": False, "sc_eligible": True, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "SC/ST proprietary or 51%+ partnership MSE with valid Udyam; claim filed on scsthub.in."
            }
        },

        # 19. MSME Sustainable (ZED)
        {
            "program": {
                "program_code": "MSME_ZED",
                "program_name": "MSME Sustainable (ZED) Certification Scheme",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Quality Council of India (QCI) / DC-MSME",
                "official_portal_url": "https://zed.msme.gov.in",
                "primary_type": "TECHNOLOGY / QUALITY",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Subsidizes certification costs across Bronze, Silver, and Gold tiers to promote Zero Defect Zero Effect manufacturing.",
                "benefit_summary": "Subsidy on certification cost: 80% for Micro, 60% for Small, 50% for Medium (+10% for Women/SC/ST/NER).",
                "benefit_type": "CERTIFICATION_SUBSIDY",
                "benefit_headline_numeric": Decimal("50000.00"),
                "benefit_headline_percentage": Decimal("80.00"),
                "target_beneficiary_summary": "Manufacturing MSMEs registered under Udyam",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Exclusively for manufacturing MSMEs with valid Udyam; applied on zed.msme.gov.in."
            }
        },

        # 20. MSME Competitive (LEAN)
        {
            "program": {
                "program_code": "MSME_LEAN",
                "program_name": "MSME Competitive (LEAN) Scheme",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Quality Council of India (QCI) / DC-MSME",
                "official_portal_url": "https://lean.msme.gov.in",
                "primary_type": "TECHNOLOGY / QUALITY",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Provides 90% government funding toward consultant fees to eliminate shopfloor waste and improve manufacturing productivity.",
                "benefit_summary": "90% government funding for consultant fees across Basic, Intermediate, and Advanced Lean interventions.",
                "benefit_type": "CONSULTANCY_SUBSIDY",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("90.00"),
                "target_beneficiary_summary": "Manufacturing MSMEs registered under Udyam",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Manufacturing MSMEs apply individually or in mini-clusters of 4-10 units on lean.msme.gov.in."
            }
        },

        # 21. MSME Digital Scheme
        {
            "program": {
                "program_code": "MSME_DIGITAL",
                "program_name": "MSME Digital Scheme (Digital MSME)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "O/o DC-MSME",
                "official_portal_url": "https://champions.gov.in",
                "primary_type": "TECHNOLOGY / QUALITY",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Financial subsidy for MSMEs to adopt cloud computing, ERP, digital accounting, and IoT solutions.",
                "benefit_summary": "Subsidized cloud services up to Rs. 1 Lakh to Rs. 5 Lakh per enterprise for transitioning to digital workflows.",
                "benefit_type": "CLOUD_ADOPTION_SUBSIDY",
                "benefit_headline_numeric": Decimal("500000.00"),
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Micro, Small, and Medium enterprises digitizing operations",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Udyam-registered enterprise; applied through MyMSME cloud portal."
            }
        },

        # 22. PTUAS Pharma
        {
            "program": {
                "program_code": "PTUAS_PHARMA",
                "program_name": "Pharmaceutical Technology Upgradation Assistance Scheme (PTUAS)",
                "owning_ministry": "Ministry of Chemicals and Fertilizers (Department of Pharmaceuticals)",
                "nodal_agency": "SIDBI / DoP",
                "official_portal_url": "https://pharmaceuticals.gov.in",
                "primary_type": "TECHNOLOGY / QUALITY",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Subsidizes MSME pharma manufacturers to upgrade manufacturing infrastructure to revised Schedule M and WHO-GMP quality standards.",
                "benefit_summary": "Interest subvention of 6% p.a. or capital subsidy of 20% on eligible investment up to Rs. 1 Crore.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("10000000.00"),
                "benefit_headline_percentage": Decimal("20.00"),
                "target_beneficiary_summary": "Micro, Small, and Medium pharmaceutical manufacturing units",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Existing pharma MSME with drug manufacturing license."
            },
            "subsidy": {
                "subsidy_pct": Decimal("20.00"),
                "max_subsidy_amount": Decimal("10000000.00"),
                "min_project_cost": None, "max_project_cost": None,
                "beneficiary_contribution_pct": None,
                "disbursement_type": "Capital Subsidy or Interest Subvention"
            }
        },

        # 23. NSSH Testing Reimbursement
        {
            "program": {
                "program_code": "NSSH_TESTING_REIMB",
                "program_name": "NSSH - Testing & Quality Certification Fee Reimbursement",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National SC-ST Hub",
                "official_portal_url": "https://www.scsthub.in",
                "primary_type": "TECHNOLOGY / QUALITY",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Financial reimbursement for testing products at NABL/BIS accredited laboratories and obtaining national/international certifications.",
                "benefit_summary": "100% reimbursement of testing fees at NABL labs; 80% to 100% reimbursement of BIS/ISO/FSSAI fees up to Rs. 1 Lakh per certification.",
                "benefit_type": "FEE_REIMBURSEMENT",
                "benefit_headline_numeric": Decimal("100000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "SC/ST-owned MSEs acquiring statutory product standards",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": False, "sc_eligible": True, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Testing at NABL-accredited or government laboratories."
            }
        },

        # 24. MSME Innovative Incubation
        {
            "program": {
                "program_code": "MSME_INNOVATIVE_INCUB",
                "program_name": "MSME Innovative Scheme - Incubation Component",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "O/o DC-MSME",
                "official_portal_url": "https://innovative.msme.gov.in",
                "primary_type": "INNOVATION / INCUBATION",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Financial assistance for developing validated prototypes from innovative ideas through approved Host Institutes.",
                "benefit_summary": "Financial grant assistance up to Rs. 15 Lakh per approved idea for developing commercial prototypes.",
                "benefit_type": "PROTOTYPE_GRANT",
                "benefit_headline_numeric": Decimal("1500000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Innovators, students, startups, and MSMEs with original commercial ideas",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Applied online via annual Hackathon calls on innovative.msme.gov.in."
            }
        },

        # 25. MSME Innovative Design
        {
            "program": {
                "program_code": "MSME_INNOVATIVE_DESIGN",
                "program_name": "MSME Innovative Scheme - Design Component",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "O/o DC-MSME",
                "official_portal_url": "https://innovative.msme.gov.in",
                "primary_type": "INNOVATION / INCUBATION",
                "secondary_types": ["TECHNOLOGY / QUALITY"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Co-funds expert design consultant and student design projects to improve product aesthetics and functional design.",
                "benefit_summary": "75% grant for Micro (up to Rs. 40 Lakh) and 60% for Small/Medium (up to Rs. 40 Lakh) for engaging design consultants.",
                "benefit_type": "DESIGN_GRANT",
                "benefit_headline_numeric": Decimal("4000000.00"),
                "benefit_headline_percentage": Decimal("75.00"),
                "target_beneficiary_summary": "Manufacturing and technical service MSMEs upgrading industrial designs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Must be paired with recognized Design Centres (e.g. NID, IISc, IITs) or qualified designers."
            }
        },

        # 26. MSME Innovative IPR
        {
            "program": {
                "program_code": "MSME_INNOVATIVE_IPR",
                "program_name": "MSME Innovative Scheme - Intellectual Property Rights (IPR) Component",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "O/o DC-MSME",
                "official_portal_url": "https://innovative.msme.gov.in",
                "primary_type": "INNOVATION / INCUBATION",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Reimbursement of statutory registration and attorney fees for obtaining domestic and international patents, trademarks, and GIs.",
                "benefit_summary": "Reimbursement: up to Rs. 5 Lakh for Foreign Patent, Rs. 1 Lakh for Domestic Patent, Rs. 2 Lakh for GI, and Rs. 10,000 for Trademark.",
                "benefit_type": "IPR_REIMBURSEMENT",
                "benefit_headline_numeric": Decimal("500000.00"),
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Udyam-registered MSMEs protecting original proprietary inventions",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Patent/trademark must be granted/published; claim submitted within window."
            }
        },

        # 27. Startup India Seed Fund (SISFS)
        {
            "program": {
                "program_code": "STARTUP_SEED_FUND",
                "program_name": "Startup India Seed Fund Scheme (SISFS)",
                "owning_ministry": "Ministry of Commerce and Industry (DPIIT)",
                "nodal_agency": "DPIIT",
                "official_portal_url": "https://seedfund.startupindia.gov.in",
                "primary_type": "INNOVATION / INCUBATION",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Financial assistance to early-stage DPIIT-recognized startups for proof of concept, prototype trials, and commercialization.",
                "benefit_summary": "Up to Rs. 20 Lakh as grant for proof of concept, and up to Rs. 50 Lakh as debt/convertible debenture for market launch.",
                "benefit_type": "SEED_GRANT_DEBT",
                "benefit_headline_numeric": Decimal("5000000.00"),
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "DPIIT-recognized early-stage startups incorporated within 2 years",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "DPIIT-recognized startup; incorporated less than 2 years ago."
            }
        },

        # 28. ESDP Training
        {
            "program": {
                "program_code": "ESDP_TRAINING",
                "program_name": "Entrepreneurship and Skill Development Programme (ESDP)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "MSME-Development and Facilitation Offices (MSME-DFOs)",
                "official_portal_url": "https://esdp.msme.gov.in",
                "primary_type": "TRAINING / ENTREPRENEURSHIP",
                "secondary_types": None,
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Organizes free and subsidized vocational, entrepreneurial, and management development training courses across India.",
                "benefit_summary": "Free/subsidized vocational training and entrepreneurial mentorship courses conducted through MSME-DFOs.",
                "benefit_type": "VOCATIONAL_TRAINING",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Aspiring entrepreneurs, youth, SC/ST, and women starting business ventures",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": [], # Unmapped: universal per guidelines
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Open to Indian citizens; special stipends/fee waivers for SC/ST/women/differently-abled."
            }
        },

        # 29. SAMARTH Textile
        {
            "program": {
                "program_code": "SAMARTH_TEXTILE",
                "program_name": "SAMARTH (Scheme for Capacity Building in Textile Sector)",
                "owning_ministry": "Ministry of Textiles",
                "nodal_agency": "Ministry of Textiles",
                "official_portal_url": "https://samarth-textiles.gov.in",
                "primary_type": "TRAINING / ENTREPRENEURSHIP",
                "secondary_types": ["OTHER MSME SUPPORT"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Demand-driven, placement-oriented skilling programme partnering with organized textile industry and MSMEs.",
                "benefit_summary": "Free NSQF skilling, biometric-tracked assessment, wage compensation, and job placement in textile units.",
                "benefit_type": "SKILL_TRAINING_PLACEMENT",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Youth and existing workers in textile, spinning, and garment MSMEs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Aadhaar-authenticated training; mandatory placement target for implementing partners."
            }
        },

        # 30. ni-msme Executive Modules
        {
            "program": {
                "program_code": "NIMSME_CAPACITY",
                "program_name": "ni-msme Executive & Managerial Capacity Building Modules",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National Institute for Micro, Small and Medium Enterprises (ni-msme)",
                "official_portal_url": "https://www.nimsme.org",
                "primary_type": "TRAINING / ENTREPRENEURSHIP",
                "secondary_types": None,
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Specialized residential and online executive management training courses in finance, marketing, and exports for MSME leaders.",
                "benefit_summary": "Subsidized executive management and industrial leadership certification courses.",
                "benefit_type": "MANAGEMENT_TRAINING",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "MSME founders, managing directors, and industrial executives",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV", "TRD"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Direct course registration through annual ni-msme calendar."
            }
        },

        # 31. Mahila Coir Yojana
        {
            "program": {
                "program_code": "MAHILA_COIR_YOJANA",
                "program_name": "Mahila Coir Yojana (under Coir Vikas Yojana)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Coir Board",
                "official_portal_url": "https://coirboard.gov.in",
                "primary_type": "TRAINING / ENTREPRENEURSHIP",
                "secondary_types": ["TRADITIONAL INDUSTRY / ARTISANS", "SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Women-oriented programme providing 2 months coir spinning training, monthly stipend, and 75% subsidy on motorized ratts.",
                "benefit_summary": "2-month skill training with monthly stipend of Rs. 3,000, plus 75% capital subsidy on motorized coir spinning equipment.",
                "benefit_type": "TRAINING_AND_TOOLKIT_SUBSIDY",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("75.00"),
                "target_beneficiary_summary": "Rural women artisans in coconut-growing regions",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "ART"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": False, "female_eligible": True, "other_gender_eligible": False,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Exclusively for women artisans; one spinning ratt distributed per trained woman."
            }
        },

        # 32. MSE-CDP CFC
        {
            "program": {
                "program_code": "MSE_CDP_CFC",
                "program_name": "MSE-CDP - Common Facility Centres (CFC)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Office of Development Commissioner (MSME)",
                "official_portal_url": "https://cdp.msme.gov.in",
                "primary_type": "CLUSTER / INFRASTRUCTURE",
                "secondary_types": ["TECHNOLOGY / QUALITY"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Grant assistance for establishing Common Facility Centres (testing labs, design studios, tool rooms, effluent plants) for industrial clusters.",
                "benefit_summary": "Grant assistance of 70% (up to 80% for special categories/NER) for projects with maximum ceiling of Rs. 30 Crore.",
                "benefit_type": "CLUSTER_INFRA_GRANT",
                "benefit_headline_numeric": Decimal("300000000.00"),
                "benefit_headline_percentage": Decimal("70.00"),
                "target_beneficiary_summary": "Special Purpose Vehicles (SPVs) formed by at least 20 MSMEs in an industrial cluster",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "SPV must have minimum 20 MSE members; minimum 10% SPV equity contribution."
            }
        },

        # 33. MSE-CDP ID
        {
            "program": {
                "program_code": "MSE_CDP_ID",
                "program_name": "MSE-CDP - Infrastructure Development (ID) Projects",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Office of Development Commissioner (MSME)",
                "official_portal_url": "https://cdp.msme.gov.in",
                "primary_type": "CLUSTER / INFRASTRUCTURE",
                "secondary_types": None,
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Financial grant for developing new industrial estates or upgrading infrastructure in existing industrial areas.",
                "benefit_summary": "Grant assistance of 60% (up to 70% for special categories) up to Rs. 15 Crore for industrial estate infrastructure.",
                "benefit_type": "INDUSTRIAL_ESTATE_GRANT",
                "benefit_headline_numeric": Decimal("150000000.00"),
                "benefit_headline_percentage": Decimal("60.00"),
                "target_beneficiary_summary": "State Industrial Development Corporations, municipal bodies, and cluster SPVs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "State agency or industrial association application submitted via State Directorate of Industries."
            }
        },

        # 34. ASPIRE LBI
        {
            "program": {
                "program_code": "ASPIRE_LBI",
                "program_name": "ASPIRE - Livelihood Business Incubators (LBI)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "O/o DC-MSME",
                "official_portal_url": "https://aspire.msme.gov.in",
                "primary_type": "CLUSTER / INFRASTRUCTURE",
                "secondary_types": ["INNOVATION / INCUBATION"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Financial grant for setting up Livelihood Business Incubators providing hands-on manufacturing training on industrial equipment.",
                "benefit_summary": "One-time 100% grant of up to Rs. 1 Crore (for government bodies) or 50% up to Rs. 50 Lakh (for private entities).",
                "benefit_type": "INCUBATOR_SETUP_GRANT",
                "benefit_headline_numeric": Decimal("10000000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Rural youth, micro-entrepreneurs, and industrial training institutes",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Focuses on agro-rural technologies and local livelihood trades."
            }
        },

        # 35. SFURTI Clusters
        {
            "program": {
                "program_code": "SFURTI_CLUSTERS",
                "program_name": "Scheme of Fund for Regeneration of Traditional Industries (SFURTI)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "KVIC / Coir Board / NCDC",
                "official_portal_url": "https://sfurti.msme.gov.in",
                "primary_type": "TRADITIONAL INDUSTRY / ARTISANS",
                "secondary_types": ["CLUSTER / INFRASTRUCTURE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Grant assistance for setting up Common Facility Centres, modern machinery, and market linkages for artisan collectives.",
                "benefit_summary": "Grant assistance up to Rs. 2.5 Crore (Regular Clusters: 500 artisans) and up to Rs. 5 Crore (Major Clusters: 1,000+ artisans).",
                "benefit_type": "ARTISAN_CLUSTER_GRANT",
                "benefit_headline_numeric": Decimal("50000000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Artisan clusters in Khadi, coir, bamboo, honey, pottery, and handicrafts",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "ART"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Artisans organize as an SPV partnered with an Implementing Agency."
            }
        },

        # 36. Gramodyog Vikas Yojana (GVY)
        {
            "program": {
                "program_code": "GVY_MISSION",
                "program_name": "Gramodyog Vikas Yojana (GVY) - Honey Mission & Kumhar Sashaktikaran",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Khadi and Village Industries Commission (KVIC)",
                "official_portal_url": "https://www.kvic.gov.in",
                "primary_type": "TRADITIONAL INDUSTRY / ARTISANS",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Free distribution of modern production toolkits (bee boxes, electric pottery wheels, toolkits) along with practical training.",
                "benefit_summary": "Free modern toolkits, processing equipment, and 5-10 day practical skill development training.",
                "benefit_type": "FREE_TOOLKIT_AND_TRAINING",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Rural potters, beekeepers, leather workers, and village craftsmen",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "AGR", "ART"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Traditional craft background or certified vocational skill in the trade."
            }
        },

        # 37. CITUS Coir
        {
            "program": {
                "program_code": "CITUS_COIR",
                "program_name": "Coir Industry Technology Upgradation Scheme (CITUS)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Coir Board",
                "official_portal_url": "https://coirboard.gov.in",
                "primary_type": "TRADITIONAL INDUSTRY / ARTISANS",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Provides 25% capital subsidy on procurement of modern coir processing plant and machinery.",
                "benefit_summary": "25% capital subsidy on procurement of eligible plant and machinery up to a project ceiling of Rs. 2.50 Crore.",
                "benefit_type": "CAPITAL_SUBSIDY",
                "benefit_headline_numeric": Decimal("6250000.00"),
                "benefit_headline_percentage": Decimal("25.00"),
                "target_beneficiary_summary": "Coir manufacturing micro, small, and medium enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "New or existing coir processing units; Udyam registration required."
            },
            "subsidy": {
                "subsidy_pct": Decimal("25.00"),
                "max_subsidy_amount": Decimal("6250000.00"),
                "min_project_cost": None, "max_project_cost": Decimal("25000000.00"),
                "beneficiary_contribution_pct": None,
                "disbursement_type": "Direct Capital Subsidy via Coir Board"
            }
        },

        # 38. NHDP Weavers MUDRA
        {
            "program": {
                "program_code": "WEAVERS_MUDRA",
                "program_name": "National Handloom Development Programme (NHDP) - Weavers MUDRA",
                "owning_ministry": "Ministry of Textiles",
                "nodal_agency": "Office of Development Commissioner for Handlooms",
                "official_portal_url": "https://handlooms.nic.in",
                "primary_type": "TRADITIONAL INDUSTRY / ARTISANS",
                "secondary_types": ["CREDIT / LOAN"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "Concessional credit scheme for handloom weavers providing margin money assistance, 7% interest subvention, and CGTMSE guarantee.",
                "benefit_summary": "Margin money up to Rs. 10,000 (up to Rs. 2 Lakh for collectives), 7% interest subvention, and collateral-free credit.",
                "benefit_type": "CONCESSIONAL_CREDIT",
                "benefit_headline_numeric": Decimal("200000.00"),
                "benefit_headline_percentage": Decimal("7.00"),
                "target_beneficiary_summary": "Individual handloom weavers, master weavers, and handloom SHGs",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "ART"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Must possess valid Handloom Weaver Pehchan Card or State Directorate recommendation."
            },
            "credit": {
                "min_loan_amount": None, "max_loan_amount": Decimal("200000.00"),
                "interest_rate_min": Decimal("6.00"), "interest_rate_max": Decimal("6.00"),
                "tenure_years": Decimal("3.0"), "moratorium_months": None,
                "collateral_required": False, "promoter_contribution_pct": None
            }
        },

        # 39. IC International Fairs
        {
            "program": {
                "program_code": "IC_INTL_FAIRS",
                "program_name": "International Cooperation (IC) Scheme - Physical Participation in International Fairs",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Ministry of MSME",
                "official_portal_url": "https://ic.msme.gov.in",
                "primary_type": "EXPORT / INTERNATIONALIZATION",
                "secondary_types": ["MARKET ACCESS"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Financial subsidy covering economy airfare and stall charges for MSE delegations participating in international trade exhibitions.",
                "benefit_summary": "100% economy airfare (up to Rs. 1.5 Lakh) and 100% stall charges (up to Rs. 3 Lakh) for foreign expos.",
                "benefit_type": "EXPORT_EXHIBITION_SUBSIDY",
                "benefit_headline_numeric": Decimal("450000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "Export-ready Micro and Small Enterprises",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Valid Udyam Registration and active IEC; max 3 international visits supported."
            }
        },

        # 40. IC CBFTE
        {
            "program": {
                "program_code": "IC_CBFTE",
                "program_name": "IC Scheme - Capacity Building of First-Time MSE Exporters (CBFTE)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Ministry of MSME / RAMP",
                "official_portal_url": "https://ic.msme.gov.in",
                "primary_type": "EXPORT / INTERNATIONALIZATION",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Direct reimbursement of statutory registration and compliance costs incurred by first-time exporter MSEs for RCMC, ECGC insurance, and testing.",
                "benefit_summary": "75% reimbursement of RCMC charges (up to Rs. 20,000), ECGC insurance (up to Rs. 10,000), and testing fees (up to Rs. 1 Lakh).",
                "benefit_type": "EXPORT_COMPLIANCE_REIMBURSEMENT",
                "benefit_headline_numeric": Decimal("130000.00"),
                "benefit_headline_percentage": Decimal("75.00"),
                "target_beneficiary_summary": "First-time MSE exporters with valid Udyam and IEC",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "MSE must have valid IEC issued within the designated prior window; online claim on ic.msme.gov.in."
            }
        },

        # 41. MAI Export
        {
            "program": {
                "program_code": "MAI_EXPORT",
                "program_name": "Market Access Initiative (MAI) Scheme",
                "owning_ministry": "Ministry of Commerce and Industry (Department of Commerce)",
                "nodal_agency": "Department of Commerce",
                "official_portal_url": "https://commerce.gov.in",
                "primary_type": "EXPORT / INTERNATIONALIZATION",
                "secondary_types": ["MARKET ACCESS"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Financial assistance for international market research, Reverse Buyer Seller Meets (RBSMs), and foreign product registration.",
                "benefit_summary": "Subsidized stall charges, airfare support, and up to 50% reimbursement of foreign statutory product registration.",
                "benefit_type": "MARKET_DEVELOPMENT_ASSISTANCE",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("50.00"),
                "target_beneficiary_summary": "Exporter MSMEs participating in EPC-organized foreign trade initiatives",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Applied through respective Export Promotion Councils (e.g. FIEO, EEPC, APEDA)."
            }
        },

        # 42. TMA Agri Export
        {
            "program": {
                "program_code": "TMA_AGRI_EXPORT",
                "program_name": "Transport and Marketing Assistance (TMA) for Specified Agriculture Products",
                "owning_ministry": "Ministry of Commerce and Industry (DGFT)",
                "nodal_agency": "Directorate General of Foreign Trade (DGFT)",
                "official_portal_url": "https://dgft.gov.in",
                "primary_type": "EXPORT / INTERNATIONALIZATION",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Financial assistance for international freight and logistics to mitigate export disadvantages for Indian agricultural products.",
                "benefit_summary": "Reimbursement of international air and ocean freight charges at prescribed rates per TEU/tonnage.",
                "benefit_type": "FREIGHT_SUBSIDY",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Exporters of eligible agricultural and processed food products",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Valid IEC; shipments to specified destinations; quarterly claims on dgft.gov.in."
            }
        },

        # 43. MSME Samadhaan
        {
            "program": {
                "program_code": "MSME_SAMADHAAN",
                "program_name": "MSME Samadhaan (Delayed Payment Monitoring & Facilitation System)",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "Micro & Small Enterprises Facilitation Councils (MSEFC)",
                "official_portal_url": "https://samadhaan.msme.gov.in",
                "primary_type": "DELAYED PAYMENT / DISPUTE",
                "secondary_types": ["OTHER MSME SUPPORT"],
                "actionability_type": "FRAMEWORK",
                "hierarchy_level": "STATUTORY_MECHANISM",
                "parent_program_code": None,
                "description": "Statutory legal arbitration mechanism under Sections 15-24 of MSMED Act 2006 for delayed payment recovery against buyers.",
                "benefit_summary": "Statutory recovery of overdue invoices beyond 45 days with mandatory compound interest at 3 times the RBI bank rate.",
                "benefit_type": "STATUTORY_LEGAL_REMEDY",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "All Udyam-registered Micro and Small Enterprises supplying goods or services",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Valid Udyam Registration at date of invoice; payment delay exceeds 45 days."
            }
        },

        # 44. TReDS Factoring
        {
            "program": {
                "program_code": "TREDS_FACTORING",
                "program_name": "Trade Receivables Discounting System (TReDS) Framework",
                "owning_ministry": "Reserve Bank of India / Ministry of MSME",
                "nodal_agency": "RBI-licensed TReDS Platforms (RXIL, M1xchange, Invoicemart)",
                "official_portal_url": "https://www.rbi.org.in",
                "primary_type": "DELAYED PAYMENT / DISPUTE",
                "secondary_types": ["CREDIT / LOAN"],
                "actionability_type": "FRAMEWORK",
                "hierarchy_level": "INSTITUTIONAL_FRAMEWORK",
                "parent_program_code": None,
                "description": "Electronic institutional auction platform enabling MSE suppliers to discount accepted trade invoices without recourse.",
                "benefit_summary": "Non-recourse, collateral-free instant invoice discounting at competitive bidding rates without blocking credit lines.",
                "benefit_type": "INVOICE_FACTORING",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Micro, Small, and Medium Enterprises seeking immediate liquidity on trade invoices",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Udyam-registered MSME onboards an RBI-licensed TReDS exchange; buyer accepts trade invoice."
            }
        },

        # 45. NSSH SPRS Subsidy
        {
            "program": {
                "program_code": "NSSH_SPRS_SUBSIDY",
                "program_name": "NSSH - Single Point Registration Scheme (SPRS) Fee Subsidy",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National Small Industries Corporation (NSIC) / NSSH",
                "official_portal_url": "https://www.scsthub.in",
                "primary_type": "OTHER MSME SUPPORT",
                "secondary_types": ["MARKET ACCESS"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "SUB_SCHEME",
                "parent_program_code": None,
                "description": "100% subsidy on NSIC registration and technical inspection fees for SC/ST MSEs under Single Point Registration Scheme.",
                "benefit_summary": "100% waiver of application fee and technical inspection fee for NSIC Single Point Registration.",
                "benefit_type": "REGISTRATION_FEE_WAIVER",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "SC/ST-owned Micro and Small Enterprises participating in government tenders",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": False, "sc_eligible": True, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "SC/ST enterprise with commercial production underway; applied via NSIC/NSSH."
            }
        },

        # 46. NSSH Bank Fee Reimb
        {
            "program": {
                "program_code": "NSSH_BANK_FEE_REIMB",
                "program_name": "NSSH - Bank Loan Processing Fee and Bank Guarantee Charges Reimbursement",
                "owning_ministry": "Ministry of MSME",
                "nodal_agency": "National SC-ST Hub",
                "official_portal_url": "https://www.scsthub.in",
                "primary_type": "OTHER MSME SUPPORT",
                "secondary_types": ["CREDIT / LOAN"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Reimbursement of bank loan processing fees and bank guarantee commission charges incurred by SC/ST MSEs.",
                "benefit_summary": "100% reimbursement of processing fees on sanctioned loans, plus 100% reimbursement of bank guarantee commission (up to Rs. 1 Lakh/year).",
                "benefit_type": "BANK_CHARGES_REIMBURSEMENT",
                "benefit_headline_numeric": Decimal("100000.00"),
                "benefit_headline_percentage": Decimal("100.00"),
                "target_beneficiary_summary": "SC/ST MSEs paying bank processing and guarantee fees on institutional loans",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": False, "sc_eligible": True, "st_eligible": True, "obc_eligible": False,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Sanctioned by scheduled commercial bank; claims submitted on scsthub.in."
            }
        },

        # 47. PM-KUSUM Component A
        {
            "program": {
                "program_code": "PM_KUSUM_A",
                "program_name": "PM-KUSUM Component A (Decentralized Solar Power Generation)",
                "owning_ministry": "Ministry of New and Renewable Energy (MNRE)",
                "nodal_agency": "State Nodal Agencies / DISCOMs",
                "official_portal_url": "https://pmkusum.mnre.gov.in",
                "primary_type": "OTHER MSME SUPPORT",
                "secondary_types": ["SUBSIDY / CAPITAL ASSISTANCE"],
                "actionability_type": "COMPONENT_RECOMMENDABLE",
                "hierarchy_level": "COMPONENT",
                "parent_program_code": None,
                "description": "Setting up grid-connected renewable power plants of capacity 500 kW to 2 MW on barren or rural land.",
                "benefit_summary": "25-year guaranteed Power Purchase Agreement (PPA) with local state DISCOM at feed-in tariffs.",
                "benefit_type": "FEED_IN_TARIFF_PPA",
                "benefit_headline_numeric": None,
                "benefit_headline_percentage": None,
                "target_beneficiary_summary": "Rural entrepreneurs, farmers, cooperatives, and MSMEs setting up clean energy generation",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["SRV", "AGR"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Power plant located within 5 km of local 33/11 kV substation; DISCOM selection."
            }
        },

        # 48. SIP-EIT
        {
            "program": {
                "program_code": "SIP_EIT_PATENT",
                "program_name": "Support for International Patent Protection in E&IT (SIP-EIT)",
                "owning_ministry": "Ministry of Electronics and Information Technology (MeitY)",
                "nodal_agency": "MeitY",
                "official_portal_url": "https://meity.gov.in/esdm/sip-eit",
                "primary_type": "OTHER MSME SUPPORT",
                "secondary_types": ["INNOVATION / INCUBATION"],
                "actionability_type": "DIRECTLY_RECOMMENDABLE",
                "hierarchy_level": "STANDALONE",
                "parent_program_code": None,
                "description": "Financial reimbursement scheme providing up to 50% of expenses in filing international patent applications for ICT and electronics MSMEs.",
                "benefit_summary": "Reimbursement up to 50% of total patent filing expenses, subject to a maximum of Rs. 15 Lakh per invention.",
                "benefit_type": "PATENT_REIMBURSEMENT",
                "benefit_headline_numeric": Decimal("1500000.00"),
                "benefit_headline_percentage": Decimal("50.00"),
                "target_beneficiary_summary": "Technology MSMEs and DPIIT-recognized startups in electronics and ICT",
                "status": "active",
                "legacy_scheme_id": None,
            },
            "sectors": ["MFG", "SRV"],
            "eligibility": {
                "rural_eligible": True, "urban_eligible": True,
                "male_eligible": True, "female_eligible": True, "other_gender_eligible": True,
                "general_eligible": True, "sc_eligible": True, "st_eligible": True, "obc_eligible": True,
                "minority_eligible": None, "pwd_eligible": None, "ex_servicemen_eligible": None,
                "min_age": 18, "max_age": None, "max_annual_income": None,
                "notes": "Indigenous ICT innovation; online application filed on MeitY portal before foreign filing."
            }
        }
    ]

    print("Beginning transactional, idempotent seeding of 60 Government Programmes...")
    with engine.begin() as conn:
        # Fetch sector mapping id by sector_code
        sector_rows = conn.execute(text("SELECT id, sector_code FROM sectors;")).fetchall()
        sector_map = {r[1]: r[0] for r in sector_rows}
        print(f"Loaded canonical sectors: {sector_map}")

        # --- A. SEED 12 LEGACY PROGRAMMES ---
        print("\nSeeding 12 legacy programmes linked to schemes 1-12...")
        for p in legacy_programs:
            p_data = dict(p)
            if isinstance(p_data.get("secondary_types"), list):
                p_data["secondary_types"] = json.dumps(p_data["secondary_types"])

            insert_prog_sql = text("""
                INSERT INTO government_programs (
                    program_code, program_name, owning_ministry, nodal_agency, official_portal_url,
                    primary_type, secondary_types, actionability_type, hierarchy_level,
                    description, benefit_summary, benefit_type, benefit_headline_numeric,
                    benefit_headline_percentage, target_beneficiary_summary, status, legacy_scheme_id
                ) VALUES (
                    :program_code, :program_name, :owning_ministry, :nodal_agency, :official_portal_url,
                    :primary_type, :secondary_types, :actionability_type, :hierarchy_level,
                    :description, :benefit_summary, :benefit_type, :benefit_headline_numeric,
                    :benefit_headline_percentage, :target_beneficiary_summary, :status, :legacy_scheme_id
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
            conn.execute(insert_prog_sql, p_data)

        # --- B. SEED 48 NEW PROGRAMMES ---
        print("Seeding 48 new programmes...")
        inserted_count = 0
        sectors_mapped_count = 0
        eligibility_count = 0
        credit_count = 0
        guarantee_count = 0
        subsidy_count = 0

        for item in new_programs:
            p = dict(item["program"])
            if isinstance(p.get("secondary_types"), list):
                p["secondary_types"] = json.dumps(p["secondary_types"])
            insert_prog_sql = text("""
                INSERT INTO government_programs (
                    program_code, program_name, owning_ministry, nodal_agency, official_portal_url,
                    primary_type, secondary_types, actionability_type, hierarchy_level,
                    description, benefit_summary, benefit_type, benefit_headline_numeric,
                    benefit_headline_percentage, target_beneficiary_summary, status, legacy_scheme_id
                ) VALUES (
                    :program_code, :program_name, :owning_ministry, :nodal_agency, :official_portal_url,
                    :primary_type, :secondary_types, :actionability_type, :hierarchy_level,
                    :description, :benefit_summary, :benefit_type, :benefit_headline_numeric,
                    :benefit_headline_percentage, :target_beneficiary_summary, :status, :legacy_scheme_id
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
            prog_id = conn.execute(insert_prog_sql, p).scalar()
            inserted_count += 1

            # Seed program_sectors
            # Delete existing mappings for this program_id to ensure clean idempotency
            conn.execute(text("DELETE FROM program_sectors WHERE program_id = :pid;"), {"pid": prog_id})
            for s_code in item.get("sectors", []):
                if s_code in sector_map:
                    conn.execute(text("""
                        INSERT INTO program_sectors (program_id, sector_id)
                        VALUES (:pid, :sid)
                        ON CONFLICT (program_id, sector_id) DO NOTHING;
                    """), {"pid": prog_id, "sid": sector_map[s_code]})
                    sectors_mapped_count += 1
                else:
                    raise ValueError(f"Unknown canonical sector code: {s_code}")

            # Seed program_eligibility
            if "eligibility" in item and item["eligibility"]:
                e = item["eligibility"].copy()
                e["program_id"] = prog_id
                e.setdefault("target_gender", None)
                e.setdefault("target_social_categories", None)
                e.setdefault("artisan_mandate", False)
                e.setdefault("street_vendor_mandate", False)
                e.setdefault("startup_mandate", False)
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

    print("\nTransaction committed successfully.")
    print(f"Summary:")
    print(f"  Legacy Programmes Seeded:   {len(legacy_programs)}")
    print(f"  New Programmes Seeded:      {inserted_count}")
    print(f"  Total Programmes:           {len(legacy_programs) + inserted_count}")
    print(f"  New Sector Mappings:        {sectors_mapped_count}")
    print(f"  New Eligibility Records:    {eligibility_count}")
    print(f"  New Credit Details:         {credit_count}")
    print(f"  New Guarantee Details:      {guarantee_count}")
    print(f"  New Subsidy Details:        {subsidy_count}")

if __name__ == "__main__":
    seed()
