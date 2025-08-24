import { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { UsersAPI } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import type { ApiUser } from "../interfaces";

export default function UsersPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState<ApiUser[]>([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [groceryId, setGroceryId] = useState("");
  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    (async () => {
      setUsers(await UsersAPI.list());
    })();
  }, [user, navigate]);

  const createSupplier = async () => {
    try {
      await UsersAPI.createSupplier({ name, email, password, grocery_id: groceryId || undefined });
      setUsers(await UsersAPI.list());
      setName(""); setEmail(""); setPassword(""); setGroceryId("");
    } catch (e: any) { setError(e?.response?.data?.error || "Failed to create supplier"); }
  };

  const createAdmin = async () => {
    try {
      await UsersAPI.createAdmin({ name: adminName, email: adminEmail, password: adminPassword });
      setUsers(await UsersAPI.list());
      setAdminName(""); setAdminEmail(""); setAdminPassword("");
    } catch (e: any) { setError(e?.response?.data?.error || "Failed to create admin"); }
  };

  const deactivate = async (uid: string) => {
    try { await UsersAPI.deactivate(uid); setUsers(await UsersAPI.list()); } catch (e: any) { setError("Failed to deactivate"); }
  };

  const editUser = async (u: any) => {
    const newName = prompt("New name", u.name) ?? u.name;
    const newEmail = prompt("New email", u.email) ?? u.email;
    try { await UsersAPI.update(u.uid, { name: newName, email: newEmail }); setUsers(await UsersAPI.list()); } catch (e: any) { setError("Failed to update user"); }
  };

  return (
    <Layout>
      <h1 className="text-2xl font-semibold mb-4">Users</h1>
      {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
      <div className="grid gap-4 mb-6">
        <div className="grid grid-cols-4 gap-2">
          <input className="border rounded px-3 py-2" placeholder="Supplier Name" value={name} onChange={(e) => setName(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Supplier Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Grocery ID (optional)" value={groceryId} onChange={(e) => setGroceryId(e.target.value)} />
        </div>
        <div>
          <button className="bg-blue-600 text-white rounded px-3 py-2" onClick={createSupplier}>Create Supplier</button>
        </div>
        <div className="grid grid-cols-3 gap-2">
          <input className="border rounded px-3 py-2" placeholder="Admin Name" value={adminName} onChange={(e) => setAdminName(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Admin Email" value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Admin Password" type="password" value={adminPassword} onChange={(e) => setAdminPassword(e.target.value)} />
        </div>
        <div>
          <button className="bg-gray-800 text-white rounded px-3 py-2" onClick={createAdmin}>Create Admin</button>
        </div>
      </div>
      <ul className="grid gap-2">
        {users.map((u) => (
          <li key={u.uid} className="border rounded p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">{u.name} <span className="text-xs text-gray-500">({u.user_type})</span></div>
                <div className="text-sm text-gray-600">{u.email}</div>
                {(u.created_at || u.updated_at) && (
                  <div className="text-xs text-gray-500">Created: {u.created_at} • Updated: {u.updated_at}</div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button className="border rounded px-2 py-1" onClick={() => editUser(u)}>Edit</button>
                <button className="border rounded px-2 py-1" onClick={() => deactivate(u.uid)}>Deactivate</button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </Layout>
  );
}


