import { useI18n } from "../i18n";

export default function ScraperCard({ scraper, testState, onDelete, onTest }) {
  const { t } = useI18n();
  const state = testState || { status: "idle" };
  const isDemo =
    scraper.url.includes("/demo/scraper.py") ||
    scraper.url.includes("megasource-demo-scraper") ||
    scraper.url.includes("megasource_scrapers");

  return (
    <div className="scraper-card">
      <div className="scraper-info">
        <div className="scraper-title">
          {scraper.name || "Scraper"}
          {isDemo && <span className="pill">{t("demo")}</span>}
        </div>
        <a
          className="scraper-url"
          href={scraper.url}
          target="_blank"
          rel="noreferrer"
          title={scraper.url}
        >
          {scraper.url}
        </a>
        {state.status === "ok" && <div className="badge ok">{state.message}</div>}
        {state.status === "error" && <div className="badge err">{state.message}</div>}
      </div>
      <div className="scraper-actions">
        <button
          className="btn ghost"
          disabled={state.status === "loading"}
          onClick={() => onTest(scraper)}
        >
          {state.status === "loading" ? t("testing") : t("test")}
        </button>
        <button className="btn danger" onClick={() => onDelete(scraper.id)}>
          {t("delete")}
        </button>
      </div>
    </div>
  );
}