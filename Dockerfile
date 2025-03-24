# Stage 1: Build stage
FROM python:3.12-slim AS builder
 
# Set working directory
WORKDIR /app
 
# Copy the application code
COPY . .

# Copy the certificates
COPY certs/* /tmp

# Add the certificates to the Python certificate file
RUN cat /tmp/biodiversity-agr-gc-ca-chain.pem >> /etc/ssl/certs/ca-certificates.crt
 
# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .
