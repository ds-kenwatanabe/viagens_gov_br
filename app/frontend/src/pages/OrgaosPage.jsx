import BarChart from '../components/BarChart.jsx';
import RankingTable from '../components/RankingTable.jsx';
import TripTable from '../components/TripTable.jsx';

export default function OrgaosPage({ rankings, comparison, trips }) {
  return (
    <section className="analytics-grid">
      <div className="panel">
        <div className="panel-header"><h3>Ranking por valor</h3></div>
        <RankingTable rows={rankings.orgaosValor || []} />
      </div>
      <div className="panel">
        <div className="panel-header"><h3>Ranking por quantidade</h3></div>
        <RankingTable rows={rankings.orgaosQuantidade || []} />
      </div>
      <div className="panel wide">
        <div className="panel-header"><h3>Comparação entre ministérios</h3></div>
        <BarChart rows={comparison} color="#0f766e" />
      </div>
      <div className="panel map-panel">
        <div className="panel-header"><h3>Órgão → beneficiário → viagem</h3></div>
        <TripTable rows={trips} />
      </div>
    </section>
  );
}
