import streamlit as st

def render(api):
    st.title("Admin Management")
    st.markdown("<div class='kicker'>Manage administrator access and platform ownership.</div>", unsafe_allow_html=True)

    with st.expander("Add administrator", expanded=True):
        with st.form("new_admin"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full name")
            email = c2.text_input("Email")
            password = st.text_input("Temporary password", type="password")
            submit = st.form_submit_button("Create administrator", type="primary")

        if submit:
            try:
                api.create_admin(name, email, password)
                st.success("Administrator created.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    st.markdown('<div class="section"><div class="section-label">Current administrators</div></div>', unsafe_allow_html=True)
    try:
        admins = api.admins()
        for admin in admins:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 4, 1, 1])
                c1.markdown(f"**{admin['name']}**")
                c2.caption(f"{admin['email']} · {admin['role']}")
                if c3.button("Edit", key=f"edit_admin_{admin['id']}"):
                    st.session_state[f"editing_admin_{admin['id']}"] = True
                if c4.button("Deactivate", key=f"delete_admin_{admin['id']}"):
                    try:
                        api.delete_admin(admin["id"])
                        st.success("Administrator deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

                if st.session_state.get(f"editing_admin_{admin['id']}"):
                    with st.form(f"edit_admin_form_{admin['id']}"):
                        edited_name = st.text_input("Name", value=admin["name"])
                        edited_email = st.text_input("Email", value=admin["email"])
                        edited_active = st.checkbox("Active", value=admin["is_active"])
                        save = st.form_submit_button("Save changes", type="primary")
                    if save:
                        try:
                            api.update_admin(admin["id"], {
                                "name": edited_name,
                                "email": edited_email,
                                "is_active": edited_active,
                            })
                            st.session_state[f"editing_admin_{admin['id']}"] = False
                            st.success("Administrator updated.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
    except Exception as exc:
        st.error(str(exc))
