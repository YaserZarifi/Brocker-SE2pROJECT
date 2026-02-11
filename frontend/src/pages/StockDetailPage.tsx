import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  Loader2,
  Zap,
} from "lucide-react";
import { TradingChart } from "@/components/charts/TradingChart";
import type { Timeframe } from "@/components/charts/TradingChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useStockStore } from "@/stores/stockStore";
import { useThemeStore } from "@/stores/themeStore";
import { useAuthStore } from "@/stores/authStore";
import { stockService } from "@/services/stockService";
import { orderService } from "@/services/orderService";
import type { Portfolio } from "@/types";
import { generatePriceHistory, generateOrderBook } from "@/services/mockData";
import {
  formatPrice,
  formatCompactNumber,
  formatPercent,
  cn,
  getChangeColor,
} from "@/lib/utils";
import type { OrderBook as OrderBookType, PriceHistory } from "@/types";

export default function StockDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { stocks, fetchStocks } = useStockStore();
  const { language, theme } = useThemeStore();

  const stock = stocks.find((s) => s.symbol === symbol);
  const { user } = useAuthStore();
  const [orderType, setOrderType] = useState<"buy" | "sell">("buy");
  const [executionType, setExecutionType] = useState<"limit" | "market" | "stop_loss" | "take_profit">("market");
  const [price, setPrice] = useState(stock?.currentPrice?.toString() || "");
  const [triggerPrice, setTriggerPrice] = useState("");
  const [quantity, setQuantity] = useState("100");
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);
  const [timeframe, setTimeframe] = useState<Timeframe>("1D");
  const [chartType, setChartType] = useState<"candlestick" | "line" | "area">("candlestick");
  const [orderBook, setOrderBook] = useState<OrderBookType | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [orderLoading, setOrderLoading] = useState(false);
  const [orderMsg, setOrderMsg] = useState("");

  useEffect(() => {
    if (stocks.length === 0) fetchStocks();
  }, []);

  useEffect(() => {
    orderService.getPortfolio().then(setPortfolio).catch(() => {});
  }, [symbol]);

  // Fetch price history and order book from API
  useEffect(() => {
    if (!symbol || !stock) return;
    stockService
      .getPriceHistory(symbol, 30, timeframe)
      .then((data) => {
        if (data.length > 0) {
          setPriceHistory(data.map((p) => ({
            timestamp: p.timestamp,
            open: Number(p.open),
            high: Number(p.high),
            low: Number(p.low),
            close: Number(p.close),
            volume: Number(p.volume),
          })));
        } else {
          const fallback = generatePriceHistory(stock.currentPrice, 30);
          setPriceHistory(fallback);
        }
      })
      .catch(() => {
        setPriceHistory(generatePriceHistory(stock.currentPrice, 30));
      });

    orderService
      .getOrderBook(symbol)
      .then((book) => {
        if (book.bids.length > 0 || book.asks.length > 0) {
          setOrderBook(book);
        } else {
          setOrderBook(generateOrderBook(stock.currentPrice));
        }
      })
      .catch(() => setOrderBook(generateOrderBook(stock.currentPrice)));
  }, [symbol, stock?.currentPrice, timeframe]);

  // Price updates happen via WebSocket in real-time (Sprint 5)

  useEffect(() => {
    if (stock) {
      setPrice(stock.currentPrice.toString());
      setTriggerPrice(stock.currentPrice.toString());
    }
  }, [stock?.currentPrice]);

  const effectivePrice = executionType === "market"
    ? (orderType === "buy"
        ? (orderBook?.bestAsk || orderBook?.currentPrice || stock?.currentPrice || 0)
        : (orderBook?.bestBid || orderBook?.currentPrice || stock?.currentPrice || 0))
    : parseFloat(price || "0");
  const holding = portfolio?.holdings.find((h) => h.stockSymbol === symbol);
  const cashBalance = portfolio?.cashBalance ?? 0;

  const handlePlaceOrder = async () => {
    if (!symbol || !quantity || parseInt(quantity) <= 0) return;
    if (executionType !== "market" && (!price || parseFloat(price) <= 0)) return;
    if ((executionType === "stop_loss" || executionType === "take_profit") && (!triggerPrice || parseFloat(triggerPrice) <= 0)) return;
    setOrderLoading(true);
    setOrderMsg("");
    try {
      const payload: Parameters<typeof orderService.createOrder>[0] = {
        stock_symbol: symbol,
        type: orderType,
        execution_type: executionType,
        quantity: parseInt(quantity),
      };
      if (executionType === "limit" || executionType === "stop_loss" || executionType === "take_profit") {
        payload.price = parseFloat(price || "0");
      }
      if (executionType === "stop_loss" || executionType === "take_profit") {
        payload.trigger_price = parseFloat(triggerPrice);
      }
      await orderService.createOrder(payload);
      setOrderMsg(t("stock.orderSuccess") || "Order placed successfully!");
      orderService.getPortfolio().then(setPortfolio).catch(() => {});
    } catch (err: any) {
      setOrderMsg(err.response?.data?.error || "Failed to place order");
    } finally {
      setOrderLoading(false);
    }
  };

  const setQuantityByPercent = (pct: number) => {
    if (!stock) return;
    if (orderType === "buy") {
      const maxQty = effectivePrice > 0 ? Math.floor(cashBalance / effectivePrice) : 0;
      setQuantity(Math.floor((maxQty * pct) / 100).toString());
    } else {
      const qty = holding?.quantity ?? 0;
      setQuantity(Math.floor((qty * pct) / 100).toString());
    }
  };

  if (!stock) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-muted-foreground">Stock not found</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate("/market")}>
          {t("common.back")}
        </Button>
      </div>
    );
  }

  const total = (effectivePrice * parseInt(quantity || "0")).toFixed(2);
  const isUp = stock.changePercent >= 0;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/market")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-muted text-lg font-bold">
              {stock.symbol.slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{stock.symbol}</h1>
                <Badge variant="outline" className="text-xs">
                  {language === "fa" ? stock.sectorFa : stock.sector}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                {language === "fa" ? stock.nameFa : stock.name}
              </p>
            </div>
          </div>
        </div>

        <div className="text-end">
          <p className="text-3xl font-bold tabular-nums">
            {formatPrice(stock.currentPrice, language)}
          </p>
          <div
            className={cn(
              "flex items-center justify-end gap-1 text-sm font-medium",
              getChangeColor(stock.changePercent)
            )}
          >
            {isUp ? (
              <ArrowUpRight className="h-4 w-4" />
            ) : (
              <ArrowDownRight className="h-4 w-4" />
            )}
            {formatPrice(Math.abs(stock.change), language)} (
            {formatPercent(stock.changePercent)})
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Chart + Stats */}
        <div className="space-y-6 xl:col-span-2">
          {/* Price Chart - Binance-style */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <CardTitle className="text-base">
                  {t("stock.priceHistory")}
                </CardTitle>
                <div className="flex items-center gap-2">
                  {/* Chart type */}
                  <div className="flex rounded-lg border border-border bg-muted/30 p-0.5">
                    {(["candlestick", "line", "area"] as const).map((ct) => (
                      <button
                        key={ct}
                        onClick={() => setChartType(ct)}
                        className={cn(
                          "rounded-md px-2 py-1 text-xs font-medium transition-colors",
                          chartType === ct ? "bg-background shadow-sm" : "text-muted-foreground hover:text-foreground"
                        )}
                      >
                        {ct === "candlestick" && t("stock.chartCandle")}
                        {ct === "line" && t("stock.chartLine")}
                        {ct === "area" && t("stock.chartArea")}
                      </button>
                    ))}
                  </div>
                  {/* Timeframe */}
                  <div className="flex rounded-lg border border-border bg-muted/30 p-0.5">
                    {(["1m", "5m", "15m", "1h", "4h", "1D", "1W"] as Timeframe[]).map((tf) => (
                      <button
                        key={tf}
                        onClick={() => setTimeframe(tf)}
                        className={cn(
                          "rounded-md px-2 py-1 text-xs font-medium transition-colors",
                          timeframe === tf ? "bg-background shadow-sm" : "text-muted-foreground hover:text-foreground"
                        )}
                      >
                        {t(`stock.timeframe${tf}`)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <TradingChart
                  data={priceHistory}
                  chartType={chartType}
                  isDark={theme === "dark"}
                  height={350}
                />
              </div>
            </CardContent>
          </Card>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: t("stock.open"), value: formatPrice(stock.open, language) },
              { label: t("stock.close"), value: formatPrice(stock.previousClose, language) },
              { label: t("stock.volume"), value: formatCompactNumber(stock.volume) },
              { label: t("stock.marketCap"), value: formatCompactNumber(stock.marketCap) },
            ].map((stat, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                  <p className="text-lg font-semibold tabular-nums mt-1">
                    {stat.value}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Order Book */}
          {orderBook && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">
                  {t("stock.orderBook")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  {/* Bids */}
                  <div>
                    <p className="text-xs font-medium text-stock-up mb-2">
                      {t("stock.bids")}
                    </p>
                    <div className="space-y-0.5">
                      {orderBook.bids.map((bid, i) => (
                        <div
                          key={i}
                          role="button"
                          tabIndex={0}
                          className="relative flex items-center justify-between rounded px-2 py-1 text-xs cursor-pointer hover:bg-muted/50 transition-colors"
                          style={{ maxWidth: "100%" }}
                          onClick={() => {
                            if (executionType === "limit" && orderType === "sell") setPrice(String(bid.price));
                          }}
                          onKeyDown={(e) => e.key === "Enter" && executionType === "limit" && orderType === "sell" && setPrice(String(bid.price))}
                        >
                          <div
                            className="absolute inset-y-0 start-0 bg-stock-up/10 rounded"
                            style={{
                              width: `${Math.min((bid.quantity / 5500) * 100, 100)}%`,
                            }}
                          />
                          <span className="relative text-stock-up tabular-nums font-medium">
                            {formatPrice(bid.price, language)}
                          </span>
                          <span className="relative text-muted-foreground tabular-nums">
                            {bid.quantity}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* Asks */}
                  <div>
                    <p className="text-xs font-medium text-stock-down mb-2">
                      {t("stock.asks")}
                    </p>
                    <div className="space-y-0.5">
                      {orderBook.asks.map((ask, i) => (
                        <div
                          key={i}
                          role="button"
                          tabIndex={0}
                          className="relative flex items-center justify-between rounded px-2 py-1 text-xs cursor-pointer hover:bg-muted/50 transition-colors"
                          style={{ maxWidth: "100%" }}
                          onClick={() => {
                            if (executionType === "limit" && orderType === "buy") setPrice(String(ask.price));
                          }}
                          onKeyDown={(e) => e.key === "Enter" && executionType === "limit" && orderType === "buy" && setPrice(String(ask.price))}
                        >
                          <div
                            className="absolute inset-y-0 end-0 bg-stock-down/10 rounded"
                            style={{
                              width: `${Math.min((ask.quantity / 5500) * 100, 100)}%`,
                            }}
                          />
                          <span className="relative text-stock-down tabular-nums font-medium">
                            {formatPrice(ask.price, language)}
                          </span>
                          <span className="relative text-muted-foreground tabular-nums">
                            {ask.quantity}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-3 flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <span>{t("stock.spread")}:</span>
                  <span className="font-medium tabular-nums">
                    {orderBook.spread} ({orderBook.spreadPercent}%)
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Trade Panel */}
        <div className="space-y-6">
          <Card className="sticky top-24">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{t("stock.trade")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs
                value={orderType}
                onValueChange={(v) => setOrderType(v as "buy" | "sell")}
              >
                <TabsList className="w-full">
                  <TabsTrigger value="buy" className="flex-1 data-[state=active]:bg-stock-up data-[state=active]:text-white">
                    {t("stock.buy")}
                  </TabsTrigger>
                  <TabsTrigger value="sell" className="flex-1 data-[state=active]:bg-stock-down data-[state=active]:text-white">
                    {t("stock.sell")}
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              {/* Execution type: Market / Limit / Stop-Loss / Take-Profit */}
              <div>
                <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
                  {t("stock.limitOrder")} / {t("stock.marketOrder")}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {(["market", "limit", "stop_loss", "take_profit"] as const).map((et) => (
                    <button
                      key={et}
                      onClick={() => setExecutionType(et)}
                      className={cn(
                        "rounded-md py-2 text-xs font-medium transition-colors",
                        executionType === et
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted/50 text-muted-foreground hover:bg-muted"
                      )}
                    >
                      {et === "market" && <Zap className="h-3 w-3 inline me-1" />}
                      {et === "market" && t("stock.market")}
                      {et === "limit" && t("stock.limit")}
                      {et === "stop_loss" && t("stock.stopLoss")}
                      {et === "take_profit" && t("stock.takeProfit")}
                    </button>
                  ))}
                </div>
              </div>

              {executionType === "market" && (
                <div className="rounded-lg bg-muted/50 p-2.5 text-xs text-muted-foreground">
                  {t("stock.atMarket")}: {formatPrice(effectivePrice, language)}
                </div>
              )}

              {(executionType === "limit" || executionType === "stop_loss" || executionType === "take_profit") && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground">{t("stock.price")}</label>
                  <Input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="mt-1 tabular-nums"
                  />
                </div>
              )}

              {(executionType === "stop_loss" || executionType === "take_profit") && (
                <div>
                  <label className="text-xs font-medium text-muted-foreground">{t("stock.triggerPrice")}</label>
                  <Input
                    type="number"
                    value={triggerPrice}
                    onChange={(e) => setTriggerPrice(e.target.value)}
                    className="mt-1 tabular-nums"
                  />
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-muted-foreground">{t("stock.quantity")}</label>
                <Input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  className="mt-1 tabular-nums"
                  min={1}
                />
              </div>

              <div className="flex gap-2">
                {[25, 50, 100, 250, 500].map((q) => (
                  <button
                    key={q}
                    onClick={() => setQuantity(q.toString())}
                    className="flex-1 rounded-md bg-muted/50 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>

              <div className="flex gap-2">
                {[25, 50, 75, 100].map((pct) => (
                  <button
                    key={pct}
                    onClick={() => setQuantityByPercent(pct)}
                    className="flex-1 rounded-md bg-muted/50 py-1.5 text-xs font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                  >
                    {pct}%
                  </button>
                ))}
              </div>

              <div className="rounded-lg bg-muted/50 p-3">
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{t("stock.total")}</span>
                  <span className="font-semibold text-foreground tabular-nums text-sm">
                    {formatPrice(parseFloat(total) || 0, language)}
                  </span>
                </div>
              </div>

              {orderMsg && (
                <div className={cn(
                  "rounded-lg p-2.5 text-xs text-center",
                  orderMsg.includes("success") || orderMsg.includes("Success")
                    ? "bg-stock-up/10 text-stock-up"
                    : "bg-destructive/10 text-destructive"
                )}>
                  {orderMsg}
                </div>
              )}

              <Button
                className="w-full h-11"
                variant={orderType === "buy" ? "success" : "danger"}
                onClick={handlePlaceOrder}
                disabled={orderLoading}
              >
                {orderLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : executionType === "market" ? (
                  <Zap className="h-4 w-4" />
                ) : (
                  <TrendingUp className="h-4 w-4" />
                )}
                {executionType === "market"
                  ? (orderType === "buy" ? t("stock.buyNow") : t("stock.sellNow"))
                  : `${t("stock.placeOrder")} - ${orderType === "buy" ? t("stock.buy") : t("stock.sell")}`}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
