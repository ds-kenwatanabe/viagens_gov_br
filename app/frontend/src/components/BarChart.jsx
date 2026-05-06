const compactFormatter = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 0,
  notation: 'compact',
});

export default function BarChart({ rows, xKey = 'valor_total', yKey = 'nome', color = '#2563eb' }) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const visibleRows = [...safeRows].slice(0, 18);
  const maxValue = Math.max(...visibleRows.map((row) => Number(row[xKey] || 0)), 0);

  if (!visibleRows.length) {
    return <div className="component-loading">Sem dados para o filtro atual.</div>;
  }

  return (
    <div className="bar-list">
      {visibleRows.map((row, index) => {
        const value = Number(row[xKey] || 0);
        const width = maxValue ? Math.max((value / maxValue) * 100, 1) : 0;
        return (
          <div className="bar-row" key={`${row[yKey] || 'row'}-${index}`}>
            <div className="bar-label" title={row[yKey]}>{row[yKey] || 'Nao informado'}</div>
            <div className="bar-track">
              <div className="bar-fill" style={{ backgroundColor: color, width: `${width}%` }} />
            </div>
            <div className="bar-value">{compactFormatter.format(value)}</div>
          </div>
        );
      })}
    </div>
  );
}
