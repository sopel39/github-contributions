import csv
import json
import datetime
import logging
from copy import deepcopy
from string import Template
from github3api import GitHubAPI
from mp4ansi import MP4ansi

logger = logging.getLogger(__name__)

QUERY = """
    {
        user(login: "$login") {
            contributionsCollection(from: "$from", to: "$to", organizationID: "$organizationID") {
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions
                totalPullRequestReviewContributions
                totalRepositoriesWithContributedCommits
                totalRepositoriesWithContributedIssues
                totalRepositoriesWithContributedPullRequests
                totalRepositoriesWithContributedPullRequestReviews
                user {
                    login
                    name
                }
            }
        }
    }
"""


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('contributions.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def get_dates():
    """ return tuple of current date and date from one year ago
    """
    current = datetime.datetime.now()
    current_strftime = current.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    last = datetime.datetime.now() - datetime.timedelta(days=365)
    last_strftime = last.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return current_strftime, last_strftime


def sanitize(query):
    """ sanitize query
    """
    q1 = query.replace(' ', '')
    q2 = q1.replace('\n', ' ')
    return q2


def get_contributions_query(login, date_from, date_to, organization_id):
    """ return contributions query
    """
    query_template = Template(sanitize(QUERY))
    arguments = {'login': login, 'from': date_from, 'to': date_to, 'organizationID': organization_id}
    return query_template.substitute(arguments)


def get_user_contribution(data):
    """ return user contribution from data
    """
    item = {
        'name': data['user']['name'],
        'login': data['user']['login'],
        'totalCommitContributions': data['totalCommitContributions'],
        'totalIssueContributions': data['totalIssueContributions'],
        'totalPullRequestContributions': data['totalPullRequestContributions'],
        'totalPullRequestReviewContributions': data['totalPullRequestReviewContributions'],
        'total': data['totalCommitContributions'] + data['totalIssueContributions'] + data['totalPullRequestContributions'] + data['totalPullRequestReviewContributions']
    }
    return item


def get_contributions(data, *args):
    """ get contributions for all members in organization
    """
    contributions = []
    organization = data['organization']
    date_from = data['date_from']
    date_to = data['date_to']
    client = GitHubAPI.get_client()
    organization_id = client.get(f'/orgs/{organization}')['node_id']
    logger.debug(f'getting github contributions for {organization} users')
    members = client.get(f'/orgs/{organization}/members', _get='all', _attributes=['login'])
    logger.debug(f'{organization} has a total of {len(members)} users')
    for member in members:
        login = member['login']
        query = get_contributions_query(login, date_from, date_to, organization_id)
        logger.debug(f'getting contributions for user {login}')
        response = client.post('/graphql', json={'query': query})
        contribution = get_user_contribution(response['data']['user']['contributionsCollection'])
        contributions.append(contribution)
    return contributions


def write_json(process_data, name):
    """ write data to json file
    """
    filename = f'{name}.json'
    with open(filename, 'w') as fp:
        json.dump(process_data, fp, indent=2)
    print(f'{name} report written to {filename}')


def write_csv(data, name):
    """ write data to csv file
    """
    filename = f'{name}.csv'
    logger.debug(f'writing {filename}')
    headers = data[0].keys()
    with open(filename, 'w') as output:
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(data)
    print(f'{name} report written to {filename}')


def main():
    """ main method
    """
    owner = 'edgexfoundry'
    print(f'Getting user contribution data for {owner} ...')
    date_to, date_from = get_dates()
    process_data = [{'date_from': date_from, 'date_to': date_to, 'organization': owner}]
    MP4ansi(
        function=get_contributions,
        process_data=process_data,
        config={
            'id_regex': r'^getting github contributions for (?P<value>.*) users$',
            'progress_bar': {
                'total': r'^.* has a total of (?P<value>\d+) users$',
                'count_regex': r'^getting contributions for user (?P<value>.*)$',
                'progress_message': 'Contributions retrieval complete'
            }
        }).execute(raise_if_error=True)
    write_json(process_data[0]['result'], 'contributions')
    write_csv(process_data[0]['result'], 'contributions')


if __name__ == '__main__':
    configure_logging()
    main()
