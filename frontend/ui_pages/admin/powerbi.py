import streamlit as st

def render(api):
    st.title("Power BI Settings")
    st.markdown("<div class='kicker'>Manage the dashboard configuration displayed to users.</div>", unsafe_allow_html=True)

    try:
        existing = api.admin_powerbi()
    except Exception as exc:
        st.error(str(exc))
        existing = []

    with st.container(border=True):
        with st.form("powerbi_form"):
            name = st.text_input("Dashboard name")
            description = st.text_area("Description")
            embed_url = st.text_input("Embed URL", placeholder="https://app.powerbi.com/view?r=...")
            active = st.checkbox("Active", value=True)
            submit = st.form_submit_button("Save dashboard", type="primary")

        if submit:
            if not embed_url:
                st.error("Embed URL is required.")
            else:
                try:
                    api.create_powerbi({
                        "name": name,
                        "description": description,
                        "embed_url": embed_url,
                        "is_active": active,
                    })
                    st.success("Power BI dashboard saved.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    st.markdown('<div class="section"><div class="section-label">Configured dashboards</div></div>', unsafe_allow_html=True)
    if existing:
        st.dataframe(
            [{"Name": x["name"], "Active": x["is_active"], "Embed URL": x["embed_url"]} for x in existing],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No dashboards configured.")
