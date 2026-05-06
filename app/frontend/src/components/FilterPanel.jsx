import { useEffect, useMemo, useState } from 'react';

import { searchFilterOptions } from '../api.js';

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
        Período inicial
        <input
          type="date"
          value={filters.data_inicio}
          onChange={(event) => update({ data_inicio: event.target.value })}
        />
      </label>

      <label>
        Período final
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
        emptyLabel="Todos os beneficiários"
        kind="beneficiarios"
        onSelect={(value) => update({ beneficiario: value })}
        options={options?.beneficiarios || []}
        selected={filters.beneficiario}
        title="Beneficiário"
      />

      <SearchableOptionList
        emptyLabel="Todos os cargos"
        kind="cargos"
        onSelect={(value) => update({ cargo: value })}
        options={options?.cargos || []}
        selected={filters.cargo}
        title="Cargo"
      />

      <div className="orgao-list">
        <div className="filter-title">Órgãos</div>
        <button className="clear-button" type="button" onClick={() => update({ orgao: [] })}>
          Limpar seleção
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

function SearchableOptionList({ emptyLabel, kind, onSelect, options, selected, title }) {
  const [query, setQuery] = useState('');
  const [remoteOptions, setRemoteOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const trimmedQuery = query.trim();

  useEffect(() => {
    let ignore = false;
    if (!trimmedQuery) {
      setRemoteOptions([]);
      return () => {
        ignore = true;
      };
    }

    setLoading(true);
    const timer = window.setTimeout(() => {
      searchFilterOptions(kind, trimmedQuery)
        .then((nextOptions) => {
          if (!ignore) setRemoteOptions(nextOptions);
        })
        .catch(() => {
          if (!ignore) setRemoteOptions([]);
        })
        .finally(() => {
          if (!ignore) setLoading(false);
        });
    }, 250);

    return () => {
      ignore = true;
      window.clearTimeout(timer);
    };
  }, [kind, trimmedQuery]);

  const visibleOptions = useMemo(() => {
    const sourceOptions = trimmedQuery ? remoteOptions : options;
    const normalizedQuery = trimmedQuery.toLowerCase();
    return sourceOptions
      .filter((option) => {
        if (!normalizedQuery) return true;
        return option.label.toLowerCase().includes(normalizedQuery);
      })
      .slice(0, 80);
  }, [options, remoteOptions, trimmedQuery]);

  const canApplyText = trimmedQuery && selected !== trimmedQuery;

  return (
    <div className="option-picker">
      <div className="filter-title">{title}</div>
      <input
        aria-label={`Buscar ${title}`}
        type="search"
        placeholder="Digite ou cole para buscar"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' && trimmedQuery) onSelect(trimmedQuery);
        }}
      />
      <div className="filter-actions">
        <button className="clear-button" type="button" onClick={() => onSelect('')}>
          {emptyLabel}
        </button>
        {canApplyText && (
          <button className="clear-button apply-button" type="button" onClick={() => onSelect(trimmedQuery)}>
            Aplicar texto
          </button>
        )}
      </div>
      {selected && <div className="selected-filter" title={selected}>Selecionado: {selected}</div>}
      <div className="choice-list">
        {loading && <div className="empty-choice">Buscando...</div>}
        {!loading && visibleOptions.map((option) => (
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
        {!loading && !visibleOptions.length && (
          <div className="empty-choice">Nenhuma opção encontrada. Use "Aplicar texto" para filtrar pelo termo colado.</div>
        )}
      </div>
    </div>
  );
}
