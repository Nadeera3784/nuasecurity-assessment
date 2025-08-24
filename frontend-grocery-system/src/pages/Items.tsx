import { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { ItemsAPI } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useNavigate } from "react-router-dom";
import type { Item } from "../interfaces";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";

export default function ItemsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [location, setLocation] = useState("");
  const [price, setPrice] = useState("");
  const [groceryId, setGroceryId] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }
    (async () => {
      setItems(await ItemsAPI.list());
    })();
  }, [user, navigate]);

  const create = async () => {
    try {
      const payload = {
        name,
        item_type: type,
        item_location: location,
        price: Number(price),
        grocery_id: groceryId,
      };
      const item = await ItemsAPI.create(payload);
      setItems((prev) => [item, ...prev]);
      setName(""); setType(""); setLocation(""); setPrice(""); setGroceryId("");
    } catch (e: any) { setError(e?.response?.data?.error || "Failed to create item"); }
  };

  const update = async (uid: string, next: any) => {
    try { const it = await ItemsAPI.update(uid, next); setItems((prev) => prev.map((x) => x.uid === uid ? it : x)); } catch (e: any) { setError("Failed to update item"); }
  };
  const remove = async (uid: string) => {
    try { await ItemsAPI.remove(uid); setItems((prev) => prev.filter((x) => x.uid !== uid)); } catch (e: any) { setError("Failed to delete item"); }
  };

  return (
    <Layout>
      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>New Item</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-5 gap-3">
              <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input placeholder="Type" value={type} onChange={(e) => setType(e.target.value)} />
              <Input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
              <Input placeholder="Price" value={price} onChange={(e) => setPrice(e.target.value)} />
              <Input placeholder="Grocery ID" value={groceryId} onChange={(e) => setGroceryId(e.target.value)} />
            </div>
            {error && <div className="text-red-600 text-sm mt-2">{error}</div>}
            <div className="mt-3">
              <Button onClick={create}>Add Item</Button>
            </div>
          </CardContent>
        </Card>
        <div className="grid gap-3">
          {items.map((it) => (
            <Card key={it.uid}>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{it.name}</div>
                    <div className="text-sm text-gray-600">{it.item_type} • {it.item_location} • ${'{'}it.price{'}'}</div>
                    {(it.created_at || it.updated_at) && (
                      <div className="text-xs text-gray-500">Created: {it.created_at} • Updated: {it.updated_at}</div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" onClick={() => {
                      const next = prompt("New price", String(it.price));
                      if (next == null) return;
                      const num = Number(next);
                      if (!Number.isFinite(num)) return;
                      update(it.uid, { price: num })
                    }}>Edit</Button>
                    <Button variant="danger" onClick={() => remove(it.uid)}>Delete</Button>
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


