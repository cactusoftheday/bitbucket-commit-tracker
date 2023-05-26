
import requests
from urllib.parse import urlparse

# Set your Bitbucket username and app password/token
USERNAME = 'cactusoftheday' # change this to your username
APP_PASSWORD = ''

if(len(APP_PASSWORD) <= 3):
    with(open('file.txt','r')) as file:
        content = file.read() # read app password if app password is empty

APP_PASSWORD = content
print(APP_PASSWORD)

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

# Get the repository URL from the user
repository_url = "https://bitbucket.org/deeptrekker/dt_bweb_crawler_control_app"

def get_total_commits_by_person(repository_url, USERNAME):
    repository_owner = get_repo_owner(repository_url)
    repository_name = get_repo_name(repository_url)

    # Construct the branches endpoint URL for the repository
    branches_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/refs/branches'

    # Set the authentication credentials
    auth = (USERNAME, APP_PASSWORD)

    # Send a GET request to retrieve the branches
    response = requests.get(branches_url, auth=auth)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        branches_data = response.json()
        branches = branches_data['values']

        total_commits_by_person = 0
        # i = 0
        # Iterate over each branch
        print(branches)
        for branch in branches:
            branch_name = branch['name']

            # Construct the commits endpoint URL for the branch
            commits_url = f'{BASE_URL}/repositories/{repository_owner}/{repository_name}/commits?branch={branch_name}'

            # Send a GET request to retrieve the commits for the branch
            response = requests.get(commits_url, auth=auth)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                commits_data = response.json()
                commits = commits_data['values']

                # Filter the commits by the person's username
                commits_by_person = [commit for commit in commits if 'user' in commit['author'] and commit['author']['user']['display_name'] == "Isaac Huang"] # change name to actual name
                #print(commits_by_person[i])
                # Get the number of commits by the person in the branch
                total_commits_by_person += len(commits_by_person)
            # i = i + 1
        return total_commits_by_person
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None

# Get the repository URL and person's username from the user

person_username = input('Enter the person\'s username: ')

# Get the total number of commits by the person in the repository
total_commits = get_total_commits_by_person(repository_url, person_username)
if total_commits is not None:
    print(f'Total commits by {person_username}: {total_commits}')