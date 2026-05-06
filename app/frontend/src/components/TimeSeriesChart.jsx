import Plot from 'react-plotly.js';

export default function TimeSeriesChart({ data }) {
  return (
    <Plot
      data={[
        {
          x: data.map((item) => item.periodo),
          y: data.map((item) => Number(item.valor_total || 0)),
          type: 'scatter',
          mode: 'lines+markers',
          name: 'Valor total',
          line: { color: '#2563eb', width: 3 },
          marker: { color: '#0f766e', size: 6 },
          yaxis: 'y',
        },
        {
          x: data.map((item) => item.periodo),
          y: data.map((item) => Number(item.quantidade || 0)),
          type: 'bar',
          name: 'Viagens',
          marker: { color: 'rgba(245, 158, 11, 0.45)' },
          yaxis: 'y2',
        },
      ]}
      layout={{
        autosize: true,
        margin: { l: 56, r: 48, t: 10, b: 42 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { family: 'Inter, system-ui, sans-serif', color: '#172033' },
        legend: { orientation: 'h', x: 0, y: 1.12 },
        yaxis: { title: 'Valor' },
        yaxis2: { title: 'Viagens', overlaying: 'y', side: 'right', showgrid: false },
      }}
      config={{ displayModeBar: false, responsive: true }}
      useResizeHandler
      className="plot"
    />
  );
}
