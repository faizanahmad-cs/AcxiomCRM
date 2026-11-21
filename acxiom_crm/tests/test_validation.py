import unittest
from datetime import date, timedelta, datetime
from pydantic import ValidationError
from acxiom_crm.backend.schemas.opportunity import OpportunityCreate, OpportunityBase
from acxiom_crm.backend.schemas.followup import FollowUpCreate, FollowUpBase
from acxiom_crm.backend.schemas.customer import CustomerCreate
from acxiom_crm.backend.schemas.lead import LeadCreate
from acxiom_crm.backend.schemas.user import UserRegisterRequest
from acxiom_crm.backend.security.password import validate_password_policy

class TestValidationRules(unittest.TestCase):

    def test_opportunity_amount_must_be_greater_than_zero(self):
        # Amount = 0 -> reject with: "Opportunity Amount must be greater than 0."
        with self.assertRaises(ValidationError) as ctx:
            OpportunityCreate(
                opportunity_name="Enterprise Deal",
                customer_id=1,
                amount=0.0,
                stage="Qualification",
                probability=50.0,
                expected_close_date=date.today() + timedelta(days=10)
            )
        self.assertIn("Opportunity Amount must be greater than 0.", str(ctx.exception))

        # Negative amount
        with self.assertRaises(ValidationError) as ctx:
            OpportunityCreate(
                opportunity_name="Enterprise Deal",
                customer_id=1,
                amount=-1000.0,
                stage="Qualification",
                probability=50.0,
                expected_close_date=date.today() + timedelta(days=10)
            )
        self.assertIn("Opportunity Amount must be greater than 0.", str(ctx.exception))

    def test_opportunity_probability_range(self):
        # Probability = 101 -> reject with: "Probability must be between 0 and 100."
        with self.assertRaises(ValidationError) as ctx:
            OpportunityCreate(
                opportunity_name="Enterprise Deal",
                customer_id=1,
                amount=50000.0,
                stage="Qualification",
                probability=101.0,
                expected_close_date=date.today() + timedelta(days=10)
            )
        self.assertIn("Probability must be between 0 and 100.", str(ctx.exception))

        # Negative probability
        with self.assertRaises(ValidationError) as ctx:
            OpportunityCreate(
                opportunity_name="Enterprise Deal",
                customer_id=1,
                amount=50000.0,
                stage="Qualification",
                probability=-5.0,
                expected_close_date=date.today() + timedelta(days=10)
            )
        self.assertIn("Probability must be between 0 and 100.", str(ctx.exception))

    def test_opportunity_expected_close_date_not_in_past(self):
        # Expected Close Date = yesterday -> reject with: "Expected Close Date cannot be in the past."
        yesterday = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            OpportunityCreate(
                opportunity_name="Enterprise Deal",
                customer_id=1,
                amount=50000.0,
                stage="Qualification",
                probability=50.0,
                expected_close_date=yesterday
            )
        self.assertIn("Expected Close Date cannot be in the past.", str(ctx.exception))

    def test_followup_date_not_earlier_than_today(self):
        # Follow-Up Date = yesterday -> reject with: "Follow-up date cannot be earlier than today."
        yesterday_dt = datetime.utcnow() - timedelta(days=1)
        with self.assertRaises(ValidationError) as ctx:
            FollowUpCreate(
                related_type="Customer",
                related_id=1,
                followup_date=yesterday_dt,
                followup_type="Call",
                subject="Client Check-in",
                status="Planned",
                assigned_to=1
            )
        self.assertIn("Follow-up date cannot be earlier than today.", str(ctx.exception))

    def test_email_validation(self):
        # Email = invalid format -> reject with: "Enter a valid email address."
        with self.assertRaises(ValidationError) as ctx:
            CustomerCreate(
                customer_name="Acme Corp",
                email="invalid-email-format",
                phone="9876543210",
                status="Active"
            )
        self.assertIn("Enter a valid email address.", str(ctx.exception))

    def test_phone_validation(self):
        # Phone = invalid length/characters -> reject with: "Enter a valid phone number."
        with self.assertRaises(ValidationError) as ctx:
            CustomerCreate(
                customer_name="Acme Corp",
                email="acme@corp.com",
                phone="12345",  # Too short
                status="Active"
            )
        self.assertIn("Enter a valid phone number.", str(ctx.exception))

    def test_password_policy(self):
        # Too short (<8 chars)
        ok, msg = validate_password_policy("Ab1!")
        self.assertFalse(ok)
        self.assertIn("at least 8 characters", msg)

        # Missing uppercase
        ok, msg = validate_password_policy("lowercase123!")
        self.assertFalse(ok)
        self.assertIn("uppercase letter", msg)

        # Missing digit
        ok, msg = validate_password_policy("Password!")
        self.assertFalse(ok)
        self.assertIn("number", msg)

        # Missing special char
        ok, msg = validate_password_policy("Password123")
        self.assertFalse(ok)
        self.assertIn("special character", msg)

        # Valid password
        ok, msg = validate_password_policy("Secure@Pass123")
        self.assertTrue(ok)

if __name__ == "__main__":
    unittest.main()
