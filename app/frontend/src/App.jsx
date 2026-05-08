import { useEffect, useMemo, useState } from 'react';
import {
  getCargoDistribution,
  getFilters,
  getKpis,
  getMapPoints,
  getOrgComparison,
  getOutliers,
  getQualityReport,
  getRanking,
  getTimeSeries,
  getTrips,
} from './api.js';
import FilterPanel from './components/FilterPanel.jsx';
import BeneficiariosPage from './pages/BeneficiariosPage.jsx';
import MapPage from './pages/MapPage.jsx';
import OrgaosPage from './pages/OrgaosPage.jsx';
import OutliersPage from './pages/OutliersPage.jsx';
import OverviewPage from './pages/OverviewPage.jsx';
import QualityPage from './pages/QualityPage.jsx';

const initialFilters = {
  orgao: [],
  data_inicio: '2024-05-01',
  data_fim: '2026-04-30',
  beneficiario: '',
  cargo: '',
  motivo_contem: '',
  tipo_viagem: '',
};

const pages = [
  ['overview', 'Visão geral'],
  ['orgaos', 'Órgãos'],
  ['beneficiarios', 'Beneficiários'],
  ['mapa', 'Mapa'],
  ['outliers', 'Outliers'],
  ['qualidade', 'Qualidade dos dados'],
];

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [filters, setFilters] = useState(initialFilters);
  const [options, setOptions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mapRegion, setMapRegion] = useState('todos');
  const [mapMode, setMapMode] = useState('clusters');
  const [data, setData] = useState({
    kpis: null,
    timeSeries: [],
    rankings: {},
    comparison: [],
    trips: [],
    cargoDistribution: [],
    mapPoints: [],
    outliers: {},
    quality: null,
  });

  const pageTitle = useMemo(
    () => pages.find(([key]) => key === activePage)?.[1] || 'Dashboard',
    [activePage],
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

    loadPageData(activePage, filters, mapMode)
      .then((nextData) => {
        if (!ignore) {
          setData((current) => ({
            ...current,
            ...nextData,
            rankings: {
              ...current.rankings,
              ...(nextData.rankings || {}),
            },
          }));
        }
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
  }, [activePage, filters, mapMode]);

  const visibleMapPoints = data.mapPoints.filter((point) => {
    if (mapRegion === 'brasil') return point.pais === 'Brasil';
    if (mapRegion === 'exterior') return point.pais !== 'Brasil';
    return true;
  });

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

        <nav className="page-nav">
          {pages.map(([key, label]) => (
            <button
              className={activePage === key ? 'active' : ''}
              key={key}
              onClick={() => setActivePage(key)}
              type="button"
            >
              {label}
            </button>
          ))}
        </nav>

        <FilterPanel filters={filters} options={options} onChange={setFilters} />
      </aside>

      <main className="main-content">
        <div className="page-header">
          <div>
            <h2>{pageTitle}</h2>
            <p>{filters.data_inicio} a {filters.data_fim}</p>
          </div>
          {loading && <span className="status-pill">Atualizando</span>}
        </div>

        {error && <div className="error-banner">{error}</div>}

        {activePage === 'overview' && (
          <OverviewPage kpis={data.kpis} timeSeries={data.timeSeries} />
        )}
        {activePage === 'orgaos' && (
          <OrgaosPage
            rankings={data.rankings}
            comparison={data.comparison}
            trips={data.trips}
          />
        )}
        {activePage === 'beneficiarios' && (
          <BeneficiariosPage
            rankings={data.rankings}
            cargoDistribution={data.cargoDistribution}
            trips={data.trips}
          />
        )}
        {activePage === 'mapa' && (
          <MapPage
            mapMode={mapMode}
            points={visibleMapPoints}
            mapRegion={mapRegion}
            onModeChange={setMapMode}
            onRegionChange={setMapRegion}
          />
        )}
        {activePage === 'outliers' && <OutliersPage outliers={data.outliers} />}
        {activePage === 'qualidade' && <QualityPage quality={data.quality} />}
      </main>
    </div>
  );
}

async function loadPageData(activePage, filters, mapMode) {
  if (activePage === 'overview') {
    const [kpis, timeSeries] = await Promise.all([
      getKpis(filters),
      getTimeSeries(filters),
    ]);
    return { kpis, timeSeries };
  }

  if (activePage === 'orgaos') {
    const [orgaosValor, orgaosQuantidade, comparison, trips] = await Promise.all([
      getRanking('orgaos', filters, 20, 'valor'),
      getRanking('orgaos', filters, 20, 'quantidade'),
      getOrgComparison(filters),
      getTrips(filters, 100),
    ]);
    return {
      rankings: { orgaosValor, orgaosQuantidade },
      comparison,
      trips,
    };
  }

  if (activePage === 'beneficiarios') {
    const [beneficiariosValor, beneficiariosQuantidade, cargoDistribution, trips] = await Promise.all([
      getRanking('beneficiarios', filters, 20, 'valor'),
      getRanking('beneficiarios', filters, 20, 'quantidade'),
      getCargoDistribution(filters),
      getTrips(filters, 100),
    ]);
    return {
      rankings: { beneficiariosValor, beneficiariosQuantidade },
      cargoDistribution,
      trips,
    };
  }

  if (activePage === 'mapa') {
    return { mapPoints: await getMapPoints(filters, mapMode) };
  }

  if (activePage === 'qualidade') {
    return { quality: await getQualityReport(filters) };
  }

  const [valoresAltos, recorrentes, cargosMedia, curtas] = await Promise.all([
    getOutliers('valores_altos', filters),
    getOutliers('recorrentes', filters),
    getOutliers('cargos_media', filters),
    getOutliers('curtas', filters),
  ]);
  return {
    outliers: {
      valores_altos: valoresAltos,
      recorrentes,
      cargos_media: cargosMedia,
      curtas,
    },
  };
}
