import { useState } from "react";
import { useI18n } from "../i18n";

export default function ManifestCard({ url }) {
  const { t } = useI18n();
  const [copied, setCopied] = useState(false);
  const [installed, setInstalled] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = url;
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand("copy");
        setCopied(true);
        setTimeout(() => setCopied(false), 1600);
      } finally {
        document.body.removeChild(ta);
      }
    }
  };

  const install = async () => {
    await copy();
    setInstalled(true);
    setTimeout(() => setInstalled(false), 6000);
    window.open(url.replace(/^https?:\/\//, "stremio://"), "_blank");
  };

  return (
    <section className="card manifest">
      <h2>{t("manifestUrl")}</h2>
      <p className="muted">{t("manifestHint")}</p>
      <div className="url-box">
        <code>{url}</code>
      </div>
      <div className="manifest-actions">
        <button className="btn primary" onClick={copy}>
          {copied ? t("copied") : t("copy")}
        </button>
        <button className="btn accent" onClick={install}>
          {t("install")}
        </button>
      </div>
      {installed && <p className="install-note">{t("installHint")}</p>}
    </section>
  );
}