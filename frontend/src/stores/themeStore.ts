import { create } from "zustand";
import type { Theme, Language, Direction } from "@/types";
import i18n from "@/i18n";

interface ThemeState {
  theme: Theme;
  language: Language;
  direction: Direction;
  sidebarCollapsed: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;
}

const getInitialTheme = (): Theme => {
  const saved = localStorage.getItem("theme") as Theme;
  if (saved) return saved;
  return "dark";
};

const getInitialLanguage = (): Language => {
  const saved = localStorage.getItem("language") as Language;
  if (saved) return saved;
  return "en";
};

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: getInitialTheme(),
  language: getInitialLanguage(),
  direction: getInitialLanguage() === "fa" ? "rtl" : "ltr",
  sidebarCollapsed: false,

  setTheme: (theme) => {
    localStorage.setItem("theme", theme);
    document.documentElement.classList.toggle("dark", theme === "dark");
    set({ theme });
  },

  toggleTheme: () => {
    const newTheme = get().theme === "dark" ? "light" : "dark";
    get().setTheme(newTheme);
  },

  setLanguage: (language) => {
    localStorage.setItem("language", language);
    const direction = language === "fa" ? "rtl" : "ltr";
    document.documentElement.setAttribute("dir", direction);
    document.documentElement.setAttribute("lang", language);
    i18n.changeLanguage(language);
    set({ language, direction });
  },

  toggleLanguage: () => {
    const newLang = get().language === "en" ? "fa" : "en";
    get().setLanguage(newLang);
  },

  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
}));
