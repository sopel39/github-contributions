import os
import sys
import csv
import json
import logging
import argparse
import datetime
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
                }
            }
        }
    }
"""


def get_parser():
    """ return argument parser
    """
    parser = argparse.ArgumentParser(
        description='A Python script to get contribution metrics for all members of a GitHub organization using the GitHub GraphQL API')
    parser.add_argument(
        '--org',
        dest='org',
        type=str,
        default=os.getenv('GH_ORG'),
        required=False,
        help='GitHub organization containing members to process')
    return parser


def configure_logging(name=None):
    """ configure logging
    """
    if not name:
        name = os.path.basename(sys.argv[0])
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(f'{name}.log')
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
    return query.replace(' ', '').replace('\n', ' ')


def get_contributions_query(login, date_from, date_to, organization_id):
    """ return contributions query
    """
    sanitized_query = sanitize(QUERY)
    query_template = Template(sanitized_query)
    arguments = {
        'login': login,
        'from': date_from,
        'to': date_to,
        'organizationID': organization_id
    }
    return query_template.substitute(arguments)


def get_user_contribution(data):
    """ return user contribution from data
    """
    return {
        # 'name': data['user']['name'],
        'login': data['user']['login'],
        'totalCommitContributions': data['totalCommitContributions'],
        'totalIssueContributions': data['totalIssueContributions'],
        'totalPullRequestContributions': data['totalPullRequestContributions'],
        'totalPullRequestReviewContributions': data['totalPullRequestReviewContributions'],
        'total': data['totalCommitContributions'] + data['totalIssueContributions'] + data['totalPullRequestContributions'] + data['totalPullRequestReviewContributions']
    }


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
        logger.debug(f'getting contributions for user {login}')
        query = get_contributions_query(login, date_from, date_to, organization_id)
        response = client.post('/graphql', json={'query': query})
        contribution = get_user_contribution(response['data']['user']['contributionsCollection'])
        contributions.append(contribution)
    return contributions


def write_json(process_data, name):
    """ write data to json file
    """
    filename = f'{name}.json'
    with open(filename, 'w') as output:
        json.dump(process_data, output, indent=2)
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
    args = get_parser().parse_args()
    configure_logging()
    print(f'Getting user contribution data for {args.org} ...')
    date_to, date_from = get_dates()
    process_data = [{'date_from': date_from, 'date_to': date_to, 'organization': args.org}]
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
    sorted_result = sorted(process_data[0]['result'], key=lambda item: item['total'], reverse=True)
    write_json(sorted_result, 'contributions')
    write_csv(sorted_result, 'contributions')


if __name__ == '__main__':
    main()
