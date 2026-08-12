import { useState } from "react";
import { useI18n } from "../i18n";

export default function ScraperForm({ onAdd }) {
  const { t } = useI18n();
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");

  const submit = (e) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;
    onAdd({ name: name.trim(), url: trimmed });
    setName("");
    setUrl("");
  };

  return (
    <form className="scraper-form" onSubmit={submit}>
      <input
        className="input"
        type="text"
        placeholder={t("scraperNamePlaceholder")}
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="input grow"
        type="url"
        required
        placeholder={t("scraperUrlPlaceholder")}
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button className="btn primary" type="submit">
        {t("addScraper")}
      </button>
    </form>
  );
}