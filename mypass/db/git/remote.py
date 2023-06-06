import requests
import json

from . import GitRepo


class GitHubRepo:

    def __init__(self, local_repo: GitRepo, name: str):
        self.local = local_repo
        self.name = name

    @staticmethod
    def create(token: str, repo_name='MyPass', repo_desc='My local hosted password manager.'):
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {
            'name': repo_name,
            'description': repo_desc,
            'auto_init': False  # Set this to True if you want to initialize the repository with a README file
        }

        api_url = 'https://api.github.com/user/repos'

        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        if response.status_code == 201:
            print('GitHub repository created successfully!')
        else:
            print('Error creating GitHub repository:', response.json())

    def push(self, remote_name='origin'):
        if remote_name not in [remote.name for remote in self.local.repo.remotes]:
            self.local.repo.create_remote(remote_name, f'https://github.com/{self.local.user_name}/{self.name}.git')
        self.local.repo.remotes[remote_name].push()
