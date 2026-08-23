import streamlit as st

def render(api):
    st.title("Documents")
    st.markdown("<div class='kicker'>Control the knowledge base used by the AI Assistant.</div>", unsafe_allow_html=True)

    # Upload Section
    with st.container(border=True):
        st.markdown("**Upload Knowledge Source**")
        st.caption("Supported: PDF, DOCX, TXT and CSV. Files are extracted, chunked, embedded and indexed in Neon pgvector.")
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded = st.file_uploader("Choose file", type=["pdf", "docx", "txt", "csv"], label_visibility="collapsed")
        with col2:
            description = st.text_input("Description (optional)", placeholder="Brief description of the document...")
        
        if uploaded and st.button("Upload and Index", type="primary"):
            try:
                # Upload with description if provided
                result = api.request(
                    "POST",
                    "/api/admin/documents/upload",
                    files={"file": uploaded},
                    data={"description": description}
                ).json()
                st.success(f"✅ Indexed {result['filename']} · {result['chunks']} chunks")
                st.rerun()
            except Exception as exc:
                st.error(f"Upload failed: {str(exc)}")

    st.markdown('<div class="section"><div class="section-label">Knowledge Sources</div></div>', unsafe_allow_html=True)
    
    # Filter and Display
    try:
        # Get documents list with status filter
        status_filter = st.selectbox(
            "Filter by status",
            ["all", "processing", "indexed", "failed"],
            key="doc_status_filter"
        )
        
        # Fetch documents
        params = {"skip": 0, "limit": 100}
        if status_filter != "all":
            params["status"] = status_filter
        
        docs = api.request("GET", "/api/admin/documents", params=params).json()
        
        if not docs:
            st.info("No documents found. Upload a document to get started!")
            return
        
        # Display documents in expandable sections
        for doc in docs:
            status_emoji = {
                "indexed": "✅",
                "processing": "⏳",
                "failed": "❌"
            }.get(doc.get("status", "unknown"), "❓")
            
            with st.expander(f"{status_emoji} {doc['filename']} ({doc.get('status', 'unknown')})"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Type", doc["file_type"].upper())
                col2.metric("Chunks", doc["chunk_count"])
                col3.metric("Status", doc.get("status", "N/A"))
                col4.metric("Progress", doc.get("processing_status", "N/A")[:20])
                
                if doc.get("description"):
                    st.write(f"**Description:** {doc['description']}")
                
                st.write(f"**Uploaded:** {doc.get('created_at', 'N/A')}")
                st.write(f"**Last Updated:** {doc.get('updated_at', 'N/A')}")
                
                # Edit and Delete Actions
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("Edit Metadata", key=f"edit_doc_{doc['id']}"):
                        st.session_state[f"editing_doc_{doc['id']}"] = True
                
                with col_delete:
                    if st.button("Delete", key=f"delete_doc_{doc['id']}", type="secondary"):
                        try:
                            api.request("DELETE", f"/api/admin/documents/{doc['id']}")
                            st.success("Document deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {str(e)}")
                
                # Edit form if editing
                if st.session_state.get(f"editing_doc_{doc['id']}", False):
                    st.write("---")
                    st.subheader("Edit Metadata")
                    
                    new_filename = st.text_input(
                        "Filename",
                        value=doc.get("filename", ""),
                        key=f"filename_{doc['id']}"
                    )
                    new_description = st.text_area(
                        "Description",
                        value=doc.get("description", ""),
                        key=f"description_{doc['id']}"
                    )
                    
                    if st.button("Save Changes", key=f"save_metadata_{doc['id']}"):
                        try:
                            api.request(
                                "PUT",
                                f"/api/admin/documents/{doc['id']}",
                                json={
                                    "filename": new_filename,
                                    "description": new_description
                                }
                            )
                            st.success("Metadata updated!")
                            st.session_state[f"editing_doc_{doc['id']}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update: {str(e)}")
    
    except Exception as exc:
        st.error(f"Error loading documents: {str(exc)}")
