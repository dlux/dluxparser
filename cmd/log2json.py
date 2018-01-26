import logging
import sys
from cliff import command


class LOG2JSON(command.Command):
 
    def take_action(self, parsed_args):
        '''Main log2json command excecution'''
        print("Under Construction")

    def get_parser(self, prog_name):
        '''The parameters that parser takes in'''
        parser = super(LOG2JSON, self).get_parser(prog_name)
        parser.add_argument('-i', '--input-files',
                    dest='_input',
                    help='The input custom log file(s) to convert into JSON.')
        return parser

    def get_description(self):
        return ("Implementation of a parser to convert custom log file with free-form key-pairs into JSON.")

    log = logging.getLogger(__name__)


if __name__ == "__main__":
    the_command = LOG2JSON()
    the_command.run()
