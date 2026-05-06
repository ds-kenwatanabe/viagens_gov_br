import BarChart from '../components/BarChart.jsx';
import RankingTable from '../components/RankingTable.jsx';
import TripTable from '../components/TripTable.jsx';

export default function BeneficiariosPage({ rankings, cargoDistribution, trips }) {
  return (
    <section className="analytics-grid">
      <div className="panel">
        <div className="panel-header"><h3>Top por valor</h3></div>
        <RankingTable rows={rankings.beneficiariosValor || []} />
      </div>
      <div className="panel">
        <div className="panel-header"><h3>Top por quantidade</h3></div>
        <RankingTable rows={rankings.beneficiariosQuantidade || []} />
      </div>
      <div className="panel wide">
        <div className="panel-header"><h3>Distribuição por cargo</h3></div>
        <BarChart rows={cargoDistribution} xKey="quantidade" color="#f59e0b" />
      </div>
      <div className="panel map-panel">
        <div className="panel-header"><h3>Detalhamento de viagens</h3></div>
        <TripTable rows={trips} />
      </div>
    </section>
  );
}
