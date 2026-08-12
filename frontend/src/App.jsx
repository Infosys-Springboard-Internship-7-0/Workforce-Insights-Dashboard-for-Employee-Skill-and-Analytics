import { Routes, Route } from "react-router-dom";

import PublicLayout from "./components/layout/PublicLayout";
import AdminLayout from "./components/layout/AdminLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import HomePage from "./pages/HomePage";
import ChatbotPage from "./pages/ChatbotPage";
import PowerBIPage from "./pages/PowerBIPage";
import DataViewerPage from "./pages/DataViewerPage";
import LoginPage from "./pages/LoginPage";

import AdminRecommendationsPage from "./pages/admin/AdminRecommendationsPage";
import AdminDocumentsPage from "./pages/admin/AdminDocumentsPage";
import AdminTeamPage from "./pages/admin/AdminTeamPage";
import AdminPowerBIPage from "./pages/admin/AdminPowerBIPage";
import AdminAssistantPage from "./pages/admin/AdminAssistantPage";
import AdminAdminsPage from "./pages/admin/AdminAdminsPage";
import AdminProfilePage from "./pages/admin/AdminProfilePage";

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/assistant" element={<ChatbotPage />} />
        <Route path="/dashboards" element={<PowerBIPage />} />
        <Route path="/data-viewer" element={<DataViewerPage />} />
      </Route>

      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminRecommendationsPage />} />
        <Route path="documents" element={<AdminDocumentsPage />} />
        <Route path="team" element={<AdminTeamPage />} />
        <Route path="powerbi" element={<AdminPowerBIPage />} />
        <Route path="assistant" element={<AdminAssistantPage />} />
        <Route path="admins" element={<AdminAdminsPage />} />
        <Route path="profile" element={<AdminProfilePage />} />
      </Route>

      <Route path="*" element={<HomePage />} />
    </Routes>
  );
}
