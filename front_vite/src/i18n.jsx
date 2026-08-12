import { createContext, useContext, useEffect, useState } from "react";

export const LOCALES = {
  en: { label: "English" },
  "pt-BR": { label: "Português (BR)" },
};

export const messages = {
  en: {
    tagline: "Pluggable Python scrapers for movies & series",
    server: "Server",
    online: "Online",
    offline: "Offline",
    scrapers: "Configured scrapers",
    scraperNamePlaceholder: "Scraper name (optional)",
    scraperUrlPlaceholder: "https://raw.githubusercontent.com/user/repo/main/scraper.py",
    addScraper: "Add scraper",
    test: "Test",
    testing: "Testing…",
    delete: "Excluir",
    clearAll: "Clear all",
    restoreDemo: "Restore scraper",
    empty: "No scrapers yet. Add your first scraper above.",
    githubHint:
      "Upload scraper_demo/scraper.py to a GitHub repository and paste its raw URL. You can add as many scrapers as you want.",
    demoTip:
      "The default scraper uses the fixed GitHub URL https://github.com/zoreu/megasource_scrapers/raw/refs/heads/main/default_scraper.py",
    demo: "Default",
    manifestUrl: "Manifest URL",
    manifestHint:
      "Copy this URL and install it in Stremio. It already carries your configured scrapers.",
    copy: "Copy",
    copied: "Copied!",
    install: "Install in Stremio",
    installHint:
      "The full link (with config) was copied. If Stremio opens without it, paste the copied link into the add-on field manually.",
    testSuccess: "Works! %{count} streams found.",
    testFail: "Failed: %{error}",
    configSaved: "Saved on server.",
    footer: "Configure • Add • Stream",
  },
  "pt-BR": {
    tagline: "Scrapers Python plugáveis para filmes e séries",
    server: "Servidor",
    online: "Online",
    offline: "Offline",
    scrapers: "Scrapers configurados",
    scraperNamePlaceholder: "Nome do scraper (opcional)",
    scraperUrlPlaceholder: "https://raw.githubusercontent.com/usuario/repositorio/main/scraper.py",
    addScraper: "Adicionar scraper",
    test: "Testar",
    testing: "Testando…",
    delete: "Excluir",
    clearAll: "Limpar tudo",
    restoreDemo: "Restaurar scraper",
    empty: "Nenhum scraper ainda. Adicione o primeiro acima.",
    githubHint:
      "Envie scraper_demo/scraper.py para um repositório no GitHub e cole a URL raw aqui. Você pode adicionar quantos scrapers quiser.",
    demoTip:
      "O scraper default usa a URL fixa do GitHub https://github.com/zoreu/megasource_scrapers/raw/refs/heads/main/default_scraper.py",
    demo: "Default",
    manifestUrl: "URL do manifest",
    manifestHint:
      "Copie esta URL e instale no Stremio. Ela já carrega os scrapers configurados.",
    copy: "Copiar",
    copied: "Copiado!",
    install: "Instalar no Stremio",
    installHint:
      "O link completo (com config) foi copiado. Se o Stremio abrir sem ele, cole o link copiado no campo de addon manualmente.",
    testSuccess: "Funcionou! %{count} streams encontrados.",
    testFail: "Falhou: %{error}",
    configSaved: "Salvo no servidor.",
    footer: "Configure • Adicione • Assista",
  },
};

const I18nContext = createContext(null);

export function I18nProvider({ children }) {
  const [locale, setLocale] = useState(() => {
    const saved = localStorage.getItem("megasource-locale");
    if (saved && messages[saved]) return saved;
    const nav = (navigator.language || "en").toLowerCase();
    return nav.startsWith("pt") ? "pt-BR" : "en";
  });

  useEffect(() => {
    localStorage.setItem("megasource-locale", locale);
    document.documentElement.lang = locale === "pt-BR" ? "pt-BR" : "en";
  }, [locale]);

  const t = (key, vars) => {
    let text = messages[locale]?.[key] ?? messages.en[key] ?? key;
    if (vars) {
      for (const [k, v] of Object.entries(vars)) {
        text = text.split(`%{${k}}`).join(String(v));
      }
    }
    return text;
  };

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside I18nProvider");
  return ctx;
}