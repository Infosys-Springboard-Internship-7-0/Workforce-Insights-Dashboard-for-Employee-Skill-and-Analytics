import requests


class APIClient:
    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def request(self, method, path, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.update(self._headers())
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=120,
            **kwargs,
        )
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise RuntimeError(f"{response.status_code}: {detail}")
        return response

    def login(self, email, password):
        return self.request(
            "POST",
            "/api/auth/login",
            json={"email": email, "password": password},
        ).json()

    def me(self):
        return self.request("GET", "/api/auth/me").json()

    def suggestions(self):
        return self.request("GET", "/api/assistant/suggestions").json()

    def assistant_documents(self):
        return self.request("GET", "/api/assistant/documents").json()

    def chat(self, question, dataset_name=None, document_filename=None):
        return self.request(
            "POST",
            "/api/assistant/chat",
            json={
                "question": question,
                "dataset_name": dataset_name,
                "document_filename": document_filename,
            },
        ).json()

    def documents(self):
        return self.request("GET", "/api/admin/documents").json()

    def analytics_dashboard(self):
        return self.request("GET", "/api/analytics/dashboard").json()

    def analytics_documents(self):
        return self.request("GET", "/api/analytics/documents").json()

    def analytics_recommendations(self):
        return self.request("GET", "/api/analytics/recommendations").json()

    def upload_document(self, filename, content):
        return self.request(
            "POST",
            "/api/admin/documents/upload",
            files={"file": (filename, content)},
        ).json()

    def delete_document(self, document_id):
        return self.request("DELETE", f"/api/admin/documents/{document_id}").json()

    def admins(self):
        return self.request("GET", "/api/auth/admins").json()

    def create_admin(self, name, email, password):
        return self.request(
            "POST",
            "/api/auth/admins",
            json={"name": name, "email": email, "password": password},
        ).json()

    def delete_admin(self, user_id):
        return self.request("DELETE", f"/api/auth/admins/{user_id}").json()

    def update_admin(self, admin_id, payload):
        return self.request(
            "PUT", f"/api/auth/admins/{admin_id}", json=payload
        ).json()

    def team(self):
        return self.request("GET", "/api/team").json()

    def create_team(self, payload):
        return self.request("POST", "/api/admin/team", json=payload).json()

    def delete_team(self, member_id):
        return self.request("DELETE", f"/api/admin/team/{member_id}").json()

    def powerbi(self):
        return self.request("GET", "/api/powerbi").json()

    def admin_powerbi(self):
        return self.request("GET", "/api/admin/powerbi").json()

    def create_powerbi(self, payload):
        return self.request("POST", "/api/admin/powerbi", json=payload).json()

    def update_powerbi(self, dashboard_id, payload):
        return self.request("PUT", f"/api/admin/powerbi/{dashboard_id}", json=payload).json()

    def datasets(self):
        return self.request("GET", "/api/datasets").json()

    def recommendations(self):
        return self.request("GET", "/api/admin/recommendations").json()

    def recommendation_datasets(self):
        return self.request("GET", "/api/admin/recommendations/datasets").json()

    def analyze_recommendations(self, dataset_name):
        return self.request(
            "POST",
            "/api/admin/recommendations/analyze",
            json={"dataset_name": dataset_name},
        ).json()

    def update_recommendation(self, recommendation_id, status):
        return self.request(
            "PATCH",
            f"/api/admin/recommendations/{recommendation_id}",
            json={"status": status},
        ).json()

    def delete_recommendation(self, recommendation_id):
        return self.request(
            "DELETE", f"/api/admin/recommendations/{recommendation_id}"
        ).json()

    def ask_recommendation(self, recommendation_id, question):
        return self.request(
            "POST",
            f"/api/admin/recommendations/{recommendation_id}/ask",
            json={"question": question},
        ).json()

    def ask_decision_assistant(self, question, dataset_name):
        return self.request(
            "POST",
            "/api/admin/recommendations/decision-assistant",
            json={"question": question, "dataset_name": dataset_name},
        ).json()

    def dataset(self, page=1, limit=50):
        return self.request(
            "GET",
            "/api/datasets/sample",
            params={"page": page, "limit": limit},
        ).json()

    # Dataset CRUD / vector search
    def create_dataset(self, name, description=""):
        return self.request(
            "POST", "/api/datasets", json={"name": name, "description": description}
        ).json()

    def get_dataset(self, dataset_id):
        return self.request("GET", f"/api/datasets/{dataset_id}").json()

    def update_dataset(self, dataset_id, payload):
        return self.request("PUT", f"/api/datasets/{dataset_id}", json=payload).json()

    def delete_dataset(self, dataset_id):
        return self.request("DELETE", f"/api/datasets/{dataset_id}").json()

    def upload_dataset_csv(self, dataset_id, filename, content, replace_existing=False):
        return self.request(
            "POST",
            f"/api/datasets/{dataset_id}/upload",
            files={"file": (filename, content, "text/csv")},
            data={"replace_existing": str(replace_existing).lower()},
        ).json()

    def dataset_rows(self, dataset_id, page=1, limit=50, search=""):
        return self.request(
            "GET",
            f"/api/datasets/{dataset_id}/rows",
            params={"page": page, "limit": limit, "search": search or None},
        ).json()

    def create_dataset_row(self, dataset_id, data):
        return self.request(
            "POST", f"/api/datasets/{dataset_id}/rows", json={"data": data}
        ).json()

    def update_dataset_row(self, dataset_id, row_id, data):
        return self.request(
            "PUT", f"/api/datasets/{dataset_id}/rows/{row_id}", json={"data": data}
        ).json()

    def delete_dataset_row(self, dataset_id, row_id):
        return self.request(
            "DELETE", f"/api/datasets/{dataset_id}/rows/{row_id}"
        ).json()

    def semantic_dataset_search(self, dataset_id, query, limit=10):
        return self.request(
            "POST",
            f"/api/datasets/{dataset_id}/search",
            json={"query": query, "limit": limit},
        ).json()
