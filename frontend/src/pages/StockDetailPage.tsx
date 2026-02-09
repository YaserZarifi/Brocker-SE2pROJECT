import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  ArrowLeft,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  Loader2,
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
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useStockStore } from "@/stores/stockStore";
import { useThemeStore } from "@/stores/themeStore";
import { stockService } from "@/services/stockService";
import { orderService } from "@/services/orderService";
import { generatePriceHistory, generateOrderBook } from "@/services/mockData";
import {
  formatPrice,
  formatCompactNumber,
  formatPercent,
  cn,
  getChangeColor,
} from "@/lib/utils";
import type { OrderBook as OrderBookType } from "@/types";

export default function StockDetailPage() {
  const { symbol } = useParams<{ symbol: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { stocks, fetchStocks } = useStockStore();
  const { language } = useThemeStore();

  const stock = stocks.find((s) => s.symbol === symbol);
  const [orderType, setOrderType] = useState<"buy" | "sell">("buy");
  const [price, setPrice] = useState(stock?.currentPrice?.toString() || "");
  const [quantity, setQuantity] = useState("100");
  const [priceHistory, setPriceHistory] = useState<{ date: string; price: number; volume: number }[]>([]);
  const [orderBook, setOrderBook] = useState<OrderBookType | null>(null);
  const [orderLoading, setOrderLoading] = useState(false);
  const [orderMsg, setOrderMsg] = useState("");

  // Fetch stocks if empty
  useEffect(() => {
    if (stocks.length === 0) fetchStocks();
  }, []);

  // Fetch price history and order book from API, with fallback to generated data
  useEffect(() => {
    if (!symbol || !stock) return;
    stockService
      .getPriceHistory(symbol, 30)
      .then((data) => {
        if (data.length > 0) {
          setPriceHistory(data.map((p) => ({ date: String(p.timestamp).slice(5), price: Number(p.close), volume: Number(p.volume) })));
        } else {
          // Fallback to generated data
          setPriceHistory(generatePriceHistory(stock.currentPrice, 30).map((p) => ({ date: p.timestamp.slice(5), price: p.close, volume: p.volume })));
        }
      })
      .catch(() => {
        setPriceHistory(generatePriceHistory(stock.currentPrice, 30).map((p) => ({ date: p.timestamp.slice(5), price: p.close, volume: p.volume })));
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
  }, [symbol, stock?.currentPrice]);

  // Price updates happen via WebSocket in real-time (Sprint 5)

  useEffect(() => {
    if (stock) setPrice(stock.currentPrice.toString());
  }, [stock?.currentPrice]);

  const handlePlaceOrder = async () => {
    if (!symbol || !price || !quantity) return;
    setOrderLoading(true);
    setOrderMsg("");
    try {
      await orderService.createOrder({
        stock_symbol: symbol,
        type: orderType,
        price: parseFloat(price),
        quantity: parseInt(quantity),
      });
      setOrderMsg(t("stock.orderSuccess") || "Order placed successfully!");
    } catch (err: any) {
      setOrderMsg(err.response?.data?.error || "Failed to place order");
    } finally {
      setOrderLoading(false);
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

  const total = (parseFloat(price || "0") * parseInt(quantity || "0")).toFixed(2);
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
          {/* Price Chart */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">
                {t("stock.priceHistory")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={priceHistory}>
                    <defs>
                      <linearGradient
                        id="priceGrad"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="0%"
                          stopColor={isUp ? "hsl(142, 71%, 45%)" : "hsl(0, 84%, 60%)"}
                          stopOpacity={0.3}
                        />
                        <stop
                          offset="100%"
                          stopColor={isUp ? "hsl(142, 71%, 45%)" : "hsl(0, 84%, 60%)"}
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="hsl(var(--border))"
                    />
                    <XAxis
                      dataKey="date"
                      tick={{
                        fontSize: 11,
                        fill: "hsl(var(--muted-foreground))",
                      }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{
                        fontSize: 11,
                        fill: "hsl(var(--muted-foreground))",
                      }}
                      axisLine={false}
                      tickLine={false}
                      domain={["auto", "auto"]}
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
                      dataKey="price"
                      stroke={isUp ? "hsl(142, 71%, 45%)" : "hsl(0, 84%, 60%)"}
                      strokeWidth={2}
                      fill="url(#priceGrad)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
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
                          className="relative flex items-center justify-between rounded px-2 py-1 text-xs"
                        >
                          <div
                            className="absolute inset-y-0 start-0 bg-stock-up/10 rounded"
                            style={{
                              width: `${(bid.quantity / 5500) * 100}%`,
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
                          className="relative flex items-center justify-between rounded px-2 py-1 text-xs"
                        >
                          <div
                            className="absolute inset-y-0 end-0 bg-stock-down/10 rounded"
                            style={{
                              width: `${(ask.quantity / 5500) * 100}%`,
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

              <div className="space-y-3">
                <div>
                  <label className="text-xs font-medium text-muted-foreground">
                    {t("stock.price")}
                  </label>
                  <Input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="mt-1 tabular-nums"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">
                    {t("stock.quantity")}
                  </label>
                  <Input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="mt-1 tabular-nums"
                  />
                </div>

                {/* Quick quantity buttons */}
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
                  ) : (
                    <TrendingUp className="h-4 w-4" />
                  )}
                  {t("stock.placeOrder")} - {orderType === "buy" ? t("stock.buy") : t("stock.sell")}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
