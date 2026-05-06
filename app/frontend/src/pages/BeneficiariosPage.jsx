import BarChart from '../components/BarChart.jsx';
import ErrorBoundary from '../components/ErrorBoundary.jsx';
import RankingTable from '../components/RankingTable.jsx';
import TripTable from '../components/TripTable.jsx';

export default function BeneficiariosPage({ rankings, cargoDistribution, trips }) {
  return (
    <section className="analytics-grid">
      <div className="panel">
        <div className="panel-header"><h3>Top por valor</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o ranking por valor." resetKey={rankings.beneficiariosValor?.length}>
          <RankingTable rows={rankings.beneficiariosValor || []} />
        </ErrorBoundary>
      </div>
      <div className="panel">
        <div className="panel-header"><h3>Top por quantidade</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o ranking por quantidade." resetKey={rankings.beneficiariosQuantidade?.length}>
          <RankingTable rows={rankings.beneficiariosQuantidade || []} />
        </ErrorBoundary>
      </div>
      <div className="panel wide">
        <div className="panel-header"><h3>Distribuição por cargo</h3></div>
        <ErrorBoundary fallback="Falha ao carregar a distribuição por cargo." resetKey={cargoDistribution?.length}>
          <BarChart rows={cargoDistribution} xKey="quantidade" color="#f59e0b" />
        </ErrorBoundary>
      </div>
      <div className="panel map-panel">
        <div className="panel-header"><h3>Detalhamento de viagens</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o detalhamento de viagens." resetKey={trips?.length}>
          <TripTable rows={trips} />
        </ErrorBoundary>
      </div>
    </section>
  );
}
