import TravelMap from '../components/TravelMap.jsx';

export default function MapPage({ points, mapMode, mapRegion, onModeChange, onRegionChange }) {
  return (
    <section className="analytics-grid single">
      <div className="panel map-panel">
        <div className="panel-header">
          <h3>{mapMode === 'clusters' ? 'Localidades agregadas' : 'Viagens geocodificadas'}</h3>
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
        <TravelMap mode={mapMode} points={points} />
      </div>
    </section>
  );
}
