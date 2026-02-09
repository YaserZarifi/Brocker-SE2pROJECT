import { Languages } from "lucide-react";
import { useThemeStore } from "@/stores/themeStore";
import { cn } from "@/lib/utils";

export function LanguageToggle() {
  const { language, toggleLanguage } = useThemeStore();

  return (
    <button
      onClick={toggleLanguage}
      className={cn(
        "flex h-9 items-center gap-1.5 rounded-lg px-2.5 transition-colors",
        "hover:bg-accent text-muted-foreground hover:text-foreground"
      )}
      title={language === "en" ? "تغییر به فارسی" : "Switch to English"}
    >
      <Languages className="h-4 w-4" />
      <span className="text-xs font-medium uppercase">
        {language === "en" ? "FA" : "EN"}
      </span>
    </button>
  );
}
