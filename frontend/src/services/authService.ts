import api, { setTokens, clearTokens } from "./api";
import type { User } from "@/types";

// ============================================
// Auth Service - User Authentication APIs
// ============================================

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  wallet_address?: string;
}

export interface ProfileResponse {
  id: string;
  name: string;
  username: string;
  email: string;
  role: "customer" | "admin";
  wallet_address: string | null;
  avatar: string | null;
  cash_balance: string;
  date_joined: string;
}

function mapProfileToUser(profile: ProfileResponse): User {
  return {
    id: profile.id,
    name: profile.name,
    email: profile.email,
    role: profile.role,
    walletAddress: profile.wallet_address || undefined,
    avatar: profile.avatar || undefined,
    createdAt: profile.date_joined,
  };
}

export const authService = {
  async login(email: string, password: string): Promise<User> {
    // Step 1: Get JWT tokens
    const { data: tokens } = await api.post<LoginResponse>("/auth/login/", {
      email,
      password,
    });
    setTokens(tokens.access, tokens.refresh);

    // Step 2: Fetch user profile
    const { data: profile } = await api.get<ProfileResponse>("/auth/profile/");
    return mapProfileToUser(profile);
  },

  async register(payload: RegisterPayload): Promise<User> {
    // Step 1: Register
    const { data } = await api.post("/auth/register/", payload);

    // Step 2: Auto-login after registration
    const { data: tokens } = await api.post<LoginResponse>("/auth/login/", {
      email: payload.email,
      password: payload.password,
    });
    setTokens(tokens.access, tokens.refresh);

    // Step 3: Fetch profile
    const { data: profile } = await api.get<ProfileResponse>("/auth/profile/");
    return mapProfileToUser(profile);
  },

  async getProfile(): Promise<User> {
    const { data: profile } = await api.get<ProfileResponse>("/auth/profile/");
    return mapProfileToUser(profile);
  },

  logout() {
    clearTokens();
  },
};
