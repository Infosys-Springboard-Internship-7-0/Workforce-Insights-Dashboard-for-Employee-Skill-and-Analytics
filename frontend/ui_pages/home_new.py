import streamlit as st
from utils.session import is_authenticated, is_admin

def render(api):
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">AI-POWERED WORKFORCE ANALYTICS &amp; TALENT INTELLIGENCE DASHBOARD</div>
        <h1>Project intelligence, analytics and decisions in one workspace.</h1>
        <p>
            A secure knowledge and analytics platform that combines document-grounded
            RAG, business intelligence, dataset exploration and AI-assisted recommendations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not is_authenticated() or not is_admin():
        if st.button("Administrator sign in", type="primary"):
            st.session_state.page = "Login"
            st.rerun()

    # Problem Statement & Objectives
    st.markdown('<div class="section"><div class="section-label">Project Overview</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">Problem Statement</div>
            <div class="card-copy">
                Organizations struggle to consolidate workforce intelligence, analytics, and decision-making into a unified platform. 
                Administrators need secure tools to manage knowledge bases, analyze datasets, and generate actionable recommendations.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">Objectives</div>
            <div class="card-copy">
                • Enable RAG-based question answering using company knowledge<br/>
                • Provide secure admin tools for knowledge management<br/>
                • Deliver analytics and insights from datasets<br/>
                • Generate AI-powered recommendations<br/>
                • Integrate business intelligence dashboards
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section"><div class="section-label">Platform Capabilities</div></div>', unsafe_allow_html=True)

    cols = st.columns(4)
    cards = [
        ("01", "AI Assistant", "Ask questions against indexed project knowledge and receive grounded answers with sources."),
        ("02", "Power BI", "Preview the organization's embedded business intelligence dashboards."),
        ("03", "Data Viewer", "Inspect datasets in a clean, searchable and paginated table."),
        ("04", "Decision Support", "Help administrators turn analyzed information into practical recommendations."),
    ]
    for col, (num, title, copy) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="card">
                <div class="eyebrow">{num}</div>
                <div class="card-title">{title}</div>
                <div class="card-copy">{copy}</div>
            </div>
            """, unsafe_allow_html=True)

    # System Architecture
    st.markdown('<div class="section"><div class="section-label">System Architecture</div></div>', unsafe_allow_html=True)
    a, b = st.columns([1.4, 1])
    with a:
        st.markdown("""
        <div class="card">
            <div class="card-title">Retrieval-Augmented Generation (RAG)</div>
            <div class="card-copy">
                Streamlit → FastAPI → embedding model → Neon PostgreSQL / pgvector
                → top relevant chunks → Groq → grounded answer.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.code("""Admin Upload
    ↓
Extract → Chunk → Embed
    ↓
Neon PostgreSQL + pgvector
    ↓
Question → Embed → Similarity Search
    ↓
Top 5 chunks → Groq → Answer + Sources""", language="text")
    with b:
        st.markdown("""
        <div class="card">
            <div class="card-title">Technology Stack</div>
            <div class="card-copy">
                • Frontend: Streamlit<br/>
                • Backend: FastAPI, SQLAlchemy<br/>
                • Database: Neon PostgreSQL, pgvector<br/>
                • AI: Groq LLM, Sentence Transformers<br/>
                • Auth: JWT, bcrypt<br/>
                • BI: Power BI Embed
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Team Contributions
    st.markdown('<div class="section"><div class="section-label">Team Contributions</div></div>', unsafe_allow_html=True)
    try:
        members = api.team()
        if not members:
            st.info("No team members configured.")
        else:
            cols = st.columns(min(3, len(members)))
            for i, member in enumerate(members):
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">{member['name']}</div>
                        <div class="eyebrow">{member['role']}</div>
                        <div class="card-copy">{member['contribution']}</div>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as exc:
        st.warning(f"Unable to load team data: {exc}")

    # Project Resources
    st.markdown('<div class="section"><div class="section-label">Project Resources</div></div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    r1.markdown("**Architecture**  \nSystem design and RAG flow.")
    r2.markdown("**Supporting Documents**  \nPolicies, project notes and knowledge sources.")
    r3.markdown("**Analytics**  \nPower BI dashboards and dataset views.")

    st.markdown('<div class="footer">AI-Powered Workforce Analytics &amp; Talent Intelligence Dashboard</div>', unsafe_allow_html=True)
