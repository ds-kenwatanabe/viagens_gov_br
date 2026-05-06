import { useMemo, useState } from 'react';

export default function FilterPanel({ filters, options, onChange }) {
  const update = (patch) => onChange({ ...filters, ...patch });

  function toggleOrgao(value) {
    const selected = new Set(filters.orgao);
    if (selected.has(value)) {
      selected.delete(value);
    } else {
      selected.add(value);
    }
    update({ orgao: Array.from(selected) });
  }

  return (
    <div className="filters">
      <label>
        Periodo inicial
        <input
          type="date"
          value={filters.data_inicio}
          onChange={(event) => update({ data_inicio: event.target.value })}
        />
      </label>

      <label>
        Periodo final
        <input
          type="date"
          value={filters.data_fim}
          onChange={(event) => update({ data_fim: event.target.value })}
        />
      </label>

      <label>
        Tipo de viagem
        <select
          value={filters.tipo_viagem}
          onChange={(event) => update({ tipo_viagem: event.target.value })}
        >
          <option value="">Todos</option>
          {(options?.tipos_viagem || []).map((option) => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </label>

      <SearchableOptionList
        emptyLabel="Todos os beneficiarios"
        onSelect={(value) => update({ beneficiario: value })}
        options={options?.beneficiarios || []}
        selected={filters.beneficiario}
        title="Beneficiario"
      />

      <SearchableOptionList
        emptyLabel="Todos os cargos"
        onSelect={(value) => update({ cargo: value })}
        options={options?.cargos || []}
        selected={filters.cargo}
        title="Cargo"
      />

      <div className="orgao-list">
        <div className="filter-title">Orgaos</div>
        <button className="clear-button" type="button" onClick={() => update({ orgao: [] })}>
          Limpar selecao
        </button>
        <div className="checkbox-list">
          {(options?.orgaos || []).slice(0, 80).map((option) => (
            <label key={option.value} className="checkbox-row">
              <input
                type="checkbox"
                checked={filters.orgao.includes(option.value)}
                onChange={() => toggleOrgao(option.value)}
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

function SearchableOptionList({ emptyLabel, onSelect, options, selected, title }) {
  const [query, setQuery] = useState('');
  const visibleOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return options
      .filter((option) => {
        if (!normalizedQuery) return true;
        return option.label.toLowerCase().includes(normalizedQuery);
      })
      .slice(0, 80);
  }, [options, query]);

  return (
    <div className="option-picker">
      <div className="filter-title">{title}</div>
      <input
        aria-label={`Buscar ${title}`}
        type="search"
        placeholder="Buscar na lista"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <button className="clear-button" type="button" onClick={() => onSelect('')}>
        {emptyLabel}
      </button>
      <div className="choice-list">
        {visibleOptions.map((option) => (
          <button
            className={selected === option.value ? 'choice-row active' : 'choice-row'}
            key={option.value}
            onClick={() => onSelect(option.value)}
            title={option.label}
            type="button"
          >
            {option.label}
          </button>
        ))}
        {!visibleOptions.length && (
          <div className="empty-choice">Nenhuma opcao encontrada.</div>
        )}
      </div>
    </div>
  );
}
