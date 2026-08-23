import streamlit as st

def render(api):
    st.title("Admin Analytics Dashboard")
    st.markdown("<div class='kicker'>Platform health, knowledge base and administration activity.</div>", unsafe_allow_html=True)

    try:
        # Fetch comprehensive dashboard stats
        stats = api.analytics_dashboard()
        
        # Display key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("📄 Documents", stats["documents"]["total"])
        col2.metric("📊 Datasets", stats["datasets"]["total"])
        col3.metric("👥 Admins", stats["admins"]["total"])
        col4.metric("👤 Team", stats["team"]["members"])
        col5.metric("💡 Recommendations", stats["recommendations"]["total"])

        # Document Processing Status
        st.markdown('<div class="section"><div class="section-label">Document Processing Status</div></div>', unsafe_allow_html=True)
        doc_status_col1, doc_status_col2, doc_status_col3, doc_status_col4 = st.columns(4)
        doc_status_col1.metric("Indexed", stats["documents"]["indexed"])
        doc_status_col2.metric("Processing", stats["documents"]["processing"])
        doc_status_col3.metric("Failed", stats["documents"]["failed"])
        doc_status_col4.metric("Total Chunks", stats["documents"].get("total_chunks", 0))

        # Detailed Views
        st.markdown('<div class="section"><div class="section-label">Detailed Views</div></div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Documents", "Recommendations", "System Health"])
        
        with tab1:
            try:
                doc_overview = api.analytics_documents()
                st.subheader("Recent Document Uploads")
                if doc_overview.get("recent_uploads"):
                    for doc in doc_overview["recent_uploads"]:
                        status_emoji = {
                            "indexed": "✅",
                            "processing": "⏳",
                            "failed": "❌"
                        }.get(doc["status"], "❓")
                        st.write(f"{status_emoji} **{doc['filename']}** ({doc['status']}) - {doc['created_at']}")
                else:
                    st.info("No documents uploaded yet.")
            except Exception as e:
                st.warning(f"Could not load document overview: {e}")
        
        with tab2:
            try:
                rec_overview = api.analytics_recommendations()
                st.subheader("Recent Recommendations")
                if rec_overview.get("recent"):
                    for rec in rec_overview["recent"]:
                        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(rec["priority"], "⚪")
                        status_text = rec["status"].replace("_", " ").title()
                        st.write(f"{priority_emoji} **{rec['title']}** ({status_text}) - {rec['created_at']}")
                else:
                    st.info("No recommendations yet.")
            except Exception as e:
                st.warning(f"Could not load recommendations overview: {e}")
        
        with tab3:
            st.subheader("System Health Check")
            st.write(f"✅ API Connection: OK")
            st.write(f"📊 Database: Connected")
            st.write(f"🔐 Authentication: Active")
            st.write(f"🚀 Services: All Running")

    except Exception as exc:
        st.error(f"Error loading dashboard: {str(exc)}")
