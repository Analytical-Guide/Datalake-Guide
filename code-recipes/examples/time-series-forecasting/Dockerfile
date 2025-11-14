# syntax=docker/dockerfile:1.6

ARG PYTHON_VERSION=3.10

# --- Builder stage for heavy dependencies -----------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies (only for compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    g++ \
    make \
    cmake \
    git \
    libopenblas-dev \
    liblapack-dev \
    libgomp1 \
    libssl-dev \
    libffi-dev \
    libcurl4-openssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel for faster builds
RUN pip install --upgrade pip wheel

# Copy requirements first for better layer caching
COPY requirements.txt .

# Build wheels for all dependencies (cached if requirements don't change)
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# --- Runtime stage (minimal final image) -----------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
    CMDSTANPY_CMDSTAN_PATH=/root/.cmdstan \
    PYSPARK_PYTHON=python \
    PYSPARK_DRIVER_PYTHON=python \
    PATH="/opt/venv/bin:$PATH"

# Install runtime system dependencies (including build tools for CmdStan)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jdk-headless \
    curl \
    libgomp1 \
    libopenblas0 \
    liblapack3 \
    libpng16-16 \
    libfreetype6 \
    build-essential \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Download Iceberg and PostgreSQL JDBC drivers
RUN mkdir -p /opt/spark/jars && \
    curl -L -o /opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.5.2.jar \
        https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.5.2/iceberg-spark-runtime-3.5_2.12-1.5.2.jar && \
    curl -L -o /opt/spark/jars/postgresql-42.7.3.jar \
        https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

# Set Spark configuration for Iceberg
ENV SPARK_HOME=/opt/spark \
    SPARK_CONF_DIR=/opt/spark/conf \
    PYSPARK_SUBMIT_ARGS="--jars /opt/spark/jars/iceberg-spark-runtime-3.5_2.12-1.5.2.jar,/opt/spark/jars/postgresql-42.7.3.jar pyspark-shell"

# Copy pre-built virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Install wheels from builder stage
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels \
    $(grep -v '^#' requirements.txt | tr '\n' ' ') && \
    rm -rf /wheels

# Pre-install CmdStan for Prophet (use multiple cores for faster compilation)
RUN python -m cmdstanpy.install_cmdstan --overwrite --progress --cores 4

WORKDIR /app

# Copy application code (changes frequently, so put last for better caching)
COPY . .

# Create data directories
RUN mkdir -p /app/data/cache /app/output

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pandas, numpy, sklearn; print('✅ Dependencies OK')" || exit 1

# Default entrypoint
ENTRYPOINT ["python", "solution.py"]
