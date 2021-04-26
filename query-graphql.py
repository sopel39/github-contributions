import json
import datetime
from copy import deepcopy
from string import Template
from github3api import GitHubAPI


QUERY1 = """
    query {
        viewer {
            login
        }
    }
"""

QUERY2 =  """
    query {
      repository(owner:"octocat", name:"Hello-World") {
        issues(last:20, states:CLOSED) {
          edges {
            node {
              title
              url
              labels(first:5) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
"""


QUERY3 = """
    {
      viewer {
        repositoriesContributedTo(first: 100, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
          nodes {
            nameWithOwner
          }
          pageInfo {
            endCursor
            hasNextPage
          }
        }
      }
    }
"""

# https://docs.github.com/en/graphql/reference/objects#contributionscollection
# date range must not exceed one year
QUERY4 = """
    {
        user(login: "$login") {
            contributionsCollection(from: "$from", to: "$to", organizationID: "$organizationID") {
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions
                totalPullRequestReviewContributions
            }
        }
    }
"""

QUERY5 = """
    {
        user(login: "soda480") {
            repositoriesContributedTo(contributionTypes: [COMMIT, REPOSITORY], last: 100, includeUserRepositories: false) {
                pageInfo {
                    startCursor
                    hasPreviousPage
                }
                nodes {
                    nameWithOwner
                }
            }
        }
    }
"""

QUERY6 = """
"""


def get_from_to_dates():
    current = datetime.datetime.now()
    current_strftime = current.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    last = datetime.datetime.now() - datetime.timedelta(days=365)
    last_strftime = last.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return current_strftime, last_strftime


def sanitize(query):
    q1 = query.replace(' ', '')
    q2 = query.replace('\n', ' ')
    return q2


def graphql(query, **kwargs):
    client = GitHubAPI.get_client()
    query_template = Template(sanitize(query))
    arguments = deepcopy(kwargs)
    to_date, from_date = get_from_to_dates()
    arguments['from'] = from_date
    arguments['to'] = to_date
    arguments['organizationID'] = client.get('/orgs/edgexfoundry')['node_id']
    query_to_execute = query_template.substitute(arguments)
    # print(query_to_execute)
    response = client.post(
        '/graphql',
        json={
            'query': query_to_execute
        })
    print(json.dumps(response, indent=2))


def main():

    graphql(QUERY4, login='soda480')
    graphql(QUERY4, login='ernestojeda')
    graphql(QUERY4, login='bill-mahoney')


if __name__ == '__main__':

    main()
