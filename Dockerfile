# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Define a build-time variable
ARG CERTIFICATE_SERVER_URL

# Copy the application files to the new working directory
COPY certs certs

RUN if [ -n "${CERTIFICATE_SERVER_URL}" ]; then \
      openssl s_client -connect ${CERTIFICATE_SERVER_URL%/}:443 -showcerts > certs.txt; \
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

# Create a non-root user
RUN useradd -m pyuser

# Set the working directory for the non-root user
WORKDIR /home/pyuser/app

# Copy the application files to the new working directory
COPY . .

# Change ownership of the directory to the non-root user
RUN chown -R pyuser:pyuser /home/pyuser/app

# Switch to the non-root user
USER pyuser

# Install dependencies and application for the non-root user
RUN pip install --user -r requirements.txt && pip install --user .

