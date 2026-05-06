const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat('pt-BR');

function toNumber(value) {
  return Number(value || 0);
}

export default function KpiGrid({ data }) {
  const items = [
    ['Valor total', moneyFormatter.format(toNumber(data?.valor_total))],
    ['Diárias', moneyFormatter.format(toNumber(data?.valor_diarias))],
    ['Passagens', moneyFormatter.format(toNumber(data?.valor_passagens))],
    ['Nº viagens', numberFormatter.format(toNumber(data?.numero_viagens))],
    ['Ticket médio', moneyFormatter.format(toNumber(data?.ticket_medio))],
  ];

  return (
    <section className="kpi-grid">
      {items.map(([label, value]) => (
        <div className="kpi-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </section>
  );
}
