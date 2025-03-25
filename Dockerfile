# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Create a non-root user
RUN useradd -m pyuser

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

# Define a build-time variable
ARG CERTIFICATE_SERVER_URL

RUN if [ -n "${CERTIFICATE_SERVER_URL}" ]; then \
      openssl s_client -connect ${CERTIFICATE_SERVER_URL}:443 -showcerts > certs.txt; \
      awk '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/' certs.txt > combined-cert.crt; \
      cp combined-cert.crt /usr/local/share/ca-certificates/; \
    else \
      echo "CERTIFICATE_SERVER_URL is not set. Will try copy .crt from certs folder"; \
      if [ -d "certs" ] && [ "$(ls -A certs/*.crt 2>/dev/null)" ]; then \
        cp certs/*.crt /usr/local/share/ca-certificates/; \
      else \
        echo "No certificates to copy"; \
      fi; \
    fi

RUN update-ca-certificates

# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .


