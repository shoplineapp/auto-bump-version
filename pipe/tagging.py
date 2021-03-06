import re

from git import Repo
from bitbucket_pipes_toolkit import get_logger
from packaging import version


class Tagging:

    def __init__(self, pipe):
        self.pipe = pipe
        self.logger = get_logger()

    def run(self):
        git = Repo().git

        commit_id = re.search(r'commit (?P<commit_id>\w+)', git.log("-1", "--no-merges"))['commit_id']
        self.logger.info('commit id: {}'.format(commit_id))

        file_changes = git.diff_tree("--no-commit-id", "--name-only", '-r', commit_id).split("\n")
        self.logger.info('file changes: {}'.format(file_changes))

        if self.pipe.get_variable('FILE_PATH') in file_changes:

            max_tag = "0.0.0"
            tags = git.tag().split('\n')

            self.logger.info('tags: {}'.format(tags))

            if tags:
                tags = [t for t in tags if re.match(r"^\d+\.\d+\.\d+$", t)]
                tags.sort(key=lambda s: list(map(int, s.split('.'))))
                max_tag = tags[-1]

            current_version = self.pipe.current_version()
            self.logger.info(f"max tag: {max_tag}")
            self.logger.info(f"current version: {current_version}")
            if version.parse(current_version) > version.parse(max_tag):
                git.config(f"http.{self.pipe.env['BITBUCKET_GIT_HTTP_ORIGIN']}.proxy", 'http://host.docker.internal:29418/')
                git.tag(a=current_version, m="auto tag version {} by bitbucket pipeline".format(current_version))
                git.push(tags=True)
