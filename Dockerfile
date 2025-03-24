# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Create a non-root user
RUN useradd -m pyuser

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

# Add the certificates
RUN cp certs/*.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .


