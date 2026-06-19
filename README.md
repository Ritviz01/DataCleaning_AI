# 🧹 DataClean AI — Universal Data Cleaning Platform

<div align="center">

![Status](https://img.shields.io/badge/status-in%20development-yellow?style=for-the-badge)
![Phase](https://img.shields.io/badge/phase-1%20of%204-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)

**An AI-powered platform that automatically analyzes, understands, detects, explains, and cleans data quality issues in virtually any dataset — with minimal human intervention.**

[Architecture](#architecture) · [Tech Stack](#tech-stack) · [Getting Started](#getting-started) · [Roadmap](#roadmap) · [Contributing](#contributing)

</div>

> ⚠️ **This project is actively under development.** Core ingestion and profiling are functional. ML detection and LLM integration are in progress. APIs and interfaces may change without notice.

---

## What is DataClean AI?

Most data cleaning tools rely on hardcoded rules that break the moment your schema changes. DataClean AI is different — it combines statistical analysis, machine learning, anomaly detection, and LLM reasoning to understand *any* dataset from *any* domain and automatically fix what's wrong.

Upload a CSV from a hospital, a JSON export from an e-commerce platform, or a Parquet file from an IoT sensor network — the platform figures out what the data means and what's broken, without you writing a single rule.

### Supported domains
Finance · Healthcare · E-commerce · Education · Manufacturing · HR · Marketing · IoT · Survey Data · Government Data

### Supported formats
CSV · Excel (xlsx/xls) · JSON · Parquet · SQL export · REST API · S3 / GCS

---

## What it does

### A. Understands your dataset automatically
- Detects column types (numerical, categorical, text, timestamp, boolean, mixed)
- Infers semantic meaning — distinguishes emails from URLs, ages from IDs, currencies from scores
- Tags columns with domain-specific meaning: `invoice_id`, `patient_age`, `transaction_amount`, etc.

### B. Profiles data quality
- Missing value analysis with pattern detection (random vs. systematic gaps)
- Duplicate and near-duplicate analysis
- Outlier detection with statistical justification
- Distribution analysis, correlation matrix, cardinality stats
- Invalid format detection (emails, phones, dates, URLs)

### C. Detects issues intelligently

| Issue Type | Detection Method |
|---|---|
| Missing values | Rule-based |
| Exact duplicates | Hash-based rule |
| Near-duplicates | MinHash LSH + RapidFuzz |
| Statistical outliers | IQR + Isolation Forest + LOF ensemble |
| Invalid email / phone / date | Regex rules |
| Unit inconsistencies | LLM reasoning |
| Category inconsistencies | Fuzzy matching + LLM |
| Schema anomalies | One-class SVM |
| Typographical errors | Edit distance + LLM |
| Data drift | KL divergence + MMD |

### D. Recommends and explains fixes
Every detected issue comes with a confidence score, a plain-English explanation, and multiple cleaning strategies ranked by estimated impact.

### E. Cleans automatically (or with your approval)
- Statistical imputation (mean / median / mode)
- ML-based imputation (MICE with LightGBM)
- LLM-assisted normalisation for categories and units
- Fuzzy deduplication with configurable threshold
- Full human-in-the-loop review mode

### F. Reports everything
- Before vs. after quality score comparison
- Data health score breakdown (completeness, uniqueness, validity, consistency, accuracy)
- Downloadable audit trail and cleaning log
- Explainability report — every fix is justified

---

## Architecture

The platform is built in seven layers, each independently deployable and testable:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — Data Ingestion & Connectors                      │
│  CSV · Excel · JSON · Parquet · SQL · S3 · REST API         │
├─────────────────────────────────────────────────────────────┤
│  Layer 2 — Schema Inference & Data Profiling                │
│  Type detection · Semantic tagging · Distributions          │
├─────────────────────────────────────────────────────────────┤
│  Layer 3 — AI/ML Quality Detection Engine                   │
│  Statistical rules · Anomaly detection · LLM reasoning      │
├─────────────────────────────────────────────────────────────┤
│  Layer 4 — Recommendation & Confidence Engine               │
│  Issue ranking · Confidence scores · Strategy suggestions   │
├─────────────────────────────────────────────────────────────┤
│  Layer 5 — Cleaning Execution Engine                        │
│  Imputation · Dedup · Normalisation · Audit log             │
├─────────────────────────────────────────────────────────────┤
│  Layer 6 — Reports & Explainability                         │
│  Before/after · Quality score · PDF export                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 7 — Infrastructure & Platform Services               │
│  FastAPI · Celery · PostgreSQL · Redis · S3 · Kubernetes    │
└─────────────────────────────────────────────────────────────┘
```

### Design principles

**Rule / ML / LLM tripartite routing** — Every problem is routed to the cheapest solver that achieves sufficient confidence. Rules handle the bulk. ML handles ambiguity at scale. LLMs handle semantic reasoning that neither rules nor ML can resolve.

**Lazy-deep profiling** — Surface statistics run synchronously (< 3 seconds). Expensive operations (correlations, embeddings, LLM tagging) run async so users see first results immediately.

**Immutable audit trail** — The original dataset is never mutated. All cleaning actions are event-sourced and reversible.

---

## Tech Stack

### Backend
- **FastAPI** — Async API framework with auto-generated OpenAPI docs
- **Celery + Redis** — Async task queue for profiling and cleaning jobs
- **Polars + DuckDB + PyArrow** — Columnar data processing (10–100× faster than Pandas)
- **scikit-learn + PyOD** — Anomaly detection (Isolation Forest, LOF, one-class SVM)
- **sentence-transformers** — Semantic column embeddings (`all-MiniLM-L6-v2`)
- **RapidFuzz + datasketch** — Near-duplicate detection via MinHash LSH
- **LangChain + Anthropic SDK** — LLM orchestration with cost-aware routing
- **Great Expectations** — Declarative data validation
- **PostgreSQL 16 + pgvector** — Primary database with vector similarity search
- **SQLAlchemy 2 + Alembic** — ORM and migrations

### Frontend
- **React 18 + TypeScript** — Component-driven UI
- **Zustand + TanStack Query** — State management
- **shadcn/ui + Tailwind CSS** — UI components
- **Recharts + D3** — Quality charts and profiling visualisations
- **TanStack Table v8** — Virtual scrolling data grids

### Infrastructure
- **Docker + Kubernetes (EKS)** — Containerised, auto-scaled deployment
- **KEDA** — Event-driven worker autoscaling based on queue depth
- **Prometheus + Grafana** — Metrics and dashboards
- **Terraform** — Infrastructure as code
- **GitHub Actions** — CI/CD pipelines

---

## Project Structure

```
dataclean-platform/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, type-check, test on PR
│       ├── cd-staging.yml          # Deploy to staging on merge to main
│       └── cd-production.yml       # Deploy to prod on release tag
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app factory
│   │   ├── config.py               # Pydantic settings
│   │   ├── api/v1/                 # API route handlers
│   │   │   ├── datasets.py
│   │   │   ├── issues.py
│   │   │   ├── cleaning.py
│   │   │   ├── reports.py
│   │   │   └── query.py
│   │   ├── core/
│   │   │   ├── ingestion/          # Format detection, parsers, normaliser
│   │   │   ├── profiling/          # Fast profiler, deep profiler, semantic tagger
│   │   │   ├── detection/          # Rule, ML, LLM detectors + anomaly + dedup
│   │   │   ├── recommendation/     # Engine, scorer, strategies
│   │   │   ├── cleaning/           # Executor, imputers, deduplicator, LLM cleaner
│   │   │   ├── reporting/          # Quality scorer, PDF generator, diff engine
│   │   │   └── llm/                # Router, prompts, cache, API clients
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── tasks/                  # Celery task definitions
│   │   └── db/                     # Session, Alembic migrations
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/               # Sample datasets per domain
│
├── frontend/
│   └── src/
│       ├── pages/                  # Upload, Profile, Issues, Clean, Report
│       ├── components/             # DataGrid, IssueCard, QualityGauge, CleaningDiff
│       ├── hooks/
│       ├── stores/                 # Zustand
│       └── api/                    # TanStack Query + axios
│
├── infra/
│   ├── terraform/                  # EKS, RDS, ElastiCache, S3, CloudFront
│   ├── kubernetes/                 # Deployments, services, ingress, KEDA
│   └── docker-compose.yml          # Full local dev stack
│
├── data/
│   ├── test_datasets/              # One representative dataset per domain
│   └── benchmarks/                 # Precision/recall benchmarks per issue type
│
└── docs/
    ├── architecture.md             # ADRs and design decisions
    ├── api.md                      # Full OpenAPI reference
    └── runbook.md                  # Incident response and ops guide
```

---

## Getting Started

> **Prerequisites:** Python 3.11+, Node.js 20+, Docker, Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/your-org/dataclean-platform.git
cd dataclean-platform
```

### 2. Start the full local stack

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, the FastAPI backend, Celery worker, and the React frontend.

### 3. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 4. Access the platform

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Celery Flower | http://localhost:5555 |

### 5. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dataclean

# Redis
REDIS_URL=redis://localhost:6379/0

# Object Storage
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=dataclean-uploads

# LLM (optional for Phase 1)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key          # fallback

# Security
SECRET_KEY=your_secret_key_here
```

### Local development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Worker (separate terminal)
celery -A app.tasks worker --loglevel=info

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

---

## API Overview

The REST API is documented via Swagger at `/docs`. Key endpoints:

```
POST   /api/v1/datasets                    Upload a dataset
GET    /api/v1/datasets/{id}               Get metadata and status
GET    /api/v1/datasets/{id}/profile       Full profiling report
GET    /api/v1/datasets/{id}/issues        List detected quality issues
GET    /api/v1/datasets/{id}/recommendations  Cleaning suggestions
POST   /api/v1/datasets/{id}/clean         Execute cleaning plan
GET    /api/v1/datasets/{id}/clean/{session}/status  Live progress (SSE)
GET    /api/v1/datasets/{id}/export        Download cleaned dataset
GET    /api/v1/datasets/{id}/report        Download quality report (PDF/JSON)
POST   /api/v1/issues/{id}/feedback        Approve / reject / modify
POST   /api/v1/datasets/{id}/query         Natural language query
```

---

## Roadmap

### Phase 1 — Foundation `[IN PROGRESS]`
> Target: Months 1–3

- [x] Project structure and Docker Compose setup
- [x] Format detection (CSV, Excel, JSON, Parquet)
- [x] Polars-based data parsing and normalisation
- [x] Fast profiler (types, nulls, cardinality, basic stats)
- [ ] Rule-based detectors (missing values, duplicates, email/phone/date)
- [ ] Simple imputation strategies (mean, median, mode)
- [ ] Basic REST API (FastAPI)
- [ ] PostgreSQL schema + S3 integration
- [ ] Basic React UI (upload + profile view)

**Exit criteria:** Upload a CSV, see a quality report, download a cleaned version.

---

### Phase 2 — ML Detection `[PLANNED]`
> Target: Months 4–6

- [ ] Isolation Forest + LOF anomaly detection
- [ ] MinHash LSH + RapidFuzz near-duplicate detection
- [ ] MICE imputation with LightGBM estimator
- [ ] Embedding-based semantic column tagger
- [ ] Confidence scoring system
- [ ] Recommendation engine with impact estimates
- [ ] Celery async task pipeline
- [ ] Quality score formula (DAMA-DMBOK dimensions)
- [ ] Basic PDF report generation

**Exit criteria:** 80%+ precision on 10 standard issue types across benchmark datasets.

---

### Phase 3 — LLM Integration `[PLANNED]`
> Target: Months 7–9

- [ ] LLM semantic column tagging (Claude Haiku, cached)
- [ ] Unit inconsistency detection
- [ ] Category normalisation (LLM + fuzzy)
- [ ] Natural language query interface
- [ ] Haiku → Sonnet cost-aware escalation router
- [ ] Prompt caching layer (Redis, 7-day TTL)
- [ ] Human-in-the-loop review UI
- [ ] Before/after comparison view
- [ ] Explainability report

**Exit criteria:** Works on 5+ domain types without domain-specific configuration.

---

### Phase 4 — Production Hardening `[PLANNED]`
> Target: Months 10–12

- [ ] Kubernetes deployment on EKS with KEDA autoscaling
- [ ] Multi-format export (Parquet, JSON, Excel, CSV)
- [ ] Full event-sourced audit trail and rollback
- [ ] RBAC + OAuth2 (Auth0 / Cognito)
- [ ] Prometheus + Grafana dashboards
- [ ] PII detection via Microsoft Presidio
- [ ] Large file support (DuckDB streaming, >2 GB)
- [ ] Multi-tenant SaaS billing integration
- [ ] API rate limiting and usage quotas

**Exit criteria:** Production SaaS, SOC2-ready audit trail, 99.9% uptime SLA.

---

## Contributing

This project is in active development. Contributions, bug reports, and design feedback are welcome.

### How to contribute

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Write tests** for any new detection or cleaning logic
4. **Run the test suite**: `pytest backend/tests/ -v`
5. **Open a PR** with a clear description of what was changed and why

### Development priorities (Phase 1)

If you want to contribute right now, these are the highest-priority open items:

- Rule-based detectors for email, phone, and date formats
- Mode imputation for categorical columns
- Upload progress indicator in the frontend
- Test fixtures for healthcare and finance domains

### Code style

```bash
# Backend
ruff check .
mypy app/
pytest

# Frontend
npm run lint
npm run type-check
```

---

## Known Limitations

- **Large files (> 2 GB):** DuckDB streaming is planned for Phase 4 but not yet implemented. Files above 500 MB may be slow.
- **LLM features:** Semantic tagging and category normalisation require an Anthropic or OpenAI API key and are gated behind Phase 3.
- **Near-duplicate detection:** Conservative default threshold (0.90). May miss some near-duplicates in highly abbreviated datasets.
- **Time-series data:** Forward-fill imputation is planned but not yet implemented.
- **Non-Latin character sets:** Fuzzy matching for CJK, Arabic, and Devanagari scripts is untested.

---

## Security

- Never commit API keys or credentials — use `.env` files (already in `.gitignore`)
- PII detection runs locally via Microsoft Presidio before any LLM call — raw rows never leave your infrastructure
- All uploaded files are encrypted at rest (AES-256 via S3 SSE-KMS)
- Report a vulnerability privately via GitHub Security Advisories

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
<sub>Built with Python · FastAPI · Polars · scikit-learn · React · PostgreSQL</sub><br>
<sub>⚠️ Work in progress — star the repo to follow development</sub>
</div>
