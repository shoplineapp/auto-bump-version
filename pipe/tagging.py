import re

from git import Repo


class Tagging:

    def __init__(self, pipe):
        self.pipe = pipe

    def run(self):
        repo = Repo()
        git = repo.git

        commit_id = re.search(r'commit (?P<commit_id>\w+)', git.log("-1"))['commit_id']
        file_changes = git.diff_tree("--no-commit-id", "--name-only", '-r', commit_id).split("\n")

        if self.pipe.get_variable('FILE_PATH') in file_changes:
            current_version = self.pipe.current_version()
            git.config(f"http.{self.pipe.env['BITBUCKET_GIT_HTTP_ORIGIN']}.proxy", 'http://host.docker.internal:29418/')
            git.tag(a=current_version, m="auto tag version {} by bitbucket pipeline".format(current_version))
            git.push(tags=True)
