# dina-py Docker

Build the image: `docker build . -t dina-py:0.1`

Build the image with automatic internal certificate configuration: `build . --build-arg CERTIFICATE_SERVER_URL=<<SERVER>> -t dina-py:0.1`

Run the image: `docker compose -f docker-compose.base.yml up`

