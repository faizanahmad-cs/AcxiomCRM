import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from acxiom_crm.backend.database import Base
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.models.audit import AuditLog, AuditActionEnum
from acxiom_crm.backend.security.password import hash_password, verify_password
from acxiom_crm.backend.services.auth_service import (
    authenticate_user, register_user, unlock_user_account,
    AccountLockedError, AuthenticationError
)

class TestAuthSecurity(unittest.TestCase):

    def setUp(self):
        # In-memory test db
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed admin
        self.admin = User(
            name="Admin User",
            email="admin@test.com",
            password_hash=hash_password("Admin@12345"),
            role=RoleEnum.ADMIN,
            is_active=True,
            failed_login_count=0
        )
        self.db.add(self.admin)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_password_hashing(self):
        hashed = hash_password("SuperSecret@123")
        self.assertNotEqual(hashed, "SuperSecret@123")
        self.assertTrue(verify_password("SuperSecret@123", hashed))
        self.assertFalse(verify_password("WrongPassword@123", hashed))

    def test_successful_login_resets_counter(self):
        # Set some failed attempts
        self.admin.failed_login_count = 3
        self.db.commit()

        user, token = authenticate_user(self.db, "admin@test.com", "Admin@12345")
        self.assertEqual(user.user_id, self.admin.user_id)
        self.assertIsNotNone(token)
        self.assertEqual(user.failed_login_count, 0)
        self.assertIsNone(user.lockout_until)

    def test_account_lockout_after_five_failed_attempts(self):
        # 1st attempt wrong
        with self.assertRaises(AuthenticationError) as ctx:
            authenticate_user(self.db, "admin@test.com", "Wrong@111")
        self.assertIn("4 attempt(s) remaining", str(ctx.exception))

        # Attempts 2, 3, 4
        for _ in range(3):
            with self.assertRaises(AuthenticationError):
                authenticate_user(self.db, "admin@test.com", "Wrong@111")

        # 5th attempt -> triggers lockout
        with self.assertRaises(AccountLockedError) as ctx:
            authenticate_user(self.db, "admin@test.com", "Wrong@111")
        self.assertIn("Account locked!", str(ctx.exception))

        # Refresh user from DB
        user = self.db.query(User).filter(User.email == "admin@test.com").first()
        self.assertTrue(user.is_locked())
        self.assertEqual(user.failed_login_count, 5)

        # Immediate attempt even with right password is still locked
        with self.assertRaises(AccountLockedError):
            authenticate_user(self.db, "admin@test.com", "Admin@12345")

        # Admin unlocks account
        unlock_user_account(self.db, user.user_id, self.admin)
        self.assertFalse(user.is_locked())
        self.assertEqual(user.failed_login_count, 0)

        # Now login succeeds
        user, token = authenticate_user(self.db, "admin@test.com", "Admin@12345")
        self.assertIsNotNone(token)

    def test_audit_log_generation(self):
        initial_count = self.db.query(AuditLog).count()
        # Trigger a failed login
        try:
            authenticate_user(self.db, "unknown@test.com", "Wrong@123")
        except AuthenticationError:
            pass

        logs = self.db.query(AuditLog).all()
        self.assertGreater(len(logs), initial_count)
        failed_log = logs[-1]
        self.assertEqual(failed_log.action, AuditActionEnum.FAILED_LOGIN)

if __name__ == "__main__":
    unittest.main()
