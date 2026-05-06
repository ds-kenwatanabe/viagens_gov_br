import RankingTable from '../components/RankingTable.jsx';

const numberFormatter = new Intl.NumberFormat('pt-BR');
const percentFormatter = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 1,
  style: 'percent',
});

function formatNumber(value) {
  return numberFormatter.format(Number(value || 0));
}

function formatConfidence(value) {
  if (value === null || value === undefined) return '-';
  return percentFormatter.format(Number(value || 0));
}

export default function QualityPage({ quality }) {
  const summary = quality?.summary || {};
  const items = [
    ['Total de viagens', formatNumber(summary.total_viagens)],
    ['Motivo vazio', formatNumber(summary.motivo_vazio)],
    ['Sem local extraído', formatNumber(summary.sem_local_extraido)],
    ['Geocodificadas', formatNumber(summary.geocodificadas)],
    ['Confiança média', formatConfidence(summary.confianca_media)],
  ];

  return (
    <>
      <section className="kpi-grid quality-kpis">
        {items.map(([label, value]) => (
          <div className="kpi-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <section className="analytics-grid">
        <div className="panel">
          <div className="panel-header">
            <h3>Geocodificações por fonte</h3>
          </div>
          <SourceTable rows={quality?.fontes || []} />
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3>Top motivos sem local encontrado</h3>
          </div>
          <RankingTable rows={quality?.motivos_sem_local || []} />
        </div>
      </section>
    </>
  );
}

function SourceTable({ rows }) {
  const safeRows = Array.isArray(rows) ? rows : [];

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Fonte</th>
            <th>Registros</th>
          </tr>
        </thead>
        <tbody>
          {safeRows.map((row) => (
            <tr key={row.fonte}>
              <td>{row.fonte}</td>
              <td>{formatNumber(row.quantidade)}</td>
            </tr>
          ))}
          {!safeRows.length && (
            <tr>
              <td colSpan="2">Sem dados para o filtro atual.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
