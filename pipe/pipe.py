import json
import re
import requests

from bitbucket import Bitbucket
from git import Repo
from bitbucket_pipes_toolkit import Pipe, get_logger

logger = get_logger()

schema = {
    'REGEX': {'type': 'string', 'required': True},
    'FILE_PATH': {'type': 'string', 'required': True},
    'VERSION': {'type': 'string', 'required': False, 'default': ''},
    'BRANCH_NAME': {'type': 'string', 'required': False, 'default': 'feature/auto-bump-version'},
    'BITBUCKET_CLIENT_ID': {'type': 'string', 'required': True},
    'BITBUCKET_CLIENT_SECRET': {'type': 'string', 'required': True},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}
}


class AutoBumpVersion(Pipe):
    def run(self):
        super().run()

        self.__replace_content()
        self.__git_push()
        url = self.__send_pull_request()

        if url:
            print('PR url: {}'.format(url))
        else:
            self.fail('Pull request create error')

    @staticmethod
    def __replace_content_with_version(content, regex, version):
        replacement = re.sub(re.search(regex, content)[1], version, re.search(regex, content)[0])
        return re.sub(regex, replacement, content)

    @staticmethod
    def __bump_version(current_version):
        major, minor, patch = list(map(int, current_version.split('.')))
        minor += 1
        return f"{major}.{minor}.{patch}"

    def __replace_content(self):
        regex = self.get_variable('REGEX')
        regex = re.sub(r'{{VERSION}}', r'([\\d\\.]+)', regex)

        with open(self.get_variable('FILE_PATH'), 'r') as f:
            content = f.read()

        version = self.get_variable('VERSION')
        if not re.search(r'\d+\.\d+\.\d+', version):
            current_version = re.search(regex, content)[1]
            version = self.__bump_version(current_version)

        content = self.__replace_content_with_version(content, regex, version)

        with open(self.get_variable('FILE_PATH'), 'w') as f:
            f.write(content)

    def __git_push(self):

        repo = Repo()
        git = repo.git
        git.config(f"http.{self.env['BITBUCKET_GIT_HTTP_ORIGIN']}.proxy", 'http://host.docker.internal:29418/')
        git.checkout('HEAD', b=self.get_variable('BRANCH_NAME'))
        git.add(self.get_variable('FILE_PATH'))
        git.commit(message="bump version")
        origin = repo.remotes.origin
        origin.push(self.get_variable('BRANCH_NAME'))

    def __send_pull_request(self):
        bitbucket = Bitbucket(self.get_variable('BITBUCKET_CLIENT_ID'), self.get_variable('BITBUCKET_CLIENT_SECRET'))
        return bitbucket.create_pull_request(self.get_variable('BRANCH_NAME'), self.env['BITBUCKET_REPO_FULL_NAME'])


if __name__ == '__main__':
    pipe = AutoBumpVersion(schema=schema)
    pipe.run()
