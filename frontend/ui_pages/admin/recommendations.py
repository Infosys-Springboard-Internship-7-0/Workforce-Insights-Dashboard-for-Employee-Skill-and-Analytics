import streamlit as st


def _priority_badge(priority: str) -> str:
    p = priority.upper()
    return f"<span class='priority priority-{priority.lower()}'>{p}</span>"


def render(api):
    st.title("AI Recommendations")
    st.markdown(
        "<div class='kicker'>Turn verified dataset analysis into actionable administrator decisions.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <style>
    .rec-hero { background:#fff; border:1px solid #D0D5DD; padding:24px; margin:20px 0; }
    .rec-hero-title { font-weight:700; font-size:17px; margin-bottom:6px; }
    .rec-hero-copy { color:#667085; font-size:13px; line-height:1.6; }
    .priority { display:inline-block; padding:4px 8px; border:1px solid #D0D5DD; font-size:11px; font-weight:700; letter-spacing:.04em; }
    .priority-high, .priority-critical { border-color:#F04438; color:#B42318; }
    .priority-medium { border-color:#FDB022; color:#B54708; }
    .priority-low { border-color:#98A2B3; color:#475467; }
    .rec-card { background:#fff; border:1px solid #E4E7EC; padding:22px; margin-bottom:14px; }
    .rec-label { color:#667085; text-transform:uppercase; font-size:11px; font-weight:700; letter-spacing:.06em; margin-top:12px; }
    .rec-reason { color:#475467; font-size:13px; line-height:1.6; }
    </style>
    """, unsafe_allow_html=True)

    try:
        datasets = api.recommendation_datasets()
    except Exception as exc:
        st.error(f"Unable to load datasets: {exc}")
        return

    st.markdown("<div class='section'><div class='section-label'>Generate recommendations</div></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='rec-hero'>
        <div class='rec-hero-title'>Data analysis → verified findings → Groq → recommendations</div>
        <div class='rec-hero-copy'>Python calculates the dataset facts first. Groq interprets those verified findings and produces grounded recommendations. Generated recommendations are stored in Neon PostgreSQL.</div>
    </div>
    """, unsafe_allow_html=True)

    if not datasets:
        st.warning("No CSV datasets are available in the backend data directory.")
    else:
        labels = [d["name"] for d in datasets]
        selected_name = st.selectbox("Dataset", labels, format_func=lambda x: next((d["name"] for d in datasets if d["name"] == x), x))
        selected = next(d for d in datasets if d["name"] == selected_name)

        a, b, c = st.columns(3)
        a.metric("Rows", f"{selected['rows']:,}")
        b.metric("Columns", selected["columns"])
        c.metric("Fields", ", ".join(selected["column_names"][:3]) + (" …" if len(selected["column_names"]) > 3 else ""))

        if st.button("Analyze Data & Generate Recommendations", type="primary", use_container_width=True):
            with st.spinner("Analyzing dataset and generating grounded recommendations..."):
                try:
                    result = api.analyze_recommendations(selected_name)
                    st.session_state["last_recommendation_analysis"] = result
                    st.success(result.get("message", "Analysis completed."))
                    if result.get("llm_warning"):
                        st.warning(result["llm_warning"])
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    try:
        recommendations = api.recommendations()
    except Exception as exc:
        st.error(str(exc))
        return

    analysis_result = st.session_state.get("last_recommendation_analysis")
    if analysis_result:
        analysis = analysis_result.get("dataset", {})
        st.markdown("<div class='section'><div class='section-label'>Latest analysis</div></div>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", f"{analysis.get('rows', 0):,}")
        m2.metric("Columns", analysis.get("columns", 0))
        m3.metric("Missing cells", analysis.get("missing_values", 0))
        m4.metric("Duplicate rows", analysis.get("duplicate_rows", 0))

        insights = analysis.get("insights", [])
        if insights:
            with st.container(border=True):
                st.markdown("**Verified findings**")
                for insight in insights:
                    st.markdown(f"• {insight}")

    st.markdown("<div class='section'><div class='section-label'>Recommendation history</div></div>", unsafe_allow_html=True)

    if not recommendations:
        st.info("No recommendations have been generated yet. Select a dataset above and click Analyze Data & Generate Recommendations.")
        return

    for item in recommendations:
        with st.container(border=True):
            st.markdown(
                f"{_priority_badge(item.get('priority', 'medium'))} &nbsp; **{item['title']}**",
                unsafe_allow_html=True,
            )
            st.write(item["recommendation"])

            if item.get("reasoning"):
                st.markdown("<div class='rec-label'>Why this was recommended</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rec-reason'>{item['reasoning']}</div>", unsafe_allow_html=True)

            if item.get("expected_impact"):
                st.markdown("<div class='rec-label'>Expected impact</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='rec-reason'>{item['expected_impact']}</div>", unsafe_allow_html=True)

            st.caption(f"Dataset: {item.get('dataset_name', '—')} · Status: {item.get('status', 'new')}")

            b1, b2, b3 = st.columns([1, 1, 2])
            if b1.button("Approve", key=f"approve_{item['id']}"):
                try:
                    api.update_recommendation(item["id"], "approved")
                    st.success("Recommendation approved.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
            if b2.button("Dismiss", key=f"dismiss_{item['id']}"):
                try:
                    api.delete_recommendation(item["id"])
                    st.success("Recommendation dismissed.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
            if b3.button("Ask AI about this recommendation", key=f"ask_{item['id']}"):
                st.session_state[f"ask_open_{item['id']}"] = True

            if st.session_state.get(f"ask_open_{item['id']}"):
                question = st.text_input(
                    "Your question",
                    key=f"question_{item['id']}",
                    placeholder="Why is this recommended? What should management do first?",
                )
                if st.button("Ask", key=f"send_ask_{item['id']}", type="primary") and question:
                    with st.spinner("Asking Groq about this recommendation..."):
                        try:
                            answer = api.ask_recommendation(item["id"], question)
                            st.markdown("**AI Decision Assistant**")
                            st.write(answer["answer"])
                        except Exception as exc:
                            st.error(str(exc))
