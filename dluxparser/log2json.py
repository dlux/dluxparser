"""
log2json is a parser to transform the information on a custom
text or custom log file into Json format.

Expected file sintaxis:

    FeatureF = free form text value
    FeatureF = free form text value
    FeatureX free form text key A = free form text value
    FeatureX free form text key B = free form text value
    FeatureY a_number free form text key A = free form text value
    FeatureY a_number free form text key B = free form text value
    FeatureY a_number+1 free form text key A = free form text value
    FeatureY a_number+2 free form text key A = free form text value
    FeatureZ a_number+1 = free form text value
    FeatureZ a_number+2 = free form text value

Expected outcome:

{
  "id": "<fileName>",
  "FeatureX": [
     {
      "free_form_text_key_A": "free_form_text_value"
      "free_form_text_key_B": "free_form_text_value"
     }
  ],
  "FeatureY": [
    {
        "free_form_text_key_A": "free_form_text_value"
        "free_form_text_key_B": "free_form_text_value"
    },
    {
        "free_form_text_key_A": "free_form_text_value"
        "free_form_text_key_B": "free_form_text_value"
    }
  ],
  "FeatureZ": [
    {"part":"free_form_text_value"},
    {"part":"free_form_text_value"}
  ]
  "FeatureF": [
    {"part":"free_form_text_value"},
    {"part":"free_form_text_value"}
  ]
}

Arguments
---------

* ``--root-dir, -d``: The parent directory where files to be parsed live.
  Folder can contain sub-folders.
* ``--output-dir, -o``: The directory where parsed files will live.

Usage
-----

log2json takes a parent folder which may contain sub-folders and
transforms all available files - notice expected input sintaxis above -
into json format.
"""
import argparse
import os
import re
import shutil
import json

from cliff import command
from datetime import datetime


class ArgumentParser():
    def __init__(self, args=None, parser=None):
        desc = ('log2json transform a text or log file to json. '
                'See expected input sintaxis on the documentation')
        if not parser:
            parser = argparse.ArgumentParser(description=desc)
        self.parser = parser

        # Add arguments
        parser.add_argument(
            "-d", "--root-dir", metavar="<dir_name>",
            action='store', required=True, dest='root_dir', type=str,
            help="The root directory where text file(s) are stored.")
        parser.add_argument(
            "-o", "--output-dir", metavar="<dir_name>",
            action='store', required=False, dest='output_dir', type=str,
            default='ParsedFiles',
            help="The directory where parsed file(s) will be saved.")

        parser.set_defaults(func='parse')

    def parse_args(self, args):
        return self.parser.parse_args(args=args)


class Log2Json():

    SPECIAL_WORDS = ('front', 'power')

    def __init__(self, args):
        self.args = args
        if not os.path.isdir(args.root_dir):
            raise Exception("You must provide a valid root folder.")

        output_dir = args.output_dir
        if os.path.abspath(args.root_dir) == os.path.abspath(output_dir):
            raise Exception("Input and Output folders must be different.")

        # Create output folder if exists back it up
        if os.path.exists(output_dir):
            shutil.move(output_dir, output_dir + '.bk.' +
                        datetime.now().isoformat())
        os.makedirs(output_dir)

    def parse(self):
        '''Main function to parse input log files into json'''
        # Get and process files
        count = 0
        for root, _, files in os.walk(self.args.root_dir):
            for filename in files:
                origin = os.path.join(root, filename)
                fname = os.path.splitext(filename)[0]
                output = os.path.join(self.args.output_dir, fname + '.json')
                count = count + 1

                # Parse data
                print("%i. Parsing file: %s" % (count, origin))
                data = self._parse(origin)
                self._write_to_file(output, json.dumps(data, indent=4))

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
        '''Locate a string patern within a file or stream.'''
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

    def _trim_plus_underscore(self, mystr):
        mystr = mystr.strip()
        mystr = re.sub(r"\s+", '_', mystr)
        return mystr

    def _parse(self, name):
        content = self._get_content(name)
        # Make sure last line is parsed correctly
        if content[len(content) - 1] != '\n':
            content = content + '\n'
        # States:
        # 0. Initial
        #   Collect any character until a digit or '=' appears.
        #   If digit:  Collected chars became a feature. Move to state 1.
        #   If '=' char: First word became a feature, the rest became a key.
        #                Move to state 2.
        # 1. Collect any character until a '=' appears.
        #    Collected chars became a key. Move to state 2.
        # 2. Collect any character until a '\n' or EOF appears.
        #    Collected chars became a value.
        #    Fix feature json output.
        #    Move to state 0.
        # Note: all blank spaces are replaced with underscores.
        json_content = {}
        nElement = feature = key = value = ''
        state = 0

        for char_ in content:
            # Verify it is not garbage if so, ignore
            try:
                char_.decode('utf-8')
            except e:
                continue

            if state == 0:
                # Initial State
                if char_.isdigit():
                    feature = self._trim_plus_underscore(feature)
                    nElement = char_
                    state = 1
                elif char_ == '=':
                    aux = re.split('\\s', feature.strip(), 1)
                    feature = self._trim_plus_underscore(aux[0])
                    tmp = feature.lower()
                    if tmp in self.SPECIAL_WORDS and len(aux) > 1:
                        # Special case for front panel and power supply
                        aux = re.split('\\s', aux[1], 1)
                        feature = (feature + '_' +
                                   self._trim_plus_underscore(aux[0]))
                    if len(aux) > 1:
                        key = self._trim_plus_underscore(aux[1])
                    state = 2
                else:
                    feature = feature + char_
            elif state == 1:
                # State - when digit was found in state 0.
                if char_ == '=':
                    key = self._trim_plus_underscore(key)
                    state = 2
                elif char_.isdigit():
                    # Handle numbers of more than one digit
                    if not key:
                        nElement = nElement + char_
                elif char_ == '\n':
                    # If line is truncated, ignore feature and restart state
                    nElement = feature = key = value = ''
                    state = 0
                else:
                    key = key + char_
            elif state == 2:
                # Last stage -  will process value assigned to feature key
                # If value available, feature is processed into json
                # If no value, feature is ignored
                if char_ == '\n':
                    value = self._trim_plus_underscore(value)
                    if value:
                        # Process JSON
                        if not json_content.get(feature):
                            json_content[feature] = []
                        jcf = json_content.get(feature)

                        # Insert {key, value} on nElement index
                        # Or insert value on nElement index if no key
                        index = int(nElement) if nElement.isdigit() else 1

                        while index + 1 > len(jcf):
                            jcf.append({})

                        if key:
                            jcf[index][key] = value
                        else:
                            jcf[index] = value

                    # Return to initial state
                    nElement = feature = key = value = ''
                    state = 0
                else:
                    value = value + char_

        for key in json_content.keys():
            # Remove empty dictionaries
            json_content[key] = filter(None, json_content[key])
            if len(json_content[key]) == 1:
                # if list has only one element remove the list
                json_content[key] = json_content[key][0]

        return json_content

    def _remove_lines_r(self, name, regex):
        '''Remove the lines that match a given regex.'''
        content = self._get_content(name)
        count = len(content.split('\n'))
        for r in regex:
            content = re.sub('.*'+r+'.*\n', '', content)
        count = count - len(content.split('\n'))
        print ('Removed %i lines.' % count)
        return content


# CLIFF CLI CREATOR CLASS
class CliffLog2Json(command.Command):
    '''Parse text or log files into json format'''

    def get_parser(self, prog_name):
        parser = super(CliffLog2Json, self).get_parser(prog_name)
        ArgumentParser(None, parser)
        return parser

    def take_action(self, parsed_args):
        main(parsed_args)


def main(opts=None):
    # Parse arguments
    if opts is None:
        opts = ArgumentParser().parse_args(opts)
    # Create commands instance
    parse2json = Log2Json(opts)
    # Run parsed subcommand function
    raise SystemExit(getattr(parse2json, opts.func)())


if __name__ == "__main__":
    main()
