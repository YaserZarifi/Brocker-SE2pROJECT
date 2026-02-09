import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import fa from "./fa.json";

const savedLang = localStorage.getItem("language") || "en";

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    fa: { translation: fa },
  },
  lng: savedLang,
  fallbackLng: "en",
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
