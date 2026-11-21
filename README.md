# AcxiomCRM — Enterprise Role-Based CRM System

*AcxiomCRM* is a production-quality, full-stack customer relationship management web application built strictly according to the enterprise specification. It manages the complete customer–sales lifecycle: **Lead → Follow-up → Opportunity → Customer**, with role-based access control, account lockout protection, append-only regulatory audit logging, interactive dashboards, and REST APIs.

---

## 🌟 Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend / UI** | **Streamlit** | Responsive, dark-themed SaaS dashboard, KPI cards, forms, tables, filters |
| **Backend API** | **FastAPI** | High-performance REST APIs, Pydantic DTOs, OpenAPI Swagger at `/docs` |
| **Database** | **SQLite + SQLAlchemy ORM** | Clean relational schema, easily switchable to PostgreSQL via env var |
| **Authentication** | **bcrypt + Python-Jose (JWT)** | Salted password hashing, complexity validator, account lockout, JWT tokens |
| **Visualizations** | **Plotly Express & Graph Objects** | Donut charts, pipeline bar funnels, monthly revenue trends, source charts |
| **Validation** | **Pydantic v2 + Custom Validators** | Multi-layer client-side & server-side business rules enforcement |
| **Audit & Security**| **Append-Only Audit Engine** | Immutable logging of authentication, CRUD, stage changes, lockouts |

---

## 👥 Role-Based Access Control (RBAC)

AcxiomCRM strictly enforces authorization on both the **presentation layer** and the **server/service/API layer**:

1. **Admin** (`admin@acxiomcrm.com` / `Admin@12345`)
   - Complete system access: User & Role management, account unlock, password reset, append-only security audit trail, all CRM data, and all executive reports.
2. **Manager** (`manager@acxiomcrm.com` / `Manager@12345`)
   - Team-wide visibility: Full sales pipeline, team leads, customer directory, follow-up SLA compliance, management reports, and read-only audit log.
3. **Sales Executive** (`sales1@acxiomcrm.com` / `Sales@12345` or `sales2@acxiomcrm.com` / `Sales@12345`)
   - Least privilege / scoped access: Can only view, create, and manage records **assigned to or created by them**. Automatically scoped across Dashboard, Customers, Leads, Opportunities, and Follow-Ups.

---

## 🔒 Security & Validation Specifications

### 1. Password Policy & Complexity
- Minimum **8 characters**
- At least 1 uppercase letter (`A-Z`)
- At least 1 lowercase letter (`a-z`)
- At least 1 number (`0-9`)
- At least 1 special character (`!@#$%^&*` etc.)
- Salted hashing with `bcrypt` (12 rounds) — plain text passwords are never stored or logged.

### 2. Account Lockout Protection
- Tracks failed login attempts per account.
- After **5 consecutive failed attempts**, the account is **temporarily locked for 15 minutes**.
- Audit log records `Failed_Login` with remaining attempts counter and triggers `Lockout` event.
- Administrators can review lockout status and **unlock accounts with 1 click**.
- Successful login automatically resets the failure counter to 0.

### 3. Strict Business Validation Rules
- **Opportunity Amount**: Must be greater than 0 (`amount > 0`). Rejects `0` or negative values with: `"Opportunity Amount must be greater than 0."`
- **Win Probability**: Must be between 0 and 100 inclusive (`0 <= probability <= 100`). Rejects `101` with: `"Probability must be between 0 and 100."`
- **Expected Close Date**: Cannot be in the past for active opportunities (`expected_close_date >= today`). Rejects past dates with: `"Expected Close Date cannot be in the past."`
- **Follow-Up Scheduling**: Follow-up date cannot be earlier than today for planned activities. Rejects yesterday with: `"Follow-up date cannot be earlier than today."`
- **Email Uniqueness & Format**: Valid email regex; rejects duplicate customer emails.
- **Phone Uniqueness & Format**: Enforces 10–15 digits pattern; rejects duplicate customer phone numbers.
- **Lead Status Transition Guards**: Once a lead is marked `Converted`, it cannot be reverted to `New` or `Contacted`.

### 4. Append-Only Audit Logging
- Logs events for: `Login`, `Failed_Login`, `Logout`, `Create`, `Update`, `Delete`, `Convert`, `Role_Change`, `Lockout`, `Unlock`, `Password_Reset`.
- Captures: `UserId`, `UserEmail`, `Action`, `EntityName`, `RecordId`, `OldValue`, `NewValue`, `Details`, `Timestamp`, `IpAddress`.
- Filterable and exportable to CSV.

---

## 📁 Project Architecture

```
acxiom_crm/
├── backend/
│   ├── api/                     # FastAPI routers & dependencies
│   │   ├── auth_routes.py       # /api/auth/login, register, logout, me
│   │   ├── customer_routes.py   # /api/customers (CRUD)
│   │   ├── lead_routes.py       # /api/leads (CRUD + /convert)
│   │   ├── opportunity_routes.py# /api/opportunities (CRUD)
│   │   ├── followup_routes.py   # /api/followups (CRUD + /complete)
│   │   ├── report_routes.py     # /api/reports/pipeline
│   │   ├── audit_routes.py      # /api/audit-logs
│   │   ├── deps.py              # JWT Bearer & RBAC dependencies
│   │   └── main.py              # FastAPI application entry point
│   ├── models/                  # SQLAlchemy ORM entities
│   │   ├── user.py, customer.py, lead.py, opportunity.py, followup.py, activity.py, audit.py
│   ├── schemas/                 # Pydantic DTOs with business validators
│   ├── security/                # Bcrypt password hashing & JWT tokens
│   ├── services/                # Business logic, workflows & role scoping
│   ├── config.py                # Environment & policy settings
│   ├── database.py              # Database engine & session management
│   └── seed_data.py             # Realistic test database generator
├── frontend/
│   ├── app.py                   # Streamlit main entry point & navigation
│   ├── styles.py                # Modern SaaS CSS & responsive layout
│   ├── state.py                 # Session state & authentication wrapper
│   └── views/                   # Modular Streamlit views
│       ├── login_view.py, dashboard_view.py, customer_view.py, lead_view.py
│       ├── opportunity_view.py, followup_view.py, activity_view.py
│       ├── user_admin_view.py, audit_view.py, reports_view.py, api_docs_view.py
├── tests/                       # Complete automated unit & workflow test suite
│   ├── test_validation.py       # Pydantic & business rule tests
│   ├── test_auth_security.py    # Bcrypt, lockout & RBAC tests
│   ├── test_crm_workflows.py    # Lead -> Convert -> Opportunity -> Customer
│   └── test_rest_api.py         # REST API status codes & DTOs
└── run_crm.py                   # Unified master launcher (FastAPI + Streamlit)
```

---

## 🚀 Getting Started

### 1. Launch the Application
Run both the Streamlit UI and FastAPI backend with a single command:

```bash
python run_crm.py
```

- **Streamlit Web Application**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

# I deployed on Render.
link to open click here: https://acxiomcrm-ptfu.onrender.com

Alternatively:
- Launch only Streamlit: `python run_crm.py --ui-only`
- Launch only FastAPI API: `python run_crm.py --api-only`

---

## 🔑 Pre-Seeded Test Credentials

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@acxiomcrm.com` | `Admin@12345` | Complete system, user admin, audit logs, all records |
| **Manager** | `manager@acxiomcrm.com` | `Manager@12345` | Team pipeline, all leads/opps, reports, audit view |
| **Sales Executive 1** | `sales1@acxiomcrm.com` | `Sales@12345` | Assigned records for Sarah Jenkins |
| **Sales Executive 2** | `sales2@acxiomcrm.com` | `Sales@12345` | Assigned records for David Miller |

*Note: The login page includes 1-click test credential buttons to instantly switch roles.*

---

## 🧪 Running Automated Tests

Run the full automated test suite covering all specifications:

```bash
# 1. Test all business validations (dates, amounts, probabilities, email, phone)
python -m unittest acxiom_crm/tests/test_validation.py

# 2. Test authentication, bcrypt, account lockout & audit logging
python -m unittest acxiom_crm/tests/test_auth_security.py

# 3. Test complete CRM lifecycle (Lead -> Convert -> Customer + Opportunity)
python -m unittest acxiom_crm/tests/test_crm_workflows.py

# 4. Test REST API endpoints & HTTP status codes (200, 201, 400, 401, 403, 404, 409)
python -m unittest acxiom_crm/tests/test_rest_api.py
```

All 18 automated test cases run and pass with 0 errors.

---

# I deployed on Render
link : https://acxiomcrm-ptfu.onrender.com

## 📡 REST API Quickstart

### Authenticate & Obtain JWT Token
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@acxiomcrm.com", "password": "Admin@12345"}'
```

### Fetch Customers (Protected)
```bash
curl -X GET "http://localhost:8000/api/customers" \
     -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Create an Opportunity with Server Validation
```bash
curl -X POST "http://localhost:8000/api/opportunities" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "opportunity_name": "Cloud Data Lake Modernization",
       "customer_id": 1,
       "amount": 95000.0,
       "stage": "Proposal",
       "probability": 60.0,
       "expected_close_date": "2026-12-15"
     }'
```
