import { Link } from "react-router-dom";
import { useAuth } from "../lib/auth";

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const isAdmin = user?.user_type === "admin";

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="sticky top-0 z-10 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="font-semibold">Grocery System</Link>
            {isAdmin ? (
              <div className="flex items-center gap-4 text-sm text-gray-700">
                <Link to="/groceries">Groceries</Link>
                <Link to="/users">Users</Link>
                <Link to="/items">Items</Link>
                <Link to="/incomes">Daily Income</Link>
              </div>
            ) : (
              <div className="flex items-center gap-4 text-sm text-gray-700">
                <Link to="/items">Items</Link>
                <Link to="/incomes">Daily Income</Link>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button className="bg-gray-900 text-white rounded-md h-9 px-3" onClick={logout}>Logout</button>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto p-6">{children}</main>
    </div>
  );
}


