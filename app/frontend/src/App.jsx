import { useEffect, useMemo, useState } from 'react';
import {
  getFilters,
  getKpis,
  getMapPoints,
  getRanking,
  getTimeSeries,
} from './api.js';
import FilterPanel from './components/FilterPanel.jsx';
import KpiGrid from './components/KpiGrid.jsx';
import RankingTable from './components/RankingTable.jsx';
import TimeSeriesChart from './components/TimeSeriesChart.jsx';
import TravelMap from './components/TravelMap.jsx';

const initialFilters = {
  orgao: [],
  data_inicio: '2024-05-01',
  data_fim: '2026-04-30',
  beneficiario: '',
  cargo: '',
  tipo_viagem: '',
};

export default function App() {
  const [filters, setFilters] = useState(initialFilters);
  const [options, setOptions] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [timeSeries, setTimeSeries] = useState([]);
  const [mapPoints, setMapPoints] = useState([]);
  const [rankings, setRankings] = useState({});
  const [activeRanking, setActiveRanking] = useState('beneficiarios');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const rankingTabs = useMemo(
    () => [
      ['beneficiarios', 'Beneficiários'],
      ['orgaos', 'Órgãos'],
      ['cargos', 'Cargos'],
      ['ugs', 'UGs'],
    ],
    [],
  );

  useEffect(() => {
    getFilters()
      .then(setOptions)
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError('');

    Promise.all([
      getKpis(filters),
      getTimeSeries(filters),
      getMapPoints(filters),
      Promise.all(rankingTabs.map(([key]) => getRanking(key, filters))),
    ])
      .then(([kpiData, seriesData, mapData, rankingData]) => {
        if (ignore) return;
        setKpis(kpiData);
        setTimeSeries(seriesData);
        setMapPoints(mapData);
        setRankings(Object.fromEntries(rankingTabs.map(([key], index) => [key, rankingData[index]])));
      })
      .catch((err) => {
        if (!ignore) setError(err.message);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [filters, rankingTabs]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">VG</span>
          <div>
            <h1>Viagens Gov BR</h1>
            <p>Dashboard local PostgreSQL</p>
          </div>
        </div>
        <FilterPanel filters={filters} options={options} onChange={setFilters} />
      </aside>

      <main className="main-content">
        <div className="page-header">
          <div>
            <h2>Gastos e deslocamentos</h2>
            <p>{filters.data_inicio} a {filters.data_fim}</p>
          </div>
          {loading && <span className="status-pill">Atualizando</span>}
        </div>

        {error && <div className="error-banner">{error}</div>}

        <KpiGrid data={kpis} />

        <section className="analytics-grid">
          <div className="panel wide">
            <div className="panel-header">
              <h3>Série temporal</h3>
            </div>
            <TimeSeriesChart data={timeSeries} />
          </div>

          <div className="panel">
            <div className="panel-header">
              <h3>Ranking</h3>
              <div className="segmented">
                {rankingTabs.map(([key, label]) => (
                  <button
                    key={key}
                    className={activeRanking === key ? 'active' : ''}
                    onClick={() => setActiveRanking(key)}
                    type="button"
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <RankingTable rows={rankings[activeRanking] || []} />
          </div>

          <div className="panel map-panel">
            <div className="panel-header">
              <h3>Mapa geográfico</h3>
            </div>
            <TravelMap points={mapPoints} />
          </div>
        </section>
      </main>
    </div>
  );
}
