import streamlit as st
from acxiom_crm.backend.models.user import User

def render_api_docs_view(current_user: User):
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">🔌 REST API & Integration Gateway</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Enterprise REST endpoints with JWT Bearer Authentication, RBAC, and Pydantic DTOs</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        AcxiomCRM features a **FastAPI backend** running alongside the frontend.
        All CRM resources (Customers, Leads, Opportunities, Follow-Ups, Reports, Audit Logs) are exposed via REST conventions with strict validation and security.

        - **Swagger Interactive UI:** `http://localhost:8000/docs`
        - **ReDoc Documentation:** `http://localhost:8000/redoc`
        - **OpenAPI JSON Schema:** `http://localhost:8000/openapi.json`
        """
    )

    st.markdown("---")
    st.markdown("##### 🔑 Authenticating with the REST API")

    st.code(
        """
# 1. Obtain JWT Bearer Token
curl -X POST "http://localhost:8000/api/auth/login" \\
     -H "Content-Type: application/json" \\
     -d '{"email": "admin@acxiomcrm.com", "password": "Admin@12345"}'

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIs...",
#   "token_type": "bearer",
#   "user": { ... }
# }

# 2. Call Protected Customer Endpoints
curl -X GET "http://localhost:8000/api/customers" \\
     -H "Authorization: Bearer <YOUR_TOKEN>"

# 3. Create a Customer via REST
curl -X POST "http://localhost:8000/api/customers" \\
     -H "Authorization: Bearer <YOUR_TOKEN>" \\
     -H "Content-Type: application/json" \\
     -d '{
       "customer_name": "Acme Innovations",
       "email": "contact@acmeinnovations.com",
       "phone": "9876543290",
       "company_name": "Acme Corp",
       "city": "Austin",
       "state": "TX",
       "status": "Active"
     }'
        """,
        language="bash"
    )

    st.markdown("##### 📡 Supported API Endpoints & Status Codes")
    api_table = [
        {"Method": "POST", "Endpoint": "/api/auth/login", "Description": "Authenticate credentials & receive JWT token", "Auth": "Public", "Status": "200, 401, 403"},
        {"Method": "GET", "Endpoint": "/api/customers", "Description": "List / search customers with role scoping", "Auth": "Bearer", "Status": "200, 401"},
        {"Method": "POST", "Endpoint": "/api/customers", "Description": "Create customer with unique email/phone checks", "Auth": "Bearer", "Status": "201, 400, 409"},
        {"Method": "GET", "Endpoint": "/api/customers/{id}", "Description": "Get customer by ID", "Auth": "Bearer", "Status": "200, 404"},
        {"Method": "PUT", "Endpoint": "/api/customers/{id}", "Description": "Update customer details", "Auth": "Bearer", "Status": "200, 400, 404, 409"},
        {"Method": "DELETE", "Endpoint": "/api/customers/{id}", "Description": "Delete customer (Admin/Manager)", "Auth": "Bearer (Admin/Mgr)", "Status": "200, 403, 404"},
        {"Method": "GET", "Endpoint": "/api/leads", "Description": "List / filter prospective leads", "Auth": "Bearer", "Status": "200, 401"},
        {"Method": "POST", "Endpoint": "/api/leads", "Description": "Capture new lead with validation", "Auth": "Bearer", "Status": "201, 400"},
        {"Method": "POST", "Endpoint": "/api/leads/{id}/convert", "Description": "Lead-to-Customer conversion workflow", "Auth": "Bearer", "Status": "200, 400"},
        {"Method": "GET", "Endpoint": "/api/opportunities", "Description": "List pipeline opportunities", "Auth": "Bearer", "Status": "200, 401"},
        {"Method": "POST", "Endpoint": "/api/opportunities", "Description": "Create deal (amount > 0, close date >= today)", "Auth": "Bearer", "Status": "201, 400"},
        {"Method": "GET", "Endpoint": "/api/followups", "Description": "List upcoming / overdue follow-ups", "Auth": "Bearer", "Status": "200, 401"},
        {"Method": "POST", "Endpoint": "/api/followups", "Description": "Schedule follow-up (date >= today)", "Auth": "Bearer", "Status": "201, 400"},
        {"Method": "GET", "Endpoint": "/api/reports/pipeline", "Description": "Retrieve pipeline analytics JSON", "Auth": "Bearer", "Status": "200, 401"},
        {"Method": "GET", "Endpoint": "/api/audit-logs", "Description": "Regulatory audit trail (Admin/Manager)", "Auth": "Bearer (Admin/Mgr)", "Status": "200, 403"},
    ]
    st.table(api_table)
