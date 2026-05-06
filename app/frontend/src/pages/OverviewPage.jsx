import ErrorBoundary from '../components/ErrorBoundary.jsx';
import KpiGrid from '../components/KpiGrid.jsx';
import TimeSeriesChart from '../components/TimeSeriesChart.jsx';

export default function OverviewPage({ kpis, timeSeries }) {
  return (
    <>
      <KpiGrid data={kpis} />
      <section className="analytics-grid single">
        <div className="panel wide">
          <div className="panel-header">
            <h3>Evolução mensal</h3>
          </div>
          <ErrorBoundary fallback="Falha ao carregar o gráfico temporal." resetKey={timeSeries?.length}>
            <TimeSeriesChart data={timeSeries} />
          </ErrorBoundary>
        </div>
      </section>
    </>
  );
}
