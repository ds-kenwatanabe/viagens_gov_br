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

CREATE OR REPLACE VIEW vw_viagens_dashboard AS
SELECT
    id,
    orgao_codigo_siafi,
    orgao_nome,
    orgao_sigla,
    beneficiario_nome,
    cargo_descricao,
    unidade_gestora_nome,
    tipo_viagem,
    situacao,
    motivo,
    data_inicio_afastamento,
    data_fim_afastamento,
    valor_total_diarias,
    valor_total_passagem,
    valor_total_viagem,
    EXTRACT(YEAR FROM data_inicio_afastamento) AS ano,
    EXTRACT(MONTH FROM data_inicio_afastamento) AS mes
FROM viagens;

CREATE OR REPLACE VIEW vw_mapa_viagens AS
SELECT
    v.id,
    v.orgao_codigo_siafi,
    v.orgao_nome,
    v.orgao_sigla,
    v.beneficiario_nome,
    v.cargo_descricao,
    v.tipo_viagem,
    v.motivo,
    v.valor_total_viagem,
    v.data_inicio_afastamento,
    v.data_fim_afastamento,
    l.cidade,
    l.estado,
    l.pais,
    l.latitude,
    l.longitude,
    l.confidence
FROM viagens v
JOIN viagem_localidades l
  ON l.viagem_id = v.id
WHERE l.latitude IS NOT NULL
  AND l.longitude IS NOT NULL;
