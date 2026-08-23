import streamlit as st

def render(api):
    st.title("Team Members")
    st.markdown("<div class='kicker'>Maintain the people, roles and contributions shown across the platform.</div>", unsafe_allow_html=True)

    with st.expander("Add team member", expanded=True):
        with st.form("team"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name")
            role = c2.text_input("Role")
            contribution = st.text_area("Contribution")
            c3, c4 = st.columns(2)
            skills = c3.text_input("Skills")
            linkedin = c4.text_input("LinkedIn")
            github = st.text_input("GitHub")
            submit = st.form_submit_button("Add member", type="primary")

        if submit:
            try:
                api.create_team({
                    "name": name, "role": role, "contribution": contribution,
                    "skills": skills, "linkedin": linkedin, "github": github
                })
                st.success("Team member added.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    try:
        members = api.team()
        if not members:
            st.info("No team members configured.")
        for member in members:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 3, 1])
                c1.markdown(f"**{member['name']}**")
                c2.markdown(f"**{member['role']}**  \n{member['contribution']}")
                if c3.button("Delete", key=f"delete_team_{member['id']}"):
                    api.delete_team(member["id"])
                    st.rerun()
    except Exception as exc:
        st.error(str(exc))
