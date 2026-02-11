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
  first_name: string;
  last_name: string;
  email: string;
  role: "customer" | "admin";
  wallet_address: string | null;
  avatar: string | null;
  cash_balance: string;
  date_joined: string;
}

export interface UpdateProfilePayload {
  first_name: string;
  last_name: string;
  username: string;
  wallet_address?: string;
  avatar?: File;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

function mapProfileToUser(profile: ProfileResponse): User {
  const name =
    [profile.first_name, profile.last_name].filter(Boolean).join(" ") ||
    profile.name ||
    profile.username;
  return {
    id: profile.id,
    name,
    email: profile.email,
    username: profile.username,
    firstName: profile.first_name || undefined,
    lastName: profile.last_name || undefined,
    role: profile.role,
    walletAddress: profile.wallet_address || undefined,
    avatar: profile.avatar || undefined,
    cashBalance: profile.cash_balance,
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

  async updateProfile(payload: UpdateProfilePayload): Promise<User> {
    const formData = new FormData();
    formData.append("first_name", payload.first_name);
    formData.append("last_name", payload.last_name);
    formData.append("username", payload.username);
    if (payload.wallet_address !== undefined) {
      formData.append("wallet_address", payload.wallet_address || "");
    }
    if (payload.avatar) {
      formData.append("avatar", payload.avatar);
    }
    const { data: profile } = await api.patch<ProfileResponse>(
      "/auth/profile/",
      formData
    );
    return mapProfileToUser(profile);
  },

  async changePassword(payload: ChangePasswordPayload): Promise<void> {
    await api.put("/auth/change-password/", payload);
  },

  logout() {
    clearTokens();
  },
};
