import streamlit as st
import streamlit.components.v1 as components

def render(api):
    st.title("Power BI")
    st.markdown("<div class='kicker'>Embedded business intelligence and reporting.</div>", unsafe_allow_html=True)

    try:
        dashboards = api.powerbi()
    except Exception as exc:
        st.error(str(exc))
        return

    if not dashboards:
        st.markdown("""
        <div class="card">
            <div class="card-title">No dashboard configured</div>
            <div class="card-copy">An administrator can add an active Power BI embed configuration from Power BI Settings.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    selected = st.selectbox("Dashboard", dashboards, format_func=lambda x: x["name"])
    st.caption(selected.get("description", ""))

    components.html(
        f"""<iframe src="{selected['embed_url']}"
        width="100%" height="720" frameborder="0"
        allowfullscreen="true"></iframe>""",
        height=740,
        scrolling=False,
    )
