import axios from "axios";
import type { LoginResponse, Grocery as GroceryT, ApiUser, Item as ItemT, DailyIncome as IncomeT } from "../interfaces";

const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers || {};
    (config.headers as any)["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

export const AuthAPI = {
  async login(payload: { email: string; password: string }): Promise<LoginResponse> {
    const { data } = await api.post<LoginResponse>("/auth/login/", payload);
    return data;
  },
  async profile() {
    const { data } = await api.get("/auth/profile/");
    return data;
  },
};

export const GroceryAPI = {
  async list() {
    const { data } = await api.get("/groceries/");
    return data as GroceryT[];
  },
  async create(payload: { name: string; location: string }) {
    const { data } = await api.post("/groceries/", payload);
    return data;
  },
  async update(uid: string, payload: Partial<{ name: string; location: string; is_active: boolean }>) {
    const { data } = await api.put(`/groceries/${uid}/`, payload);
    return data;
  },
  async remove(uid: string) {
    const { data } = await api.delete(`/groceries/${uid}/`);
    return data;
  },
  async assignSupplier(uid: string, supplier_id: string) {
    const { data } = await api.post(`/groceries/${uid}/assign_supplier/`, { supplier_id });
    return data;
  },
};

export const UsersAPI = {
  async list() {
    const { data } = await api.get("/users/");
    return data as ApiUser[];
  },
  async update(uid: string, payload: Partial<{ name: string; email: string; is_active: boolean }>) {
    const { data } = await api.put(`/users/${uid}/`, payload);
    return data;
  },
  async deactivate(uid: string) {
    const { data } = await api.delete(`/users/${uid}/`);
    return data;
  },
  async createSupplier(payload: { name: string; email: string; password: string; grocery_id?: string }) {
    const { data } = await api.post(`/auth/register/supplier/`, payload);
    return data;
  },
  async createAdmin(payload: { name: string; email: string; password: string }) {
    const { data } = await api.post(`/auth/register/admin/`, payload);
    return data;
  },
};

export const ItemsAPI = {
  async list(params?: { grocery_id?: string }) {
    const { data } = await api.get(`/items/`, { params });
    return data as ItemT[];
  },
  async create(payload: { name: string; item_type: string; item_location: string; price: number; grocery_id: string }) {
    const { data } = await api.post(`/items/`, payload);
    return data;
  },
  async update(uid: string, payload: Partial<{ name: string; item_type: string; item_location: string; price: number }>) {
    const { data } = await api.put(`/items/${uid}/`, payload);
    return data;
  },
  async remove(uid: string) {
    const { data } = await api.delete(`/items/${uid}/`);
    return data;
  },
};

export const IncomesAPI = {
  async list(params?: { grocery_id?: string }) {
    const { data } = await api.get(`/daily-income/`, { params });
    return data as IncomeT[];
  },
  async create(payload: { date: string; amount: number; grocery_id?: string }) {
    const { data } = await api.post(`/daily-income/`, payload);
    return data;
  },
  async get(uid: string) {
    const { data } = await api.get(`/daily-income/${uid}/`);
    return data;
  },
};


