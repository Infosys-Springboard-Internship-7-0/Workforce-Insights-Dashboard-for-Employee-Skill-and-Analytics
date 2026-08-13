import { useState } from "react";
import { UserCircle, Check, AlertCircle } from "lucide-react";
import api from "../../api/client";
import { useAuth } from "../../context/AuthContext";

export default function AdminProfilePage() {
  const { admin, updateAdminProfile } = useAuth();
  const [name, setName] = useState(admin?.name || "");
  const [email, setEmail] = useState(admin?.email || "");
  const [profileMsg, setProfileMsg] = useState("");
  const [profileError, setProfileError] = useState("");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordMsg, setPasswordMsg] = useState("");
  const [passwordError, setPasswordError] = useState("");

  async function handleProfileSubmit(e) {
    e.preventDefault();
    setProfileMsg("");
    setProfileError("");
    try {
      const res = await api.put("/api/auth/me", { name, email });
      updateAdminProfile(res.data);
      setProfileMsg("Profile updated.");
    } catch (err) {
      setProfileError(err.response?.data?.detail || "Could not update profile.");
    }
  }

  async function handlePasswordSubmit(e) {
    e.preventDefault();
    setPasswordMsg("");
    setPasswordError("");
    try {
      await api.post("/api/auth/me/change-password", { current_password: currentPassword, new_password: newPassword });
      setPasswordMsg("Password updated.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordError(err.response?.data?.detail || "Could not update password.");
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-8 py-8 space-y-8">
      <div>
        <h1 className="text-xl font-bold text-ink-900 flex items-center gap-2">
          <UserCircle size={20} /> My Profile
        </h1>
        <p className="text-sm text-ink-500">Update your name, email, and password.</p>
      </div>

      <form onSubmit={handleProfileSubmit} className="card p-6 space-y-4">
        <h2 className="font-semibold text-ink-900 text-sm">Profile Details</h2>
        {profileMsg && <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 text-sm px-3 py-2"><Check size={15} /> {profileMsg}</div>}
        {profileError && <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2"><AlertCircle size={15} /> {profileError}</div>}
        <div>
          <label className="label">Name</label>
          <input className="input-field" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label className="label">Email</label>
          <input type="email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <button type="submit" className="btn-primary">Save Profile</button>
      </form>

      <form onSubmit={handlePasswordSubmit} className="card p-6 space-y-4">
        <h2 className="font-semibold text-ink-900 text-sm">Change Password</h2>
        {passwordMsg && <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 text-sm px-3 py-2"><Check size={15} /> {passwordMsg}</div>}
        {passwordError && <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2"><AlertCircle size={15} /> {passwordError}</div>}
        <div>
          <label className="label">Current Password</label>
          <input type="password" required className="input-field" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} />
        </div>
        <div>
          <label className="label">New Password (min 8 characters)</label>
          <input type="password" required minLength={8} className="input-field" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
        </div>
        <button type="submit" className="btn-primary">Update Password</button>
      </form>
    </div>
  );
}
