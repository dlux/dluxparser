"""
shrinker is a CLI providing few commands to shrink the size of a text or log
file.

----------------
Common Arguments
----------------

* ``--root-dir, -d``: The parent directory where files to be parsed live.
  Folder can contain sub-folders.
* ``--output-dir, -o``: The directory where parsed files will live.
* ``--inline``: The parsed files will replace the original ones.

Available sub-commands:

---------------------
extract-section sub-command:
---------------------

Extracts a section of a custom log by removing anything
before a given initSectionStr and removing anything after
a given endSectionStr.
Removes additional lines from the top and bottom of the output.

Arguments
~~~~~~~~~

* ``--initstr, -i``: All lines before (and including) initstr regex will be
  removed from outcome file.
* ``--endstr, -e``: All lines after (and including) endstr regex will be
  removed from outcome file.
* ``--remove-from-top, -t``: (Optional) Removes t number of lines from the
  top of the outcome file.
* ``--remove-from-bottom, -b``: (Optional) Removes b number of lines from the
  bottom of the outcome file.
* ``--to-lower, -l: All text within the files are turned into lower case.``:

Usage
~~~~~

extract-section takes a parent folder which may contain sub-folders and
text file(s) to be parsed.
At the same level of parent folder, shrinklog creates ParsedFiles folder to
hold all the files parsed.

---------------------
remove-section sub-command:
---------------------

Removes a section of a custom log by removing anything
between a given initSectionStr and a given endSectionStr.

Arguments
~~~~~~~~~

* ``--initstr, -i``: All lines before (and including) initstr regex will be
  removed from outcome file.
* ``--endstr, -e``: All lines after (and including) endstr regex will be
  removed from outcome file.
* ``--to-lower, -l: All text within the files are turned into lower case.``:

Usage
~~~~~

remove-section takes a parent folder which may contain sub-folders and
text file(s) to be parsed.
At the same level of parent folder, shrinklog creates ParsedFiles folder to
hold all the files parsed.

----------------------------
remove-from-top sub-command:
----------------------------

Removes N number of lines from the top of the file.

Arguments
~~~~~~~~~

* ``--number, -n``: The number of lines to be removed.

Usage
~~~~~

remove-from-top takes an int argument for the number of lines to
remove from the top.

-------------------------------
remove-from-bottom sub-command:
-------------------------------

Removes N number of lines from the bottom of the file.

Arguments
~~~~~~~~~

* ``--number, -n``: The number of lines to be removed.

Usage
~~~~~

remove-from-bottom takes an int argument for the number of lines to
remove from the bottom.

------------------------------
remove-from-regex sub-command:
------------------------------

Removes the lines which matches the given regex(es)

Arguments
~~~~~~~~~

* ``--regex, -r``: The regex(es) to remove from the file..

Usage
~~~~~

remove-from-regex takes a regex or several regexes to delete the lines that
matches the given regex(es).

------------------------------
to-lower:
------------------------------

Makes all the lines in the file lower case.

Usage
~~~~~

to-lower takes a directory and make all files content lower case.
"""
import argparse
import os
import re
import time
import shutil

from cliff import command
from datetime import datetime


class ArgumentParser():
    def __init__(self, args=None, parser=None):
        desc = 'shrinker provide sub-commands to shrink a text or log file.'
        usage = ('shrinker [-h] <SUB-COMMAND> ...\n\n'
                 'To see help on a specific sub-command, do:\n'
                 'shrinker <SUB-COMMAND> --help\n\n')
        if not parser:
            parser = argparse.ArgumentParser(
                description=desc,
                usage=usage
            )
        self.parser = parser

        subparsers = parser.add_subparsers(title='Sub-Commands',
                                           help='\nAvailable sub-commands.\n')

        # Add arguments that goes with all sub-commands
        common_args = self.add_common_args()

        # Add sub-command parsers:
        self.add_extract_section_parser(subparsers, [common_args])
        self.add_remove_section_parser(subparsers, [common_args])
        self.add_remove_from(subparsers, [common_args])
        self.add_remove_from(subparsers, [common_args], 'bottom')
        self.add_remove_from_regex(subparsers, [common_args])
        _lower = subparsers.add_parser('to-lower', parents=[common_args],
                                       help='Make file(s) content lower case.')
        _lower.set_defaults(func='to_lower')

    def parse_args(self, args):
        return self.parser.parse_args(args=args)

    def add_common_args(self):
        '''Common arguments to all subcommands of shrinker cli.'''
        # Arguments that go with all subcommands.
        shared_args = argparse.ArgumentParser(add_help=False)
        shared_args.add_argument(
            "-d", "--root-dir", metavar="<dir_name>",
            action='store', required=True, dest='root_dir', type=str,
            help="The root directory where text file(s) are stored.")
        group = shared_args.add_mutually_exclusive_group()
        group.add_argument(
            "-o", "--output-dir", metavar="<dir_name>",
            action='store', required=False, dest='output_dir', type=str,
            default='ParsedFiles',
            help="The directory where parsed file(s) will be saved.")
        group.add_argument(
            "--inline", action='store_true',
            required=False,
            help='Asume parsed file must replace existing original one.'
        )

        # Return common args
        return shared_args

    def add_extract_section_parser(self, subparsers, parents=None):
        '''Arguments for extract-section subcommand.'''
        desc = "subcommand extracts a portion of a custom text or log file."
        parser_sl = subparsers.add_parser('extract-section', parents=parents,
                                          help=desc)
        parser_sl.add_argument(
            "-i", "--initstr", metavar="<regex>",
            action='store', required=True, type=str,
            help="String where program start extracting data.")

        parser_sl.add_argument(
            "-e", "--endstr", metavar="<regex>",
            action='store', required=True, type=str,
            help="String where program stop extracting data.")

        parser_sl.add_argument(
            "-t", "--remove-from-top", metavar="N",
            action='store', dest="remove_top", default=0, type=int,
            help="Additional lines to remove from the top.")

        parser_sl.add_argument(
            "-b", "--remove-from-bottom", metavar="N",
            action='store', dest="remove_bottom", default=0, type=int,
            help="Additional lines to remove from the bottom.")

        parser_sl.add_argument(
            "-l", "--to-lower", required=False,
            action='store_true', dest="to_lower",
            help="Will make file(s) content lower case.")

        parser_sl.set_defaults(func="shrink", func2='extract')

    def add_remove_section_parser(self, subparsers, parents=None):
        '''Arguments for remove-section subcommand.'''
        desc = "subcommand removes a portion of a custom text or log file."
        parser_sl = subparsers.add_parser('remove-section', parents=parents,
                                          help=desc)
        parser_sl.add_argument(
            "-i", "--initstr", metavar="<regex>",
            action='store', required=True, type=str,
            help="String where program start extracting data.")

        parser_sl.add_argument(
            "-e", "--endstr", metavar="<regex>",
            action='store', required=True, type=str,
            help="String where program stop extracting data.")

        parser_sl.add_argument(
            "-l", "--to-lower", required=False,
            action='store_true', dest="to_lower",
            help="Will make file(s) content lower case.")

        parser_sl.set_defaults(func="shrink", func2='remove')

    def add_remove_from(self, subparsers, parents=None, pos='top'):
        '''Arguments for remove-from-top and remove-from-bottom subcommands.'''
        desc = ("subcommand remove N lines from the %s of the file." % pos)
        parser_rf = subparsers.add_parser(('remove-from-%s' % pos),
                                          parents=parents, help=desc)
        parser_rf.add_argument(
            "-n", "--number", metavar="<number>",
            action='store', required=True, type=int,
            help="Number of lines to delete.")

        parser_rf.set_defaults(func='remove_from', func2=pos)

    def add_remove_from_regex(self, subparsers, parents=None):
        '''Arguments for remove-from-regex subcommand.'''
        desc = "Remove lines from a file, when it matches given regex(es)."
        parser_rf = subparsers.add_parser('remove-from-regex',
                                          parents=parents,
                                          help=desc)
        parser_rf.add_argument(
            "-r", "--regex", metavar="<regex>",
            action='store', required=True,
            type=str, nargs='*',
            help="Regex(ex) to look for on the files to parse.")

        parser_rf.set_defaults(func='remove_from', func2='regex')


class Shrinker():
    def __init__(self, args):
        self.args = args
        if not os.path.isdir(args.root_dir):
            raise Exception("You must provide a valid root folder.")

        output_dir = args.output_dir
        if args.inline:
            output_dir = '/tmp/ParsedFiles'+datetime.now().isoformat()
            self.args.output_dir = output_dir
        if os.path.abspath(args.root_dir) == os.path.abspath(output_dir):
            raise Exception("Input and Output folders must be different.")

        # Create output folder if exists rename it
        if os.path.exists(output_dir):
            shutil.move(output_dir, output_dir + '.bk.' +
                        datetime.now().isoformat())
        os.makedirs(output_dir)

    def shrink(self):
        '''Main function for extract and remove section subcommands'''
        # Get and process files
        count = 0
        for root, _, files in os.walk(self.args.root_dir):
            for filename in files:
                origin = os.path.join(root, filename)
                output = os.path.join(self.args.output_dir, filename)
                count = count + 1
                print("%i. Parsing File: %s" % (count, origin))
                data = self._get_content(origin)
                # Remove return carriage characters
                data = ''.join(data.split('\r'))
                # Extract a section of the file
                if self.args.func2 == 'extract':
                    # Remove content before initStr
                    data = self._remove_before(data, self.args.initstr)
                    # Remove N lines from the top
                    data = self._remove_lines(data, self.args.remove_top + 1)
                    # Remove content after endStr
                    data = self._remove_after(data, self.args.endstr)
                    # Remove N lines from the bottom
                    data = self._remove_lines(data, self.args.remove_bottom,
                                              False)
                # Remove a portion of the file
                elif self.args.func2 == 'remove':
                    data = self._remove_between(data, self.args.initstr,
                                                self.args.endstr)

                if self.args.to_lower:
                    data = data.lower()

                self._write_to_file(output, data)

        # Handle inline parameter
        self._ifinline()
        print("Found %i files." % count)

    def remove_from(self):
        '''Main function for remove-from-[top|bottom|regex] subcommands.'''
        # Get and process files
        count = 0
        for root, _, files in os.walk(self.args.root_dir):
            for filename in files:
                origin = os.path.join(root, filename)
                output = os.path.join(self.args.output_dir, filename)
                count = count + 1
                print("%i. Parsing File: %s" % (count, origin))
                if self.args.func2 == 'top':
                    data = self._remove_lines(origin, self.args.number)
                elif self.args.func2 == 'bottom':
                    data = self._remove_lines(origin, self.args.number, False)
                elif self.args.func2 == 'regex':
                    data = self._remove_lines_r(origin, self.args.regex)

                self._write_to_file(output, data)

        # Handle inline parameter
        self._ifinline()
        print("Found %i files." % count)

    def to_lower(self):
        '''Main function to make file(s) content lower case.'''
        # Get and process files
        count = 0
        for root, _, files in os.walk(self.args.root_dir):
            for filename in files:
                origin = os.path.join(root, filename)
                output = os.path.join(self.args.output_dir, filename)
                count = count + 1
                data = self._get_content(origin).lower()

                self._write_to_file(output, data)

        # Handle inline parameter
        self._ifinline()
        print("Found %i files." % count)

    # #### Internal methods - To be used by the subcommands #####
    def _get_content(self, name):
        '''Get the content from a file or from stream.'''
        if os.path.exists(name):
            the_file = open(name, 'r')
            content = the_file.read()
            the_file.close()
        else:
            content = name
        return content

    def _locate_match(self, name, pattern):
        '''Locate a string patern whithin a file or stream.'''
        content = self._get_content(name)
        return re.split(pattern, content, 1)

    def _write_to_file(self, file_name, plain_content):
        '''Writes a given text into a file.'''
        if not plain_content:
            print ("<-- Error: Empty processed data for file %s" % file_name)
            plain_content = " "

        the_file = open(file_name, "w")
        the_file.write(plain_content)
        the_file.close()

    def _ifinline(self):
        '''Replaces the original folder with parsed output when inline
           parameter is passed'''
        # If parsed file should replace original files
        if self.args.inline:
            shutil.rmtree(self.args.root_dir)
            shutil.move(self.args.output_dir, self.args.root_dir)

    def _remove_before(self, name, initstr):
        '''Remove lines from the top of a file or stream until
           given string regex matches'''
        content = self._locate_match(name, initstr)
        if len(content) > 1:
            return content[1]
        else:
            return content[0]

    def _remove_between(self, name, initstr, endstr):
        '''Remove the lines that are between two regexes'''
        content = self._locate_match(name, initstr)

        if len(content) == 1:
            print ("<-- Error: Initial string not found  %s" % initstr)
            return content[0]

        beforeInitRegex = content[0]
        content = self._locate_match(content[1], endstr)

        if len(content) == 1:
            print ("<-- Error: End string not found  %s" % endstr)
            return (beforeInitRegex + content[0])

        return beforeInitRegex + content[1]

    def _remove_after(self, name, endstr):
        '''Remove the lines from a file or stream after a
           given string regex matches'''
        content = self._locate_match(name, endstr)
        return content[0]

    def _remove_lines(self, name, num, top=True):
        '''Remove num lines from the top or bottom of a given file or stream'''
        content = self._get_content(name)
        # Return content if nothing to remove
        if num == 0:
            return content

        if top:
            return re.split('\n', content, num)[num]
        else:
            content = content[::-1]
            content = re.split('\n', content, num)[num]
            return content[::-1]

    def _remove_lines_r(self, name, regex):
        '''Remove the lines that match a given regex.'''
        # Add a \n to make sure last line is parsed properly
        content = self._get_content(name) + '\n'
        count = len(content.split('\n'))
        for r in regex:
            content = re.sub('.*'+r+'.*\n', '', content)
        count = count - len(content.split('\n'))
        print ('Removed %i lines.' % count)
        return content[:-1]


# CLIFF CLI CREATOR CLASS
class CliffShrinker(command.Command):
    '''Shrinker commands'''

    def get_parser(self, prog_name):
        parser = super(CliffShrinker, self).get_parser(prog_name)
        ArgumentParser(None, parser)
        return parser

    def take_action(self, parsed_args):
        main(parsed_args)


def main(opts=None):
    # Parse arguments
    if opts is None:
        opts = ArgumentParser().parse_args(opts)
    # Create commands instance
    shrinker = Shrinker(opts)
    # Run parsed subcommand function
    raise SystemExit(getattr(shrinker, opts.func)())


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))


# MFG 1/25/2018 parameters::
# shrinker shrinklog
#     --root-dir original
#     --initstr "Tx64 display.cfg file.*\n[*]+"
#     --endstr "[*][*][*]+" (real_lenght is 25 starts)
#     --remove-from-top 2
#     --remove-from-bottom 2
#     --to-lower
# 2/5/2018
# shrinker remove-section --initstr "[*][*][*]+"
#     --endstr "Tx64 display.cfg file.*\n[*]+"
# shrinker extract-section --initstr "dlux"
#     --endstr "[*][*][*]+" --remove-from-bottom 2 --to-lower
# shrinker remove-from-regex
#     -r "number of" "present" "count" "empty" "[.][.][.]+" "display.cfg"
#     --root-dir parsed1 --inline
