import json

import requests
from urllib.parse import urlparse
from tqdm import tqdm
import threading
import concurrent.futures

# Set your Bitbucket username and app password/token
USERNAME = 'cactusoftheday' # change this to your username
APP_PASSWORD = ''

if(len(APP_PASSWORD) <= 3):
    with(open('file.txt','r')) as file:
        content = file.read() # read app password if app password is empty

content = content.split('\n')

APP_PASSWORD = content[0]

# Set the Bitbucket API base URL
BASE_URL = 'https://api.bitbucket.org/2.0'

class BitbucketInfo:
    def __init__(self, branch, commitId, repositoryName, insertions, deletions, date):
        self.branch = branch
        self.commitId = commitId
        self.repositoryName = repositoryName
        self.insertions = insertions
        self.deletions = deletions
        self.date = date

# Function to extract repository owner from the URL
def get_repo_owner(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    return path_parts[0]

# Function to extract repository name from the URL
def get_repo_name(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    return path_parts[1]

repository_url = content[1] # yet to figure out how to get all repos
# example repo url: https://bitbucket.org/deeptrekker/repo_name
import re

def extract_bitbucket_info(repo_url):
    # Extract repo_slug and workspace from the repository URL
    regex = r"https?://bitbucket.org/([^/]+)/([^/]+)/?"
    match = re.search(regex, repo_url)
    if match:
        workspace = match.group(1)
        repo_slug = match.group(2)
    else:
        raise ValueError("Invalid Bitbucket repository URL")

    return workspace, repo_slug
def get_branches(branches_url):
    allBranches = []
    page = 1
    auth = (USERNAME, APP_PASSWORD)
    repository_owner = get_repo_owner(repository_url)
    repository_name = get_repo_name(repository_url)

    # Construct the branches endpoint URL for the repository
    branches_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/refs/branches'
    params = {'page': 1, 'pagelen': 50}
    response = requests.get(branches_url, auth=auth, params=params)

    if(response.status_code == 200):
        branchesData = response.json()
        branches = branchesData['values']

        allBranches.extend(branches)

        while 'next' in branchesData:
            next_page_url = branchesData['next']
            response = requests.get(next_page_url, auth=auth,params=params)
            print(page)
            params ={'page':page, 'pagelen': 50}
            page += 1
            if response.status_code == 200:
                branchesData = response.json()
                branches = branchesData['values']
                allBranches.extend(branches)
            else:
                print(f'Error: {response.status_code} - {response.text}')
                return None
    #print(response.status_code)
    print(len(allBranches))
    return allBranches


'''def get_commit_diffstat(workspace, repo_slug, commit_sha, auth):
    url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/diffstat/{commit_sha}"

    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        diffstat_data = response.json()
        print(diffstat_data)
        diffstat_values = diffstat_data["values"]
        lines_added = diffstat_values[0]["lines_added"]
        lines_removed = diffstat_values[0]["lines_removed"]
    else:
        print("Error:", response.status_code)
    #return lines_added,lines_removed'''
'''def get_total_commits_by_person(repository_url, USERNAME, userName):
    repository_owner = get_repo_owner(repository_url)
    repository_name = get_repo_name(repository_url)

    # Construct the branches endpoint URL for the repository
    branches_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/refs/branches'

    # Set the authentication credentials
    auth = (USERNAME, APP_PASSWORD)

    # Send a GET request to retrieve the branches
    branches = get_branches(branches_url)
    totalCommitsByPerson = 0
    #print(branches[len(branches)-1])
    progressBar = tqdm(total=len(branches), desc="Progress", unit=' branches')
    totalInsertions = 0
    totalDeletions = 0
    biggestChange = (0,None)
    params = {'pagelen': 100, "fields": "+values.diffstat"}
    for branch in branches:
        branch_name = branch['name']

        # Construct the commits endpoint URL for the branch
        commits_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/commits/{branch_name}'

        # Send a GET request to retrieve the commits for the branch
        response = requests.get(commits_url, auth=auth,params=params)
        # Check if the request was successful (status code 200)
        first = False #debug variable
        if response.status_code == 200:
            commits_data = response.json()
            commits = commits_data['values']
            commits_by_person = []
            for commit in commits:
                if first:
                    print(commit)
                try:
                    #date = commit['date']
                    #workspace, repo_slug = extract_bitbucket_info(repository_url)
                    #commit_sha = commit['hash']
                    #insertions, deletions = get_commit_diffstat(workspace, repo_slug, commit_sha, auth)
                    if commit['author']['user']['display_name'] == userName:
                        commits_by_person.append(json.dumps(commit))
                        #shortHash = commit["hash"][:8]
                except Exception as e:
                    print(e)
                    print(commit)
                    print("This commit caused something to break! skipping over it.")
                    continue
                first = False
                #print((totalCommitsByPerson))
            progressBar.update(1)
            commits_by_person = list(set(commits_by_person))
            totalCommitsByPerson += len(commits_by_person)
        else:
            print("whoops error!", response.status_code)
    progressBar.close()
    return totalCommitsByPerson
    # Check if the request was successful (status code 200)'''
# Get the repository URL and person's username from the user
def process_branch(repository_owner, repository_name, branch_name, auth, userName):
    commits_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/commits/{branch_name}'
    params = {'page': 1, 'pagelen': 50}
    response = requests.get(commits_url, auth=auth, params=params)
    if response.status_code == 200:
        commits_data = response.json()
        commits = commits_data['values']
        commits_by_person = []
        for commit in commits:
            try:
                if commit['author']['user']['display_name'] == userName:
                    commits_by_person.append(json.dumps(commit))
            except Exception as e:
                print(e)
                print(commit)
                print("This commit caused something to break! skipping over it.")
                continue
        return len(set(commits_by_person))
    else:
        print("whoops error!", response.status_code)
        return 0

def get_total_commits_by_person(repository_url, USERNAME, userName):
    repository_owner = get_repo_owner(repository_url)
    repository_name = get_repo_name(repository_url)

    branches_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/refs/branches'
    auth = (USERNAME, APP_PASSWORD)
    branches = get_branches(branches_url)
    totalCommitsByPerson = 0
    progressBar = tqdm(total=len(branches), desc="Progress", unit=' branches')
    params = {'pagelen': 100}

    def worker(branch):
        count = process_branch(repository_owner, repository_name, branch['name'], auth, userName)
        progressBar.update(1)
        return count

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_branch = {executor.submit(worker, branch): branch for branch in branches}
        for future in concurrent.futures.as_completed(future_to_branch):
            totalCommitsByPerson += future.result()

    progressBar.close()
    return totalCommitsByPerson

person_username = input('Enter the person\'s username: ')
person_username = 'cactusoftheday'
userName = input('Enter the person\'s proper name: ')
userName = 'Matt Robichaud'

# Get the total number of commits by the person in the repository
total_commits = get_total_commits_by_person(repository_url, person_username, userName)
if total_commits is not None:
    print(f'Total commits by {userName}: {total_commits}')