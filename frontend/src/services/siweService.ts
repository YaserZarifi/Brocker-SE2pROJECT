/**
 * SIWE (Sign-In with Ethereum) Service
 * Sprint 5 - EIP-4361 MetaMask Integration
 *
 * Flow:
 * 1. Request MetaMask account access
 * 2. Fetch nonce from backend
 * 3. Construct EIP-4361 message
 * 4. Ask MetaMask to sign the message
 * 5. Send signed message to backend for verification
 * 6. Receive JWT tokens
 */

import { BrowserProvider, getAddress } from "ethers";
import api, { setTokens } from "./api";
import type { User } from "@/types";

declare global {
  interface Window {
    ethereum?: any;
  }
}

export interface SiweLoginResult {
  user: User;
  access: string;
  refresh: string;
}

export const siweService = {
  /**
   * Check if MetaMask (or compatible wallet) is available.
   */
  isWalletAvailable(): boolean {
    return typeof window.ethereum !== "undefined";
  },

  /**
   * Request MetaMask to connect and return the selected account address.
   */
  async connectWallet(): Promise<string> {
    if (!this.isWalletAvailable()) {
      throw new Error("MetaMask is not installed. Please install MetaMask to use wallet login.");
    }

    try {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });

      if (!accounts || accounts.length === 0) {
        throw new Error("No accounts found. Please unlock MetaMask.");
      }

      // Convert to EIP-55 checksum format (MetaMask returns lowercase)
      return getAddress(accounts[0] as string);
    } catch (err: any) {
      if (err.code === 4001) {
        throw new Error("Connection rejected. Please approve the MetaMask connection.");
      }
      throw err;
    }
  },

  /**
   * Fetch a nonce from the backend for SIWE authentication.
   */
  async getNonce(): Promise<string> {
    const { data } = await api.get<{ nonce: string }>("/auth/siwe/nonce/");
    return data.nonce;
  },

  /**
   * Create an EIP-4361 SIWE message.
   */
  createSiweMessage(address: string, nonce: string): string {
    const domain = window.location.host;
    const origin = window.location.origin;
    const issuedAt = new Date().toISOString();

    // EIP-4361 message format
    return `${domain} wants you to sign in with your Ethereum account:
${address}

Sign in to BourseChain - Online Stock Brokerage Platform

URI: ${origin}
Version: 1
Chain ID: 1
Nonce: ${nonce}
Issued At: ${issuedAt}`;
  },

  /**
   * Sign a message using MetaMask (personal_sign).
   */
  async signMessage(message: string, address: string): Promise<string> {
    const provider = new BrowserProvider(window.ethereum);
    const signer = await provider.getSigner(address);
    const signature = await signer.signMessage(message);
    return signature;
  },

  /**
   * Complete SIWE flow: connect wallet → get nonce → sign → verify → get JWT.
   */
  async loginWithEthereum(): Promise<SiweLoginResult> {
    // Step 1: Connect wallet
    const address = await this.connectWallet();

    // Step 2: Get nonce from backend
    const nonce = await this.getNonce();

    // Step 3: Create EIP-4361 message
    const message = this.createSiweMessage(address, nonce);

    // Step 4: Sign message with MetaMask
    const signature = await this.signMessage(message, address);

    // Step 5: Verify with backend and get JWT tokens
    const { data } = await api.post<{
      access: string;
      refresh: string;
      user: User;
    }>("/auth/siwe/verify/", {
      message,
      signature,
    });

    // Step 6: Store tokens
    setTokens(data.access, data.refresh);

    return {
      user: data.user,
      access: data.access,
      refresh: data.refresh,
    };
  },
};
