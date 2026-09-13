-- ============================================================
-- GOI SCHEMES + MSME MARKET RESEARCH DATABASE
-- PostgreSQL 18
-- Database: goi_schemes
-- ============================================================


-- ============================================================
-- 1. SCHEMES
-- ============================================================

CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Government classification
    ministry VARCHAR(255),
    scheme_type VARCHAR(100),
    category VARCHAR(100),

    -- Business applicability
    business_type VARCHAR(255),
    sector VARCHAR(100),
    target_group VARCHAR(255),

    -- Financial support
    income_limit NUMERIC(14,2),
    min_project_cost NUMERIC(14,2),
    max_project_cost NUMERIC(14,2),

    loan_percentage NUMERIC(5,2),
    min_loan_amount NUMERIC(14,2),
    max_loan_amount NUMERIC(14,2),

    beneficiary_contribution_percentage NUMERIC(5,2),

    subsidy_percentage NUMERIC(5,2),
    max_subsidy NUMERIC(14,2),

    interest_rate NUMERIC(5,2),
    tenure_years NUMERIC(5,2),
    moratorium_months INTEGER,
    repayment_frequency VARCHAR(50),

    -- Business stage
    new_business_only BOOLEAN DEFAULT FALSE,
    existing_business_allowed BOOLEAN DEFAULT TRUE,

    -- Security
    collateral_required BOOLEAN DEFAULT FALSE,

    -- Information
    benefit TEXT,
    eligibility_text TEXT,
    documents_required TEXT,
    application_url TEXT,

    -- Status
    status VARCHAR(50) DEFAULT 'active',
    last_verified DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. SCHEME ELIGIBILITY
-- ============================================================

CREATE TABLE IF NOT EXISTS scheme_eligibility (
    id SERIAL PRIMARY KEY,

    scheme_id INTEGER NOT NULL
        REFERENCES schemes(id)
        ON DELETE CASCADE,

    -- Geography
    rural_eligible BOOLEAN DEFAULT TRUE,
    urban_eligible BOOLEAN DEFAULT TRUE,

    -- Gender
    male_eligible BOOLEAN DEFAULT TRUE,
    female_eligible BOOLEAN DEFAULT TRUE,
    other_gender_eligible BOOLEAN DEFAULT TRUE,

    -- Social category
    general_eligible BOOLEAN DEFAULT TRUE,
    sc_eligible BOOLEAN DEFAULT FALSE,
    st_eligible BOOLEAN DEFAULT FALSE,
    obc_eligible BOOLEAN DEFAULT FALSE,

    -- Additional groups
    minority_eligible BOOLEAN DEFAULT FALSE,
    pwd_eligible BOOLEAN DEFAULT FALSE,
    ex_servicemen_eligible BOOLEAN DEFAULT FALSE,

    -- Age
    min_age INTEGER,
    max_age INTEGER,

    -- Income
    max_annual_income NUMERIC(14,2),

    -- Additional conditions
    notes TEXT,

    UNIQUE(scheme_id)
);


-- ============================================================
-- 3. STATES
-- ============================================================

CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,

    state_code VARCHAR(10) UNIQUE,
    state_name VARCHAR(100) NOT NULL UNIQUE,

    region VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 4. DISTRICTS
-- ============================================================

CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,

    district_code VARCHAR(20) UNIQUE,

    district_name VARCHAR(150) NOT NULL,

    state_id INTEGER NOT NULL
        REFERENCES states(id)
        ON DELETE CASCADE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(state_id, district_name)
);


-- ============================================================
-- 5. MSME STATE DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS msme_state_data (
    id BIGSERIAL PRIMARY KEY,

    state_id INTEGER NOT NULL
        REFERENCES states(id)
        ON DELETE CASCADE,

    reporting_date DATE,

    -- Enterprise classification
    micro_enterprises BIGINT DEFAULT 0,
    small_enterprises BIGINT DEFAULT 0,
    medium_enterprises BIGINT DEFAULT 0,

    -- Activity
    manufacturing_enterprises BIGINT DEFAULT 0,
    service_enterprises BIGINT DEFAULT 0,
    trading_enterprises BIGINT DEFAULT 0,

    -- Employment
    employment BIGINT DEFAULT 0,

    -- Ownership
    male_owned BIGINT DEFAULT 0,
    female_owned BIGINT DEFAULT 0,
    other_gender_owned BIGINT DEFAULT 0,

    -- Social category
    sc_enterprises BIGINT DEFAULT 0,
    st_enterprises BIGINT DEFAULT 0,
    obc_enterprises BIGINT DEFAULT 0,

    -- Source tracking
    source_name VARCHAR(255),
    source_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(state_id, reporting_date)
);


-- ============================================================
-- 6. MSME DISTRICT DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS msme_district_data (
    id BIGSERIAL PRIMARY KEY,

    district_id INTEGER NOT NULL
        REFERENCES districts(id)
        ON DELETE CASCADE,

    reporting_date DATE,

    -- Enterprise classification
    micro_enterprises BIGINT DEFAULT 0,
    small_enterprises BIGINT DEFAULT 0,
    medium_enterprises BIGINT DEFAULT 0,

    -- Sector
    manufacturing_enterprises BIGINT DEFAULT 0,
    service_enterprises BIGINT DEFAULT 0,
    trading_enterprises BIGINT DEFAULT 0,

    -- Employment
    employment BIGINT DEFAULT 0,

    -- Ownership
    male_owned BIGINT DEFAULT 0,
    female_owned BIGINT DEFAULT 0,

    -- Social category
    sc_enterprises BIGINT DEFAULT 0,
    st_enterprises BIGINT DEFAULT 0,
    obc_enterprises BIGINT DEFAULT 0,

    -- Source tracking
    source_name VARCHAR(255),
    source_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(district_id, reporting_date)
);


-- ============================================================
-- 7. SECTORS
-- ============================================================

CREATE TABLE IF NOT EXISTS sectors (
    id SERIAL PRIMARY KEY,

    sector_code VARCHAR(20) UNIQUE,
    sector_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT
);


-- ============================================================
-- 8. NIC ACTIVITIES
-- National Industrial Classification
-- ============================================================

CREATE TABLE IF NOT EXISTS nic_activities (
    id SERIAL PRIMARY KEY,

    nic_code VARCHAR(20) UNIQUE NOT NULL,

    section_code VARCHAR(10),
    division_code VARCHAR(10),
    group_code VARCHAR(10),
    class_code VARCHAR(10),

    activity_name VARCHAR(255) NOT NULL,

    sector_id INTEGER
        REFERENCES sectors(id)
        ON DELETE SET NULL,

    description TEXT
);


-- ============================================================
-- 9. MSME NIC / ACTIVITY DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS msme_activity_data (
    id BIGSERIAL PRIMARY KEY,

    state_id INTEGER
        REFERENCES states(id)
        ON DELETE CASCADE,

    district_id INTEGER
        REFERENCES districts(id)
        ON DELETE CASCADE,

    nic_activity_id INTEGER
        REFERENCES nic_activities(id)
        ON DELETE SET NULL,

    reporting_date DATE,

    enterprise_count BIGINT DEFAULT 0,

    employment BIGINT DEFAULT 0,

    micro_enterprises BIGINT DEFAULT 0,
    small_enterprises BIGINT DEFAULT 0,
    medium_enterprises BIGINT DEFAULT 0,

    source_name VARCHAR(255),
    source_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 10. SCHEME ↔ SECTOR
-- ============================================================

CREATE TABLE IF NOT EXISTS scheme_sectors (
    scheme_id INTEGER NOT NULL
        REFERENCES schemes(id)
        ON DELETE CASCADE,

    sector_id INTEGER NOT NULL
        REFERENCES sectors(id)
        ON DELETE CASCADE,

    PRIMARY KEY (scheme_id, sector_id)
);


-- ============================================================
-- 11. SCHEME ↔ STATE
-- ============================================================

CREATE TABLE IF NOT EXISTS scheme_states (
    scheme_id INTEGER NOT NULL
        REFERENCES schemes(id)
        ON DELETE CASCADE,

    state_id INTEGER NOT NULL
        REFERENCES states(id)
        ON DELETE CASCADE,

    PRIMARY KEY (scheme_id, state_id)
);


-- ============================================================
-- 12. INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_districts_state
    ON districts(state_id);

CREATE INDEX IF NOT EXISTS idx_msme_state_date
    ON msme_state_data(state_id, reporting_date);

CREATE INDEX IF NOT EXISTS idx_msme_district_date
    ON msme_district_data(district_id, reporting_date);

CREATE INDEX IF NOT EXISTS idx_msme_activity_state
    ON msme_activity_data(state_id);

CREATE INDEX IF NOT EXISTS idx_msme_activity_district
    ON msme_activity_data(district_id);

CREATE INDEX IF NOT EXISTS idx_msme_activity_nic
    ON msme_activity_data(nic_activity_id);

CREATE INDEX IF NOT EXISTS idx_schemes_sector
    ON schemes(sector);

CREATE INDEX IF NOT EXISTS idx_schemes_category
    ON schemes(category);

CREATE INDEX IF NOT EXISTS idx_schemes_ministry
    ON schemes(ministry);

CREATE INDEX IF NOT EXISTS idx_schemes_status
    ON schemes(status);


SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;



SELECT COUNT(*) AS scheme_count
FROM schemes;
