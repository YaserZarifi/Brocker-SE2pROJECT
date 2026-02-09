import { TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTranslation } from "react-i18next";

interface LogoProps {
  collapsed?: boolean;
  className?: string;
}

export function Logo({ collapsed = false, className }: LogoProps) {
  const { t } = useTranslation();

  return (
    <div className={cn("flex items-center gap-2.5", className)}>
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/20">
        <TrendingUp className="h-5 w-5 text-white" />
      </div>
      {!collapsed && (
        <div className="flex flex-col">
          <span className="text-base font-bold tracking-tight text-foreground">
            {t("app.name")}
          </span>
          <span className="text-[10px] text-muted-foreground leading-none">
            {t("app.tagline")}
          </span>
        </div>
      )}
    </div>
  );
}
