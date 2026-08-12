import { useCallback, useEffect, useMemo, useState } from "react";
import { useI18n } from "./i18n";
import LanguageSwitcher from "./components/LanguageSwitcher";
import ScraperForm from "./components/ScraperForm";
import ScraperCard from "./components/ScraperCard";
import ManifestCard from "./components/ManifestCard";

const DEMO_SCRAPER_URL =
  "https://github.com/zoreu/megasource_scrapers/raw/refs/heads/main/default_scraper.py";

const DEMO = {
  id: "default",
  name: "MegaSource default",
  url: DEMO_SCRAPER_URL,
  description: "Default scraper hosted on GitHub.",
};

function encodeConfig(scrapers) {
  return btoa(unescape(encodeURIComponent(JSON.stringify(scrapers))))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

export default function App() {
  const { t } = useI18n();
  const [scrapers, setScrapers] = useState([DEMO]);
  const [baseUrl, setBaseUrl] = useState(window.location.origin);
  const [online, setOnline] = useState(false);
  const [tests, setTests] = useState({});

  useEffect(() => {
    fetch("/api/state")
      .then((r) => r.json())
      .then((data) => {
        setOnline(true);
        if (data.base_url) setBaseUrl(data.base_url);
      })
      .catch(() => setOnline(false));
  }, []);

  const addScraper = useCallback(
    ({ name, url }) => {
      const item = {
        id: `scraper-${Date.now()}`,
        name: name || "Scraper",
        url,
        description: "",
      };
      setScrapers((prev) => [...prev, item]);
    },
    []
  );

  const removeScraper = useCallback(
    (id) => setScrapers((prev) => prev.filter((s) => s.id !== id)),
    []
  );

  const clearAll = useCallback(() => {
    setTests({});
    setScrapers([]);
  }, []);

  const restoreDemo = useCallback(() => setScrapers([DEMO]), []);

  const testScraper = useCallback(
    async (scraper) => {
      setTests((prev) => ({ ...prev, [scraper.id]: { status: "loading" } }));
      try {
        const res = await fetch("/api/test-scraper", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: scraper.url }),
        });
        const data = await res.json();
        if (data.ok) {
          setTests((prev) => ({
            ...prev,
            [scraper.id]: {
              status: "ok",
              message: t("testSuccess", { count: data.count }),
            },
          }));
        } else {
          setTests((prev) => ({
            ...prev,
            [scraper.id]: {
              status: "error",
              message: t("testFail", { error: data.error }),
            },
          }));
        }
      } catch (e) {
        setTests((prev) => ({
          ...prev,
          [scraper.id]: {
            status: "error",
            message: t("testFail", { error: String(e) }),
          },
        }));
      }
    },
    [t]
  );

  const manifestUrl = useMemo(() => {
    const base = baseUrl.endsWith("/") ? baseUrl : baseUrl + "/";
    const suffix = scrapers.length
      ? `${encodeConfig(scrapers)}/manifest.json`
      : "manifest.json";
    return new URL(suffix, base).href;
  }, [scrapers, baseUrl]);

  return (
    <div className="page">
      <header className="header">
        <div className="brand">
          <div className="logo">MS</div>
          <div>
            <h1>MegaSource</h1>
            <p className="muted">{t("tagline")}</p>
          </div>
        </div>
        <div className="header-right">
          <span className={`status ${online ? "ok" : "err"}`}>
            <span className="dot" />
            {online ? t("online") : t("offline")}
          </span>
          <LanguageSwitcher />
        </div>
      </header>

      <main>
        <section className="card">
          <h2>{t("scrapers")}</h2>
          <ScraperForm onAdd={addScraper} />
          <p className="hint">{t("githubHint")}</p>
          <p className="hint highlight">{t("demoTip")}</p>

          <div className="scraper-list">
            {scrapers.map((s) => (
              <ScraperCard
                key={s.id}
                scraper={s}
                testState={tests[s.id]}
                onDelete={removeScraper}
                onTest={testScraper}
              />
            ))}
            {scrapers.length === 0 && <p className="empty">{t("empty")}</p>}
          </div>

          <div className="list-actions">
            <button className="btn ghost" onClick={restoreDemo}>
              {t("restoreDemo")}
            </button>
            {scrapers.length > 0 && (
              <button className="btn ghost danger" onClick={clearAll}>
                {t("clearAll")}
              </button>
            )}
          </div>
        </section>

        <ManifestCard url={manifestUrl} />
      </main>

      <footer className="footer muted">{t("footer")}</footer>
    </div>
  );
}