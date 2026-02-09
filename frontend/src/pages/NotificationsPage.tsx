import { useTranslation } from "react-i18next";
import {
  Bell,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  ArrowLeftRight,
  CheckCheck,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useNotificationStore } from "@/stores/notificationStore";
import { useThemeStore } from "@/stores/themeStore";
import { cn } from "@/lib/utils";

const typeConfig = {
  order_matched: { icon: CheckCircle, color: "text-stock-up", bg: "bg-stock-up-bg" },
  order_cancelled: { icon: XCircle, color: "text-stock-down", bg: "bg-stock-down-bg" },
  price_alert: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10" },
  system: { icon: Info, color: "text-blue-500", bg: "bg-blue-500/10" },
  transaction: { icon: ArrowLeftRight, color: "text-purple-500", bg: "bg-purple-500/10" },
};

export default function NotificationsPage() {
  const { t } = useTranslation();
  const { notifications, markAsRead, markAllAsRead, unreadCount } =
    useNotificationStore();
  const { language } = useThemeStore();

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{t("notifications.title")}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {unreadCount > 0
              ? `${unreadCount} unread`
              : t("notifications.empty")}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button variant="outline" size="sm" onClick={markAllAsRead}>
            <CheckCheck className="h-4 w-4 me-1.5" />
            {t("notifications.markAllRead")}
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="p-0 divide-y divide-border">
          {notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <Bell className="h-10 w-10 mb-3 opacity-30" />
              <p>{t("notifications.empty")}</p>
            </div>
          ) : (
            notifications.map((notif) => {
              const cfg = typeConfig[notif.type];
              const Icon = cfg.icon;
              return (
                <div
                  key={notif.id}
                  className={cn(
                    "flex items-start gap-4 p-5 transition-colors hover:bg-muted/30 cursor-pointer",
                    !notif.read && "bg-muted/20"
                  )}
                  onClick={() => markAsRead(notif.id)}
                >
                  <div
                    className={cn(
                      "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                      cfg.bg
                    )}
                  >
                    <Icon className={cn("h-5 w-5", cfg.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className={cn("text-sm font-medium", !notif.read && "font-semibold")}>
                          {language === "fa" ? notif.titleFa : notif.title}
                        </p>
                        <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">
                          {language === "fa" ? notif.messageFa : notif.message}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        {!notif.read && (
                          <div className="h-2 w-2 rounded-full bg-blue-500" />
                        )}
                        <span className="text-xs text-muted-foreground whitespace-nowrap">
                          {new Date(notif.createdAt).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>
    </div>
  );
}
