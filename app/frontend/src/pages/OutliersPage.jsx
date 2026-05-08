import RankingTable from '../components/RankingTable.jsx';

export default function OutliersPage({ outliers }) {
  const sections = [
    ['valores_altos', 'Valores muito altos'],
    ['recorrentes', 'Viagens recorrentes'],
    ['cargos_media', 'Cargos com maiores médias'],
    ['curtas', 'Muitas viagens curtas'],
    ['beneficiario_mes', 'Beneficiário com maior valor por mês'],
    ['orgao_aumento_mensal', 'Órgão com maior aumento mês contra mês'],
    ['internacionais_caras', 'Viagens internacionais mais caras'],
    ['passagem_alta_diaria_baixa', 'Passagem alta e diária baixa'],
    ['acima_percentis', 'Valor total acima do p95/p99'],
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
