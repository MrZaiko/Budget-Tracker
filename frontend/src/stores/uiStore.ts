import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  hasNetworkError: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setHasNetworkError: (has: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  hasNetworkError: false,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setHasNetworkError: (has) => set({ hasNetworkError: has }),
}));
