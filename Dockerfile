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

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app

RUN wget https://jdbc.postgresql.org/download/postgresql-42.6.0.jar && \
    mkdir -p /opt/jars && \
    mv postgresql-42.6.0.jar /opt/jars/

RUN echo "alias ll='ls -al'" >> /root/.bashrc && \
    echo "export PATH=\$PATH:/app/bin/" >> /root/.bashrc && \
    echo "export PYTHONPATH=/app" >> /root/.bashrc

CMD ["tail", "-f", "/dev/null"]

# docker build -t dev-mspr-601-ml .
# docker run --name dev_mspr_601_ml -v ./:/app -e PYTHONPATH=/app \-d dev-mspr-601-ml