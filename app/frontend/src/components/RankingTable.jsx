const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat('pt-BR');

export default function RankingTable({ rows, onSelect, selectedName }) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const hasDetail = safeRows.some((row) => row.detalhe);

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Viagens</th>
            <th>Valor</th>
            {hasDetail && <th>Detalhe</th>}
          </tr>
        </thead>
        <tbody>
          {safeRows.map((row, index) => (
            <tr
              className={selectedName === row.nome ? 'selectable-row active' : onSelect ? 'selectable-row' : ''}
              key={`${row.nome}-${index}`}
              onClick={() => onSelect?.(row)}
            >
              <td title={row.nome}>{row.nome}</td>
              <td>{numberFormatter.format(Number(row.quantidade || 0))}</td>
              <td>{moneyFormatter.format(Number(row.valor_total || 0))}</td>
              {hasDetail && <td title={row.detalhe}>{row.detalhe || '-'}</td>}
            </tr>
          ))}
          {!safeRows.length && (
            <tr>
              <td colSpan={hasDetail ? 4 : 3}>Sem dados para o filtro atual.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
