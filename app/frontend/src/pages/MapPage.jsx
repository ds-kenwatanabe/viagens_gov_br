import CsvExportButton from '../components/CsvExportButton.jsx';
import TravelMap from '../components/TravelMap.jsx';

export default function MapPage({ filters, points, mapMode, mapRegion, onModeChange, onRegionChange }) {
  return (
    <section className="analytics-grid single">
      <div className="panel map-panel">
        <div className="panel-header">
          <h3>{mapMode === 'clusters' ? 'Localidades agregadas' : 'Viagens geocodificadas'}</h3>
          <div className="panel-actions">
            <CsvExportButton
              filters={filters}
              kind="map"
              options={{ group_by: mapMode === 'clusters' ? 'city' : 'country', limit: 100000 }}
              title="Exportar dados agregados do mapa em CSV"
            >
              CSV
            </CsvExportButton>
            <div className="segmented">
              {[
                ['clusters', 'Clusters'],
                ['points', 'Pontos'],
              ].map(([key, label]) => (
                <button
                  className={mapMode === key ? 'active' : ''}
                  key={key}
                  onClick={() => onModeChange(key)}
                  type="button"
                >
                  {label}
                </button>
              ))}
              {[
                ['todos', 'Todos'],
                ['brasil', 'Brasil'],
                ['exterior', 'Exterior'],
              ].map(([key, label]) => (
                <button
                  className={mapRegion === key ? 'active' : ''}
                  key={key}
                  onClick={() => onRegionChange(key)}
                  type="button"
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>
        <TravelMap mode={mapMode} points={points} />
      </div>
    </section>
  );
}
