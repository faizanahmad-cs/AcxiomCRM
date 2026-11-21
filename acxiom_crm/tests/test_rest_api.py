import unittest
from datetime import date, timedelta
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request
from acxiom_crm.backend.database import Base
from acxiom_crm.backend.models import User, RoleEnum
from acxiom_crm.backend.security.password import hash_password
from acxiom_crm.backend.schemas.user import UserLoginRequest
from acxiom_crm.backend.schemas.customer import CustomerCreate
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate
from acxiom_crm.backend.api.auth_routes import login
from acxiom_crm.backend.api.customer_routes import list_customers, create_new_customer, get_customer, remove_customer
from acxiom_crm.backend.api.opportunity_routes import create_new_opportunity

class DummyRequest:
    client = type("Client", (), {"host": "127.0.0.1"})()
    headers = {}

class TestRestApiDirect(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Admin user
        self.admin = User(
            name="Admin User",
            email="admin@test.com",
            password_hash=hash_password("Admin@12345"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        # Sales user
        self.sales = User(
            name="Sales User",
            email="sales@test.com",
            password_hash=hash_password("Sales@12345"),
            role=RoleEnum.SALES_EXECUTIVE,
            is_active=True
        )
        self.db.add_all([self.admin, self.sales])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_auth_login_api_success(self):
        req = DummyRequest()
        body = UserLoginRequest(email="admin@test.com", password="Admin@12345")
        res = login(login_data=body, request=req, db=self.db)
        self.assertTrue(hasattr(res, "access_token"))
        self.assertEqual(res.user.email, "admin@test.com")

    def test_auth_login_api_failure(self):
        req = DummyRequest()
        body = UserLoginRequest(email="admin@test.com", password="WrongPassword@123")
        with self.assertRaises(HTTPException) as ctx:
            login(login_data=body, request=req, db=self.db)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_customer_api_crud_and_status_codes(self):
        req = DummyRequest()
        cust_in = CustomerCreate(
            customer_name="Delta Global",
            email="delta@global.com",
            phone="9876543210"
        )
        # 1. Create (201 Created)
        created = create_new_customer(customer_in=cust_in, request=req, current_user=self.admin, db=self.db)
        self.assertEqual(created.customer_name, "Delta Global")
        self.assertEqual(created.customer_id, 1)

        # 2. Duplicate Create -> 409 Conflict
        with self.assertRaises(HTTPException) as ctx:
            create_new_customer(customer_in=cust_in, request=req, current_user=self.admin, db=self.db)
        self.assertEqual(ctx.exception.status_code, 409)

        # 3. Get existing -> 200 OK
        retrieved = get_customer(customer_id=1, current_user=self.admin, db=self.db)
        self.assertEqual(retrieved.email, "delta@global.com")

        # 4. Get non-existent -> 404 Not Found
        with self.assertRaises(HTTPException) as ctx:
            get_customer(customer_id=999, current_user=self.admin, db=self.db)
        self.assertEqual(ctx.exception.status_code, 404)

        # 5. Delete -> 200 OK
        del_res = remove_customer(customer_id=1, request=req, current_user=self.admin, db=self.db)
        self.assertIn("successfully deleted", del_res["message"])

    def test_opportunity_business_validation_api(self):
        req = DummyRequest()
        # Customer first
        cust = create_new_customer(
            customer_in=CustomerCreate(customer_name="Omega Inc", email="omega@inc.com", phone="9876543299"),
            request=req,
            current_user=self.admin,
            db=self.db
        )
        # Invalid Opportunity Amount <= 0 -> 400 Bad Request
        with self.assertRaises(HTTPException) as ctx:
            opp_in = OpportunityCreate.model_construct(
                opportunity_name="Invalid Deal",
                customer_id=cust.customer_id,
                amount=0.0,
                stage="Qualification",
                probability=20.0,
                expected_close_date=date.today() + timedelta(days=10),
                status="Open"
            )
            create_new_opportunity(opp_in=opp_in, request=req, current_user=self.admin, db=self.db)
        self.assertEqual(ctx.exception.status_code, 400)

if __name__ == "__main__":
    unittest.main()
