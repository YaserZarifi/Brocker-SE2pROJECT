import api from "./api";
import type { Order, Portfolio, OrderBook } from "@/types";

// ============================================
// Order Service - Orders + Portfolio APIs
// ============================================

export interface CreateOrderPayload {
  stock_symbol: string;
  type: "buy" | "sell";
  execution_type?: "limit" | "market" | "stop_loss" | "take_profit";
  price?: number;
  quantity: number;
  trigger_price?: number;
}

export const orderService = {
  async getOrders(): Promise<Order[]> {
    const { data } = await api.get<{ results: Order[] }>("/orders/");
    // DRF pagination wraps in {results, count, ...}, but if no pagination returns array
    const orders = Array.isArray(data) ? data : data.results;
    return orders.map(normalizeOrder);
  },

  async createOrder(payload: CreateOrderPayload): Promise<Order> {
    const { data } = await api.post<Order>("/orders/create/", payload);
    return normalizeOrder(data);
  },

  async cancelOrder(id: string): Promise<Order> {
    const { data } = await api.put<Order>(`/orders/${id}/cancel/`);
    return normalizeOrder(data);
  },

  async getPortfolio(): Promise<Portfolio> {
    const { data } = await api.get<Record<string, unknown>>("/orders/portfolio/");
    return normalizePortfolio(toPortfolioShape(data));
  },

  async getOrderBook(symbol: string): Promise<OrderBook> {
    const { data } = await api.get<OrderBook>(`/orders/book/${symbol}/`);
    return data;
  },
};

function normalizeOrder(o: Order): Order {
  return {
    ...o,
    price: Number(o.price),
    quantity: Number(o.quantity),
    filledQuantity: Number(o.filledQuantity),
  };
}

/** Normalize API response (handles both camelCase and snake_case from backend). */
function toPortfolioShape(raw: Record<string, unknown>): Portfolio {
  const hv = (v: unknown) => (v ?? 0) as number;
  const arr = raw.holdings as unknown[];
  const holdings = Array.isArray(arr) ? arr : [];

  return {
    userId: String(raw.userId ?? raw.user_id ?? ""),
    totalValue: hv(raw.totalValue ?? raw.total_value),
    totalInvested: hv(raw.totalInvested ?? raw.total_invested),
    totalProfitLoss: hv(raw.totalProfitLoss ?? raw.total_profit_loss),
    totalProfitLossPercent: hv(raw.totalProfitLossPercent ?? raw.total_profit_loss_percent),
    cashBalance: hv(raw.cashBalance ?? raw.cash_balance),
    holdings: holdings.map((h) => toHoldingShape(h as Record<string, unknown>)),
  };
}

function toHoldingShape(h: Record<string, unknown>): Portfolio["holdings"][0] {
  const n = (v: unknown) => Number(v ?? 0);
  return {
    stockSymbol: String(h.stockSymbol ?? h.stock_symbol ?? ""),
    stockName: String(h.stockName ?? h.stock_name ?? ""),
    stockNameFa: String(h.stockNameFa ?? h.stock_name_fa ?? ""),
    quantity: n(h.quantity),
    averageBuyPrice: n(h.averageBuyPrice ?? h.average_buy_price),
    currentPrice: n(h.currentPrice ?? h.current_price),
    totalValue: n(h.totalValue ?? h.total_value),
    profitLoss: n(h.profitLoss ?? h.profit_loss),
    profitLossPercent: n(h.profitLossPercent ?? h.profit_loss_percent),
  };
}

function normalizePortfolio(p: Portfolio): Portfolio {
  return {
    ...p,
    totalValue: Number(p.totalValue),
    totalInvested: Number(p.totalInvested),
    totalProfitLoss: Number(p.totalProfitLoss),
    totalProfitLossPercent: Number(p.totalProfitLossPercent),
    cashBalance: Number(p.cashBalance),
    holdings: (p.holdings ?? []).map((h) => ({
      ...h,
      quantity: Number(h.quantity),
      averageBuyPrice: Number(h.averageBuyPrice),
      currentPrice: Number(h.currentPrice),
      totalValue: Number(h.totalValue),
      profitLoss: Number(h.profitLoss),
      profitLossPercent: Number(h.profitLossPercent),
    })),
  };
}
