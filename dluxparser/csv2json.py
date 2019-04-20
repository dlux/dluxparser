'''
csv2json is a parser to transform a csv file into json

Arguments:
- ``--file | -f``: The csv file name to be transformed
- ``--delimiter | -d``: The delimiter of csv file, defaults to ','
'''

import argparse
import csv
import json
import os

from cliff import command
from datetime import datetime


class ArgumentParser():
    def __init__(self, args=None, parser=None):
        desc = ('csv2json transform a csv file to json. '
                'See expected input sintaxis on the documentation')
        if not parser:
            parser = argparse.ArgumentParser(description=desc)
        self.parser = parser

        # Add arguments
        parser.add_argument(
            "-f", "--file", metavar="<file_name>",
            action='store', required=True, dest='csvfile', type=str,
            help="The directory where file is stored.")
        parser.add_argument(
            "-d", "--delimiter", metavar="<delimiter>",
            action='store', required=False, dest='delimiter', type=str,
            default=',',
            help="Delimiter of csv file - defaults to ','")
        parser.set_defaults(func='parse')

    def parse_args(self, args):
        return self.parser.parse_args(args=args)


class Csv2Json(object):
    '''This class is to transform a csv input file into a json file'''

    def __init__(self, args):
        self.args = args
        if not os.path.isfile(args.csvfile):
            raise Exception("You must provide a valid file.")
        self.csvfile = os.path.abspath(args.csvfile)
        self.jsonfile = os.path.splitext(args.csvfile)[0] + '.json'
        self.delimiter = args.delimiter

    def parse(self):
        '''Main function to parse input csv file into json'''
        with open(self.csvfile, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            out = json.dumps([row for row in reader])
            with open(self.jsonfile, 'w+') as jsonfile:
                jsonfile.write(out)
        return self.jsonfile


# CLIFF CLI CREATOR CLASS - GENERIC
class CliffCsv2Json(command.Command):
    '''Parse csv files into json format'''

    def get_parser(self, prog_name):
        parser = super(CliffCsv2Json, self).get_parser(prog_name)
        ArgumentParser(None, parser)
        return parser

    def take_action(self, parsed_args):
        main(parsed_args)


def main(opts=None):
    # Parse arguments
    if opts is None:
        opts = ArgumentParser().parse_args(opts)
    # Create commands instance
    parse2json = Csv2Json(opts)
    # Run parsed subcommand function
    raise SystemExit(getattr(parse2json, opts.func)())


if __name__ == "__main__":
    main()
