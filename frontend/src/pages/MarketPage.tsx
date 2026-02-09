import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Search, ArrowUpRight, ArrowDownRight, SlidersHorizontal } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useStockStore } from "@/stores/stockStore";
import { useThemeStore } from "@/stores/themeStore";
import { formatPrice, formatCompactNumber, formatPercent, cn, getChangeColor, getChangeBgColor } from "@/lib/utils";

export default function MarketPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { language } = useThemeStore();
  const {
    searchQuery,
    setSearchQuery,
    selectedSector,
    setSelectedSector,
    sortBy,
    setSortBy,
    getFilteredStocks,
    simulatePriceUpdate,
    marketStats,
  } = useStockStore();

  const { fetchStocks, fetchMarketStats } = useStockStore();
  const filteredStocks = getFilteredStocks();

  useEffect(() => {
    fetchStocks();
    fetchMarketStats();
  }, []);

  useEffect(() => {
    const interval = setInterval(simulatePriceUpdate, 3000);
    return () => clearInterval(interval);
  }, [simulatePriceUpdate]);

  const sectors = [
    "all",
    "Metals & Mining",
    "Energy",
    "Automotive",
    "Banking",
    "Petrochemical",
    "Telecom",
  ];

  const sectorsFa: Record<string, string> = {
    all: "همه",
    "Metals & Mining": "فلزات و معادن",
    Energy: "انرژی",
    Automotive: "خودرو",
    Banking: "بانکداری",
    Petrochemical: "پتروشیمی",
    Telecom: "مخابرات",
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">{t("market.title")}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {filteredStocks.length} {t("dashboard.activeStocks")} &middot;{" "}
            <span className="text-stock-up">{marketStats.gainers} {t("dashboard.gainers")}</span>{" / "}
            <span className="text-stock-down">{marketStats.losers} {t("dashboard.losers")}</span>
          </p>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder={t("market.search")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="ps-10"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="h-10 rounded-lg border border-input bg-transparent px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="symbol">{t("market.sort")}: A-Z</option>
            <option value="price_desc">{t("market.price")} ↓</option>
            <option value="price_asc">{t("market.price")} ↑</option>
            <option value="change_desc">{t("market.change")} ↓</option>
            <option value="change_asc">{t("market.change")} ↑</option>
            <option value="volume">{t("market.volume")}</option>
          </select>
        </div>
      </div>

      {/* Sector Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {sectors.map((sector) => (
          <button
            key={sector}
            onClick={() => setSelectedSector(sector)}
            className={cn(
              "shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              selectedSector === sector
                ? "bg-primary text-primary-foreground shadow-sm"
                : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
          >
            {language === "fa" ? sectorsFa[sector] : sector === "all" ? "All" : sector}
          </button>
        ))}
      </div>

      {/* Stock Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="px-5 py-3.5 text-start font-medium">{t("market.sector")}</th>
                  <th className="px-5 py-3.5 text-end font-medium">{t("market.price")}</th>
                  <th className="px-5 py-3.5 text-end font-medium">{t("market.change")}</th>
                  <th className="px-5 py-3.5 text-end font-medium hidden md:table-cell">{t("market.volume")}</th>
                  <th className="px-5 py-3.5 text-end font-medium hidden lg:table-cell">{t("market.marketCap")}</th>
                  <th className="px-5 py-3.5 text-end font-medium hidden lg:table-cell">{t("market.high")}</th>
                  <th className="px-5 py-3.5 text-end font-medium hidden lg:table-cell">{t("market.low")}</th>
                  <th className="px-5 py-3.5 text-end font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {filteredStocks.map((stock) => (
                  <tr
                    key={stock.symbol}
                    className="border-b border-border/50 last:border-0 transition-colors hover:bg-muted/30 cursor-pointer"
                    onClick={() => navigate(`/market/${stock.symbol}`)}
                  >
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-sm font-bold">
                          {stock.symbol.slice(0, 2)}
                        </div>
                        <div>
                          <p className="font-semibold text-sm">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground">
                            {language === "fa" ? stock.nameFa : stock.name}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-end">
                      <span className="font-semibold tabular-nums text-sm">
                        {formatPrice(stock.currentPrice, language)}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-end">
                      <div className="flex items-center justify-end gap-1">
                        <Badge
                          variant={stock.changePercent >= 0 ? "success" : "danger"}
                          className="font-mono text-xs"
                        >
                          {stock.changePercent >= 0 ? (
                            <ArrowUpRight className="h-3 w-3 me-0.5" />
                          ) : (
                            <ArrowDownRight className="h-3 w-3 me-0.5" />
                          )}
                          {formatPercent(stock.changePercent)}
                        </Badge>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-end text-sm text-muted-foreground tabular-nums hidden md:table-cell">
                      {formatCompactNumber(stock.volume)}
                    </td>
                    <td className="px-5 py-4 text-end text-sm text-muted-foreground tabular-nums hidden lg:table-cell">
                      {formatCompactNumber(stock.marketCap)}
                    </td>
                    <td className="px-5 py-4 text-end text-sm tabular-nums hidden lg:table-cell text-stock-up">
                      {formatPrice(stock.high24h, language)}
                    </td>
                    <td className="px-5 py-4 text-end text-sm tabular-nums hidden lg:table-cell text-stock-down">
                      {formatPrice(stock.low24h, language)}
                    </td>
                    <td className="px-5 py-4 text-end">
                      <Button variant="ghost" size="sm">
                        {t("market.viewDetails")}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredStocks.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <SlidersHorizontal className="h-10 w-10 mb-3 opacity-30" />
              <p>{t("market.noResults")}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
