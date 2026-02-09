import api from "./api";
import type { Stock, PriceHistory, MarketStats, OrderBook } from "@/types";

// ============================================
// Stock Service - Stock Market APIs
// ============================================

export const stockService = {
  async getStocks(): Promise<Stock[]> {
    const { data } = await api.get<Stock[]>("/stocks/");
    return data.map(normalizeStock);
  },

  async getStock(symbol: string): Promise<Stock> {
    const { data } = await api.get<Stock>(`/stocks/${symbol}/`);
    return normalizeStock(data);
  },

  async getPriceHistory(symbol: string, days = 30): Promise<PriceHistory[]> {
    const { data } = await api.get<PriceHistory[]>(
      `/stocks/${symbol}/history/`,
      { params: { days } }
    );
    return data;
  },

  async getMarketStats(): Promise<MarketStats> {
    const { data } = await api.get<MarketStats>("/stocks/stats/");
    return data;
  },
};

/** Ensure numeric fields are numbers (DRF returns decimals as strings) */
function normalizeStock(s: Stock): Stock {
  return {
    ...s,
    currentPrice: Number(s.currentPrice),
    previousClose: Number(s.previousClose),
    change: Number(s.change),
    changePercent: Number(s.changePercent),
    volume: Number(s.volume),
    marketCap: Number(s.marketCap),
    high24h: Number(s.high24h),
    low24h: Number(s.low24h),
    open: Number(s.open),
  };
}
