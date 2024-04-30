import requests
import psycopg2

# URL da API de viagens e os parâmetros da consulta
url = 'https://api.portaldatransparencia.gov.br/api-de-dados/viagens'

# As datas possuem um período máximo de 1 mês
params = {
    'dataIdaDe': '01/01/2024',
    'dataIdaAte': '31/01/2024',
    'dataRetornoDe': '01/01/2024',
    'dataRetornoAte': '31/01/2024',
    'codigoOrgao': '35000',  # Código SIAFI Ministério Relações Exteriores
    'pagina': '1'
}

# Chave de API
headers = {
    'accept': '*/*',
    'chave-api-dados': 'CHAVE_API'  # Substitua 'CHAVE_API' pela sua chave de API
}

# Faça a solicitação GET para a API
response = requests.get(url, params=params, headers=headers)

# Verifique se a solicitação foi bem-sucedida
if response.status_code == 200:
    data = response.json()  # Converte a resposta para JSON

    # Conecte ao banco de dados PostgreSQL
    # Substitua com os do seu banco de dados
    conn = psycopg2.connect(
        dbname='database',
        user='usuario',
        password='senha',
        host='host',
        port='port'
    )

    cursor = conn.cursor()

    # Crie uma tabela no banco de dados para armazenar os resultados das viagens
    cursor.execute('''CREATE TABLE IF NOT EXISTS viagens (
                    id INTEGER PRIMARY KEY,
                    motivo TEXT,
                    pcdp TEXT,
                    ano INTEGER,
                    num_pcdp TEXT,
                    justificativa_urgente TEXT,
                    urgencia_viagem TEXT,
                    situacao TEXT,
                    beneficiario_cpf TEXT,
                    beneficiario_nis TEXT,
                    beneficiario_nome TEXT,
                    cargo_codigo_siape TEXT,
                    cargo_descricao TEXT,
                    funcao_codigo_siape TEXT,
                    funcao_descricao TEXT,
                    tipo_viagem TEXT,
                    orgao_nome TEXT,
                    orgao_codigo_siafi TEXT,
                    orgao_cnpj TEXT,
                    orgao_sigla TEXT,
                    orgao_descricao_poder TEXT,
                    orgao_pagamento_nome TEXT,
                    orgao_pagamento_codigo_siafi TEXT,
                    orgao_pagamento_cnpj TEXT,
                    orgao_pagamento_sigla TEXT,
                    unidade_gestora_codigo TEXT,
                    unidade_gestora_nome TEXT,
                    unidade_gestora_descricao_poder TEXT,
                    data_inicio_afastamento DATE,
                    data_fim_afastamento DATE,
                    valor_total_restituicao NUMERIC,
                    valor_total_taxa_agenciamento NUMERIC,
                    valor_multa NUMERIC,
                    valor_total_diarias NUMERIC,
                    valor_total_passagem NUMERIC,
                    valor_total_viagem NUMERIC,
                    valor_total_devolucao NUMERIC
                )''')

    # Insira os dados da API no banco de dados
    for item in data:
        try:
            cursor.execute('''
                INSERT INTO viagens (
                    id,
                    motivo,
                    pcdp,
                    ano,
                    num_pcdp,
                    justificativa_urgente,
                    urgencia_viagem,
                    situacao,
                    beneficiario_cpf,
                    beneficiario_nis,
                    beneficiario_nome,
                    cargo_codigo_siape,
                    cargo_descricao,
                    funcao_codigo_siape,
                    funcao_descricao,
                    tipo_viagem,
                    orgao_nome,
                    orgao_codigo_siafi,
                    orgao_cnpj,
                    orgao_sigla,
                    orgao_descricao_poder,
                    orgao_pagamento_nome,
                    orgao_pagamento_codigo_siafi,
                    orgao_pagamento_cnpj,
                    orgao_pagamento_sigla,   
                    unidade_gestora_codigo,
                    unidade_gestora_nome,
                    unidade_gestora_descricao_poder,
                    data_inicio_afastamento,
                    data_fim_afastamento, 
                    valor_total_restituicao,
                    valor_total_taxa_agenciamento,
                    valor_multa,
                    valor_total_diarias,
                    valor_total_passagem,
                    valor_total_viagem,
                    valor_total_devolucao
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                )
            ''', (
                item['id'],
                item['viagem']['motivo'],
                item['viagem']['pcdp'],
                item['viagem']['ano'],
                item['viagem']['numPcdp'],
                item['viagem']['justificativaUrgente'],
                item['viagem']['urgenciaViagem'],
                item['situacao'],
                item['beneficiario']['cpfFormatado'],
                item['beneficiario']['nis'],
                item['beneficiario']['nome'],
                item['cargo']['codigoSIAPE'],
                item['cargo']['descricao'],
                item['funcao']['codigoSIAPE'],
                item['funcao']['descricao'],
                item['tipoViagem'],
                item['orgao']['nome'],
                item['orgao']['codigoSIAFI'],
                item['orgao']['cnpj'],
                item['orgao']['sigla'],
                item['orgao']['descricaoPoder'],
                item['orgaoPagamento']['nome'],
                item['orgaoPagamento']['codigoSIAFI'],
                item['orgaoPagamento']['cnpj'],
                item['orgaoPagamento']['sigla'],
                item['unidadeGestoraResponsavel']['codigo'],
                item['unidadeGestoraResponsavel']['nome'],
                item['unidadeGestoraResponsavel']['descricaoPoder'],
                item['dataInicioAfastamento'],
                item['dataFimAfastamento'],
                item['valorTotalRestituicao'],
                item['valorTotalTaxaAgenciamento'],
                item['valorMulta'],
                item['valorTotalDiarias'],
                item['valorTotalPassagem'],
                item['valorTotalViagem'],
                item['valorTotalDevolucao']
            ))
        except KeyError as ke:
            print(f"KeyError {ke} in item {item}")

        except TypeError as te:
            print(f"TypeError: {te}")
            break
    # Commit para salvar as alterações no banco de dados
    conn.commit()

    # Feche a conexão com o banco de dados
    conn.close()

    print("Dados das viagens foram inseridos no banco de dados PostgreSQL com sucesso!")
else:
    print("Erro ao acessar a API:", response.status_code)
    