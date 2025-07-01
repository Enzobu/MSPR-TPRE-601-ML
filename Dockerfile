FROM python:3.10-slim

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    wget \
    nano \
    gcc \
    build-essential \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    matplotlib  \
    requests \
    psycopg2-binary \
    python-dotenv \
    country_converter \
    kagglehub \
    pylint \
    psycopg2 \
    pandas \
    prophet \
    pystan \
    plotly \
    joblib

WORKDIR /app

RUN wget https://jdbc.postgresql.org/download/postgresql-42.6.0.jar && \
    mkdir -p /opt/jars && \
    mv postgresql-42.6.0.jar /opt/jars/

RUN echo "alias ll='ls -al'" >> /root/.bashrc && \
    echo "export PATH=\$PATH:/app/bin/" >> /root/.bashrc && \
    echo "export PYTHONPATH=/app" >> /root/.bashrc

CMD ["tail", "-f", "/dev/null"]