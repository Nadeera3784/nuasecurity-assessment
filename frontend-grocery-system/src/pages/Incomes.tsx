import { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { IncomesAPI } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import type { DailyIncome } from "../interfaces";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";

export default function IncomesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [incomes, setIncomes] = useState<DailyIncome[]>([]);
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState<string>(() => new Date().toISOString());
  const [groceryId, setGroceryId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return navigate("/login");
    (async () => {
      setIncomes(await IncomesAPI.list());
    })();
  }, [user, navigate]);

  const load = async () => {
    try {
      const data = await IncomesAPI.list(groceryId ? { grocery_id: groceryId } : undefined);
      setIncomes(data);
    } catch (e: any) { setError("Failed to load incomes"); }
  };

  const create = async () => {
    try {
      const payload: any = { date, amount: Number(amount) };
      if (groceryId) payload.grocery_id = groceryId;
      const inc = await IncomesAPI.create(payload);
      setIncomes((prev) => [inc, ...prev]);
      setAmount("");
    } catch (e: any) { setError(e?.response?.data?.error || "Failed to add income"); }
  };

  return (
    <Layout>
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Record Income</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-5 gap-3">
              <Input placeholder="Amount" value={amount} onChange={(e) => setAmount(e.target.value)} />
              <Input placeholder="ISO Date" value={date} onChange={(e) => setDate(e.target.value)} />
              <Input placeholder="Grocery ID (admin only)" value={groceryId} onChange={(e) => setGroceryId(e.target.value)} />
              <Button onClick={create}>Add Income</Button>
              <Button variant="ghost" onClick={load}>Filter</Button>
            </div>
            {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
          </CardContent>
        </Card>
        <div className="grid gap-3">
          {incomes.map((it) => (
            <Card key={it.uid}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{it.amount}</div>
                    <div className="text-sm text-gray-600">{it.date} {it.grocery_name ? `• ${it.grocery_name}` : ""}</div>
                    {(it.created_at || it.updated_at) && (
                      <div className="text-xs text-gray-500">Created: {it.created_at} • Updated: {it.updated_at}</div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </Layout>
  );
}


