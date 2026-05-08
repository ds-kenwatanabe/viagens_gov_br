import { getCsvExportUrl } from '../api.js';

export default function CsvExportButton({
  children,
  filters,
  kind,
  options,
  title,
}) {
  return (
    <a
      className="export-button"
      href={getCsvExportUrl(kind, filters, options)}
      title={title || 'Exportar CSV'}
    >
      <span className="export-icon" aria-hidden="true">DL</span>
      <span>{children}</span>
    </a>
  );
}
