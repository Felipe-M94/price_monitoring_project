# Price Monitoring Project

## Visão Geral
O **Price Monitoring Project** é uma solução para coleta, processamento e visualização de preços de criptomoedas. Utiliza Apache Airflow para orquestração, PostgreSQL como banco de dados e Grafana para visualizações.

## Tecnologias Utilizadas
- **Apache Airflow**: Automação e agendamento de tarefas.
- **PostgreSQL**: Armazenamento dos dados coletados.
- **Grafana**: Visualização de métricas.
- **dbt (Data Build Tool)**: Transformação e modelagem de dados.
- **Docker**: Utilizado na implantação do ambiente de desenvolvimento.

## Estrutura do Projeto
```
price_monitoring_project/
│-- dags/                 # DAGs do Apache Airflow
│-- dbt/                  # Modelos dbt
│-- scripts/              # Scripts auxiliares
│-- docker-compose.yml    # Configuração dos serviços via Docker
│-- Dockerfile            # Configuração da imagem personalizada do Airflow
│-- README.md             # Documentação do projeto
│-- requirements.txt      # Dependências do projeto
│-- .gitignore            # Arquivos ignorados pelo Git
```

## Como Executar
### 1. Clonar o Repositório
```bash
git clone https://github.com/Felipe-M94/price_monitoring_project.git
cd price_monitoring_project
```

### 2. Subir os Serviços com Docker
```bash
docker-compose up -d
```
Isso iniciará os serviços do Airflow e PostgreSQL.

### 3. Acessar os Serviços
- **Airflow UI**: http://localhost:8080 (usuário: `admin`, senha: `admin`)
- **Grafana**: http://localhost:3000 (se configurado no `docker-compose.yml`)
- **PostgreSQL**: `localhost:5433`, banco `crypto_db`

## DAGs do Airflow
As DAGs responsáveis pela coleta e transformação dos dados estão no diretório `dags/` e são executadas automaticamente conforme agendamento definido.

## Modelagem de Dados com dbt
Os modelos dbt estão na pasta `dbt/`, organizados em três camadas:
1. **stg_crypto_prices**: Dados brutos extraídos da API.
2. **silver_crypto_prices**: Dados limpos e transformados.
3. **mart_crypto_prices_summary**: Dados agregados para visualizações.

## Visualização no Grafana
Os dados processados podem ser visualizados no Grafana, utilizando consultas SQL diretamente no PostgreSQL.

## Personalização
Para modificar variáveis, edite o arquivo `docker-compose.yml`.

## Espaço para Imagens
(Aqui você pode adicionar imagens do projeto)

---
### Autor
Felipe M. 🚀

