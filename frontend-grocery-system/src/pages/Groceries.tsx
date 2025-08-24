import { useEffect, useState } from "react";
import { GroceryAPI } from "../lib/api";
import { Layout } from "../components/Layout";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import type { Grocery } from "../interfaces";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";

export default function GroceriesPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [groceries, setGroceries] = useState<Grocery[]>([]);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    (async () => {
      const data = await GroceryAPI.list();
      setGroceries(data);
    })();
  }, [user, navigate]);

  const create = async () => {
    try {
      const g = await GroceryAPI.create({ name, location });
      setGroceries((prev) => [g, ...prev]);
      setName("");
      setLocation("");
    } catch (e: any) {
      setError(e?.response?.data?.error || "Failed to create grocery");
    }
  };

  const update = async (uid: string, next: { name?: string; location?: string }) => {
    try {
      const g = await GroceryAPI.update(uid, next);
      setGroceries((prev) => prev.map((x) => (x.uid === uid ? g : x)));
    } catch (e: any) {
      setError(e?.response?.data?.error || "Failed to update grocery");
    }
  };

  const remove = async (uid: string) => {
    try {
      await GroceryAPI.remove(uid);
      setGroceries((prev) => prev.filter((x) => x.uid !== uid));
    } catch (e: any) {
      setError(e?.response?.data?.error || "Failed to delete grocery");
    }
  };

  return (
    <Layout>
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>New Grocery</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-3">
              <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
              <Button onClick={create}>Create</Button>
            </div>
            {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
          </CardContent>
        </Card>
        <div className="grid gap-3">
          {groceries.map((g) => (
            <Card key={g.uid}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{g.name}</div>
                    <div className="text-sm text-gray-600">{g.location}</div>
                    {(g.created_at || g.updated_at) && (
                      <div className="text-xs text-gray-500">Created: {g.created_at} • Updated: {g.updated_at}</div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" onClick={() => update(g.uid, { name: prompt("New name", g.name) || g.name })}>Edit</Button>
                    <Button variant="ghost" onClick={() => update(g.uid, { location: prompt("New location", g.location) || g.location })}>Move</Button>
                    <Button variant="danger" onClick={() => remove(g.uid)}>Delete</Button>
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


