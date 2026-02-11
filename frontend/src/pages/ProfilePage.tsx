import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  User,
  Shield,
  Palette,
  Camera,
  Mail,
  Wallet,
  Calendar,
  DollarSign,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { authService } from "@/services/authService";
import { getAvatarUrl, formatPrice } from "@/lib/utils";

export default function ProfilePage() {
  const { t } = useTranslation();
  const { user, setUser, checkAuth } = useAuthStore();
  const { theme, language, setTheme, setLanguage } = useThemeStore();

  const [profileForm, setProfileForm] = useState({
    firstName: user?.firstName ?? "",
    lastName: user?.lastName ?? "",
    username: user?.username ?? "",
    walletAddress: user?.walletAddress ?? "",
  });
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const [passwordForm, setPasswordForm] = useState({
    oldPassword: "",
    newPassword: "",
    confirmNewPassword: "",
  });

  const [profileLoading, setProfileLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    if (user) {
      setProfileForm({
        firstName: user.firstName ?? "",
        lastName: user.lastName ?? "",
        username: user.username ?? "",
        walletAddress: user.walletAddress ?? "",
      });
    }
  }, [user]);

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    setProfileError(null);
    setProfileSuccess(false);
    try {
      const updatedUser = await authService.updateProfile({
        first_name: profileForm.firstName,
        last_name: profileForm.lastName,
        username: profileForm.username,
        wallet_address: profileForm.walletAddress || undefined,
        avatar: avatarFile ?? undefined,
      });
      setUser(updatedUser);
      setAvatarFile(null);
      setAvatarPreview(null);
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { [k: string]: string[] } } })?.response?.data?.username?.[0] ||
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to update profile";
      setProfileError(message);
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
      setPasswordError(t("auth.confirmPassword") + " do not match");
      return;
    }
    setPasswordLoading(true);
    setPasswordError(null);
    setPasswordSuccess(false);
    try {
      await authService.changePassword({
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword,
      });
      setPasswordForm({ oldPassword: "", newPassword: "", confirmNewPassword: "" });
      setPasswordSuccess(true);
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Failed to change password";
      setPasswordError(message);
    } finally {
      setPasswordLoading(false);
    }
  };

  const initials = user?.name
    ?.split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
  const avatarUrl = avatarPreview || (user?.avatar ? getAvatarUrl(user.avatar) : undefined);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(language === "fa" ? "fa-IR" : "en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (!user) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Profile Header */}
      <Card className="overflow-hidden">
        <div className="h-24 bg-gradient-to-br from-primary/20 via-primary/10 to-transparent" />
        <CardContent className="relative pt-0">
          <div className="-mt-14 flex flex-col items-start gap-4 sm:flex-row sm:items-end">
            <div className="relative">
              <Avatar className="h-28 w-28 border-4 border-background shadow-lg">
                <AvatarImage src={avatarUrl} alt={user.name} />
                <AvatarFallback className="bg-gradient-to-br from-primary to-primary/70 text-2xl text-white">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <label className="absolute bottom-0 end-0 flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border-2 border-background bg-primary text-primary-foreground shadow-md transition-colors hover:bg-primary/90">
                <Camera className="h-4 w-4" />
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarChange}
                />
              </label>
            </div>
            <div className="flex-1 space-y-1 pb-1">
              <h1 className="text-2xl font-bold">{user.name || user.email}</h1>
              <p className="flex items-center gap-2 text-muted-foreground">
                <Mail className="h-4 w-4" />
                {user.email}
              </p>
              <div className="flex flex-wrap gap-4 pt-2">
                {user.cashBalance && (
                  <span className="flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-3 py-1 text-sm font-medium text-emerald-600 dark:text-emerald-400">
                    <DollarSign className="h-4 w-4" />
                    {formatPrice(parseFloat(user.cashBalance), language)}
                  </span>
                )}
                <span className="flex items-center gap-1.5 rounded-full bg-muted px-3 py-1 text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4" />
                  {t("profile.memberSince")} {formatDate(user.createdAt)}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="personal" className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="personal" className="gap-2">
            <User className="h-4 w-4" />
            {t("profile.personalInfo")}
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-2">
            <Shield className="h-4 w-4" />
            {t("profile.security")}
          </TabsTrigger>
          <TabsTrigger value="preferences" className="gap-2">
            <Palette className="h-4 w-4" />
            {t("profile.preferences")}
          </TabsTrigger>
        </TabsList>

        {/* Personal Info */}
        <TabsContent value="personal" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("profile.personalInfo")}</CardTitle>
              <CardDescription>
                Update your personal information and display name.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">{t("profile.firstName")}</label>
                    <Input
                      value={profileForm.firstName}
                      onChange={(e) =>
                        setProfileForm((p) => ({ ...p, firstName: e.target.value }))
                      }
                      placeholder="Ali"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">{t("profile.lastName")}</label>
                    <Input
                      value={profileForm.lastName}
                      onChange={(e) =>
                        setProfileForm((p) => ({ ...p, lastName: e.target.value }))
                      }
                      placeholder="Rezaei"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("profile.username")}</label>
                  <Input
                    value={profileForm.username}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, username: e.target.value }))
                    }
                    placeholder="alirezaei"
                  />
                </div>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm font-medium">
                    <Wallet className="h-4 w-4" />
                    {t("profile.walletAddress")}
                  </label>
                  <Input
                    value={profileForm.walletAddress}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, walletAddress: e.target.value }))
                    }
                    placeholder="0x..."
                  />
                </div>
                {profileError && (
                  <p className="text-sm text-destructive">{profileError}</p>
                )}
                {profileSuccess && (
                  <p className="text-sm text-emerald-600 dark:text-emerald-400">
                    {t("profile.updateSuccess")}
                  </p>
                )}
                <Button type="submit" disabled={profileLoading}>
                  {profileLoading ? t("common.loading") : t("profile.updateProfile")}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("profile.changePassword")}</CardTitle>
              <CardDescription>
                Change your password. Use a strong password for security.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("profile.currentPassword")}</label>
                  <Input
                    type="password"
                    value={passwordForm.oldPassword}
                    onChange={(e) =>
                      setPasswordForm((p) => ({ ...p, oldPassword: e.target.value }))
                    }
                    required
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">{t("profile.newPassword")}</label>
                  <Input
                    type="password"
                    value={passwordForm.newPassword}
                    onChange={(e) =>
                      setPasswordForm((p) => ({ ...p, newPassword: e.target.value }))
                    }
                    required
                    minLength={8}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    {t("profile.confirmNewPassword")}
                  </label>
                  <Input
                    type="password"
                    value={passwordForm.confirmNewPassword}
                    onChange={(e) =>
                      setPasswordForm((p) => ({ ...p, confirmNewPassword: e.target.value }))
                    }
                    required
                  />
                </div>
                {passwordError && (
                  <p className="text-sm text-destructive">{passwordError}</p>
                )}
                {passwordSuccess && (
                  <p className="text-sm text-emerald-600 dark:text-emerald-400">
                    {t("profile.passwordSuccess")}
                  </p>
                )}
                <Button type="submit" disabled={passwordLoading}>
                  {passwordLoading ? t("common.loading") : t("profile.changePassword")}
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences */}
        <TabsContent value="preferences" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("profile.preferences")}</CardTitle>
              <CardDescription>
                Customize your display and language settings.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <label className="text-sm font-medium">{t("profile.theme")}</label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={theme === "light" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTheme("light")}
                  >
                    {t("profile.light")}
                  </Button>
                  <Button
                    type="button"
                    variant={theme === "dark" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setTheme("dark")}
                  >
                    {t("profile.dark")}
                  </Button>
                </div>
              </div>
              <Separator />
              <div className="space-y-3">
                <label className="text-sm font-medium">{t("profile.language")}</label>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant={language === "en" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLanguage("en")}
                  >
                    English
                  </Button>
                  <Button
                    type="button"
                    variant={language === "fa" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLanguage("fa")}
                  >
                    فارسی
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
