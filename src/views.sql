CREATE TABLE IF NOT EXISTS viagem_localidades (
    id SERIAL PRIMARY KEY,
    viagem_id INTEGER REFERENCES viagens(id),
    local_texto TEXT,
    cidade TEXT,
    estado TEXT,
    pais TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    confidence NUMERIC,
    fonte TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (viagem_id, local_texto)
);

CREATE INDEX IF NOT EXISTS idx_viagens_filtros
    ON viagens (orgao_codigo_siafi, data_inicio_afastamento, tipo_viagem);

CREATE INDEX IF NOT EXISTS idx_viagens_beneficiario
    ON viagens (beneficiario_nome);

CREATE INDEX IF NOT EXISTS idx_viagens_cargo
    ON viagens (cargo_descricao);

CREATE INDEX IF NOT EXISTS idx_viagem_localidades_viagem_id
    ON viagem_localidades (viagem_id);

CREATE INDEX IF NOT EXISTS idx_viagem_localidades_geo
    ON viagem_localidades (latitude, longitude);

CREATE OR REPLACE VIEW vw_viagens_mensal AS
SELECT orgao_codigo_siafi,
       orgao_nome,
       date_trunc('month', data_inicio_afastamento)::date AS mes,
       tipo_viagem,
       COUNT(*) AS numero_viagens,
       SUM(valor_total_viagem) AS valor_total,
       SUM(valor_total_diarias) AS valor_diarias,
       SUM(valor_total_passagem) AS valor_passagens
  FROM viagens
 GROUP BY orgao_codigo_siafi, orgao_nome, date_trunc('month', data_inicio_afastamento)::date, tipo_viagem;
