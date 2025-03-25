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

RUN openssl s_client -connect ${CERTIFICATE_SERVER_URL}:443 -showcerts > certs.txt
RUN awk '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/' certs.txt > combined-cert.crt


# Add the certificates
RUN combined-cert.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .


