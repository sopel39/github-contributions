# github-graphql
Python script to query GitHub GraphQL collections

Build the Docker image:
```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t ghgraphql:latest .
```

Run the Docker container:
```bash
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/ghgraphql \
ghgraphql:latest /bin/sh
```
