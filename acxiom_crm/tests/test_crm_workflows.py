import unittest
from datetime import date, timedelta, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from acxiom_crm.backend.database import Base
from acxiom_crm.backend.models import (
    User, RoleEnum, Customer, Lead, LeadStatusEnum,
    Opportunity, OpportunityStageEnum, OpportunityStatusEnum,
    FollowUp, FollowUpStatusEnum, FollowUpTypeEnum, RelatedTypeEnum,
    AuditLog, AuditActionEnum
)
from acxiom_crm.backend.schemas.customer import CustomerCreate
from acxiom_crm.backend.schemas.lead import LeadCreate, LeadConvertRequest
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate
from acxiom_crm.backend.schemas.followup import FollowUpCreate
from acxiom_crm.backend.services.customer_service import create_customer, get_customers
from acxiom_crm.backend.services.lead_service import create_lead, convert_lead, get_leads
from acxiom_crm.backend.services.opportunity_service import create_opportunity, update_opportunity
from acxiom_crm.backend.services.followup_service import create_followup, complete_followup
from acxiom_crm.backend.security.password import hash_password

class TestCRMWorkflows(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        self.sales_user = User(
            name="John Sales",
            email="sales@test.com",
            password_hash=hash_password("Sales@12345"),
            role=RoleEnum.SALES_EXECUTIVE,
            is_active=True
        )
        self.admin_user = User(
            name="Admin User",
            email="admin@test.com",
            password_hash=hash_password("Admin@12345"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        self.db.add_all([self.sales_user, self.admin_user])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_customer_uniqueness_and_creation(self):
        # Create valid customer
        cust_in = CustomerCreate(
            customer_name="Acme Corporation",
            email="contact@acme.com",
            phone="9876543210",
            company_name="Acme Corp",
            city="Seattle",
            state="WA"
        )
        cust = create_customer(self.db, cust_in, self.sales_user)
        self.assertEqual(cust.customer_name, "Acme Corporation")
        self.assertTrue(cust.customer_code.startswith("CUST-"))

        # Duplicate email should fail
        with self.assertRaises(ValueError) as ctx:
            create_customer(self.db, cust_in, self.sales_user)
        self.assertIn("already exists", str(ctx.exception))

        # Duplicate phone should fail
        cust_in2 = CustomerCreate(
            customer_name="Acme Subsidiary",
            email="other@acme.com",
            phone="9876543210",  # Same phone
        )
        with self.assertRaises(ValueError) as ctx:
            create_customer(self.db, cust_in2, self.sales_user)
        self.assertIn("already exists", str(ctx.exception))

    def test_lead_to_customer_and_opportunity_conversion_workflow(self):
        # 1. Create a Lead
        lead_in = LeadCreate(
            lead_name="Sophia Martinez",
            email="sophia@stellar.io",
            phone="9876543230",
            company_name="Stellar Technologies",
            source="Website",
            expected_value=75000.0,
            priority="High"
        )
        lead = create_lead(self.db, lead_in, self.sales_user)
        self.assertEqual(lead.status, LeadStatusEnum.NEW)

        # 2. Convert Lead to Customer + Opportunity
        convert_req = LeadConvertRequest(
            create_opportunity=True,
            opportunity_name="Stellar Enterprise Tier",
            opportunity_amount=75000.0,
            expected_close_date=date.today() + timedelta(days=20)
        )
        customer, opp = convert_lead(self.db, lead.lead_id, convert_req, self.sales_user)

        # Verifications
        self.assertIsNotNone(customer)
        self.assertEqual(customer.email, "sophia@stellar.io")
        self.assertEqual(customer.status, "Lead_Converted")
        self.assertIsNotNone(opp)
        self.assertEqual(opp.amount, 75000.0)
        self.assertEqual(opp.customer_id, customer.customer_id)

        # Lead status updated
        refreshed_lead = self.db.query(Lead).filter(Lead.lead_id == lead.lead_id).first()
        self.assertEqual(refreshed_lead.status, LeadStatusEnum.CONVERTED)
        self.assertEqual(refreshed_lead.converted_customer_id, customer.customer_id)

        # Attempting to convert again fails
        with self.assertRaises(ValueError) as ctx:
            convert_lead(self.db, lead.lead_id, convert_req, self.sales_user)
        self.assertIn("already been converted", str(ctx.exception))

        # Check conversion audit log
        audit = self.db.query(AuditLog).filter(
            AuditLog.action == AuditActionEnum.CONVERT,
            AuditLog.record_id == str(lead.lead_id)
        ).first()
        self.assertIsNotNone(audit)

    def test_followup_workflow(self):
        # Create customer
        cust_in = CustomerCreate(
            customer_name="Beta Labs",
            email="beta@labs.com",
            phone="9876543240"
        )
        cust = create_customer(self.db, cust_in, self.sales_user)

        # Schedule follow-up
        fol_in = FollowUpCreate(
            related_type=RelatedTypeEnum.CUSTOMER,
            related_id=cust.customer_id,
            followup_date=datetime.utcnow() + timedelta(days=2),
            followup_type=FollowUpTypeEnum.CALL,
            subject="Pricing Discussion",
            status=FollowUpStatusEnum.PLANNED,
            assigned_to=self.sales_user.user_id
        )
        followup = create_followup(self.db, fol_in, self.sales_user)
        self.assertEqual(followup.status, FollowUpStatusEnum.PLANNED)

        # Complete follow-up
        completed = complete_followup(self.db, followup.followup_id, "Customer agreed to proposal.", self.sales_user)
        self.assertEqual(completed.status, FollowUpStatusEnum.COMPLETED)
        self.assertIsNotNone(completed.completed_at)

if __name__ == "__main__":
    unittest.main()
