import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  LayoutDashboard,
  TrendingUp,
  Briefcase,
  ClipboardList,
  ArrowLeftRight,
  Bell,
  User,
  Shield,
  ChevronLeft,
  ChevronRight,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Logo } from "@/components/common/Logo";
import { useThemeStore } from "@/stores/themeStore";
import { useAuthStore } from "@/stores/authStore";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const navItems = [
  { key: "dashboard", path: "/dashboard", icon: LayoutDashboard },
  { key: "market", path: "/market", icon: TrendingUp },
  { key: "portfolio", path: "/portfolio", icon: Briefcase },
  { key: "orders", path: "/orders", icon: ClipboardList },
  { key: "transactions", path: "/transactions", icon: ArrowLeftRight },
  { key: "notifications", path: "/notifications", icon: Bell },
];

const adminItems = [
  { key: "admin", path: "/admin", icon: Shield },
];

export function Sidebar() {
  const { t } = useTranslation();
  const { sidebarCollapsed, toggleSidebar, direction } = useThemeStore();
  const { user, logout } = useAuthStore();
  const isRtl = direction === "rtl";

  return (
    <aside
      className={cn(
        "fixed top-0 z-40 flex h-screen flex-col border-e border-border bg-sidebar transition-all duration-300",
        isRtl ? "right-0" : "left-0",
        sidebarCollapsed ? "w-[68px]" : "w-[240px]"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between px-4">
        <Logo collapsed={sidebarCollapsed} />
      </div>

      <Separator />

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="flex flex-col gap-1">
          {[...navItems, { key: "profile", path: "/profile", icon: User }].map(({ key, path, icon: Icon }) => (
            <Tooltip key={key} delayDuration={sidebarCollapsed ? 100 : 1000}>
              <TooltipTrigger asChild>
                <NavLink
                  to={path}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                      isActive
                        ? "bg-accent text-foreground shadow-sm"
                        : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                      sidebarCollapsed && "justify-center px-0"
                    )
                  }
                >
                  <Icon className="h-[18px] w-[18px] shrink-0" />
                  {!sidebarCollapsed && (
                    <span className="truncate">{t(`nav.${key}`)}</span>
                  )}
                </NavLink>
              </TooltipTrigger>
              {sidebarCollapsed && (
                <TooltipContent side={isRtl ? "left" : "right"}>
                  {t(`nav.${key}`)}
                </TooltipContent>
              )}
            </Tooltip>
          ))}

          {user?.role === "admin" && (
            <>
              <Separator className="my-2" />
              {adminItems.map(({ key, path, icon: Icon }) => (
                <Tooltip key={key} delayDuration={sidebarCollapsed ? 100 : 1000}>
                  <TooltipTrigger asChild>
                    <NavLink
                      to={path}
                      className={({ isActive }) =>
                        cn(
                          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                          isActive
                            ? "bg-accent text-foreground shadow-sm"
                            : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                          sidebarCollapsed && "justify-center px-0"
                        )
                      }
                    >
                      <Icon className="h-[18px] w-[18px] shrink-0" />
                      {!sidebarCollapsed && (
                        <span className="truncate">{t(`nav.${key}`)}</span>
                      )}
                    </NavLink>
                  </TooltipTrigger>
                  {sidebarCollapsed && (
                    <TooltipContent side={isRtl ? "left" : "right"}>
                      {t(`nav.${key}`)}
                    </TooltipContent>
                  )}
                </Tooltip>
              ))}
            </>
          )}
        </nav>
      </ScrollArea>

      <Separator />

      {/* Bottom Actions */}
      <div className="p-3">
        <Tooltip delayDuration={sidebarCollapsed ? 100 : 1000}>
          <TooltipTrigger asChild>
            <button
              onClick={logout}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive",
                sidebarCollapsed && "justify-center px-0"
              )}
            >
              <LogOut className="h-[18px] w-[18px] shrink-0" />
              {!sidebarCollapsed && <span>{t("auth.logout")}</span>}
            </button>
          </TooltipTrigger>
          {sidebarCollapsed && (
            <TooltipContent side={isRtl ? "left" : "right"}>
              {t("auth.logout")}
            </TooltipContent>
          )}
        </Tooltip>
      </div>

      {/* Collapse Toggle */}
      <button
        onClick={toggleSidebar}
        className={cn(
          "absolute top-20 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-background shadow-sm transition-colors hover:bg-accent",
          isRtl ? "-left-3" : "-right-3"
        )}
      >
        {sidebarCollapsed ? (
          isRtl ? (
            <ChevronLeft className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )
        ) : isRtl ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </button>
    </aside>
  );
}
