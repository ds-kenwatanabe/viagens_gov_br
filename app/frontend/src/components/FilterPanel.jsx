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

      <label>
        Beneficiário
        <input
          type="search"
          placeholder="Nome"
          value={filters.beneficiario}
          onChange={(event) => update({ beneficiario: event.target.value })}
        />
      </label>

      <label>
        Cargo
        <input
          type="search"
          placeholder="Descrição"
          value={filters.cargo}
          onChange={(event) => update({ cargo: event.target.value })}
        />
      </label>

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
