import TravelMap from '../components/TravelMap.jsx';

export default function MapPage({ points, mapRegion, onRegionChange }) {
  return (
    <section className="analytics-grid single">
      <div className="panel map-panel">
        <div className="panel-header">
          <h3>Pontos geocodificados</h3>
          <div className="segmented">
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
        <TravelMap points={points} />
      </div>
    </section>
  );
}
