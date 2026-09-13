# India Government & MSME Scheme Recommendation Platform — Backend Foundation

A production-ready FastAPI backend and deterministic rule-based eligibility engine for Indian Government and MSME schemes. This service connects to a local PostgreSQL database (`goi_schemes`), exposes versioned RESTful APIs with multi-criteria filtering, manages database migrations via Alembic, provides secure User and BusinessProfile management with Argon2 password hashing, and establishes clean architectural boundaries for future Machine Learning (ranking) and LLM (explanation & guidance) integration.

---

## 1. Project Purpose & Architecture

The overarching platform helps Indian MSMEs, artisans, street vendors, and entrepreneurs discover and evaluate their eligibility for Central and State government schemes (such as PMMY MUDRA, PMEGP, PM Vishwakarma, PM SVANidhi, and NSFDC schemes).

### Conceptual Pipeline

```
                    ┌──────────────────────────────┐
                    │      User / MSME Profile     │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │  Rule-Based Eligibility      │
                    │  (Deterministic Engine)      │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   Eligible Schemes Subset    │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   Future: ML Recommendation  │
                    │   (scikit-learn Ranking)     │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   Future: LLM Explanation   │
                    │   & Conversational Guidance  │
                    └──────────────────────────────┘
```

> **Design Principle**: Statutory and legal eligibility is strictly deterministic (`app/services/eligibility_service.py`) and never outsourced to an ML model or LLM.

---

## 2. Layer Responsibilities & Structure

The codebase is structured under `app/`:

```
backend/
├── alembic/                            # Alembic database migration scripts
│   ├── versions/                       # Versioned migration revisions
│   └── env.py                          # Migration environment wired to DATABASE_URL
├── alembic.ini                         # Alembic configuration
├── app/
│   ├── main.py                         # FastAPI app setup, CORS, error handling
│   │
│   ├── core/
│   │   ├── config.py                   # Environment settings & config loading
│   │   ├── security.py                 # CORS middleware & Argon2 password hashing
│   │   └── exceptions.py               # Custom exceptions and sanitized error handlers
│   │
│   ├── db/
│   │   ├── database.py                 # SQLAlchemy engine (pre-ping pool) & Base
│   │   └── session.py                  # SessionLocal & get_db dependency
│   │
│   ├── models/
│   │   ├── scheme.py                   # Scheme model mapped to live 'schemes' table
│   │   ├── master.py                   # State, District, Sector, MSME macro models
│   │   ├── user.py                     # User account model
│   │   ├── business_profile.py         # MSME Business Profile model
│   │   └── research.py                 # ResearchRequest, ResearchReport, DataSource models
│   │
│   ├── schemas/
│   │   ├── scheme.py                   # Pydantic v2 schemas for Scheme requests & responses
│   │   ├── eligibility.py              # UserProfile & EligibilityResult schemas
│   │   ├── user.py                     # Pydantic v2 schemas for User CRUD
│   │   ├── business_profile.py         # Pydantic v2 schemas for BusinessProfile CRUD
│   │   └── research.py                 # Pydantic v2 schemas for Research & DataSources
│   │
│   ├── repositories/
│   │   ├── scheme_repository.py        # Database queries & SQL filtering for schemes
│   │   ├── user_repository.py          # Database operations for User
│   │   └── business_profile_repository.py # Database operations for BusinessProfile
│   │
│   ├── services/
│   │   ├── scheme_service.py           # Scheme business operations
│   │   ├── eligibility_service.py      # Deterministic rule evaluation engine
│   │   ├── user_service.py             # User registration & verification logic
│   │   └── business_profile_service.py # BusinessProfile management logic
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── health.py               # Health check and DB status endpoints
│   │       ├── schemes.py              # Scheme listing, details, & eligibility endpoints
│   │       ├── users.py                # User registration & profile management
│   │       └── business_profiles.py    # Business profile lookup & updates
│   │
│   ├── ml/
│   │   └── README.md                   # ML architecture documentation & future roadmap
│   │
│   └── utils/
│
├── tests/
│   ├── conftest.py                     # TestClient and read-only DB session fixtures
│   ├── test_health.py                  # Root, health, and DB connectivity tests
│   ├── test_schemes.py                 # Scheme listing, detail, filtering, & eligibility tests
│   └── test_users_and_profiles.py      # User and BusinessProfile CRUD & security tests
│
├── main.py                             # Root compatibility wrapper
├── database.py                         # Root compatibility wrapper
├── models.py                           # Root compatibility wrapper
├── schemes.py                          # Root compatibility wrapper
├── requirements.txt                    # Project dependencies
├── .env.example                        # Configuration template (placeholders only)
└── README.md                           # Documentation
```

---

## 3. Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.x, psycopg3 (`psycopg[binary]`)
- **Database Migrations**: Alembic
- **Security & Cryptography**: Argon2id (`pwdlib[argon2]`)
- **Data Validation & Schemas**: Pydantic v2
- **Configuration**: python-dotenv, environment variables
- **Testing**: pytest, FastAPI TestClient (httpx)
- **Future ML Engine**: scikit-learn, pandas, NumPy, joblib (see `app/ml/README.md`)

---

## 4. PostgreSQL Setup & Configuration

The application connects to a local PostgreSQL database (`goi_schemes`) running on `localhost:5432`.

### Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set your local database credentials in `.env`:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/goi_schemes
   ENVIRONMENT=development
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```
> **Security Note**: Never commit `.env` or hard-code credentials. The `.gitignore` file already excludes `.env`.

---

## 5. Getting Started

### 1. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

Apply Alembic migrations to create the application domain tables:

```bash
alembic upgrade head
```

### 4. Run the Backend

Start the development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

*Note: Backward-compatible root execution `uvicorn main:app --reload` is also fully supported.*

The server will start at: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc UI: `http://127.0.0.1:8000/redoc`

---

## 6. API Endpoints

### System & Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Root status message and metadata |
| `GET` | `/health` | Root health check and active scheme count |
| `GET` | `/api/v1/health` | Versioned health check endpoint |

### Government Schemes

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/schemes` | List schemes with optional filters & pagination |
| `GET` | `/api/v1/schemes/{scheme_id}` | Retrieve detailed information for a scheme |
| `POST` | `/api/v1/schemes/evaluate-eligibility` | Evaluate a user profile against all schemes |
| `GET` | `/api/schemes` | Legacy backwards-compatible scheme listing |

### Users & Business Profiles

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/users` | Register a new user (Argon2 password hashing) |
| `GET` | `/api/v1/users` | List registered users with pagination |
| `GET` | `/api/v1/users/{user_id}` | Retrieve user profile by ID |
| `PUT` | `/api/v1/users/{user_id}` | Update user profile details |
| `POST` | `/api/v1/users/{user_id}/business-profiles` | Create a business profile for user |
| `GET` | `/api/v1/users/{user_id}/business-profiles` | List business profiles for user |
| `GET` | `/api/v1/business-profiles` | List all business profiles |
| `GET` | `/api/v1/business-profiles/{profile_id}` | Get business profile details |
| `PUT` | `/api/v1/business-profiles/{profile_id}` | Update business profile details |

### Query Filter Parameters (`GET /api/v1/schemes`)

- `state` (string): Filter by state name (e.g., `Rajasthan`, `Maharashtra`, `All India`)
- `sector` (string): Filter by sector (e.g., `Manufacturing`, `Micro Enterprise`, `Artisan Enterprise`)
- `scheme_type` (string): Filter by scheme type (e.g., `loan`, `Credit`, `concessional loan`)
- `category` (string): Filter by category (e.g., `Direct Financing`, `NSFDC Financing`)
- `target_group` (string): Target group (e.g., `Scheduled Caste entrepreneurs`, `Micro entrepreneurs`)
- `business_type` (string): Business activity filter
- `target_gender` (string): Gender target (e.g., `Female`, `All`)
- `rural_only` (boolean): `true` or `false`
- `include_all_india` (boolean, default: `true`): When filtering by a specific state, also includes nationwide Central schemes
- `skip` (integer, default: `0`): Pagination offset
- `limit` (integer, default: `50`): Maximum records to return (up to 100)

---

## 7. Running Tests

Execute the automated test suite with pytest:

```bash
pytest tests/ -v
```

The test suite validates:
1. Root endpoint (`GET /`)
2. Health check (`GET /health`)
3. Versioned health check (`GET /api/v1/health`)
4. Direct database connectivity & scheme count validation (verifying 12 schemes)
5. Scheme listing (`GET /api/v1/schemes`)
6. Scheme detail by ID (`GET /api/v1/schemes/1`)
7. 404 response for nonexistent scheme
8. State filtering (nationwide vs. strict state)
9. Sector filtering (primary sector & business activity matching)
10. Multi-filter combinations
11. Backwards compatibility wrapper routes
12. Deterministic rule-based eligibility evaluation engine
13. User creation with Argon2 password hashing
14. Duplicate email validation (400 Bad Request)
15. User retrieval and listing
16. User update
17. Business profile creation for user
18. Duplicate UDYAM number validation (400 Bad Request)
19. Business profile listing for user
20. Single business profile retrieval
21. Business profile updates
22. 404 handling for nonexistent user and profile

---

## 8. Production Code Quality & Judge Readiness (SIH26091)

This project strictly enforces **enterprise-level code quality standards**:
- **Zero Hard-coded Values**: All API URLs, timeouts, secret keys, theme options, and model identifiers are driven strictly from environment variables (`.env.example`) and centralized constants (`frontend/src/config/constants.ts` & `app/core/config.py`).
- **Containerized Stack**: Single-command startup with Docker Compose for PostgreSQL, Redis, FastAPI Backend, and Next.js Frontend.
- **Automated CI/CD**: Full GitHub Actions test and build verification workflow in `.github/workflows/deploy.yml`.

### Docker Startup Command

```bash
docker-compose up -d --build
```

- **Next.js Frontend**: http://localhost:3000
- **FastAPI Core Engine**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
# unnat33
