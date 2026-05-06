import BarChart from '../components/BarChart.jsx';
import ErrorBoundary from '../components/ErrorBoundary.jsx';
import RankingTable from '../components/RankingTable.jsx';
import TripTable from '../components/TripTable.jsx';

export default function OrgaosPage({ rankings, comparison, trips }) {
  return (
    <section className="analytics-grid">
      <div className="panel">
        <div className="panel-header"><h3>Ranking por valor</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o ranking por valor." resetKey={rankings.orgaosValor?.length}>
          <RankingTable rows={rankings.orgaosValor || []} />
        </ErrorBoundary>
      </div>
      <div className="panel">
        <div className="panel-header"><h3>Ranking por quantidade</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o ranking por quantidade." resetKey={rankings.orgaosQuantidade?.length}>
          <RankingTable rows={rankings.orgaosQuantidade || []} />
        </ErrorBoundary>
      </div>
      <div className="panel wide">
        <div className="panel-header"><h3>Comparação entre ministérios</h3></div>
        <ErrorBoundary fallback="Falha ao carregar a comparação entre ministérios." resetKey={comparison?.length}>
          <BarChart rows={comparison} color="#0f766e" />
        </ErrorBoundary>
      </div>
      <div className="panel map-panel">
        <div className="panel-header"><h3>Órgão → beneficiário → viagem</h3></div>
        <ErrorBoundary fallback="Falha ao carregar o detalhamento de viagens." resetKey={trips?.length}>
          <TripTable rows={trips} />
        </ErrorBoundary>
      </div>
    </section>
  );
}
