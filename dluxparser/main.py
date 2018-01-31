import logging
import sys

from cliff import app
from cliff import commandmanager
from pbr import version as vr


class ParserMainApp(app.App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(ParserMainApp, self).__init__(
            description='Dlux CLI to parse a file into a different format.',
            version=vr.VersionInfo('dluxparser').version_string_with_vcs(),
            command_manager=commandmanager.CommandManager('dluxparser.cm'),
            deferred_help=True,
            )

    def initialize_app(self, argv):
        self.log.debug('Initializing parser application')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('Dluxparser got an error: %s', err)


def main(argv=sys.argv[1:]):
    parser_app = ParserMainApp()
    return parser_app.run(argv)


if __name__ == '__main__':
    sys.exit(main())
