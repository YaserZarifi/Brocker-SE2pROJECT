import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useStockStore } from "@/stores/stockStore";
import { useThemeStore } from "@/stores/themeStore";
import { orderService } from "@/services/orderService";
import { transactionService } from "@/services/transactionService";
import { stockService } from "@/services/stockService";
import { generatePriceHistory } from "@/services/mockData";
import { formatPrice, formatCompactNumber, formatPercent, cn, getChangeColor } from "@/lib/utils";
import type { Portfolio, Transaction, PriceHistory } from "@/types";

const indexHistory = generatePriceHistory(2_187_450, 30).map((p) => ({
  date: p.timestamp.slice(5),
  value: Math.floor(p.close),
}));

export default function DashboardPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { stocks, marketStats, simulatePriceUpdate, fetchStocks, fetchMarketStats } = useStockStore();
  const { language } = useThemeStore();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  // Fetch data from API
  useEffect(() => {
    fetchStocks();
    fetchMarketStats();
    orderService.getPortfolio().then(setPortfolio).catch(() => {});
    transactionService.getTransactions().then(setTransactions).catch(() => {});
  }, []);

  // Simulate real-time price updates
  useEffect(() => {
    const interval = setInterval(simulatePriceUpdate, 3000);
    return () => clearInterval(interval);
  }, [simulatePriceUpdate]);

  const topGainers = [...stocks]
    .sort((a, b) => b.changePercent - a.changePercent)
    .slice(0, 5);
  const topLosers = [...stocks]
    .sort((a, b) => a.changePercent - b.changePercent)
    .slice(0, 5);

  const statCards = [
    {
      title: t("dashboard.marketIndex"),
      value: formatCompactNumber(marketStats.indexValue),
      change: marketStats.indexChangePercent,
      icon: Activity,
      color: "from-blue-500 to-indigo-500",
    },
    {
      title: t("dashboard.totalValue"),
      value: formatPrice(portfolio?.totalValue ?? 0, language),
      change: portfolio?.totalProfitLossPercent ?? 0,
      icon: DollarSign,
      color: "from-emerald-500 to-green-500",
    },
    {
      title: t("dashboard.totalVolume"),
      value: formatCompactNumber(marketStats.totalVolume),
      change: 5.2,
      icon: BarChart3,
      color: "from-purple-500 to-pink-500",
    },
    {
      title: t("dashboard.cashBalance"),
      value: formatPrice(portfolio?.cashBalance ?? 0, language),
      change: 0,
      icon: Wallet,
      color: "from-amber-500 to-orange-500",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Title */}
      <div>
        <h1 className="text-2xl font-bold">{t("dashboard.title")}</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {t("dashboard.marketOverview")}
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((stat, i) => (
          <Card key={i} className="overflow-hidden">
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold tabular-nums">{stat.value}</p>
                  {stat.change !== 0 && (
                    <div
                      className={cn(
                        "flex items-center gap-1 text-sm font-medium",
                        getChangeColor(stat.change)
                      )}
                    >
                      {stat.change > 0 ? (
                        <ArrowUpRight className="h-3.5 w-3.5" />
                      ) : (
                        <ArrowDownRight className="h-3.5 w-3.5" />
                      )}
                      {formatPercent(stat.change)}
                    </div>
                  )}
                </div>
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-lg",
                    stat.color
                  )}
                >
                  <stat.icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Market Index Chart */}
        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-base">{t("dashboard.marketIndex")}</CardTitle>
            <Badge variant="success">
              {formatPercent(marketStats.indexChangePercent)}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={indexHistory}>
                  <defs>
                    <linearGradient id="indexGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="hsl(220, 70%, 50%)" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="hsl(220, 70%, 50%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => formatCompactNumber(v)}
                  />
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="hsl(220, 70%, 50%)"
                    strokeWidth={2}
                    fill="url(#indexGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Portfolio Summary */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">
              {t("dashboard.portfolioSummary")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">
                {t("dashboard.totalValue")}
              </p>
              <p className="text-3xl font-bold tabular-nums">
                {formatPrice(portfolio?.totalValue ?? 0, language)}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">
                  {t("dashboard.todayPL")}
                </p>
                <p
                  className={cn(
                    "text-lg font-semibold tabular-nums",
                    getChangeColor(portfolio?.totalProfitLoss ?? 0)
                  )}
                >
                  {(portfolio?.totalProfitLoss ?? 0) > 0 ? "+" : ""}
                  {formatPrice(portfolio?.totalProfitLoss ?? 0, language)}
                </p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-xs text-muted-foreground">
                  {t("dashboard.totalPL")}
                </p>
                <p
                  className={cn(
                    "text-lg font-semibold",
                    getChangeColor(portfolio?.totalProfitLossPercent ?? 0)
                  )}
                >
                  {formatPercent(portfolio?.totalProfitLossPercent ?? 0)}
                </p>
              </div>
            </div>

            {/* Holdings preview */}
            <div className="space-y-2">
              {(portfolio?.holdings ?? []).slice(0, 4).map((h) => (
                <div
                  key={h.stockSymbol}
                  className="flex items-center justify-between py-1.5"
                >
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-md bg-muted text-xs font-bold">
                      {h.stockSymbol.slice(0, 2)}
                    </div>
                    <span className="text-sm font-medium">{h.stockSymbol}</span>
                  </div>
                  <span
                    className={cn(
                      "text-sm font-medium tabular-nums",
                      getChangeColor(h.profitLossPercent)
                    )}
                  >
                    {formatPercent(h.profitLossPercent)}
                  </span>
                </div>
              ))}
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={() => navigate("/portfolio")}
            >
              {t("common.seeAll")}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Gainers & Losers */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top Gainers */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="h-4 w-4 text-stock-up" />
              {t("dashboard.topGainers")}
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate("/market")}>
              {t("common.seeAll")}
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {topGainers.map((stock) => (
                <div
                  key={stock.symbol}
                  className="flex items-center justify-between rounded-lg p-2.5 transition-colors hover:bg-muted/50 cursor-pointer"
                  onClick={() => navigate(`/market/${stock.symbol}`)}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted font-bold text-xs">
                      {stock.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{stock.symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {language === "fa" ? stock.nameFa : stock.name}
                      </p>
                    </div>
                  </div>
                  <div className="text-end">
                    <p className="text-sm font-medium tabular-nums">
                      {formatPrice(stock.currentPrice, language)}
                    </p>
                    <Badge variant="success" className="text-xs">
                      <ArrowUpRight className="h-3 w-3 me-0.5" />
                      {formatPercent(stock.changePercent)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Losers */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingDown className="h-4 w-4 text-stock-down" />
              {t("dashboard.topLosers")}
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate("/market")}>
              {t("common.seeAll")}
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {topLosers.map((stock) => (
                <div
                  key={stock.symbol}
                  className="flex items-center justify-between rounded-lg p-2.5 transition-colors hover:bg-muted/50 cursor-pointer"
                  onClick={() => navigate(`/market/${stock.symbol}`)}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted font-bold text-xs">
                      {stock.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{stock.symbol}</p>
                      <p className="text-xs text-muted-foreground">
                        {language === "fa" ? stock.nameFa : stock.name}
                      </p>
                    </div>
                  </div>
                  <div className="text-end">
                    <p className="text-sm font-medium tabular-nums">
                      {formatPrice(stock.currentPrice, language)}
                    </p>
                    <Badge variant="danger" className="text-xs">
                      <ArrowDownRight className="h-3 w-3 me-0.5" />
                      {formatPercent(stock.changePercent)}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="text-base">
            {t("dashboard.recentTransactions")}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/transactions")}
          >
            {t("common.seeAll")}
          </Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="pb-3 text-start font-medium">{t("transactions.id")}</th>
                  <th className="pb-3 text-start font-medium">{t("transactions.stock")}</th>
                  <th className="pb-3 text-end font-medium">{t("transactions.price")}</th>
                  <th className="pb-3 text-end font-medium">{t("transactions.qty")}</th>
                  <th className="pb-3 text-end font-medium">{t("transactions.total")}</th>
                  <th className="pb-3 text-end font-medium">{t("transactions.status")}</th>
                </tr>
              </thead>
              <tbody>
                {transactions.slice(0, 5).map((tx) => (
                  <tr
                    key={tx.id}
                    className="border-b border-border/50 last:border-0"
                  >
                    <td className="py-3 text-sm font-mono text-muted-foreground">
                      {tx.id}
                    </td>
                    <td className="py-3">
                      <span className="text-sm font-medium">{tx.stockSymbol}</span>
                    </td>
                    <td className="py-3 text-end text-sm tabular-nums">
                      {formatPrice(tx.price, language)}
                    </td>
                    <td className="py-3 text-end text-sm tabular-nums">
                      {tx.quantity}
                    </td>
                    <td className="py-3 text-end text-sm font-medium tabular-nums">
                      {formatPrice(tx.totalValue, language)}
                    </td>
                    <td className="py-3 text-end">
                      <Badge variant="success" className="text-[10px]">
                        {t(`transactions.${tx.status}`)}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
