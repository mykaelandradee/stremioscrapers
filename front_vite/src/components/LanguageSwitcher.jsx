import { LOCALES, useI18n } from "../i18n";

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <div className="lang-switcher">
      {Object.entries(LOCALES).map(([code, meta]) => (
        <button
          key={code}
          className={`lang-btn ${locale === code ? "active" : ""}`}
          onClick={() => setLocale(code)}
          title={meta.label}
        >
          {meta.label}
        </button>
      ))}
    </div>
  );
}