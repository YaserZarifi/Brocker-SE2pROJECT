// ============================================
// Core Domain Types - Brokerage System
// ============================================

export interface User {
  id: string;
  name: string;
  email: string;
  role: "customer" | "admin";
  walletAddress?: string;
  avatar?: string;
  createdAt: string;
}

export interface Stock {
  symbol: string;
  name: string;
  nameFa: string;
  currentPrice: number;
  previousClose: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  high24h: number;
  low24h: number;
  open: number;
  sector: string;
  sectorFa: string;
  logo?: string;
}

export type OrderType = "buy" | "sell";
export type OrderStatus = "pending" | "matched" | "partial" | "cancelled" | "expired";

export interface Order {
  id: string;
  userId: string;
  stockSymbol: string;
  stockName: string;
  type: OrderType;
  price: number;
  quantity: number;
  filledQuantity: number;
  status: OrderStatus;
  createdAt: string;
  updatedAt: string;
}

export interface Transaction {
  id: string;
  buyOrderId: string;
  sellOrderId: string;
  stockSymbol: string;
  stockName: string;
  price: number;
  quantity: number;
  totalValue: number;
  buyerId: string;
  sellerId: string;
  blockchainHash?: string;
  executedAt: string;
  status: "confirmed" | "pending" | "failed";
}

export interface PortfolioHolding {
  stockSymbol: string;
  stockName: string;
  stockNameFa: string;
  quantity: number;
  averageBuyPrice: number;
  currentPrice: number;
  totalValue: number;
  profitLoss: number;
  profitLossPercent: number;
}

export interface Portfolio {
  userId: string;
  holdings: PortfolioHolding[];
  totalValue: number;
  totalInvested: number;
  totalProfitLoss: number;
  totalProfitLossPercent: number;
  cashBalance: number;
}

export interface Notification {
  id: string;
  userId: string;
  title: string;
  titleFa: string;
  message: string;
  messageFa: string;
  type: "order_matched" | "order_cancelled" | "price_alert" | "system" | "transaction";
  read: boolean;
  createdAt: string;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
  total: number;
  count: number;
}

export interface OrderBook {
  symbol: string;
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  spread: number;
  spreadPercent: number;
}

export interface PriceHistory {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface MarketStats {
  totalStocks: number;
  totalVolume: number;
  totalMarketCap: number;
  gainers: number;
  losers: number;
  unchanged: number;
  indexValue: number;
  indexChange: number;
  indexChangePercent: number;
}

// Theme
export type Theme = "light" | "dark";
export type Language = "en" | "fa";
export type Direction = "ltr" | "rtl";
