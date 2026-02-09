import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useThemeStore } from "@/stores/themeStore";
import { cn } from "@/lib/utils";

export function MainLayout() {
  const { sidebarCollapsed, direction } = useThemeStore();
  const isRtl = direction === "rtl";

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={cn(
          "flex flex-col transition-all duration-300",
          isRtl
            ? sidebarCollapsed
              ? "mr-[68px]"
              : "mr-[240px]"
            : sidebarCollapsed
              ? "ml-[68px]"
              : "ml-[240px]"
        )}
      >
        <Header />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
