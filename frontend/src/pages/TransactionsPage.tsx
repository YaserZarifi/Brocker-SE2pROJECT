import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { ArrowLeftRight, ExternalLink, CheckCircle, Clock, XCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { transactionService } from "@/services/transactionService";
import { useThemeStore } from "@/stores/themeStore";
import { formatPrice, cn } from "@/lib/utils";
import type { Transaction } from "@/types";

const statusConfig = {
  confirmed: { icon: CheckCircle, variant: "success" as const, color: "text-stock-up" },
  pending: { icon: Clock, variant: "warning" as const, color: "text-amber-500" },
  failed: { icon: XCircle, variant: "danger" as const, color: "text-stock-down" },
};

export default function TransactionsPage() {
  const { t } = useTranslation();
  const { language } = useThemeStore();
  const [mockTransactions, setTransactions] = useState<Transaction[]>([]);

  useEffect(() => {
    transactionService.getTransactions().then(setTransactions).catch(() => {});
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold">{t("transactions.title")}</h1>
        <p className="text-sm text-muted-foreground mt-1">
          {mockTransactions.length} {t("transactions.title").toLowerCase()}
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-stock-up-bg">
              <CheckCircle className="h-5 w-5 text-stock-up" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockTransactions.filter((tx) => tx.status === "confirmed").length}</p>
              <p className="text-xs text-muted-foreground">{t("transactions.confirmed")}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10">
              <Clock className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">{mockTransactions.filter((tx) => tx.status === "pending").length}</p>
              <p className="text-xs text-muted-foreground">{t("transactions.pending")}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-muted">
              <ArrowLeftRight className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <p className="text-2xl font-bold tabular-nums">
                {formatPrice(
                  mockTransactions.reduce((sum, tx) => sum + tx.totalValue, 0),
                  language
                )}
              </p>
              <p className="text-xs text-muted-foreground">{t("transactions.total")}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Transactions Table */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <ArrowLeftRight className="h-4 w-4" />
            {t("transactions.title")}
          </CardTitle>
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
                  <th className="pb-3 text-start font-medium hidden md:table-cell">{t("transactions.blockchain")}</th>
                  <th className="pb-3 text-center font-medium">{t("transactions.status")}</th>
                  <th className="pb-3 text-end font-medium">{t("transactions.date")}</th>
                </tr>
              </thead>
              <tbody>
                {mockTransactions.map((tx) => {
                  const cfg = statusConfig[tx.status];
                  const StatusIcon = cfg.icon;
                  return (
                    <tr key={tx.id} className="border-b border-border/50 last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="py-3.5 text-sm font-mono text-muted-foreground">{tx.id}</td>
                      <td className="py-3.5">
                        <span className="text-sm font-medium">{tx.stockSymbol}</span>
                      </td>
                      <td className="py-3.5 text-end text-sm tabular-nums">{formatPrice(tx.price, language)}</td>
                      <td className="py-3.5 text-end text-sm tabular-nums">{tx.quantity}</td>
                      <td className="py-3.5 text-end text-sm tabular-nums font-medium">{formatPrice(tx.totalValue, language)}</td>
                      <td className="py-3.5 hidden md:table-cell">
                        {tx.blockchainHash && (
                          <Button variant="ghost" size="sm" className="h-7 gap-1 font-mono text-xs text-muted-foreground">
                            {tx.blockchainHash}
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        )}
                      </td>
                      <td className="py-3.5 text-center">
                        <Badge variant={cfg.variant} className="gap-1 text-xs">
                          <StatusIcon className="h-3 w-3" />
                          {t(`transactions.${tx.status}`)}
                        </Badge>
                      </td>
                      <td className="py-3.5 text-end text-xs text-muted-foreground">
                        {new Date(tx.executedAt).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
