# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Create a non-root user
RUN useradd -m pyuser

# Set working directory
WORKDIR /app

# Copy the certificates
COPY certs/* /tmp/

# Add the certificates
RUN cp /tmp/*.pem /usr/share/ca-certificates/
RUN update-ca-certificates

# Copy the application code
COPY . .

# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .


