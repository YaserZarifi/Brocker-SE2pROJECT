import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { ArrowUpRight, ArrowDownRight, PieChart, Briefcase, Loader2 } from "lucide-react";
import {
  PieChart as RechartsPie,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { orderService } from "@/services/orderService";
import { useThemeStore } from "@/stores/themeStore";
import {
  formatPrice,
  formatPercent,
  cn,
  getChangeColor,
} from "@/lib/utils";
import type { Portfolio } from "@/types";

const COLORS = [
  "hsl(220, 70%, 50%)",
  "hsl(160, 60%, 45%)",
  "hsl(30, 80%, 55%)",
  "hsl(280, 65%, 60%)",
  "hsl(340, 75%, 55%)",
];

export default function PortfolioPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { language } = useThemeStore();
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    orderService.getPortfolio()
      .then(setPortfolio)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
        <p>Could not load portfolio</p>
      </div>
    );
  }

  const pieData = portfolio.holdings.map((h) => ({
    name: h.stockSymbol,
    value: h.totalValue,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">{t("portfolio.title")}</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">{t("dashboard.totalValue")}</p>
            <p className="text-2xl font-bold tabular-nums mt-1">
              {formatPrice(portfolio.totalValue, language)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">{t("dashboard.totalPL")}</p>
            <p className={cn("text-2xl font-bold tabular-nums mt-1", getChangeColor(portfolio.totalProfitLoss))}>
              {portfolio.totalProfitLoss > 0 ? "+" : ""}
              {formatPrice(portfolio.totalProfitLoss, language)}
            </p>
            <Badge
              variant={portfolio.totalProfitLossPercent >= 0 ? "success" : "danger"}
              className="mt-1"
            >
              {portfolio.totalProfitLossPercent >= 0 ? <ArrowUpRight className="h-3 w-3 me-0.5" /> : <ArrowDownRight className="h-3 w-3 me-0.5" />}
              {formatPercent(portfolio.totalProfitLossPercent)}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">{t("dashboard.cashBalance")}</p>
            <p className="text-2xl font-bold tabular-nums mt-1">
              {formatPrice(portfolio.cashBalance, language)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground">{t("portfolio.holdings")}</p>
            <p className="text-2xl font-bold mt-1">{portfolio.holdings.length}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("dashboard.activeStocks")}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        {/* Holdings Table */}
        <Card className="xl:col-span-2">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <Briefcase className="h-4 w-4" />
              {t("portfolio.holdings")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border text-xs text-muted-foreground">
                    <th className="pb-3 text-start font-medium">{t("portfolio.symbol")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.shares")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.avgPrice")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.currentPrice")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.value")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.pl")}</th>
                    <th className="pb-3 text-end font-medium">{t("portfolio.plPercent")}</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.holdings.map((h) => (
                    <tr
                      key={h.stockSymbol}
                      className="border-b border-border/50 last:border-0 hover:bg-muted/30 cursor-pointer transition-colors"
                      onClick={() => navigate(`/market/${h.stockSymbol}`)}
                    >
                      <td className="py-3.5">
                        <div className="flex items-center gap-2.5">
                          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted text-xs font-bold">
                            {h.stockSymbol.slice(0, 2)}
                          </div>
                          <div>
                            <p className="text-sm font-semibold">{h.stockSymbol}</p>
                            <p className="text-xs text-muted-foreground">
                              {language === "fa" ? h.stockNameFa : h.stockName}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 text-end text-sm tabular-nums">{h.quantity}</td>
                      <td className="py-3.5 text-end text-sm tabular-nums text-muted-foreground">
                        {formatPrice(h.averageBuyPrice, language)}
                      </td>
                      <td className="py-3.5 text-end text-sm tabular-nums font-medium">
                        {formatPrice(h.currentPrice, language)}
                      </td>
                      <td className="py-3.5 text-end text-sm tabular-nums font-medium">
                        {formatPrice(h.totalValue, language)}
                      </td>
                      <td className={cn("py-3.5 text-end text-sm tabular-nums font-medium", getChangeColor(h.profitLoss))}>
                        {h.profitLoss > 0 ? "+" : ""}
                        {formatPrice(h.profitLoss, language)}
                      </td>
                      <td className="py-3.5 text-end">
                        <Badge variant={h.profitLossPercent >= 0 ? "success" : "danger"}>
                          {formatPercent(h.profitLossPercent)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Allocation Chart */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <PieChart className="h-4 w-4" />
              {t("portfolio.allocation")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                    formatter={(value: number | undefined) => formatPrice(value ?? 0, language)}
                  />
                </RechartsPie>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 space-y-2.5">
              {portfolio.holdings.map((h, i) => {
                const pct = (h.totalValue / portfolio.totalValue) * 100;
                return (
                  <div key={h.stockSymbol} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className="h-3 w-3 rounded-full"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        <span className="font-medium">{h.stockSymbol}</span>
                      </div>
                      <span className="text-muted-foreground tabular-nums">
                        {pct.toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={pct} className="h-1.5" />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
