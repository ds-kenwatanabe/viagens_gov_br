import RankingTable from '../components/RankingTable.jsx';

export default function OutliersPage({ outliers }) {
  const sections = [
    ['valores_altos', 'Valores muito altos'],
    ['recorrentes', 'Viagens recorrentes'],
    ['cargos_media', 'Cargos com maiores médias'],
    ['curtas', 'Muitas viagens curtas'],
  ];

  return (
    <section className="analytics-grid">
      {sections.map(([key, title]) => (
        <div className="panel" key={key}>
          <div className="panel-header"><h3>{title}</h3></div>
          <RankingTable rows={outliers[key] || []} />
        </div>
      ))}
    </section>
  );
}
