import streamlit as st

SUGGESTED_QUESTIONS = [
    "Which department requires attention?",
    "What are the major workforce trends?",
    "What are the most important findings from the latest dataset?",
    "What actions should management consider?",
]


def render(api):
    st.title("Admin Decision Assistant")
    st.markdown(
        "<div class='kicker'>Use workforce data and generated recommendations to support management decisions.</div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section"><div class="section-label">Suggested questions</div></div>', unsafe_allow_html=True)
    columns = st.columns(2)
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        with columns[index % 2]:
            if st.button(question, key=f"decision_question_{index}", use_container_width=True):
                st.session_state.decision_question = question

    try:
        datasets = api.recommendation_datasets()
    except Exception as exc:
        st.error(f"Unable to load datasets: {exc}")
        return

    if not datasets:
        st.info("No datasets are available. Upload or create a dataset before using the Decision Assistant.")
        return

    dataset_options = {
        item["name"]: item
        for item in datasets
    }
    selected_dataset = st.selectbox(
        "Select a dataset",
        options=list(dataset_options),
        format_func=lambda name: (
            f"{name} · {dataset_options[name]['rows']:,} rows · "
            f"{dataset_options[name]['columns']} columns"
        ),
    )

    question = st.text_area(
        "Question",
        value=st.session_state.get("decision_question", ""),
        placeholder="Ask about workforce trends, findings, or management actions...",
    )

    if st.button("Ask Decision Assistant", type="primary", disabled=not question.strip()):
        try:
            result = api.ask_decision_assistant(question.strip(), selected_dataset)
            st.markdown('<div class="section"><div class="section-label">Decision support</div></div>', unsafe_allow_html=True)
            st.markdown(result["answer"])
            st.caption(f"Analyzed dataset: {result['dataset']}")
        except Exception as exc:
            st.error(str(exc))
