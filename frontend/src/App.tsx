import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { router } from "@/router";
import { useThemeStore } from "@/stores/themeStore";
import { useAuthStore } from "@/stores/authStore";
import { useNotificationStore } from "@/stores/notificationStore";
import { useStockStore } from "@/stores/stockStore";
import "@/i18n";

export default function App() {
  const { theme, language, direction } = useThemeStore();
  const { checkAuth, isAuthenticated } = useAuthStore();
  const { fetchNotifications, connectWebSocket: connectNotificationWs, disconnectWebSocket: disconnectNotificationWs } = useNotificationStore();
  const { connectWebSocket: connectStockWs } = useStockStore();

  // Apply theme on mount and change
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.setAttribute("dir", direction);
    root.setAttribute("lang", language);
  }, [theme, direction, language]);

  // Check authentication on app load
  useEffect(() => {
    checkAuth();
  }, []);

  // Connect stock price WebSocket on mount (public, no auth needed)
  useEffect(() => {
    connectStockWs();
  }, []);

  // When authenticated: fetch notifications + connect notification WebSocket
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
      connectNotificationWs();
    } else {
      disconnectNotificationWs();
    }
  }, [isAuthenticated]);

  return (
    <TooltipProvider delayDuration={300}>
      <RouterProvider router={router} />
    </TooltipProvider>
  );
}
