FROM apache/airflow:2.7.3

# Definir variáveis de ambiente necessárias para o Airflow
ENV AIRFLOW_HOME=/opt/airflow

# Instalar pacotes adicionais (se necessário)
RUN pip install --no-cache-dir apache-airflow-providers-http==4.6.0

# Criar diretórios para DAGs, logs e dbt
RUN mkdir -p $AIRFLOW_HOME/dags $AIRFLOW_HOME/logs $AIRFLOW_HOME/dbt

# Copiar DAGs e outros arquivos necessários para o container
COPY ./dags $AIRFLOW_HOME/dags
COPY ./crypto_prices_transformation $AIRFLOW_HOME/dbt

# Definir permissões adequadas
RUN chown -R airflow:airflow $AIRFLOW_HOME

# Comando de inicialização do Airflow
CMD bash -c "airflow db upgrade && \
            airflow db init && \
            airflow users create --username admin --password admin --firstname Felipe --lastname Crypto --role Admin --email admin@example.com && \
            (airflow webserver & airflow scheduler)"
