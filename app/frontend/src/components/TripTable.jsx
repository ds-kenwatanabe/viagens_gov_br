const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

export default function TripTable({ rows }) {
  return (
    <div className="table-wrap detail-table">
      <table>
        <thead>
          <tr>
            <th>Beneficiário</th>
            <th>Órgão</th>
            <th>Cargo</th>
            <th>Tipo</th>
            <th>Período</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td title={row.beneficiario_nome}>{row.beneficiario_nome || 'Não informado'}</td>
              <td title={row.orgao_nome}>{row.orgao_nome || 'Não informado'}</td>
              <td title={row.cargo_descricao}>{row.cargo_descricao || 'Não informado'}</td>
              <td>{row.tipo_viagem || '-'}</td>
              <td>{row.data_inicio_afastamento || '-'} a {row.data_fim_afastamento || '-'}</td>
              <td>{moneyFormatter.format(Number(row.valor_total_viagem || 0))}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
