import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { ClipboardList, X, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { orderService } from "@/services/orderService";
import { useThemeStore } from "@/stores/themeStore";
import { formatPrice, cn } from "@/lib/utils";
import type { Order, OrderStatus } from "@/types";

const statusVariant: Record<OrderStatus, "success" | "warning" | "danger" | "secondary" | "outline"> = {
  matched: "success",
  pending: "warning",
  partial: "warning",
  cancelled: "danger",
  expired: "secondary",
};

export default function OrdersPage() {
  const { t } = useTranslation();
  const { language } = useThemeStore();
  const [filter, setFilter] = useState("all");
  const [allOrders, setAllOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    orderService.getOrders()
      .then(setAllOrders)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const orders = filter === "all"
    ? allOrders
    : allOrders.filter((o) => o.status === filter);

  const handleCancel = async (id: string) => {
    try {
      const updated = await orderService.cancelOrder(id);
      setAllOrders((prev) => prev.map((o) => (o.id === id ? updated : o)));
    } catch {}
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">{t("orders.title")}</h1>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {(["pending", "matched", "partial", "cancelled"] as OrderStatus[]).map((status) => (
          <Card key={status} className="cursor-pointer hover:border-primary/50 transition-colors" onClick={() => setFilter(status)}>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">{allOrders.filter((o) => o.status === status).length}</p>
              <p className="text-xs text-muted-foreground mt-1">{t(`orders.${status}`)}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <ClipboardList className="h-4 w-4" />
            {t("orders.title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Filter Tabs */}
          <Tabs value={filter} onValueChange={setFilter} className="mb-4">
            <TabsList>
              <TabsTrigger value="all">{t("orders.all")}</TabsTrigger>
              <TabsTrigger value="pending">{t("orders.pending")}</TabsTrigger>
              <TabsTrigger value="matched">{t("orders.matched")}</TabsTrigger>
              <TabsTrigger value="partial">{t("orders.partial")}</TabsTrigger>
              <TabsTrigger value="cancelled">{t("orders.cancelled")}</TabsTrigger>
            </TabsList>
          </Tabs>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border text-xs text-muted-foreground">
                  <th className="pb-3 text-start font-medium">{t("orders.orderId")}</th>
                  <th className="pb-3 text-start font-medium">{t("orders.stock")}</th>
                  <th className="pb-3 text-center font-medium">{t("orders.type")}</th>
                  <th className="pb-3 text-end font-medium">{t("orders.price")}</th>
                  <th className="pb-3 text-end font-medium">{t("orders.qty")}</th>
                  <th className="pb-3 text-end font-medium">{t("orders.filled")}</th>
                  <th className="pb-3 text-center font-medium">{t("orders.status")}</th>
                  <th className="pb-3 text-end font-medium">{t("orders.date")}</th>
                  <th className="pb-3 text-end font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr
                    key={order.id}
                    className="border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3.5 text-sm font-mono text-muted-foreground">
                      {order.id}
                    </td>
                    <td className="py-3.5">
                      <span className="text-sm font-medium">{order.stockSymbol}</span>
                    </td>
                    <td className="py-3.5 text-center">
                      <Badge
                        variant={order.type === "buy" ? "success" : "danger"}
                        className="text-xs"
                      >
                        {t(`stock.${order.type}`)}
                      </Badge>
                    </td>
                    <td className="py-3.5 text-end text-sm tabular-nums">
                      {formatPrice(order.price, language)}
                    </td>
                    <td className="py-3.5 text-end text-sm tabular-nums">
                      {order.quantity}
                    </td>
                    <td className="py-3.5 text-end text-sm tabular-nums">
                      {order.filledQuantity}/{order.quantity}
                    </td>
                    <td className="py-3.5 text-center">
                      <Badge variant={statusVariant[order.status]} className="text-xs">
                        {t(`orders.${order.status}`)}
                      </Badge>
                    </td>
                    <td className="py-3.5 text-end text-xs text-muted-foreground">
                      {new Date(order.createdAt).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 text-end">
                      {order.status === "pending" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-destructive hover:text-destructive h-7"
                          onClick={() => handleCancel(order.id)}
                        >
                          <X className="h-3 w-3" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {orders.length === 0 && (
            <div className="py-12 text-center text-muted-foreground">
              {t("orders.noOrders")}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
