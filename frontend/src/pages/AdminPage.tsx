import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Shield,
  Users,
  BarChart3,
  ArrowLeftRight,
  Activity,
  Plus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useStockStore } from "@/stores/stockStore";
import { useThemeStore } from "@/stores/themeStore";
import { orderService } from "@/services/orderService";
import { transactionService } from "@/services/transactionService";
import { formatPrice, formatCompactNumber } from "@/lib/utils";
import type { Order, Transaction, Stock } from "@/types";

export default function AdminPage() {
  const { t } = useTranslation();
  const { language } = useThemeStore();
  const { stocks, fetchStocks } = useStockStore();
  const [orders, setOrders] = useState<Order[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    if (stocks.length === 0) fetchStocks();
    orderService.getOrders().then(setOrders).catch(() => {});
    transactionService.getTransactions().then(setTransactions).catch(() => {});
  }, []);

  const mockStocks = stocks;
  const mockOrders = orders;
  const mockTransactions = transactions;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{t("admin.title")}</h1>
        </div>
        <Button>
          <Plus className="h-4 w-4 me-1.5" />
          {t("admin.addStock")}
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10">
              <Users className="h-5 w-5 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">1,284</p>
              <p className="text-xs text-muted-foreground">{t("admin.totalUsers")}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10">
              <BarChart3 className="h-5 w-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockOrders.length}</p>
              <p className="text-xs text-muted-foreground">{t("admin.totalOrders")}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10">
              <ArrowLeftRight className="h-5 w-5 text-purple-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockTransactions.length}</p>
              <p className="text-xs text-muted-foreground">{t("admin.totalTransactions")}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-stock-up-bg">
              <Activity className="h-5 w-5 text-stock-up" />
            </div>
            <div>
              <p className="text-2xl font-bold">99.8%</p>
              <p className="text-xs text-muted-foreground">{t("admin.systemHealth")}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="stocks">
        <TabsList>
          <TabsTrigger value="stocks">{t("admin.stocks")}</TabsTrigger>
          <TabsTrigger value="users">{t("admin.users")}</TabsTrigger>
        </TabsList>

        <TabsContent value="stocks">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{t("admin.stocks")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border text-xs text-muted-foreground">
                      <th className="pb-3 text-start font-medium">{t("portfolio.symbol")}</th>
                      <th className="pb-3 text-end font-medium">{t("market.price")}</th>
                      <th className="pb-3 text-end font-medium">{t("market.volume")}</th>
                      <th className="pb-3 text-end font-medium">{t("market.marketCap")}</th>
                      <th className="pb-3 text-start font-medium">{t("market.sector")}</th>
                      <th className="pb-3 text-end font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {mockStocks.map((stock) => (
                      <tr key={stock.symbol} className="border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted text-xs font-bold">
                              {stock.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <p className="text-sm font-medium">{stock.symbol}</p>
                              <p className="text-xs text-muted-foreground">
                                {language === "fa" ? stock.nameFa : stock.name}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 text-end text-sm tabular-nums">{formatPrice(stock.currentPrice, language)}</td>
                        <td className="py-3 text-end text-sm text-muted-foreground tabular-nums">{formatCompactNumber(stock.volume)}</td>
                        <td className="py-3 text-end text-sm text-muted-foreground tabular-nums">{formatCompactNumber(stock.marketCap)}</td>
                        <td className="py-3">
                          <Badge variant="outline" className="text-xs">
                            {language === "fa" ? stock.sectorFa : stock.sector}
                          </Badge>
                        </td>
                        <td className="py-3 text-end">
                          <div className="flex gap-1 justify-end">
                            <Button variant="ghost" size="sm" className="h-7 text-xs">{t("common.edit")}</Button>
                            <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive">{t("common.delete")}</Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{t("admin.users")}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border text-xs text-muted-foreground">
                      <th className="pb-3 text-start font-medium">User</th>
                      <th className="pb-3 text-start font-medium">Email</th>
                      <th className="pb-3 text-center font-medium">Role</th>
                      <th className="pb-3 text-start font-medium hidden md:table-cell">Wallet</th>
                      <th className="pb-3 text-end font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { name: "Ali Rezaei", email: "ali@example.com", role: "customer", wallet: "0x742d...bD18" },
                      { name: "Sara Ahmadi", email: "sara@example.com", role: "customer", wallet: "0x1a2b...cD34" },
                      { name: "Admin User", email: "admin@boursechain.com", role: "admin", wallet: "0xABCD...EF01" },
                    ].map((user, i) => (
                      <tr key={i} className="border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-3 text-sm font-medium">{user.name}</td>
                        <td className="py-3 text-sm text-muted-foreground">{user.email}</td>
                        <td className="py-3 text-center">
                          <Badge variant={user.role === "admin" ? "default" : "secondary"} className="text-xs">
                            {user.role}
                          </Badge>
                        </td>
                        <td className="py-3 text-sm font-mono text-muted-foreground hidden md:table-cell">{user.wallet}</td>
                        <td className="py-3 text-end">
                          <Button variant="ghost" size="sm" className="h-7 text-xs">{t("common.edit")}</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
