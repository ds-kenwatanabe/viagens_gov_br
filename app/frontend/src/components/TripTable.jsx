import { useMemo, useState } from 'react';

const moneyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  maximumFractionDigits: 0,
});

const columns = [
  { key: 'beneficiario_nome', label: 'Beneficiário', type: 'text' },
  { key: 'orgao_nome', label: 'Órgão', type: 'text' },
  { key: 'cargo_descricao', label: 'Cargo', type: 'text' },
  { key: 'tipo_viagem', label: 'Tipo', type: 'text' },
  { key: 'motivo', label: 'Motivo', type: 'text' },
  { key: 'data_inicio_afastamento', label: 'Período', type: 'date' },
  { key: 'valor_total_viagem', label: 'Valor', type: 'number' },
];

export default function TripTable({ rows, onSelect, selectedId }) {
  const safeRows = Array.isArray(rows) ? rows : [];
  const [sortConfig, setSortConfig] = useState({
    direction: 'desc',
    key: 'valor_total_viagem',
  });

  const sortedRows = useMemo(() => {
    const column = columns.find((item) => item.key === sortConfig.key);
    return [...safeRows].sort((a, b) => compareRows(a, b, column, sortConfig.direction));
  }, [safeRows, sortConfig]);

  function updateSort(key) {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  }

  return (
    <div className="table-wrap detail-table">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>
                <button
                  className={sortConfig.key === column.key ? 'sort-button active' : 'sort-button'}
                  onClick={() => updateSort(column.key)}
                  type="button"
                >
                  <span>{column.label}</span>
                  <span className="sort-indicator">
                    {sortConfig.key === column.key ? (sortConfig.direction === 'asc' ? '↑' : '↓') : '↕'}
                  </span>
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row) => (
            <tr
              className={selectedId === row.id ? 'selectable-row active' : onSelect ? 'selectable-row' : ''}
              key={row.id}
              onClick={() => onSelect?.(row)}
            >
              <td title={row.beneficiario_nome}>{row.beneficiario_nome || 'Não informado'}</td>
              <td title={row.orgao_nome}>{row.orgao_nome || 'Não informado'}</td>
              <td title={row.cargo_descricao}>{row.cargo_descricao || 'Não informado'}</td>
              <td>{row.tipo_viagem || '-'}</td>
              <td title={row.motivo}>{row.motivo || 'Não informado'}</td>
              <td>{row.data_inicio_afastamento || '-'} a {row.data_fim_afastamento || '-'}</td>
              <td>{moneyFormatter.format(Number(row.valor_total_viagem || 0))}</td>
            </tr>
          ))}
          {!safeRows.length && (
            <tr>
              <td colSpan={columns.length}>Sem dados para o filtro atual.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function compareRows(a, b, column, direction) {
  const modifier = direction === 'asc' ? 1 : -1;
  const type = column?.type || 'text';
  const aValue = normalizeValue(a[column?.key], type);
  const bValue = normalizeValue(b[column?.key], type);

  if (type === 'text') {
    return modifier * String(aValue).localeCompare(String(bValue), 'pt-BR', { sensitivity: 'base' });
  }

  if (aValue < bValue) return -1 * modifier;
  if (aValue > bValue) return 1 * modifier;
  return 0;
}

function normalizeValue(value, type) {
  if (type === 'number') return Number(value || 0);
  if (type === 'date') {
    const timestamp = Date.parse(value || '');
    return Number.isNaN(timestamp) ? 0 : timestamp;
  }
  return value || '';
}
