from flask import Flask, render_template, request
import requests
from datetime import datetime
from urllib.parse import urljoin


app = Flask(__name__)


# GitHub API base URL
GITHUB_API_BASE_URL = "https://api.github.com/"


# Helper function to fetch followers
def get_followers(username):
    followers_url = urljoin(GITHUB_API_BASE_URL, f"users/{username}/followers")
    response = requests.get(followers_url)
    return response.json() if response.status_code == 200 else []


# Helper function to fetch following list
def get_following(username):
    following_url = urljoin(GITHUB_API_BASE_URL, f"users/{username}/following")
    response = requests.get(following_url)
    return response.json() if response.status_code == 200 else []


# Helper function to fetch GitHub repository information
def get_github_repos(username):
    # Construct user repos URL
    repos_url = urljoin(GITHUB_API_BASE_URL, f"users/{username}/repos")
    response = requests.get(repos_url)
    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            # Format updated_at field
            repo['updated_at'] = datetime.strptime(
                repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y-%m-%d %H:%M")

            # Fetch latest commit information
            commits_url = urljoin(
                GITHUB_API_BASE_URL,
                f"repos/{username}/{repo['name']}/commits")
            commit_response = requests.get(commits_url)
            if commit_response.status_code == 200:
                commits = commit_response.json()
                if commits:
                    latest_commit = commits[0]  # Get the most recent commit
                    repo['latest_commit'] = {
                        'sha': latest_commit['sha'],
                        'author': latest_commit['commit']['author']['name'],
                        'date': datetime.strptime(
                            latest_commit['commit']['author']['date'],
                            "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M"),
                        'message': latest_commit['commit']['message']
                    }
            else:
                repo['latest_commit'] = None
        return repos
    else:
        return None


@app.route('/github_user', methods=['GET', 'POST'])
def github_user():
    if request.method == 'POST':
        username = request.form['username']
        repos = get_github_repos(username)
        followers = get_followers(username)
        following = get_following(username)
        return render_template(
            'repos.html', repos=repos, username=username,
            followers=followers, following=following)
    return render_template('github_user.html')


if __name__ == '__main__':
    app.run(debug=True)
