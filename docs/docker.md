# dina-py Docker

## Build the image

`docker build . -t dina-py:0.1`

If internal certificates are required you can add them to the `certs` folder or the docker build can get them from a server using `docker build . --build-arg CERTIFICATE_SERVER_URL=<<SERVER>> -t dina-py:0.1`.

For debugging purposes, `--progress=plain` can be added to the build command to see echo messages.


## Run the container

User the provided docker compose file: `docker compose -f docker-compose.base.yml up`

## Connect to container

`docker exec -it dina_py_container bash`
