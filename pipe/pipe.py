import re

from bitbucket_pipes_toolkit import Pipe
from bump_version import BumpVersion
from tagging import Tagging

schema = {
    'REGEX': {'type': 'string', 'required': True},
    'FILE_PATH': {'type': 'string', 'required': True},
    'VERSION': {'type': 'string', 'required': False, 'default': ''},
    'BRANCH_NAME': {'type': 'string', 'required': False, 'default': 'feature/auto-bump-version'},
    'BITBUCKET_CLIENT_ID': {'type': 'string', 'required': True},
    'BITBUCKET_CLIENT_SECRET': {'type': 'string', 'required': True},
    'TAGGING': {'type': 'boolean', 'required': True, 'default': False},
    'DEBUG': {'type': 'boolean', 'required': False, 'default': False}
}


class AutoBumpVersion(Pipe):

    version_replacement = r'{{VERSION}}'

    def run(self):
        super().run()

        if self.get_variable('TAGGING'):
            Tagging(self).run()
        else:
            BumpVersion(self).run()

    def regex(self):
        regex = self.get_variable('REGEX')

        if self.version_replacement not in regex:
            self.fail("no {} replacement in the variable".format(self.version_replacement))

        return re.sub(self.version_replacement, r'([\\d\\.]+)', regex)

    def current_version(self):
        with open(self.get_variable('FILE_PATH'), 'r') as f:
            content = f.read()

        return re.search(self.regex(), content)[1]


if __name__ == '__main__':
    pipe = AutoBumpVersion(schema=schema)
    pipe.run()
