import type {
  Stock,
  Order,
  Transaction,
  Portfolio,
  Notification,
  OrderBook,
  PriceHistory,
  MarketStats,
  User,
} from "@/types";

// ============================================
// Mock Stocks
// ============================================
export const mockStocks: Stock[] = [
  {
    symbol: "FOLD",
    name: "Foolad Mobarakeh",
    nameFa: "فولاد مبارکه",
    currentPrice: 8750,
    previousClose: 8520,
    change: 230,
    changePercent: 2.7,
    volume: 45_200_000,
    marketCap: 2_625_000_000,
    high24h: 8820,
    low24h: 8490,
    open: 8530,
    sector: "Metals & Mining",
    sectorFa: "فلزات و معادن",
  },
  {
    symbol: "SHPN",
    name: "Pars Oil Refinery",
    nameFa: "شپنا - پالایش نفت",
    currentPrice: 4320,
    previousClose: 4480,
    change: -160,
    changePercent: -3.57,
    volume: 38_100_000,
    marketCap: 1_296_000_000,
    high24h: 4510,
    low24h: 4290,
    open: 4470,
    sector: "Energy",
    sectorFa: "انرژی",
  },
  {
    symbol: "KGDR",
    name: "Gol Gohar Mining",
    nameFa: "کگل - گل‌گهر",
    currentPrice: 12450,
    previousClose: 12200,
    change: 250,
    changePercent: 2.05,
    volume: 22_800_000,
    marketCap: 4_980_000_000,
    high24h: 12580,
    low24h: 12180,
    open: 12220,
    sector: "Metals & Mining",
    sectorFa: "فلزات و معادن",
  },
  {
    symbol: "FMLI",
    name: "National Copper",
    nameFa: "فملی - ملی مس",
    currentPrice: 6780,
    previousClose: 6650,
    change: 130,
    changePercent: 1.95,
    volume: 31_500_000,
    marketCap: 3_390_000_000,
    high24h: 6830,
    low24h: 6620,
    open: 6660,
    sector: "Metals & Mining",
    sectorFa: "فلزات و معادن",
  },
  {
    symbol: "SHBN",
    name: "Bandar Abbas Refinery",
    nameFa: "شبندر - پالایش بندرعباس",
    currentPrice: 3890,
    previousClose: 4010,
    change: -120,
    changePercent: -2.99,
    volume: 28_900_000,
    marketCap: 1_167_000_000,
    high24h: 4030,
    low24h: 3860,
    open: 4000,
    sector: "Energy",
    sectorFa: "انرژی",
  },
  {
    symbol: "IKCO",
    name: "Iran Khodro",
    nameFa: "خودرو - ایران خودرو",
    currentPrice: 2150,
    previousClose: 2080,
    change: 70,
    changePercent: 3.37,
    volume: 89_400_000,
    marketCap: 6_450_000_000,
    high24h: 2190,
    low24h: 2060,
    open: 2090,
    sector: "Automotive",
    sectorFa: "خودرو",
  },
  {
    symbol: "SSEP",
    name: "Sepah Bank",
    nameFa: "وسپه - بانک سپه",
    currentPrice: 1540,
    previousClose: 1560,
    change: -20,
    changePercent: -1.28,
    volume: 15_600_000,
    marketCap: 924_000_000,
    high24h: 1575,
    low24h: 1520,
    open: 1555,
    sector: "Banking",
    sectorFa: "بانکداری",
  },
  {
    symbol: "TAPK",
    name: "TAPICO Holding",
    nameFa: "تاپیکو",
    currentPrice: 9870,
    previousClose: 9640,
    change: 230,
    changePercent: 2.39,
    volume: 18_200_000,
    marketCap: 3_948_000_000,
    high24h: 9920,
    low24h: 9600,
    open: 9650,
    sector: "Petrochemical",
    sectorFa: "پتروشیمی",
  },
  {
    symbol: "PTRO",
    name: "Petrol Group",
    nameFa: "پترول - گروه پتروشیمی",
    currentPrice: 5430,
    previousClose: 5310,
    change: 120,
    changePercent: 2.26,
    volume: 25_700_000,
    marketCap: 2_172_000_000,
    high24h: 5480,
    low24h: 5280,
    open: 5320,
    sector: "Petrochemical",
    sectorFa: "پتروشیمی",
  },
  {
    symbol: "MKBT",
    name: "Mobin Telecom",
    nameFa: "همراه اول",
    currentPrice: 7250,
    previousClose: 7380,
    change: -130,
    changePercent: -1.76,
    volume: 12_300_000,
    marketCap: 4_350_000_000,
    high24h: 7410,
    low24h: 7200,
    open: 7370,
    sector: "Telecom",
    sectorFa: "مخابرات",
  },
  {
    symbol: "SSAN",
    name: "Saipa Auto",
    nameFa: "خساپا - سایپا",
    currentPrice: 1820,
    previousClose: 1790,
    change: 30,
    changePercent: 1.68,
    volume: 72_100_000,
    marketCap: 3_640_000_000,
    high24h: 1850,
    low24h: 1780,
    open: 1795,
    sector: "Automotive",
    sectorFa: "خودرو",
  },
  {
    symbol: "ZINC",
    name: "Iran Zinc Mines",
    nameFa: "فزر - زنگان روی",
    currentPrice: 15680,
    previousClose: 15200,
    change: 480,
    changePercent: 3.16,
    volume: 8_900_000,
    marketCap: 1_568_000_000,
    high24h: 15750,
    low24h: 15150,
    open: 15220,
    sector: "Metals & Mining",
    sectorFa: "فلزات و معادن",
  },
];

// ============================================
// Mock User
// ============================================
export const mockUser: User = {
  id: "user-001",
  name: "Ali Rezaei",
  email: "ali@example.com",
  role: "customer",
  walletAddress: "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
  avatar: undefined,
  createdAt: "2025-06-15T10:30:00Z",
};

// ============================================
// Mock Portfolio
// ============================================
export const mockPortfolio: Portfolio = {
  userId: "user-001",
  holdings: [
    {
      stockSymbol: "FOLD",
      stockName: "Foolad Mobarakeh",
      stockNameFa: "فولاد مبارکه",
      quantity: 500,
      averageBuyPrice: 8200,
      currentPrice: 8750,
      totalValue: 4_375_000,
      profitLoss: 275_000,
      profitLossPercent: 6.71,
    },
    {
      stockSymbol: "IKCO",
      stockName: "Iran Khodro",
      stockNameFa: "ایران خودرو",
      quantity: 2000,
      averageBuyPrice: 1950,
      currentPrice: 2150,
      totalValue: 4_300_000,
      profitLoss: 400_000,
      profitLossPercent: 10.26,
    },
    {
      stockSymbol: "SHPN",
      stockName: "Pars Oil Refinery",
      stockNameFa: "شپنا",
      quantity: 800,
      averageBuyPrice: 4600,
      currentPrice: 4320,
      totalValue: 3_456_000,
      profitLoss: -224_000,
      profitLossPercent: -6.09,
    },
    {
      stockSymbol: "TAPK",
      stockName: "TAPICO Holding",
      stockNameFa: "تاپیکو",
      quantity: 300,
      averageBuyPrice: 9400,
      currentPrice: 9870,
      totalValue: 2_961_000,
      profitLoss: 141_000,
      profitLossPercent: 5.0,
    },
    {
      stockSymbol: "KGDR",
      stockName: "Gol Gohar Mining",
      stockNameFa: "کگل",
      quantity: 150,
      averageBuyPrice: 11800,
      currentPrice: 12450,
      totalValue: 1_867_500,
      profitLoss: 97_500,
      profitLossPercent: 5.51,
    },
  ],
  totalValue: 16_959_500,
  totalInvested: 16_270_000,
  totalProfitLoss: 689_500,
  totalProfitLossPercent: 4.24,
  cashBalance: 5_340_500,
};

// ============================================
// Mock Orders
// ============================================
export const mockOrders: Order[] = [
  {
    id: "ORD-001",
    userId: "user-001",
    stockSymbol: "FOLD",
    stockName: "Foolad Mobarakeh",
    type: "buy",
    price: 8700,
    quantity: 200,
    filledQuantity: 200,
    status: "matched",
    createdAt: "2026-02-09T09:30:00Z",
    updatedAt: "2026-02-09T09:31:15Z",
  },
  {
    id: "ORD-002",
    userId: "user-001",
    stockSymbol: "SHPN",
    stockName: "Pars Oil Refinery",
    type: "sell",
    price: 4350,
    quantity: 300,
    filledQuantity: 0,
    status: "pending",
    createdAt: "2026-02-09T10:15:00Z",
    updatedAt: "2026-02-09T10:15:00Z",
  },
  {
    id: "ORD-003",
    userId: "user-001",
    stockSymbol: "IKCO",
    stockName: "Iran Khodro",
    type: "buy",
    price: 2100,
    quantity: 500,
    filledQuantity: 350,
    status: "partial",
    createdAt: "2026-02-09T08:45:00Z",
    updatedAt: "2026-02-09T09:10:22Z",
  },
  {
    id: "ORD-004",
    userId: "user-001",
    stockSymbol: "KGDR",
    stockName: "Gol Gohar Mining",
    type: "buy",
    price: 12300,
    quantity: 100,
    filledQuantity: 100,
    status: "matched",
    createdAt: "2026-02-08T14:20:00Z",
    updatedAt: "2026-02-08T14:22:45Z",
  },
  {
    id: "ORD-005",
    userId: "user-001",
    stockSymbol: "SSAN",
    stockName: "Saipa Auto",
    type: "sell",
    price: 1900,
    quantity: 1000,
    filledQuantity: 0,
    status: "cancelled",
    createdAt: "2026-02-07T11:00:00Z",
    updatedAt: "2026-02-07T16:00:00Z",
  },
  {
    id: "ORD-006",
    userId: "user-001",
    stockSymbol: "PTRO",
    stockName: "Petrol Group",
    type: "buy",
    price: 5400,
    quantity: 400,
    filledQuantity: 0,
    status: "pending",
    createdAt: "2026-02-09T11:30:00Z",
    updatedAt: "2026-02-09T11:30:00Z",
  },
];

// ============================================
// Mock Transactions
// ============================================
export const mockTransactions: Transaction[] = [
  {
    id: "TX-001",
    buyOrderId: "ORD-001",
    sellOrderId: "ORD-EXT-101",
    stockSymbol: "FOLD",
    stockName: "Foolad Mobarakeh",
    price: 8700,
    quantity: 200,
    totalValue: 1_740_000,
    buyerId: "user-001",
    sellerId: "user-042",
    blockchainHash: "0x8a3b...f7c2",
    executedAt: "2026-02-09T09:31:15Z",
    status: "confirmed",
  },
  {
    id: "TX-002",
    buyOrderId: "ORD-003",
    sellOrderId: "ORD-EXT-102",
    stockSymbol: "IKCO",
    stockName: "Iran Khodro",
    price: 2100,
    quantity: 350,
    totalValue: 735_000,
    buyerId: "user-001",
    sellerId: "user-015",
    blockchainHash: "0x2c4e...a1d9",
    executedAt: "2026-02-09T09:10:22Z",
    status: "confirmed",
  },
  {
    id: "TX-003",
    buyOrderId: "ORD-004",
    sellOrderId: "ORD-EXT-103",
    stockSymbol: "KGDR",
    stockName: "Gol Gohar Mining",
    price: 12300,
    quantity: 100,
    totalValue: 1_230_000,
    buyerId: "user-001",
    sellerId: "user-088",
    blockchainHash: "0x5f1a...c3e8",
    executedAt: "2026-02-08T14:22:45Z",
    status: "confirmed",
  },
  {
    id: "TX-004",
    buyOrderId: "ORD-EXT-201",
    sellOrderId: "ORD-EXT-202",
    stockSymbol: "TAPK",
    stockName: "TAPICO Holding",
    price: 9500,
    quantity: 300,
    totalValue: 2_850_000,
    buyerId: "user-001",
    sellerId: "user-033",
    blockchainHash: "0x9d7c...b4f1",
    executedAt: "2026-02-07T15:45:30Z",
    status: "confirmed",
  },
  {
    id: "TX-005",
    buyOrderId: "ORD-EXT-301",
    sellOrderId: "ORD-EXT-302",
    stockSymbol: "SHPN",
    stockName: "Pars Oil Refinery",
    price: 4600,
    quantity: 800,
    totalValue: 3_680_000,
    buyerId: "user-001",
    sellerId: "user-077",
    blockchainHash: "0x1e3f...d6a2",
    executedAt: "2026-02-05T10:12:00Z",
    status: "confirmed",
  },
];

// ============================================
// Mock Notifications
// ============================================
export const mockNotifications: Notification[] = [
  {
    id: "notif-001",
    userId: "user-001",
    title: "Order Matched",
    titleFa: "سفارش تطبیق شد",
    message: "Your buy order for 200 FOLD at 8,700 has been matched.",
    messageFa: "سفارش خرید ۲۰۰ سهم فولاد با قیمت ۸,۷۰۰ تطبیق شد.",
    type: "order_matched",
    read: false,
    createdAt: "2026-02-09T09:31:15Z",
  },
  {
    id: "notif-002",
    userId: "user-001",
    title: "Partial Fill",
    titleFa: "تطبیق جزئی",
    message: "350 of 500 shares filled for IKCO buy order at 2,100.",
    messageFa: "۳۵۰ از ۵۰۰ سهم ایران خودرو با قیمت ۲,۱۰۰ تطبیق شد.",
    type: "order_matched",
    read: false,
    createdAt: "2026-02-09T09:10:22Z",
  },
  {
    id: "notif-003",
    userId: "user-001",
    title: "Transaction Confirmed",
    titleFa: "تراکنش تأیید شد",
    message: "Transaction TX-001 recorded on blockchain. Hash: 0x8a3b...f7c2",
    messageFa: "تراکنش TX-001 در بلاکچین ثبت شد. هش: 0x8a3b...f7c2",
    type: "transaction",
    read: true,
    createdAt: "2026-02-09T09:32:00Z",
  },
  {
    id: "notif-004",
    userId: "user-001",
    title: "Price Alert",
    titleFa: "هشدار قیمت",
    message: "ZINC has surged +3.16% today. Current price: 15,680",
    messageFa: "فزر امروز ۳.۱۶٪ رشد داشته. قیمت فعلی: ۱۵,۶۸۰",
    type: "price_alert",
    read: true,
    createdAt: "2026-02-09T08:00:00Z",
  },
  {
    id: "notif-005",
    userId: "user-001",
    title: "Order Cancelled",
    titleFa: "سفارش لغو شد",
    message: "Your sell order for 1000 SSAN at 1,900 has been cancelled.",
    messageFa: "سفارش فروش ۱,۰۰۰ سهم خساپا با قیمت ۱,۹۰۰ لغو شد.",
    type: "order_cancelled",
    read: true,
    createdAt: "2026-02-07T16:00:00Z",
  },
];

// ============================================
// Generate Price History
// ============================================
export function generatePriceHistory(
  basePrice: number,
  days: number = 30
): PriceHistory[] {
  const history: PriceHistory[] = [];
  let price = basePrice * 0.85;

  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const volatility = 0.03;
    const change = (Math.random() - 0.48) * volatility;
    const open = price;
    const close = +(price * (1 + change)).toFixed(2);
    const high = +(Math.max(open, close) * (1 + Math.random() * 0.015)).toFixed(2);
    const low = +(Math.min(open, close) * (1 - Math.random() * 0.015)).toFixed(2);
    const volume = Math.floor(Math.random() * 50_000_000) + 5_000_000;

    history.push({
      timestamp: date.toISOString().split("T")[0],
      open,
      high,
      low,
      close,
      volume,
    });

    price = close;
  }

  return history;
}

// ============================================
// Generate Order Book
// ============================================
export function generateOrderBook(currentPrice: number): OrderBook {
  const bids: { price: number; quantity: number; total: number; count: number }[] = [];
  const asks: { price: number; quantity: number; total: number; count: number }[] = [];

  for (let i = 1; i <= 10; i++) {
    const bidPrice = +(currentPrice - i * (currentPrice * 0.002)).toFixed(2);
    const askPrice = +(currentPrice + i * (currentPrice * 0.002)).toFixed(2);
    const bidQty = Math.floor(Math.random() * 5000) + 500;
    const askQty = Math.floor(Math.random() * 5000) + 500;

    bids.push({
      price: bidPrice,
      quantity: bidQty,
      total: +(bidPrice * bidQty).toFixed(2),
      count: Math.floor(Math.random() * 20) + 1,
    });

    asks.push({
      price: askPrice,
      quantity: askQty,
      total: +(askPrice * askQty).toFixed(2),
      count: Math.floor(Math.random() * 20) + 1,
    });
  }

  const spread = asks[0].price - bids[0].price;

  return {
    symbol: "",
    bids,
    asks,
    spread: +spread.toFixed(2),
    spreadPercent: +((spread / currentPrice) * 100).toFixed(3),
  };
}

// ============================================
// Market Stats
// ============================================
export const mockMarketStats: MarketStats = {
  totalStocks: 12,
  totalVolume: 408_700_000,
  totalMarketCap: 36_460_000_000,
  gainers: 8,
  losers: 4,
  unchanged: 0,
  indexValue: 2_187_450,
  indexChange: 28_340,
  indexChangePercent: 1.31,
};
