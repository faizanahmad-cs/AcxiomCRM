import streamlit as st
from acxiom_crm.backend.database import SessionLocal
from acxiom_crm.backend.models.user import RoleEnum
from acxiom_crm.backend.services.auth_service import (
    authenticate_user, register_user, AccountLockedError, AuthenticationError
)
from acxiom_crm.backend.security.password import validate_password_policy
from acxiom_crm.frontend.state import set_logged_in_user

def render_login_view():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 60px; height: 60px; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); border-radius: 16px; color: white; font-size: 32px; font-weight: 800; box-shadow: 0 8px 24px rgba(37,99,235,0.4); margin-bottom: 12px;">
                A
            </div>
            <h1 style="font-size: 30px; font-weight: 800; color: #f8fafc; margin: 0; letter-spacing: -0.5px;">AcxiomCRM</h1>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 4px;">Role-Based Enterprise Sales & Customer Lifecycle Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_left, col_card, col_right = st.columns([1, 2, 1])

    with col_card:
        # Pre-seed fast login buttons for testers
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px; margin-bottom: 20px;">
                <p style="font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px;">
                    ⚡ Quick Test Credentials (1-Click Fill)
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        bcol1, bcol2, bcol3, bcol4 = st.columns(4)
        if bcol1.button("👑 Admin", use_container_width=True, help="Full system & security access"):
            st.session_state["login_email_val"] = "admin@acxiomcrm.com"
            st.session_state["login_pass_val"] = "Admin@12345"
            st.rerun()

        if bcol2.button("👔 Manager", use_container_width=True, help="Pipeline & team reports"):
            st.session_state["login_email_val"] = "manager@acxiomcrm.com"
            st.session_state["login_pass_val"] = "Manager@12345"
            st.rerun()

        if bcol3.button("💼 Sales 1", use_container_width=True, help="Sarah Jenkins (Assigned scope)"):
            st.session_state["login_email_val"] = "sales1@acxiomcrm.com"
            st.session_state["login_pass_val"] = "Sales@12345"
            st.rerun()

        if bcol4.button("💼 Sales 2", use_container_width=True, help="David Miller (Assigned scope)"):
            st.session_state["login_email_val"] = "sales2@acxiomcrm.com"
            st.session_state["login_pass_val"] = "Sales@12345"
            st.rerun()

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("##### Account Login")
            default_email = st.session_state.get("login_email_val", "")
            default_pass = st.session_state.get("login_pass_val", "")

            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Work Email", value=default_email, placeholder="e.g. admin@acxiomcrm.com")
                password = st.text_input("Password", value=default_pass, type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In to AcxiomCRM", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        db = SessionLocal()
                        try:
                            user, token = authenticate_user(
                                db=db,
                                email=email.strip(),
                                password=password,
                                ip_address="127.0.0.1"
                            )
                            set_logged_in_user(user, token)
                            st.success(f"Welcome back, {user.name} ({user.role})!")
                            st.rerun()
                        except AccountLockedError as e:
                            st.error(f"🔒 {str(e)}")
                        except AuthenticationError as e:
                            st.error(f"❌ {str(e)}")
                        except Exception as e:
                            st.error(f"Authentication error: {str(e)}")
                        finally:
                            db.close()

        with tab_register:
            st.markdown("##### New User Registration")
            st.info("Passwords must have at least 8 characters, 1 uppercase, 1 lowercase, 1 number, and 1 special symbol.")

            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Jordan Smith")
                reg_email = st.text_input("Corporate Email", placeholder="e.g. jordan@acxiomcrm.com")
                reg_pass = st.text_input("Password", type="password", placeholder="Min 8 chars with complexity")
                reg_role = st.selectbox("Designated Role", [RoleEnum.SALES_EXECUTIVE, RoleEnum.MANAGER, RoleEnum.ADMIN])
                reg_submit = st.form_submit_button("Register New Account", use_container_width=True)

                if reg_submit:
                    if not reg_name.strip():
                        st.error("Full name is required.")
                    elif not reg_email.strip():
                        st.error("Email is required.")
                    else:
                        valid, msg = validate_password_policy(reg_pass)
                        if not valid:
                            st.error(f"Password Policy Violation: {msg}")
                        else:
                            db = SessionLocal()
                            try:
                                new_user = register_user(
                                    db=db,
                                    name=reg_name.strip(),
                                    email=reg_email.strip(),
                                    password=reg_pass,
                                    role=reg_role,
                                    ip_address="127.0.0.1"
                                )
                                st.success(f"Account for '{new_user.name}' ({new_user.role}) registered! You can now sign in.")
                            except Exception as e:
                                st.error(f"Registration failed: {str(e)}")
                            finally:
                                db.close()
