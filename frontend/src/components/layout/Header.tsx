import { useTranslation } from "react-i18next";
import { Bell, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/stores/authStore";
import { getAvatarUrl } from "@/lib/utils";
import { useNotificationStore } from "@/stores/notificationStore";
import { useThemeStore } from "@/stores/themeStore";

export function Header() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { unreadCount } = useNotificationStore();
  const { sidebarCollapsed, direction } = useThemeStore();
  const isRtl = direction === "rtl";

  const initials = user?.name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/80 px-6 backdrop-blur-md transition-all duration-300",
        isRtl
          ? sidebarCollapsed
            ? "mr-[68px]"
            : "mr-[240px]"
          : sidebarCollapsed
            ? "ml-[68px]"
            : "ml-[240px]"
      )}
    >
      {/* Search */}
      <div className="relative w-full max-w-md">
        <Search className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder={t("common.search")}
          className="h-9 ps-9 bg-muted/50 border-none focus-visible:ring-1"
        />
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-1">
        <LanguageToggle />
        <ThemeToggle />

        {/* Notifications */}
        <button
          onClick={() => navigate("/notifications")}
          className="relative flex h-9 w-9 items-center justify-center rounded-lg transition-colors hover:bg-accent text-muted-foreground hover:text-foreground"
        >
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -end-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-blue-500 px-1 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </button>

        {/* User */}
        <div
          onClick={() => navigate("/profile")}
          className="ms-2 flex items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-accent cursor-pointer"
        >
          <Avatar className="h-8 w-8">
            <AvatarImage src={user?.avatar ? getAvatarUrl(user.avatar) : undefined} alt={user?.name} />
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-xs font-semibold">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="hidden md:flex flex-col">
            <span className="text-sm font-medium leading-tight">
              {user?.name}
            </span>
            <span className="text-[11px] text-muted-foreground leading-tight">
              {user?.email}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
