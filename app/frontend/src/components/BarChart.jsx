import Plot from 'react-plotly.js';

export default function BarChart({ rows, xKey = 'valor_total', yKey = 'nome', color = '#2563eb' }) {
  const sortedRows = [...rows].reverse();
  return (
    <Plot
      data={[
        {
          x: sortedRows.map((row) => Number(row[xKey] || 0)),
          y: sortedRows.map((row) => row[yKey]),
          type: 'bar',
          orientation: 'h',
          marker: { color },
        },
      ]}
      layout={{
        autosize: true,
        margin: { l: 160, r: 16, t: 8, b: 32 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter, system-ui, sans-serif', color: '#172033', size: 11 },
      }}
      config={{ displayModeBar: false, responsive: true }}
      useResizeHandler
      className="plot compact"
    />
  );
}
