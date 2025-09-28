import React, { createContext, useContext, ReactNode } from "react";

interface I18nContextType {
  t: (key: string, params?: Record<string, any>) => string;
  language: string;
  setLanguage: (lang: string) => void;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

interface I18nProviderProps {
  children: ReactNode;
}

export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  const [language, setLanguage] = React.useState("en");

  const t = (key: string, params?: Record<string, any>): string => {
    // Simple translation function - in a real app, this would use a translation library
    return key;
  };

  const value = {
    t,
    language,
    setLanguage,
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export const useI18n = (): I18nContextType => {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error("useI18n must be used within an I18nProvider");
  }
  return context;
};

// Alias for backward compatibility
export const useTranslationHook = useI18n;
