from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from acxiom_crm.backend.database import engine, SessionLocal, Base
from acxiom_crm.backend.models import (
    User, RoleEnum, Customer, Lead, LeadStatusEnum,
    Opportunity, OpportunityStageEnum, OpportunityStatusEnum,
    FollowUp, FollowUpStatusEnum, FollowUpTypeEnum, RelatedTypeEnum,
    Activity, ActivityTypeEnum, AuditLog, AuditActionEnum
)
from acxiom_crm.backend.security.password import hash_password

def seed_database():
    """Initializes tables and seeds initial realistic test data."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already contains records. Skipping seed.")
            return

        print("Seeding AcxiomCRM database with initial users and records...")

        # 1. Create Users
        admin_user = User(
            name="Alexander Wright (Admin)",
            email="admin@acxiomcrm.com",
            password_hash=hash_password("Admin@12345"),
            role=RoleEnum.ADMIN,
            is_active=True,
            failed_login_count=0,
            created_at=datetime.utcnow() - timedelta(days=60)
        )

        manager_user = User(
            name="Elena Rostova (Manager)",
            email="manager@acxiomcrm.com",
            password_hash=hash_password("Manager@12345"),
            role=RoleEnum.MANAGER,
            is_active=True,
            failed_login_count=0,
            created_at=datetime.utcnow() - timedelta(days=50)
        )

        sales1_user = User(
            name="Sarah Jenkins",
            email="sales1@acxiomcrm.com",
            password_hash=hash_password("Sales@12345"),
            role=RoleEnum.SALES_EXECUTIVE,
            is_active=True,
            failed_login_count=0,
            created_at=datetime.utcnow() - timedelta(days=40)
        )

        sales2_user = User(
            name="David Miller",
            email="sales2@acxiomcrm.com",
            password_hash=hash_password("Sales@12345"),
            role=RoleEnum.SALES_EXECUTIVE,
            is_active=True,
            failed_login_count=0,
            created_at=datetime.utcnow() - timedelta(days=40)
        )

        db.add_all([admin_user, manager_user, sales1_user, sales2_user])
        db.commit()

        # 2. Customers
        c1 = Customer(
            customer_code="CUST-0001",
            customer_name="John Henderson",
            email="john@globallogistics.com",
            phone="9876543210",
            company_name="Global Logistics Inc.",
            address="450 Fleet Boulevard, Suite 300",
            city="Chicago",
            state="Illinois",
            status="Active",
            assigned_to=sales1_user.user_id,
            created_by=admin_user.user_id,
            notes="Key enterprise client for automated dispatch systems.",
            created_at=datetime.utcnow() - timedelta(days=45)
        )

        c2 = Customer(
            customer_code="CUST-0002",
            customer_name="Dr. Patricia Vance",
            email="pvance@apexhealth.org",
            phone="9876543211",
            company_name="Apex Health Systems",
            address="1200 Medical Center Way",
            city="Boston",
            state="Massachusetts",
            status="Active",
            assigned_to=sales2_user.user_id,
            created_by=admin_user.user_id,
            notes="Multi-hospital EHR integration project.",
            created_at=datetime.utcnow() - timedelta(days=35)
        )

        c3 = Customer(
            customer_code="CUST-0003",
            customer_name="Vikram Mehta",
            email="v.mehta@technova.io",
            phone="9876543212",
            company_name="TechNova Solutions",
            address="77 Silicon Ave, Tech Park",
            city="San Francisco",
            state="California",
            status="Active",
            assigned_to=sales1_user.user_id,
            created_by=manager_user.user_id,
            notes="Cloud migration and custom CRM modules.",
            created_at=datetime.utcnow() - timedelta(days=20)
        )

        c4 = Customer(
            customer_code="CUST-0004",
            customer_name="Rachel Green",
            email="rachel@horizonretail.com",
            phone="9876543213",
            company_name="Horizon Retail Corp",
            address="800 Commerce Way",
            city="New York",
            state="New York",
            status="Active",
            assigned_to=sales2_user.user_id,
            created_by=sales2_user.user_id,
            notes="Omnichannel point of sale expansion.",
            created_at=datetime.utcnow() - timedelta(days=15)
        )

        db.add_all([c1, c2, c3, c4])
        db.commit()

        # 3. Leads
        l1 = Lead(
            lead_code="LEAD-0001",
            lead_name="Marcus Aurelius",
            email="m.aurelius@stoictech.com",
            phone="9876543220",
            company_name="Stoic Tech Labs",
            source="Website",
            status=LeadStatusEnum.QUALIFIED,
            priority="High",
            expected_value=45000.0,
            assigned_to=sales1_user.user_id,
            created_by=sales1_user.user_id,
            notes="Expressed strong interest in our enterprise analytics tier.",
            created_at=datetime.utcnow() - timedelta(days=12)
        )

        l2 = Lead(
            lead_code="LEAD-0002",
            lead_name="Samantha Ray",
            email="samantha@zenithpharma.com",
            phone="9876543221",
            company_name="Zenith Pharma",
            source="Referral",
            status=LeadStatusEnum.CONTACTED,
            priority="Medium",
            expected_value=28000.0,
            assigned_to=sales2_user.user_id,
            created_by=sales2_user.user_id,
            notes="Scheduled introductory platform overview.",
            created_at=datetime.utcnow() - timedelta(days=8)
        )

        l3 = Lead(
            lead_code="LEAD-0003",
            lead_name="Carlos Santana",
            email="carlos@urbanmobility.es",
            phone="9876543222",
            company_name="Urban Mobility Hub",
            source="Trade Show",
            status=LeadStatusEnum.NEW,
            priority="Low",
            expected_value=15000.0,
            assigned_to=sales1_user.user_id,
            created_by=manager_user.user_id,
            notes="Met at National Logistics Expo 2026.",
            created_at=datetime.utcnow() - timedelta(days=3)
        )

        l4 = Lead(
            lead_code="LEAD-0004",
            lead_name="Emily Thorne",
            email="emily@hamptonsfinance.com",
            phone="9876543223",
            company_name="Hamptons Financial Group",
            source="Email Campaign",
            status=LeadStatusEnum.CONVERTED,
            priority="High",
            expected_value=60000.0,
            assigned_to=sales2_user.user_id,
            created_by=sales2_user.user_id,
            converted_customer_id=c4.customer_id,
            notes="Converted successfully into active client.",
            created_at=datetime.utcnow() - timedelta(days=25)
        )

        l5 = Lead(
            lead_code="LEAD-0005",
            lead_name="Brian O'Connor",
            email="brian@fastfreight.com",
            phone="9876543224",
            company_name="Fast Freight Trans",
            source="Cold Call",
            status=LeadStatusEnum.LOST,
            priority="Low",
            expected_value=12000.0,
            assigned_to=sales1_user.user_id,
            created_by=sales1_user.user_id,
            notes="Competitor pricing was preferred.",
            created_at=datetime.utcnow() - timedelta(days=18)
        )

        db.add_all([l1, l2, l3, l4, l5])
        db.commit()

        # 4. Opportunities
        op1 = Opportunity(
            opportunity_name="Global Fleet Optimization Suite",
            customer_id=c1.customer_id,
            lead_id=None,
            amount=85000.0,
            stage=OpportunityStageEnum.NEGOTIATION,
            probability=80.0,
            expected_close_date=date.today() + timedelta(days=14),
            status=OpportunityStatusEnum.OPEN,
            assigned_to=sales1_user.user_id,
            notes="Final SLA and security audit terms under review.",
            created_at=datetime.utcnow() - timedelta(days=25)
        )

        op2 = Opportunity(
            opportunity_name="Apex Regional Hospital Integration",
            customer_id=c2.customer_id,
            lead_id=None,
            amount=120000.0,
            stage=OpportunityStageEnum.PROPOSAL,
            probability=50.0,
            expected_close_date=date.today() + timedelta(days=30),
            status=OpportunityStatusEnum.OPEN,
            assigned_to=sales2_user.user_id,
            notes="RFP submitted, presentation scheduled next Tuesday.",
            created_at=datetime.utcnow() - timedelta(days=15)
        )

        op3 = Opportunity(
            opportunity_name="TechNova Cloud Analytics Deployment",
            customer_id=c3.customer_id,
            lead_id=None,
            amount=55000.0,
            stage=OpportunityStageEnum.WON,
            probability=100.0,
            expected_close_date=date.today() - timedelta(days=5),
            status=OpportunityStatusEnum.WON,
            assigned_to=sales1_user.user_id,
            notes="Contract signed and initial invoice settled.",
            created_at=datetime.utcnow() - timedelta(days=35)
        )

        op4 = Opportunity(
            opportunity_name="Horizon POS Digital Signage Expansion",
            customer_id=c4.customer_id,
            lead_id=l4.lead_id,
            amount=42000.0,
            stage=OpportunityStageEnum.QUALIFICATION,
            probability=30.0,
            expected_close_date=date.today() + timedelta(days=45),
            status=OpportunityStatusEnum.OPEN,
            assigned_to=sales2_user.user_id,
            notes="Evaluating initial hardware requirements.",
            created_at=datetime.utcnow() - timedelta(days=10)
        )

        db.add_all([op1, op2, op3, op4])
        db.commit()

        # 5. Follow-Ups (Mix of Planned, Completed, and Overdue)
        today = datetime.utcnow()
        f1 = FollowUp(
            customer_id=c1.customer_id,
            lead_id=None,
            opportunity_id=op1.opportunity_id,
            related_type=RelatedTypeEnum.OPPORTUNITY,
            related_id=op1.opportunity_id,
            followup_date=today + timedelta(days=2, hours=3),
            followup_type=FollowUpTypeEnum.MEETING,
            subject="Executive Contract Review Call",
            remarks="Go over revised pricing table with CFO.",
            status=FollowUpStatusEnum.PLANNED,
            assigned_to=sales1_user.user_id,
            created_at=today - timedelta(days=2)
        )

        f2 = FollowUp(
            customer_id=None,
            lead_id=l1.lead_id,
            opportunity_id=None,
            related_type=RelatedTypeEnum.LEAD,
            related_id=l1.lead_id,
            followup_date=today + timedelta(hours=5),
            followup_type=FollowUpTypeEnum.DEMO,
            subject="Product Walkthrough Demo with Marcus",
            remarks="Focus on live dashboard widgets and reporting exports.",
            status=FollowUpStatusEnum.PLANNED,
            assigned_to=sales1_user.user_id,
            created_at=today - timedelta(days=1)
        )

        # Overdue Follow-up to demonstrate overdue filtering!
        f3 = FollowUp(
            customer_id=c2.customer_id,
            lead_id=None,
            opportunity_id=op2.opportunity_id,
            related_type=RelatedTypeEnum.CUSTOMER,
            related_id=c2.customer_id,
            followup_date=today - timedelta(days=1, hours=2),
            followup_type=FollowUpTypeEnum.EMAIL,
            subject="Send Security Compliance Whitepaper",
            remarks="Action required: send HIPAA compliance docs to compliance officer.",
            status=FollowUpStatusEnum.PLANNED,
            assigned_to=sales2_user.user_id,
            created_at=today - timedelta(days=3)
        )

        f4 = FollowUp(
            customer_id=c3.customer_id,
            lead_id=None,
            opportunity_id=op3.opportunity_id,
            related_type=RelatedTypeEnum.OPPORTUNITY,
            related_id=op3.opportunity_id,
            followup_date=today - timedelta(days=6),
            followup_type=FollowUpTypeEnum.CALL,
            subject="Onboarding Kickoff Call",
            remarks="Completed successfully with Vikram. Handover to deployment team.",
            status=FollowUpStatusEnum.COMPLETED,
            assigned_to=sales1_user.user_id,
            created_at=today - timedelta(days=10),
            completed_at=today - timedelta(days=6)
        )

        db.add_all([f1, f2, f3, f4])
        db.commit()

        # 6. Activities
        a1 = Activity(
            activity_type=ActivityTypeEnum.CALL,
            subject="Introductory Discovery Call",
            description="Discussed current pain points regarding delivery route delays.",
            activity_date=today - timedelta(days=22),
            customer_id=c1.customer_id,
            assigned_to=sales1_user.user_id,
            status="Completed"
        )
        a2 = Activity(
            activity_type=ActivityTypeEnum.MEETING,
            subject="Architecture Deep-Dive",
            description="Presented cloud vs on-prem security architecture.",
            activity_date=today - timedelta(days=14),
            customer_id=c2.customer_id,
            assigned_to=sales2_user.user_id,
            status="Completed"
        )
        db.add_all([a1, a2])
        db.commit()

        # 7. Audit Logs
        audit1 = AuditLog(
            user_id=admin_user.user_id,
            user_email=admin_user.email,
            action=AuditActionEnum.LOGIN,
            entity_name="Auth",
            record_id=str(admin_user.user_id),
            details="Admin successfully logged in from office network",
            timestamp=today - timedelta(days=1),
            ip_address="192.168.1.100"
        )
        audit2 = AuditLog(
            user_id=sales1_user.user_id,
            user_email=sales1_user.email,
            action=AuditActionEnum.CREATE,
            entity_name="Opportunity",
            record_id=str(op1.opportunity_id),
            details="Created opportunity 'Global Fleet Optimization Suite'",
            timestamp=today - timedelta(days=25),
            ip_address="192.168.1.105"
        )
        audit3 = AuditLog(
            user_id=sales2_user.user_id,
            user_email=sales2_user.email,
            action=AuditActionEnum.CONVERT,
            entity_name="Lead",
            record_id=str(l4.lead_id),
            details="Lead Hamptons Financial converted to Customer CUST-0004",
            timestamp=today - timedelta(days=25),
            ip_address="192.168.1.110"
        )
        db.add_all([audit1, audit2, audit3])
        db.commit()

        print("Database seeded successfully with test credentials:")
        print("  Admin:           admin@acxiomcrm.com    / Admin@12345")
        print("  Manager:         manager@acxiomcrm.com  / Manager@12345")
        print("  Sales Executive: sales1@acxiomcrm.com   / Sales@12345")
        print("  Sales Executive: sales2@acxiomcrm.com   / Sales@12345")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
