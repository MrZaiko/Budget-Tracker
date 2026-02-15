import { create } from 'zustand';

type Severity = 'success' | 'error' | 'warning' | 'info';

interface SnackbarMessage {
  id: string;
  message: string;
  severity: Severity;
}

interface SnackbarState {
  messages: SnackbarMessage[];
  showSnackbar: (message: string, severity?: Severity) => void;
  dismissSnackbar: (id: string) => void;
}

export const useSnackbarStore = create<SnackbarState>((set) => ({
  messages: [],
  showSnackbar: (message, severity = 'info') =>
    set((state) => ({
      messages: [
        ...state.messages,
        { id: crypto.randomUUID(), message, severity },
      ],
    })),
  dismissSnackbar: (id) =>
    set((state) => ({
      messages: state.messages.filter((m) => m.id !== id),
    })),
}));
