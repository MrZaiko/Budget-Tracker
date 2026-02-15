export interface User {
  id: string;
  sub: string;
  email: string;
  display_name: string;
  base_currency: string;
  auth_provider: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserUpdate {
  display_name?: string;
  base_currency?: string;
}
