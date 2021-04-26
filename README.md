# github-contributions
[![GitHub Workflow Status](https://github.com/soda480/github-contributions/workflows/build/badge.svg)](https://github.com/soda480/github-contributions/actions)
[![Code Grade](https://www.code-inspector.com/project/21990/status/svg)](https://frontend.code-inspector.com/project/21990/dashboard)
[![complexity](https://img.shields.io/badge/complexity-Simple:%202-green)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![python](https://img.shields.io/badge/python-3.6-teal)](https://www.python.org/downloads/)

A Python script to get contribution metrics for all members of a GitHub organization. The script utilizes the GitHub GraphQL API and exports the report to a csv file.

## `ghcontrib`
```bash
usage: ghcontrib [-h] [--org ORG]

A Python script to get contribution metrics for all members of a GitHub
organization using the GitHub GraphQL API

optional arguments:
  -h, --help  show this help message and exit
  --org ORG   GitHub organization containing members to process
  ```

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
ghcontrib --org edgexfoundry
```

![preview](https://raw.githubusercontent.com/soda480/github-contributions/master/docs/images/contributions.gif)
