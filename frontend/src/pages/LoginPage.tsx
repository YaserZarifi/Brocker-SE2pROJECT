import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { TrendingUp, Mail, Lock, Wallet, ArrowRight, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/authStore";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import { LanguageToggle } from "@/components/common/LanguageToggle";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, loginWithEthereum, isLoading } = useAuthStore();
  const [email, setEmail] = useState("ali@example.com");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
    navigate("/dashboard");
  };

  const handleSIWE = async () => {
    await loginWithEthereum("0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18");
    navigate("/dashboard");
  };

  return (
    <div className="relative flex min-h-screen">
      {/* Top Right Controls */}
      <div className="absolute top-4 end-4 z-10 flex items-center gap-1">
        <LanguageToggle />
        <ThemeToggle />
      </div>

      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-12 text-white relative overflow-hidden">
        {/* Background Decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 -left-20 h-64 w-64 rounded-full bg-white blur-3xl" />
          <div className="absolute bottom-20 right-10 h-96 w-96 rounded-full bg-white blur-3xl" />
        </div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
              <TrendingUp className="h-7 w-7" />
            </div>
            <span className="text-2xl font-bold">{t("app.name")}</span>
          </div>
          <p className="text-white/70 text-sm">{t("app.tagline")}</p>
        </div>

        <div className="relative z-10 space-y-8">
          <div>
            <h1 className="text-4xl font-bold leading-tight mb-4">
              {t("auth.welcomeBack")}
            </h1>
            <p className="text-lg text-white/80 leading-relaxed">
              {t("auth.welcomeDesc")}
            </p>
          </div>

          {/* Feature Highlights */}
          <div className="space-y-4">
            {[
              { label: "Real-time Stock Prices", labelFa: "قیمت لحظه‌ای سهام" },
              { label: "Blockchain Secured Trades", labelFa: "معاملات امن بلاکچینی" },
              { label: "Smart Order Matching", labelFa: "تطبیق هوشمند سفارشات" },
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10">
                  <ArrowRight className="h-4 w-4" />
                </div>
                <span className="text-white/90">{feature.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-sm text-white/50">
          &copy; 2026 BourseChain. Amirkabir University - SE2 Project
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex w-full items-center justify-center p-8 lg:w-1/2">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">{t("app.name")}</span>
          </div>

          <div>
            <h2 className="text-2xl font-bold">{t("auth.login")}</h2>
            <p className="mt-2 text-muted-foreground">
              {t("auth.welcomeDesc")}
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t("auth.email")}</label>
              <div className="relative">
                <Mail className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="ps-10"
                  placeholder="email@example.com"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t("auth.password")}</label>
              <div className="relative">
                <Lock className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="ps-10 pe-10"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute end-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Options */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" className="rounded" defaultChecked />
                {t("auth.rememberMe")}
              </label>
              <a href="#" className="text-sm text-blue-500 hover:underline">
                {t("auth.forgotPassword")}
              </a>
            </div>

            <Button type="submit" className="w-full h-11" disabled={isLoading}>
              {isLoading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              ) : (
                t("auth.login")
              )}
            </Button>
          </form>

          <div className="relative">
            <Separator />
            <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-3 text-xs text-muted-foreground">
              {t("auth.orContinueWith")}
            </span>
          </div>

          {/* SIWE */}
          <Button
            variant="outline"
            className={cn("w-full h-11 gap-2.5")}
            onClick={handleSIWE}
            disabled={isLoading}
          >
            <Wallet className="h-4 w-4" />
            {t("auth.siwe")}
          </Button>
          <p className="text-center text-xs text-muted-foreground">
            {t("auth.siweDesc")}
          </p>

          {/* Register Link */}
          <p className="text-center text-sm text-muted-foreground">
            {t("auth.noAccount")}{" "}
            <Link to="/register" className="font-medium text-blue-500 hover:underline">
              {t("auth.register")}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
