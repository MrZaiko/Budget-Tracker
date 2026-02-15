import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface LocalAuthState {
  token: string | null;
  expiresAt: number | null; // Unix seconds from JWT `exp`
  setToken: (token: string) => void;
  clearToken: () => void;
  isExpired: () => boolean;
}

function parseExp(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return typeof payload.exp === 'number' ? payload.exp : null;
  } catch {
    return null;
  }
}

export const useLocalAuthStore = create<LocalAuthState>()(
  persist(
    (set, get) => ({
      token: null,
      expiresAt: null,
      setToken: (token) => set({ token, expiresAt: parseExp(token) }),
      clearToken: () => set({ token: null, expiresAt: null }),
      isExpired: () => {
        const { expiresAt } = get();
        if (expiresAt === null) return false;
        return Date.now() / 1000 > expiresAt;
      },
    }),
    { name: 'local-auth' }
  )
);
