const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function buildQuery(filters = {}) {
  const params = new URLSearchParams();

  (filters.orgao || []).forEach((orgao) => {
    if (orgao) params.append('orgao', orgao);
  });

  ['orgao_nome', 'beneficiario', 'cargo', 'motivo_contem', 'tipo_viagem', 'data_inicio', 'data_fim'].forEach((key) => {
    if (filters[key]) params.set(key, filters[key]);
  });

  return params.toString();
}

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Erro ${response.status} ao consultar ${path}`);
  }
  return response.json();
}

export function getFilters() {
  return request('/filters');
}

export function searchFilterOptions(kind, search, limit = 80) {
  const params = new URLSearchParams();
  if (search) params.set('search', search);
  params.set('limit', String(limit));
  return request(`/filters/${kind}?${params.toString()}`);
}

export function getKpis(filters) {
  const query = buildQuery(filters);
  return request(`/kpis${query ? `?${query}` : ''}`);
}

export function getRanking(dimension, filters, limit = 15, orderBy = 'valor') {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/rankings/${dimension}${query ? `?${query}` : ''}${sep}limit=${limit}&order_by=${orderBy}`);
}

export function getTimeSeries(filters) {
  const query = buildQuery(filters);
  return request(`/timeseries${query ? `?${query}` : ''}`);
}

export function getMapPoints(filters, mapMode = 'clusters', limit = 1000) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/map${query ? `?${query}` : ''}${sep}map_mode=${mapMode}&limit=${limit}`);
}

export function getOrgComparison(filters) {
  const query = buildQuery(filters);
  return request(`/comparison/orgaos${query ? `?${query}` : ''}`);
}

export function getTrips(filters, limit = 100) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/trips${query ? `?${query}` : ''}${sep}limit=${limit}`);
}

export function getTripLocations(tripId) {
  return request(`/trips/${tripId}/locations`);
}

export function getCargoDistribution(filters, limit = 30) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/distribution/cargos${query ? `?${query}` : ''}${sep}limit=${limit}`);
}

export function getOutliers(kind, filters, limit = 30) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/outliers/${kind}${query ? `?${query}` : ''}${sep}limit=${limit}`);
}

export function getQualityReport(filters, limit = 20) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/quality${query ? `?${query}` : ''}${sep}limit=${limit}`);
}

export function getCsvExportUrl(kind, filters = {}, options = {}) {
  const query = buildQuery(filters);
  const params = new URLSearchParams(query);
  const paths = {
    trips: '/export/trips.csv',
    map: '/export/map.csv',
    ranking: '/export/ranking.csv',
    hierarchy: '/export/orgao-beneficiario-viagem.csv',
  };

  Object.entries(options).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value));
    }
  });

  return `${API_BASE_URL}${paths[kind]}${params.toString() ? `?${params.toString()}` : ''}`;
}
