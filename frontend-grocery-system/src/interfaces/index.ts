export interface ApiUser {
  uid: string;
  name: string;
  email: string;
  user_type: 'admin' | 'supplier';
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Grocery {
  uid: string;
  name: string;
  location: string;
  supplier_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Item {
  uid: string;
  name: string;
  item_type: string;
  item_location: string;
  price: number;
  created_at?: string;
  updated_at?: string;
}

export interface DailyIncome {
  uid: string;
  date: string;
  amount: number;
  grocery_name?: string;
  recorded_by_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface LoginResponse {
  user: ApiUser;
  tokens: { access: string; refresh: string };
}


