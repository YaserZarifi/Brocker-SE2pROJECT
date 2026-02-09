import { create } from "zustand";
import type { Stock, MarketStats } from "@/types";
import { stockService } from "@/services/stockService";
import { generateRandomPrice } from "@/lib/utils";

interface StockState {
  stocks: Stock[];
  marketStats: MarketStats;
  searchQuery: string;
  selectedSector: string;
  sortBy: string;
  isLoading: boolean;
  error: string | null;
  setSearchQuery: (query: string) => void;
  setSelectedSector: (sector: string) => void;
  setSortBy: (sort: string) => void;
  getFilteredStocks: () => Stock[];
  simulatePriceUpdate: () => void;
  fetchStocks: () => Promise<void>;
  fetchMarketStats: () => Promise<void>;
}

const defaultMarketStats: MarketStats = {
  totalStocks: 0,
  totalVolume: 0,
  totalMarketCap: 0,
  gainers: 0,
  losers: 0,
  unchanged: 0,
  indexValue: 0,
  indexChange: 0,
  indexChangePercent: 0,
};

export const useStockStore = create<StockState>((set, get) => ({
  stocks: [],
  marketStats: defaultMarketStats,
  searchQuery: "",
  selectedSector: "all",
  sortBy: "symbol",
  isLoading: false,
  error: null,

  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSelectedSector: (selectedSector) => set({ selectedSector }),
  setSortBy: (sortBy) => set({ sortBy }),

  fetchStocks: async () => {
    set({ isLoading: true, error: null });
    try {
      const stocks = await stockService.getStocks();
      set({ stocks, isLoading: false });
    } catch (err: any) {
      set({ isLoading: false, error: "Failed to load stocks" });
    }
  },

  fetchMarketStats: async () => {
    try {
      const stats = await stockService.getMarketStats();
      set({ marketStats: stats });
    } catch {
      // Silently fail - stats are optional
    }
  },

  getFilteredStocks: () => {
    const { stocks, searchQuery, selectedSector, sortBy } = get();
    let filtered = [...stocks];

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.symbol.toLowerCase().includes(q) ||
          s.name.toLowerCase().includes(q) ||
          s.nameFa.includes(q)
      );
    }

    if (selectedSector !== "all") {
      filtered = filtered.filter((s) => s.sector === selectedSector);
    }

    switch (sortBy) {
      case "price_asc":
        filtered.sort((a, b) => a.currentPrice - b.currentPrice);
        break;
      case "price_desc":
        filtered.sort((a, b) => b.currentPrice - a.currentPrice);
        break;
      case "change_desc":
        filtered.sort((a, b) => b.changePercent - a.changePercent);
        break;
      case "change_asc":
        filtered.sort((a, b) => a.changePercent - b.changePercent);
        break;
      case "volume":
        filtered.sort((a, b) => b.volume - a.volume);
        break;
      default:
        filtered.sort((a, b) => a.symbol.localeCompare(b.symbol));
    }

    return filtered;
  },

  simulatePriceUpdate: () => {
    set((state) => ({
      stocks: state.stocks.map((stock) => {
        const newPrice = generateRandomPrice(stock.currentPrice, 0.005);
        const change = +(newPrice - stock.previousClose).toFixed(2);
        const changePercent = +((change / stock.previousClose) * 100).toFixed(2);
        return {
          ...stock,
          currentPrice: newPrice,
          change,
          changePercent,
          high24h: Math.max(stock.high24h, newPrice),
          low24h: Math.min(stock.low24h, newPrice),
        };
      }),
    }));
  },
}));
