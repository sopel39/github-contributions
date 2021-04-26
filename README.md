# github-contributions
A Python script to get contribution metrics for all members of a GitHub organization. The script utilizes the GitHub GraphQL API and exports the report to a csv file.

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

Export the required environment variable and execute the script:
```bash
export GH_TOKEN_PSW=--github-token--
python contributions.py
```

![preview](https://raw.githubusercontent.com/soda480/github-contributions/master/docs/images/contributions.gif)
