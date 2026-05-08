import { useEffect, useState } from 'react';

import { getTripLocations } from '../api.js';

const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 2,
});

export default function TripDetailDrawer({ trip, onClose }) {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let ignore = false;
    if (!trip?.id) return undefined;

    setLoading(true);
    getTripLocations(trip.id)
      .then((items) => {
        if (!ignore) setLocations(items);
      })
      .catch(() => {
        if (!ignore) setLocations([]);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [trip?.id]);

  if (!trip) return null;

  return (
    <aside className="detail-drawer" aria-label="Detalhe da viagem">
      <div className="drawer-header">
        <div>
          <h3>Detalhe da viagem</h3>
          <p>{trip.data_inicio_afastamento || '-'} a {trip.data_fim_afastamento || '-'}</p>
        </div>
        <button className="icon-button" type="button" onClick={onClose} aria-label="Fechar detalhe">x</button>
      </div>

      <div className="drawer-section">
        <Detail label="Beneficiário" value={trip.beneficiario_nome} />
        <Detail label="Órgão" value={trip.orgao_nome} />
        <Detail label="Cargo" value={trip.cargo_descricao} />
        <Detail label="Tipo" value={trip.tipo_viagem} />
        <Detail label="Valor total" value={moneyFormatter.format(Number(trip.valor_total_viagem || 0))} />
        <Detail label="Diárias" value={moneyFormatter.format(Number(trip.valor_total_diarias || 0))} />
        <Detail label="Passagens" value={moneyFormatter.format(Number(trip.valor_total_passagem || 0))} />
      </div>

      <div className="drawer-section">
        <h4>Motivo</h4>
        <p className="drawer-text">{trip.motivo || 'Não informado'}</p>
      </div>

      <div className="drawer-section">
        <h4>Mapa/local</h4>
        {loading && <p className="drawer-text">Carregando localidades...</p>}
        {!loading && locations.map((location, index) => (
          <div className="location-item" key={`${location.local_texto}-${index}`}>
            <strong>{[location.cidade, location.estado, location.pais].filter(Boolean).join(', ') || 'Sem local extraído'}</strong>
            <span>{location.local_texto || '-'}</span>
            <span>Fonte: {location.fonte || 'none'} · Confiança: {formatConfidence(location.confidence)}</span>
            <span>Lat/Lon: {formatCoordinate(location.latitude)}, {formatCoordinate(location.longitude)}</span>
          </div>
        ))}
        {!loading && !locations.length && <p className="drawer-text">Nenhuma localidade registrada.</p>}
      </div>
    </aside>
  );
}

function Detail({ label, value }) {
  return (
    <div className="detail-row">
      <span>{label}</span>
      <strong>{value || 'Não informado'}</strong>
    </div>
  );
}

function formatConfidence(value) {
  if (value === null || value === undefined) return '-';
  return Number(value).toLocaleString('pt-BR', { maximumFractionDigits: 2 });
}

function formatCoordinate(value) {
  if (value === null || value === undefined) return '-';
  return Number(value).toLocaleString('pt-BR', { maximumFractionDigits: 6 });
}
