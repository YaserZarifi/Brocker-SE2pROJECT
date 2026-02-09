import api from "./api";
import type { Order, Portfolio, OrderBook } from "@/types";

// ============================================
// Order Service - Orders + Portfolio APIs
// ============================================

export interface CreateOrderPayload {
  stock_symbol: string;
  type: "buy" | "sell";
  price: number;
  quantity: number;
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
    const { data } = await api.get<Portfolio>("/orders/portfolio/");
    return normalizePortfolio(data);
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

function normalizePortfolio(p: Portfolio): Portfolio {
  return {
    ...p,
    totalValue: Number(p.totalValue),
    totalInvested: Number(p.totalInvested),
    totalProfitLoss: Number(p.totalProfitLoss),
    totalProfitLossPercent: Number(p.totalProfitLossPercent),
    cashBalance: Number(p.cashBalance),
    holdings: p.holdings.map((h) => ({
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
