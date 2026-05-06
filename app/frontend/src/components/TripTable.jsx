const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

export default function TripTable({ rows }) {
  const safeRows = Array.isArray(rows) ? rows : [];

  return (
    <div className="table-wrap detail-table">
      <table>
        <thead>
          <tr>
            <th>Beneficiario</th>
            <th>Orgao</th>
            <th>Cargo</th>
            <th>Tipo</th>
            <th>Motivo</th>
            <th>Periodo</th>
            <th>Valor</th>
          </tr>
        </thead>
        <tbody>
          {safeRows.map((row) => (
            <tr key={row.id}>
              <td title={row.beneficiario_nome}>{row.beneficiario_nome || 'Nao informado'}</td>
              <td title={row.orgao_nome}>{row.orgao_nome || 'Nao informado'}</td>
              <td title={row.cargo_descricao}>{row.cargo_descricao || 'Nao informado'}</td>
              <td>{row.tipo_viagem || '-'}</td>
              <td title={row.motivo}>{row.motivo || 'Nao informado'}</td>
              <td>{row.data_inicio_afastamento || '-'} a {row.data_fim_afastamento || '-'}</td>
              <td>{moneyFormatter.format(Number(row.valor_total_viagem || 0))}</td>
            </tr>
          ))}
          {!safeRows.length && (
            <tr>
              <td colSpan="7">Sem dados para o filtro atual.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
