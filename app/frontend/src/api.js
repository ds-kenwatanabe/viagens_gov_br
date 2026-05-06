const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

function buildQuery(filters = {}) {
  const params = new URLSearchParams();

  (filters.orgao || []).forEach((orgao) => {
    if (orgao) params.append('orgao', orgao);
  });

  ['beneficiario', 'cargo', 'tipo_viagem', 'data_inicio', 'data_fim'].forEach((key) => {
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

export function getKpis(filters) {
  const query = buildQuery(filters);
  return request(`/kpis${query ? `?${query}` : ''}`);
}

export function getRanking(dimension, filters, limit = 15) {
  const query = buildQuery(filters);
  const sep = query ? '&' : '?';
  return request(`/rankings/${dimension}${query ? `?${query}` : ''}${sep}limit=${limit}`);
}

export function getTimeSeries(filters) {
  const query = buildQuery(filters);
  return request(`/timeseries${query ? `?${query}` : ''}`);
}

export function getMapPoints(filters) {
  const query = buildQuery(filters);
  return request(`/map${query ? `?${query}` : ''}`);
}
