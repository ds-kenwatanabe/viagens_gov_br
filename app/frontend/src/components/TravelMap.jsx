import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';

const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

export default function TravelMap({ mode, points }) {
  return (
    <MapContainer center={[-14.235, -51.9253]} zoom={4} scrollWheelZoom className="map">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((point) => {
        const radius = Math.max(6, Math.min(30, Math.sqrt(Number(point.quantidade || 1)) * 2));
        const label = [point.cidade, point.estado, point.pais].filter(Boolean).join(', ');
        return (
          <CircleMarker
            key={`${mode}-${point.latitude}-${point.longitude}-${label}`}
            center={[point.latitude, point.longitude]}
            radius={radius}
            pathOptions={{ color: '#0f766e', fillColor: '#14b8a6', fillOpacity: 0.45, weight: 2 }}
          >
            <Popup>
              <strong>{label || 'Localidade'}</strong>
              <br />
              {mode === 'points' && (
                <>
                  Beneficiário: {point.beneficiario_nome || 'Não informado'}
                  <br />
                </>
              )}
              Órgão: {point.orgao_nome || 'Não informado'}
              <br />
              Tipo: {point.tipo_viagem || '-'}
              <br />
              Período: {point.data_inicio_afastamento || '-'} a {point.data_fim_afastamento || '-'}
              <br />
              {mode === 'points' && (
                <>
                  Motivo: {point.motivo || '-'}
                  <br />
                </>
              )}
              Viagens: {point.quantidade}
              <br />
              Valor: {moneyFormatter.format(Number(point.valor_total || 0))}
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
