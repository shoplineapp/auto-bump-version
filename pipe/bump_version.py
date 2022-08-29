import re
import os
from bitbucket import Bitbucket
from git import Repo


class BumpVersion:

    def __init__(self, pipe):
        self.pipe = pipe
        self.pr_target_branch = self.pipe.env["BITBUCKET_BRANCH"]
        self.pr_source_branch = self.pipe.get_variable('BRANCH_NAME')

    def run(self):
        self.__replace_content()
        self.__git_push()
        url = self.__send_pull_request()

        if url:
            print('PR url: {}'.format(url))
        else:
            self.pipe.fail('Pull request create error')

    @staticmethod
    def __replace_content_with_version(content, regex, version):
        replacement = re.sub(re.search(regex, content)[1], version, re.search(regex, content)[0])
        return re.sub(regex, replacement, content)

    @staticmethod
    def __bump_version(current_version, is_patch):
        major, minor, patch = list(map(int, current_version.split('.')))
        if is_patch:
            patch += 1
        else:
            patch = 0
            minor += 1

        return f"{major}.{minor}.{patch}"

    def __replace_content(self):

        self.pipe.log_info("IS_PATCH is: " + str(self.pipe.get_variable('IS_PATCH')))
        version = self.pipe.get_variable('VERSION')
        if not re.search(r'\d+\.\d+\.\d+', version):
            version = self.__bump_version(self.pipe.current_version(), self.pipe.get_variable('IS_PATCH'))

        with open(self.pipe.get_variable('FILE_PATH'), 'r') as f:
            content = f.read()

        content = self.__replace_content_with_version(content, self.pipe.regex(), version)
        with open(self.pipe.get_variable('FILE_PATH'), 'w') as f:
            f.write(content)

    def __git_push(self):

        repo = Repo()
        git = repo.git
        git.config("--global", "safe.directory", os.getcwd())
        git.config(f"http.{self.pipe.env['BITBUCKET_GIT_HTTP_ORIGIN']}.proxy", 'http://host.docker.internal:29418/')
        git.checkout('HEAD', b=self.pipe.get_variable('BRANCH_NAME'))
        git.add(self.pipe.get_variable('FILE_PATH'))
        git.commit(message="bump version")
        origin = repo.remotes.origin
        origin.push(self.pipe.get_variable('BRANCH_NAME'))

    def __send_pull_request(self):
        try:
            bitbucket = Bitbucket(
                self.pipe.get_variable('BITBUCKET_CLIENT_ID'), self.pipe.get_variable('BITBUCKET_CLIENT_SECRET'))
            self.pipe.log_info("bitbucket result: " + str(bitbucket))

            self.pipe.log_info("Pull Request Creating: " + self.pr_source_branch + " -> " + self.pr_target_branch)
            return bitbucket.create_pull_request(
                self.pr_source_branch, self.pr_target_branch, self.pipe.env['BITBUCKET_REPO_FULL_NAME'])
        except KeyError:
            self.pipe.fail('missing variable BITBUCKET_CLIENT_ID or BITBUCKET_CLIENT_SECRET')
