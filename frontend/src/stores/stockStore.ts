import { create } from "zustand";
import type { Stock, MarketStats } from "@/types";
import { mockStocks, mockMarketStats } from "@/services/mockData";
import { generateRandomPrice } from "@/lib/utils";

interface StockState {
  stocks: Stock[];
  marketStats: MarketStats;
  searchQuery: string;
  selectedSector: string;
  sortBy: string;
  isLoading: boolean;
  setSearchQuery: (query: string) => void;
  setSelectedSector: (sector: string) => void;
  setSortBy: (sort: string) => void;
  getFilteredStocks: () => Stock[];
  simulatePriceUpdate: () => void;
}

export const useStockStore = create<StockState>((set, get) => ({
  stocks: mockStocks,
  marketStats: mockMarketStats,
  searchQuery: "",
  selectedSector: "all",
  sortBy: "symbol",
  isLoading: false,

  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setSelectedSector: (selectedSector) => set({ selectedSector }),
  setSortBy: (sortBy) => set({ sortBy }),

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
