# Dados de viagens do Governo Brasileiro

## Introdução
Este é um projeto que utiliza da API do [Portal da Transparência](https://portaldatransparencia.gov.br) para acessar dados de viagens feitas por funcionários do governo brasileiro e inseri-los em uma base de dados PostgreSQL.
<br />
<br />
Os dados que foram utilizados neste projeto correspondem aos dados de viagens de funcionários do Ministério das Relações Exteriores, Ministério da Saúde e Presidência da República, durante o período de 01/01/2023 até 30/04/2024. Um total de 36104 dados foram coletados.

### Sobre o Portal da Transparência e a API de dados

O Portal da Transparência do Governo Federal é um site destinado a divulgar dados e informações detalhadas sobre a execução orçamentária e financeira da União. 
As informações disponíveis no Portal abrangem o Poder Executivo e a esfera federal. Essa ferramenta também publica dados sobre assuntos relacionados à função da maioria desses órgãos.
<br />
<br />
O Portal da transparência também possuí uma API de dados que pode ser acessada por indivíduos brasileiros que possuem uma conta gov.br com autenticação de dois fatores. Esta autenticação é necessária para receber uma chave da API que deverá ser utilizada para acessar os dados.
Para mais informações sobre a API e como acessar os dados, acesse o site da [API de dados](https://portaldatransparencia.gov.br/api-de-dados).

### Sobre o banco de dados postgreSQL

Os dados recebidos através da API serão inseridos em um banco de dados PostgreSQL. Caso tenha dúvidas sobre o PostgreSQL, acesse o [site](https://www.postgresql.org/about/). Você também pode fazer o download [aqui](https://www.postgresql.org/download/).

## Dados importantes ❗
* Sua chave de API - deve ser requerida no site da API de dados. Cuidado para não compartilhar a sua chave! Ela pode ser protegida utilizando um arquivo .env, que será explicado na seção [Gerando um arquivo .env](#arquivo-env)
*  Após configurar seu banco de dados, você poderá utilizar o arquivo [requests_viagens.py](requests_viagens.py), inserir seus dados. Os dados que você precisará são:
    1. Nome do seu banco de dados;
    2. Nome do usuário;
    3. Senha do banco de dados;
    4. Nome do Host;
    5. Número da porta.  
* O código do Sistema Integrado de Administração Financeira (SIAFI).
* O SIAFI é utilizado para registro da execução orçamentária, financeira, patrimonial e contábil dos órgãos da Administração Pública Direta federal, das autarquias, fundações e empresas públicas federais e das sociedades de economia mista que estiverem contempladas no Orçamento Fiscal e/ou no Orçamento da Seguridade Social da União.
* O código SIAFI é necessário para especificar de qual órgão você está requerindo os dados.
  * Os códigos que foram utilizados para o projeto são:
  * 35000 - Ministério Relações Exteriores
  * 36000 - Ministério da Saúde
  * 20000 - Presidência da República

<a name="arquivo-env"></a>
## Gerando um arquivo .env
