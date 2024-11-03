import requests
import csv



GITHUB_TOKEN = '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'

def make_github_request(url):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'  # Tells GitHub we want data in version 3 format
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

import requests
import csv

def fetch_users_in_sydney():
    users = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/search/users?q=location:Sydney+followers:>100&page={page}')
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Error fetching users: {response.json().get('message', 'Unknown error')}")
            break
        
        data = response.json()
        
        # If there are no more users, break the loop
        if 'items' not in data or not data['items']:
            break
        
        for user in data['items']:
            # Fetch additional user details
            user_details = fetch_user_details(user['login'])
            if user_details:
                users.append(user_details)
        
        page += 1

    return users

import requests
import time

def fetch_user_details(username):
    response = requests.get(f'https://api.github.com/users/{username}')
    
    # Check for rate limiting
    if response.status_code == 403:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        wait_time = max(0, reset_time - int(time.time())) + 5  # Add a buffer time
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        return fetch_user_details(username)  # Retry after waiting

    if response.status_code != 200:
        print(f"Error fetching user details for {username}: {response.json().get('message', 'Unknown error')}")
        return None
    
    user_data = response.json()

    # Ensure company is not None before calling strip()
    company_name = user_data.get('company', '')
    if company_name:
        company_name = company_name.strip('@').upper()  # Clean company name
    else:
        company_name = ''

    return {
        'login': user_data.get('login', ''),
        'name': user_data.get('name', ''),
        'company': company_name,
        'location': user_data.get('location', ''),
        'email': user_data.get('email', ''),
        'hireable': user_data.get('hireable', ''),
        'bio': user_data.get('bio', ''),
        'public_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'following': user_data.get('following', 0),
        'created_at': user_data.get('created_at', ''),
    }


def save_users_to_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
    print(f"Saved {len(users)} users to users.csv")



def fetch_user_repositories(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=500"
    return make_github_request(url)

def extract_repository_info(repositories, username):
    repo_list = []
    for repo in repositories:
        repo_info = {
            'login': username,  # User's GitHub ID
            'full_name': repo.get('full_name', ''),
            'created_at': repo.get('created_at', ''),
            'stargazers_count': repo.get('stargazers_count', 0),
            'watchers_count': repo.get('watchers_count', 0),
            'language': repo.get('language', ''),
            'has_projects': repo.get('has_projects', False),
            'has_wiki': repo.get('has_wiki', False),
            # Handle the case where the license might be None
            'license_name': repo.get('license')['name'] if repo.get('license') else ''
        }
        repo_list.append(repo_info)
    return repo_list



def save_repositories_to_csv(repositories):
    with open('repositories.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'login', 'full_name', 'created_at', 'stargazers_count', 
            'watchers_count', 'language', 'has_projects', 
            'has_wiki', 'license_name'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()  # Write the header row
        for repo in repositories:
            writer.writerow(repo)  # Write repository data rows


if __name__ == "__main__":
    # Fetch users in Sydney with over 100 followers
    users = fetch_users_in_sydney()  # Updated to use the new fetch function
    
    if users:
        save_users_to_csv(users)  # Save the fetched user data to users.csv
        print(f"Saved {len(users)} users to users.csv")
        
        all_repositories = []
        for user in users:
            username = user['login']
            repositories = fetch_user_repositories(username)  # Ensure this function is defined
            if repositories:
                extracted_repos = extract_repository_info(repositories, username)  # Ensure this function is defined
                all_repositories.extend(extracted_repos)

        # Save all repositories data
        save_repositories_to_csv(all_repositories)  # Save the repository data
        print(f"Saved {len(all_repositories)} repositories to repositories.csv")



