# LMPC Compliance Scanner (SIH26034)

An automated compliance scanning and verification system for packaged commodity labels under India's **Legal Metrology (Packaged Commodities) Rules, 2011**.

Developed for **Smart India Hackathon (Problem Statement: SIH26034)**.

---

## Tech Stack

- **Backend**: Python 3.10+ / FastAPI (Async REST API with OpenAPI documentation)
- **Database**: SQLite (local development zero-config) / PostgreSQL (production-ready via SQLAlchemy)
- **OCR Engine**: EasyOCR (PyTorch-powered text + bounding box extraction with fallback support)
- **Rule Engine**: Decoupled JSON-driven compliance rules (`backend/app/rules/compliance_rules.json`)
- **PDF Reports**: ReportLab
- **Frontend**: React 19 + Vite + Tailwind CSS + Lucide Icons + Recharts

---

## Directory Structure

```text
SIH26034/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app with CORS & health endpoint
│   │   ├── models/              # Database models via SQLAlchemy
│   │   │   ├── database.py      # SQLite / PostgreSQL engine & session
│   │   │   └── scan.py          # ScanRecord model
│   │   ├── routers/             # API route controllers
│   │   │   ├── upload.py        # Image upload & storage endpoint
│   │   │   ├── scan.py          # OCR & inspection triggers
│   │   │   ├── reports.py       # PDF report generation & export
│   │   │   └── dashboard.py     # Analytics & violation statistics
│   │   ├── services/            # Business logic services
│   │   │   ├── ocr_service.py   # OCR extraction service
│   │   │   ├── rule_engine.py   # JSON-driven validation engine
│   │   │   └── report_service.py# PDF report generation service
│   │   └── rules/
│   │       └── compliance_rules.json # Editable LMPC rule definitions
│   ├── tests/                   # Automated pytest suite
│   │   └── test_health.py
│   ├── requirements.txt         # Backend Python dependencies
│   └── venv/                    # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── api/                 # API client utilities (backend health & endpoints)
│   │   │   └── client.js
│   │   ├── components/          # Reusable UI components
│   │   │   └── HealthStatus.jsx
│   │   ├── pages/               # Application views
│   │   │   └── HomePage.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css            # Tailwind CSS styling
│   ├── package.json
│   └── vite.config.js
├── uploads/                     # Local storage for label images
├── README.md
└── .gitignore
```

---

## Getting Started Locally

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.12 / 3.14)
- **Node.js 18+** & **npm**
- **Git**

---

### 2. Backend Setup

1. Open a terminal in the root project directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI development server:
   - From the `backend` directory:
     ```bash
     uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
     ```

5. Verify the backend:
   - **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - **Alternative Docs (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

6. Run backend automated tests:
   ```bash
   pytest tests
   ```

---

### 3. Frontend Setup

1. Open a second terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser.
   - The homepage immediately polls and displays live health connectivity with the FastAPI backend.

---

## Incremental Development Roadmap

1. **Phase 0: Project Skeleton & End-to-End Health Connectivity** *(Completed)*
2. **Phase 1: Image Upload & Storage** (Validation, SHA-256 deduplication, SQLite persistence)
3. **Phase 2: OCR Extraction Engine** (EasyOCR text + polygon/bbox coordinate mapping)
4. **Phase 3: Field Classifier** (Mapping extracted text chunks to 8 mandatory LMPC declarations)
5. **Phase 4: Decoupled Rule Engine** (Config-driven validator via `compliance_rules.json`)
6. **Phase 5: Report Generator** (PDF inspection reports with ReportLab + JSON export)
7. **Phase 6: Repository & Search** (Scan history, filters, audit trail)
8. **Phase 7: Dashboard & Analytics** (Violation charts, compliance metrics with Recharts)
