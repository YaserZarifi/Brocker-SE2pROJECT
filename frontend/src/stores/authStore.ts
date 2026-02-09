import { create } from "zustand";
import type { User } from "@/types";
import { authService } from "@/services/authService";
import { siweService } from "@/services/siweService";
import { getAccessToken } from "@/services/api";
import { wsManager } from "@/services/websocketService";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  loginWithEthereum: () => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const user = await authService.login(email, password);
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      const message =
        err.response?.data?.detail || "Login failed. Check your credentials.";
      set({ isLoading: false, error: message });
      throw new Error(message);
    }
  },

  loginWithEthereum: async () => {
    set({ isLoading: true, error: null });
    try {
      // Check if MetaMask is available
      if (!siweService.isWalletAvailable()) {
        throw new Error(
          "MetaMask is not installed. Please install MetaMask browser extension."
        );
      }

      // Complete SIWE flow: connect → sign → verify → JWT
      const result = await siweService.loginWithEthereum();

      set({
        user: result.user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      const message =
        err.response?.data?.detail ||
        err.message ||
        "Ethereum login failed.";
      set({ isLoading: false, error: message });
      throw new Error(message);
    }
  },

  register: async (name: string, email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const [firstName, ...lastParts] = name.split(" ");
      const lastName = lastParts.join(" ");
      const user = await authService.register({
        username: email.split("@")[0],
        email,
        password,
        password_confirm: password,
        first_name: firstName,
        last_name: lastName,
      });
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      const message =
        err.response?.data?.email?.[0] ||
        err.response?.data?.username?.[0] ||
        err.response?.data?.password?.[0] ||
        "Registration failed.";
      set({ isLoading: false, error: message });
      throw new Error(message);
    }
  },

  logout: () => {
    authService.logout();
    wsManager.disconnectAll();
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const user = await authService.getProfile();
      set({ user, isAuthenticated: true });
    } catch {
      // Token expired or invalid
      authService.logout();
    }
  },
}));
