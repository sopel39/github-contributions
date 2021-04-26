# github-contributions
A python script to get contribution metrics for all members of a GitHub organization. The script utilizes the GitHub GraphQL API and exports the report to a csv file.

Build the Docker image:
```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t ghcontrib:latest .
```

Run the Docker container:
```bash
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/ghcontrib \
ghcontrib:latest /bin/sh
```
