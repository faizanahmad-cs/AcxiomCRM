import streamlit as st
import pandas as pd
from datetime import datetime
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.user import User, RoleEnum
from acxiom_crm.backend.services.user_service import get_all_users, update_user_profile, admin_reset_password
from acxiom_crm.backend.services.auth_service import register_user, unlock_user_account
from acxiom_crm.backend.security.password import validate_password_policy

def render_user_admin_view(current_user: User):
    if current_user.role != RoleEnum.ADMIN:
        st.error("⛔ Access Denied: User Administration is restricted to Administrators only.")
        return

    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; color: #f8fafc; font-weight: 700;">👤 User & Access Administration</h3>
                <p style="margin: 0; color: #94a3b8; font-size: 13px;">Manage employee credentials, RBAC permissions, and account lockout security</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    db = SessionLocal()
    try:
        tab_users, tab_new_user = st.tabs(["👥 Active Users & Lockout Management", "➕ Provision New User"])

        with tab_new_user:
            st.markdown("##### Provision New Employee Account")
            with st.form("admin_create_user_form"):
                u1, u2 = st.columns(2)
                with u1:
                    name = st.text_input("Full Name *", placeholder="e.g. Rachel Adams")
                    email = st.text_input("Work Email *", placeholder="e.g. radams@acxiomcrm.com")
                with u2:
                    role = st.selectbox("Assigned Role *", RoleEnum.ALL, index=2)
                    temp_pass = st.text_input("Temporary Password *", type="password", placeholder="Complexity policy applied")

                st.caption("Password requires at least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special character.")
                submit_user = st.form_submit_button("Provision User", type="primary", use_container_width=True)

                if submit_user:
                    if not name.strip() or not email.strip():
                        st.error("Name and email are mandatory.")
                    else:
                        valid, msg = validate_password_policy(temp_pass)
                        if not valid:
                            st.error(f"Password Policy Violation: {msg}")
                        else:
                            try:
                                new_u = register_user(
                                    db=db,
                                    name=name.strip(),
                                    email=email.strip().lower(),
                                    password=temp_pass,
                                    role=role,
                                    created_by_user=current_user,
                                    ip_address="127.0.0.1"
                                )
                                st.success(f"User '{new_u.name}' ({new_u.role}) successfully created!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to create user: {str(ex)}")

        with tab_users:
            users = get_all_users(db)
            now = datetime.utcnow()

            table_data = []
            for u in users:
                is_locked = u.is_locked()
                lock_status = "🔓 Normal"
                if is_locked:
                    rem = int((u.lockout_until - now).total_seconds() / 60) + 1
                    lock_status = f"🔒 LOCKED ({rem}m left)"
                elif u.failed_login_count > 0:
                    lock_status = f"⚠️ {u.failed_login_count}/5 Fails"

                table_data.append({
                    "ID": u.user_id,
                    "Name": u.name,
                    "Email": u.email,
                    "Role": u.role,
                    "Status": "Active" if u.is_active else "Inactive",
                    "Security State": lock_status,
                    "Failed Attempts": u.failed_login_count,
                    "Last Login": u.last_login_at.strftime("%Y-%m-%d %H:%M") if u.last_login_at else "Never"
                })

            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### 🛠️ Manage Selected User Account")

            user_choices = {u.user_id: f"#{u.user_id}: {u.name} ({u.email}) - {u.role}" for u in users}
            target_id = st.selectbox("Select User Account", options=list(user_choices.keys()), format_func=lambda x: user_choices.get(x, str(x)))

            if target_id:
                target_user = db.query(User).filter(User.user_id == target_id).first()

                col_actions1, col_actions2, col_actions3 = st.columns(3)

                # Action 1: Unlock Account
                with col_actions1:
                    st.markdown("**Account Lockout Status**")
                    if target_user.is_locked() or target_user.failed_login_count > 0:
                        st.warning(f"Lockout: {target_user.failed_login_count} failed attempts.")
                        if st.button("🔓 Unlock Account & Clear Failures", type="primary", key=f"unlock_{target_id}"):
                            try:
                                unlock_user_account(db, target_id, current_user)
                                st.success(f"Account {target_user.email} unlocked!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {str(ex)}")
                    else:
                        st.success("Account is healthy and unlocked.")

                # Action 2: Change Role / Activation
                with col_actions2:
                    st.markdown("**Update Profile & Role**")
                    with st.form(f"update_role_form_{target_id}"):
                        new_name = st.text_input("Name", value=target_user.name)
                        new_role = st.selectbox("Role", RoleEnum.ALL, index=RoleEnum.ALL.index(target_user.role))
                        new_active = st.checkbox("Account Active", value=target_user.is_active)
                        if st.form_submit_button("Update User Profile"):
                            try:
                                update_user_profile(
                                    db=db,
                                    user_id=target_id,
                                    name=new_name,
                                    role=new_role,
                                    is_active=new_active,
                                    admin_user=current_user
                                )
                                st.success("User updated successfully!")
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Error: {str(ex)}")

                # Action 3: Password Reset
                with col_actions3:
                    st.markdown("**Admin Password Reset**")
                    with st.form(f"admin_pw_reset_{target_id}"):
                        admin_pw = st.text_input("New Password", type="password", placeholder="Enter new password")
                        if st.form_submit_button("🔑 Reset Password"):
                            valid, msg = validate_password_policy(admin_pw)
                            if not valid:
                                st.error(msg)
                            else:
                                try:
                                    admin_reset_password(db, target_id, admin_pw, current_user)
                                    st.success(f"Password reset for {target_user.email}!")
                                    st.rerun()
                                except Exception as ex:
                                    st.error(f"Error: {str(ex)}")
    finally:
        db.close()
