import { useEffect, useState } from 'react';

import { getRanking, getTrips } from '../api.js';
import BarChart from '../components/BarChart.jsx';
import ErrorBoundary from '../components/ErrorBoundary.jsx';
import RankingTable from '../components/RankingTable.jsx';
import TripDetailDrawer from '../components/TripDetailDrawer.jsx';
import TripTable from '../components/TripTable.jsx';

export default function OrgaosPage({ filters, rankings, comparison, trips }) {
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState(null);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [drillTrips, setDrillTrips] = useState([]);
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [loadingDrill, setLoadingDrill] = useState(false);

  useEffect(() => {
    setSelectedOrg(null);
    setSelectedBeneficiary(null);
    setBeneficiaries([]);
    setDrillTrips([]);
    setSelectedTrip(null);
  }, [filters]);

  useEffect(() => {
    let ignore = false;
    if (!selectedOrg) return undefined;

    setLoadingDrill(true);
    setSelectedBeneficiary(null);
    setSelectedTrip(null);
    getRanking('beneficiarios', { ...filters, orgao_nome: selectedOrg.nome }, 30, 'valor')
      .then((rows) => {
        if (!ignore) setBeneficiaries(rows);
      })
      .finally(() => {
        if (!ignore) setLoadingDrill(false);
      });

    return () => {
      ignore = true;
    };
  }, [filters, selectedOrg]);

  useEffect(() => {
    let ignore = false;
    if (!selectedOrg || !selectedBeneficiary) return undefined;

    setLoadingDrill(true);
    setSelectedTrip(null);
    getTrips(
      {
        ...filters,
        orgao_nome: selectedOrg.nome,
        beneficiario: selectedBeneficiary.nome,
      },
      200,
    )
      .then((rows) => {
        if (!ignore) setDrillTrips(rows);
      })
      .finally(() => {
        if (!ignore) setLoadingDrill(false);
      });

    return () => {
      ignore = true;
    };
  }, [filters, selectedBeneficiary, selectedOrg]);

  return (
    <>
      <section className="analytics-grid">
        <div className="panel">
          <div className="panel-header"><h3>Ranking por valor</h3></div>
          <ErrorBoundary fallback="Falha ao carregar o ranking por valor." resetKey={rankings.orgaosValor?.length}>
            <RankingTable
              rows={rankings.orgaosValor || []}
              selectedName={selectedOrg?.nome}
              onSelect={setSelectedOrg}
            />
          </ErrorBoundary>
        </div>
        <div className="panel">
          <div className="panel-header"><h3>Ranking por quantidade</h3></div>
          <ErrorBoundary fallback="Falha ao carregar o ranking por quantidade." resetKey={rankings.orgaosQuantidade?.length}>
            <RankingTable
              rows={rankings.orgaosQuantidade || []}
              selectedName={selectedOrg?.nome}
              onSelect={setSelectedOrg}
            />
          </ErrorBoundary>
        </div>
        <div className="panel wide">
          <div className="panel-header"><h3>Comparação entre ministérios</h3></div>
          <ErrorBoundary fallback="Falha ao carregar a comparação entre ministérios." resetKey={comparison?.length}>
            <BarChart rows={comparison} color="#0f766e" />
          </ErrorBoundary>
        </div>
        <div className="panel map-panel">
          <div className="panel-header">
            <h3>Órgão → beneficiário → viagem</h3>
            {loadingDrill && <span className="status-pill">Atualizando</span>}
          </div>
          <div className="drill-grid">
            <div>
              <h4>Beneficiários do órgão</h4>
              <RankingTable
                rows={selectedOrg ? beneficiaries : []}
                selectedName={selectedBeneficiary?.nome}
                onSelect={setSelectedBeneficiary}
              />
            </div>
            <div>
              <h4>Viagens</h4>
              <ErrorBoundary fallback="Falha ao carregar o detalhamento de viagens." resetKey={drillTrips?.length || trips?.length}>
                <TripTable
                  rows={selectedBeneficiary ? drillTrips : trips}
                  selectedId={selectedTrip?.id}
                  onSelect={setSelectedTrip}
                />
              </ErrorBoundary>
            </div>
          </div>
        </div>
      </section>
      <TripDetailDrawer trip={selectedTrip} onClose={() => setSelectedTrip(null)} />
    </>
  );
}
