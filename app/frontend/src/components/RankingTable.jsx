const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat('pt-BR');

export default function RankingTable({ rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Viagens</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.nome}>
              <td title={row.nome}>{row.nome}</td>
              <td>{numberFormatter.format(Number(row.quantidade || 0))}</td>
              <td>{moneyFormatter.format(Number(row.valor_total || 0))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
