import { useEffect, useState } from "react";
import { GroceryAPI } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import { Layout } from "../components/Layout";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [groceries, setGroceries] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    (async () => {
      try {
        const data = await GroceryAPI.list();
        setGroceries(data);
      } catch (e: any) {
        setError(e?.response?.data?.error || "Failed to load groceries");
      }
    })();
  }, [user, navigate]);

  return (
    <Layout>
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
      <h2 className="text-lg font-medium mt-6 mb-2">Groceries</h2>
      <ul className="grid gap-2">
        {groceries.map((g) => (
          <li key={g.uid} className="border rounded p-3">
            <div className="font-medium">{g.name}</div>
            <div className="text-sm text-gray-600">{g.location} {g.supplier_name ? `(Supplier: ${g.supplier_name})` : ""}</div>
          </li>
        ))}
      </ul>
    </Layout>
  );
}


