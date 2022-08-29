import json
import requests


class Bitbucket:
    
    def __init__(self, client_id, client_secret):
        self.client_secret = client_secret
        self.client_id = client_id

    def get_access_token(self):
        response = requests.post(
            url="https://bitbucket.org/site/oauth2/access_token",
            data={
                "grant_type": "client_credentials"
            },
            auth=(self.client_id, self.client_secret))

        if response.status_code != 200:
            raise Exception('invalid Bitbucket credential: ' + str(response.content))

        return response.json()['access_token']

    def create_pull_request(self, source_branch, target_branch, repo):
        
        url = f"https://api.bitbucket.org/2.0/repositories/{repo}/pullrequests"
        data = {
            'title': source_branch,
            'state': 'OPEN',
            'open': True,
            'closed': False,
            'source': {
                'branch': {
                    'name': source_branch
                }
            },
            'destination': {
                'branch': {
                    'name': target_branch
                }
            }
        }

        header = {
            "Authorization": "Bearer " + self.get_access_token()
        }

        response = requests.post(url, json=data, headers=header)
        content = json.loads(response.content)

        if content['type'] == 'error':
            return False
        else:
            return f"https://bitbucket.org/{repo}/pull-requests/{content['id']}"
