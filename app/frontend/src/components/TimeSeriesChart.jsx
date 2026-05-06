const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  maximumFractionDigits: 0,
  notation: 'compact',
});

export default function TimeSeriesChart({ data }) {
  const safeData = Array.isArray(data) ? data : [];

  if (!safeData.length) {
    return <div className="component-loading">Sem dados para o filtro atual.</div>;
  }

  const width = 920;
  const height = 320;
  const padding = { top: 20, right: 28, bottom: 54, left: 68 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(...safeData.map((item) => Number(item.valor_total || 0)), 0);
  const maxTrips = Math.max(...safeData.map((item) => Number(item.quantidade || 0)), 0);
  const step = safeData.length > 1 ? chartWidth / (safeData.length - 1) : chartWidth;

  const points = safeData.map((item, index) => {
    const value = Number(item.valor_total || 0);
    const x = padding.left + index * step;
    const y = padding.top + chartHeight - (maxValue ? (value / maxValue) * chartHeight : 0);
    return { ...item, value, x, y };
  });

  const linePath = points
    .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ');

  return (
    <div className="timeseries-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Evolucao mensal de viagens">
        <line className="axis-line" x1={padding.left} x2={padding.left} y1={padding.top} y2={padding.top + chartHeight} />
        <line className="axis-line" x1={padding.left} x2={padding.left + chartWidth} y1={padding.top + chartHeight} y2={padding.top + chartHeight} />
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
          const y = padding.top + chartHeight - tick * chartHeight;
          return (
            <g key={tick}>
              <line className="grid-line" x1={padding.left} x2={padding.left + chartWidth} y1={y} y2={y} />
              <text className="axis-label" x={padding.left - 10} y={y + 4} textAnchor="end">
                {moneyFormatter.format(maxValue * tick)}
              </text>
            </g>
          );
        })}

        {points.map((point) => {
          const trips = Number(point.quantidade || 0);
          const barHeight = maxTrips ? (trips / maxTrips) * chartHeight : 0;
          return (
            <rect
              className="trip-bar"
              height={barHeight}
              key={`bar-${point.periodo}`}
              width={Math.max(step * 0.45, 6)}
              x={point.x - Math.max(step * 0.45, 6) / 2}
              y={padding.top + chartHeight - barHeight}
            />
          );
        })}

        <path className="value-line" d={linePath} />
        {points.map((point, index) => (
          <g key={point.periodo}>
            <circle className="value-point" cx={point.x} cy={point.y} r="4" />
            {(index === 0 || index === points.length - 1 || index % 4 === 0) && (
              <text className="axis-label" x={point.x} y={height - 22} textAnchor="middle">
                {String(point.periodo).slice(0, 7)}
              </text>
            )}
          </g>
        ))}
      </svg>
    </div>
  );
}
