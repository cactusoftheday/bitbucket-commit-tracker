
import requests
from urllib.parse import urlparse
from tqdm import tqdm

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
#print(repository_url)

def get_branches(branches_url):
    allBranches = []
    page = 1
    pageSize = 200
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

def get_total_commits_by_person(repository_url, USERNAME, userName):
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
    progressBar = tqdm(total=len(branches), desc="Progress", unit='branch')
    for branch in branches:
        branch_name = branch['name']

        # Construct the commits endpoint URL for the branch
        commits_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/commits/{branch_name}'

        # Send a GET request to retrieve the commits for the branch
        response = requests.get(commits_url, auth=auth)

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
                    if commit['author']['user']['display_name'] == userName:
                        commits_by_person.append(commit)
                except:
                    print(commit)
                    print("This commit caused something to break! skipping over it.")
                    continue
                first = False
                #print((totalCommitsByPerson))
            progressBar.update(len(branches))
            totalCommitsByPerson += len(commits_by_person)
        else:
            print("whoops error!", response.status_code)
    progressBar.close()
    return totalCommitsByPerson
    # Check if the request was successful (status code 200)
# Get the repository URL and person's username from the user

person_username = input('Enter the person\'s username: ')
person_username = 'cactusoftheday'
userName = input('Enter the person\'s proper name: ')
userName = 'Isaac Huang'

# Get the total number of commits by the person in the repository
total_commits = get_total_commits_by_person(repository_url, person_username, userName)
if total_commits is not None:
    print(f'Total commits by {person_username}: {total_commits}')