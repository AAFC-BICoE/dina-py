# Stage 1: Build stage
FROM python:3.12-slim AS builder
 
# Set working directory
WORKDIR /app
 
# Copy the application code
COPY . .
 
# Install the dependencies
RUN pip install --user -r requirements.txt
 
# Install the application
RUN pip install --user .
