import api from "./api";
import type { Transaction } from "@/types";

// ============================================
// Transaction Service - Transaction APIs
// ============================================

export const transactionService = {
  async getTransactions(): Promise<Transaction[]> {
    const { data } = await api.get<{ results: Transaction[] }>("/transactions/");
    const txs = Array.isArray(data) ? data : data.results;
    return txs.map(normalizeTx);
  },
};

function normalizeTx(tx: Transaction): Transaction {
  return {
    ...tx,
    price: Number(tx.price),
    quantity: Number(tx.quantity),
    totalValue: Number(tx.totalValue),
  };
}
