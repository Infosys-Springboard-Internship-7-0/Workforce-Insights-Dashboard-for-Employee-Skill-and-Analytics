import streamlit as st

SUGGESTIONS = [
    "What is the project architecture?",
    "What technologies are being used?",
    "Summarize the project documentation.",
    "What are the major findings from the dataset?",
    "What recommendations can be made?",
    "Explain the RAG pipeline.",
]

def render(api):
    st.title("AI Assistant")
    st.markdown("<div class='kicker'>Project-grounded answers powered by retrieval-augmented generation.</div>", unsafe_allow_html=True)

    try:
        datasets = api.datasets()
    except Exception as exc:
        st.warning(f"Unable to load datasets: {exc}")
        datasets = []

    dataset_options = {"No dataset selected": None}
    dataset_options.update({
        item["name"]: item["name"]
        for item in datasets
    })
    selected_dataset = st.selectbox(
        "Select a dataset (optional)",
        options=list(dataset_options),
        format_func=lambda name: (
            "No dataset selected"
            if dataset_options[name] is None
            else f"{name} · {next(item['row_count'] for item in datasets if item['name'] == name):,} rows"
        ),
    )
    selected_dataset_name = dataset_options[selected_dataset]

    try:
        documents = api.assistant_documents()
    except Exception as exc:
        try:
            documents = [
                item for item in api.documents()
                if item.get("status") == "indexed"
            ]
        except Exception:
            st.warning(f"Unable to load uploaded files: {exc}")
            documents = []

    document_options = {"All uploaded files": None}
    document_options.update({
        item["filename"]: item["filename"]
        for item in documents
    })
    selected_document = st.selectbox(
        "Select an uploaded file (optional)",
        options=list(document_options),
        format_func=lambda name: (
            "All uploaded files"
            if document_options[name] is None
            else (
                f"{name} · {next(
                    (item.get('chunk_count', 0) for item in documents if item['filename'] == name),
                    0,
                )} chunks"
            )
        ),
    )
    selected_document_name = document_options[selected_document]

    st.markdown('<div class="section"><div class="section-label">Suggested questions</div></div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, question in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(question, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.pending_question = question

    st.markdown('<div class="section"><div class="section-label">Conversation</div></div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        st.markdown("""
        <div class="card">
            <div class="card-title">Ask the project knowledge base</div>
            <div class="card-copy">
                Your question is embedded, matched against the top relevant document chunks
                in Neon pgvector, and then answered by Groq using that context.
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.markdown(
                    "<div class='source'><b>Sources:</b> " +
                    " · ".join(msg["sources"]) +
                    "</div>",
                    unsafe_allow_html=True,
                )

    question = st.chat_input("Ask about the project, documents or data...")
    question = question or st.session_state.pop("pending_question", None)

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving context and generating answer..."):
                try:
                    result = api.chat(
                        question,
                        selected_dataset_name,
                        selected_document_name,
                    )
                    answer = result["answer"]
                    source_names = [
                        f"{s['filename']}" + (f" · p.{s['page']}" if s.get("page") else "")
                        for s in result.get("sources", [])
                    ]
                except Exception as exc:
                    answer = f"Unable to answer: {exc}"
                    source_names = []
            st.markdown(answer)
            if source_names:
                st.markdown(
                    "<div class='source'><b>Sources:</b> " +
                    " · ".join(source_names) +
                    "</div>",
                    unsafe_allow_html=True,
                )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": source_names,
        })
