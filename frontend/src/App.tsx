import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { router } from "@/router";
import { useThemeStore } from "@/stores/themeStore";
import "@/i18n";

export default function App() {
  const { theme, language, direction } = useThemeStore();

  // Apply theme on mount and change
  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.setAttribute("dir", direction);
    root.setAttribute("lang", language);
  }, [theme, direction, language]);

  return (
    <TooltipProvider delayDuration={300}>
      <RouterProvider router={router} />
    </TooltipProvider>
  );
}
