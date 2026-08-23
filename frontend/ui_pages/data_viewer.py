import json
import pandas as pd
import streamlit as st


def _safe_json_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return "" if value is None else str(value)


def _editor_to_dict(dataset_columns):
    data = {}
    for column in dataset_columns:
        key = st.text_input(str(column), key=f"new_row_{column}")
        data[str(column)] = key
    return data


def render(api):
    st.markdown(
        """
        <div class='hero' style='padding:28px 32px;margin-bottom:20px;'>
            <div class='eyebrow'>DATA MANAGEMENT</div>
            <h1 style='margin-bottom:6px;'>Data Viewer</h1>
            <p style='margin:0;'>Manage datasets stored in Neon PostgreSQL, edit records, import CSV files, and run semantic vector search using pgvector.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        datasets = api.datasets()
    except Exception as exc:
        st.error(f"Unable to load datasets: {exc}")
        return

    # ---------------- Dataset toolbar ----------------
    top1, top2, top3 = st.columns([2.2, 1, 1])
    with top1:
        options = {item["name"]: item["id"] for item in datasets}
        selected_name = st.selectbox(
            "Dataset",
            list(options.keys()) if options else ["No datasets"],
            label_visibility="collapsed",
        )
    with top2:
        create_clicked = st.button("+ New Dataset", use_container_width=True, type="primary")
    with top3:
        refresh_clicked = st.button("↻ Refresh", use_container_width=True)

    if refresh_clicked:
        st.rerun()

    if create_clicked:
        st.session_state["show_create_dataset"] = True

    if st.session_state.get("show_create_dataset"):
        with st.container(border=True):
            st.subheader("Create dataset")
            c1, c2 = st.columns([1, 2])
            with c1:
                name = st.text_input("Dataset name", key="create_dataset_name")
            with c2:
                description = st.text_input("Description", key="create_dataset_description")
            a, b = st.columns(2)
            with a:
                if st.button("Create", type="primary", use_container_width=True):
                    if not name.strip():
                        st.warning("Dataset name is required.")
                    else:
                        try:
                            api.create_dataset(name.strip(), description.strip())
                            st.session_state["show_create_dataset"] = False
                            st.success("Dataset created.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
            with b:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["show_create_dataset"] = False
                    st.rerun()

    if not datasets:
        st.info("No datasets yet. Create a dataset and upload a CSV to get started.")
        return

    dataset_id = options[selected_name]
    dataset = next(item for item in datasets if item["id"] == dataset_id)

    # ---------------- Metrics ----------------
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{dataset['row_count']:,}")
    m2.metric("Columns", len(dataset.get("columns", [])))
    m3.metric("Storage", "Neon PostgreSQL")
    m4.metric("Vectors", "pgvector")

    # ---------------- Management tabs ----------------
    browse, add, import_tab, settings_tab, search_tab = st.tabs(
        ["Browse", "Add Row", "Import CSV", "Dataset Settings", "Semantic Search"]
    )

    with browse:
        c1, c2, c3 = st.columns([2.5, 1, 1])
        with c1:
            search = st.text_input(
                "Filter rows",
                placeholder="Filter current dataset...",
                label_visibility="collapsed",
            )
        with c2:
            limit = st.selectbox("Rows", [25, 50, 100, 200], index=1, label_visibility="collapsed")
        with c3:
            page = st.number_input("Page", min_value=1, value=1, step=1, label_visibility="collapsed")

        try:
            result = api.dataset_rows(dataset_id, int(page), int(limit), search)
        except Exception as exc:
            st.error(str(exc))
            return

        rows = result.get("rows", [])
        if not rows:
            st.info("No rows match the current filter.")
        else:
            records = []
            for row in rows:
                record = dict(row["data"])
                record["__row_id"] = row["id"]
                records.append(record)
            df = pd.DataFrame(records)
            if "__row_id" in df.columns:
                display_df = df.drop(columns=["__row_id"])
            else:
                display_df = df
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=430)

            st.markdown("#### Row actions")
            row_labels = {
                f"Row {row['row_index'] + 1} · {row['id'][:8]}": row
                for row in rows
            }
            selected_label = st.selectbox("Select row", list(row_labels.keys()))
            selected_row = row_labels[selected_label]

            with st.container(border=True):
                st.markdown(f"**Editing row {selected_row['row_index'] + 1}**")
                edited = {}
                columns = dataset.get("columns", []) or list(selected_row["data"].keys())
                form_cols = st.columns(2)
                for index, column in enumerate(columns):
                    with form_cols[index % 2]:
                        edited[str(column)] = st.text_input(
                            str(column),
                            value=_safe_json_value(selected_row["data"].get(column)),
                            key=f"edit_{selected_row['id']}_{column}",
                        )
                a, b = st.columns(2)
                with a:
                    if st.button("Save Changes", type="primary", use_container_width=True):
                        try:
                            api.update_dataset_row(dataset_id, selected_row["id"], edited)
                            st.success("Row updated and embedding regenerated.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                with b:
                    if st.button("Delete Selected Row", use_container_width=True):
                        try:
                            api.delete_dataset_row(dataset_id, selected_row["id"])
                            st.success("Row deleted.")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))

        st.caption(f"Page {result.get('page', 1)} of {result.get('pages', 1)} · {result.get('total', 0):,} matching rows")

    with add:
        st.subheader("Add a new record")
        columns = dataset.get("columns", [])
        if not columns:
            st.info("Import a CSV first so the application can determine the dataset columns.")
        else:
            with st.form("add_dataset_row"):
                data = {}
                form_cols = st.columns(2)
                for index, column in enumerate(columns):
                    with form_cols[index % 2]:
                        data[str(column)] = st.text_input(str(column))
                submitted = st.form_submit_button("Add Row", type="primary", use_container_width=True)
            if submitted:
                try:
                    api.create_dataset_row(dataset_id, data)
                    st.success("Row created and embedded.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

    with import_tab:
        st.subheader("Import CSV")
        st.caption("CSV import creates/updates all rows and generates 384-dimensional embeddings with all-MiniLM-L6-v2.")
        uploaded = st.file_uploader("Choose CSV", type=["csv"], key=f"csv_{dataset_id}")
        replace_existing = st.checkbox("Replace existing rows", value=False)
        if uploaded and st.button("Import CSV", type="primary"):
            try:
                result = api.upload_dataset_csv(dataset_id, uploaded.name, uploaded.getvalue(), replace_existing)
                st.success(f"Imported {result['imported_rows']:,} rows.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with settings_tab:
        st.subheader("Dataset Settings")
        with st.form(f"dataset_settings_{dataset_id}"):
            new_name = st.text_input("Name", value=dataset["name"])
            new_description = st.text_area("Description", value=dataset.get("description", ""))
            save = st.form_submit_button("Save Dataset", type="primary")
        if save:
            try:
                api.update_dataset(dataset_id, {"name": new_name, "description": new_description})
                st.success("Dataset updated.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        st.divider()
        st.warning("Deleting a dataset permanently deletes all of its rows and vectors.")
        confirm = st.checkbox("I understand this cannot be undone", key=f"confirm_delete_{dataset_id}")
        if st.button("Delete Dataset", disabled=not confirm):
            try:
                api.delete_dataset(dataset_id)
                st.success("Dataset deleted.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    with search_tab:
        st.subheader("Semantic Vector Search")
        st.caption("Search by meaning rather than exact keywords. Results are ranked by cosine similarity in Neon pgvector.")
        query = st.text_input("Search query", placeholder="e.g. employees with machine learning experience")
        top_k = st.slider("Results", 1, 20, 8)
        if st.button("Run Semantic Search", type="primary"):
            if not query.strip():
                st.warning("Enter a search query.")
            else:
                try:
                    result = api.semantic_dataset_search(dataset_id, query.strip(), top_k)
                    if not result["results"]:
                        st.info("No vector results found.")
                    for item in result["results"]:
                        similarity = item.pop("similarity")
                        with st.container(border=True):
                            st.markdown(f"**Similarity: {similarity:.3f}**")
                            st.json(item["data"], expanded=False)
                except Exception as exc:
                    st.error(str(exc))
