# -- Base image --
FROM python:3.11.0-slim as development

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Upgrade system packages to install security updates
RUN apt-get update && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all sources
COPY . /app/

# Install ramralph along with development dependencies
RUN pip install .[dev]

# Un-privileged user running the application
USER ${DOCKER_USER:-1000}

CMD ["ralph"]
