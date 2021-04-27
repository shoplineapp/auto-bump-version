from git import Repo


class Tagging:

    def __init__(self, pipe):
        self.pipe = pipe

    def run(self):

        current_version = self.pipe.current_version()

        repo = Repo()
        git = repo.git
        git.config(f"http.{self.pipe.env['BITBUCKET_GIT_HTTP_ORIGIN']}.proxy", 'http://host.docker.internal:29418/')
        git.tag(a=current_version, m="auto tag version {} by bitbucket pipeline".format(current_version))
        git.push(tags=True)
