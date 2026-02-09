import { create } from "zustand";
import type { User } from "@/types";
import { mockUser } from "@/services/mockData";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithEthereum: (address: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (_email: string, _password: string) => {
    set({ isLoading: true });
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1000));
    set({
      user: mockUser,
      isAuthenticated: true,
      isLoading: false,
    });
  },

  loginWithEthereum: async (address: string) => {
    set({ isLoading: true });
    await new Promise((r) => setTimeout(r, 1500));
    set({
      user: { ...mockUser, walletAddress: address },
      isAuthenticated: true,
      isLoading: false,
    });
  },

  register: async (name: string, email: string, _password: string) => {
    set({ isLoading: true });
    await new Promise((r) => setTimeout(r, 1200));
    set({
      user: { ...mockUser, name, email },
      isAuthenticated: true,
      isLoading: false,
    });
  },

  logout: () => {
    set({ user: null, isAuthenticated: false });
  },
}));
