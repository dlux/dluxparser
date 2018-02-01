"""
txt2json is a parser to transform the information on a text or log file into
Json fomat.
Expected file sintaxis:

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
}

Arguments
---------

* ``--root-dir, -d``: The parent directory where files to be parsed live.
  Folder can contain sub-folders.
* ``--output-dir, -o``: The directory where parsed files will live.
 
Usage
-----

txt2json takes a parent folder which may contain sub-folders and
transforms all available files into json format as described above.

"""
import argparse
import os
import re
import time
import shutil
import json

from cliff import command
from datetime import datetime
import pdb


class ArgumentParser():
    def __init__(self, args=None, parser=None):
        desc = ('txt2json transform a text or log file to json. '
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
            default =  'ParsedFiles',
            help="The directory where parsed file(s) will be saved.")

        parser.set_defaults(func='parse')

    def parse_args(self, args):
        return self.parser.parse_args(args=args)

class Text2Json():

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
        '''Main function to parse input txt files into json'''
        # Get and process files
        count = 0
        for root, _, files in os.walk(self.args.root_dir):
            for filename in files:
                origin = os.path.join(root, filename)
                output = os.path.join(self.args.output_dir, filename + '.json')
                count = count + 1

                # Parse data
                data = self._parse(origin)
                pdb.set_trace()
                self._write_to_file(output, json.dumps(data, indent=4))

        print("Found %i files." % count)

    ##### Internal methods - To be used by the subcommands #####
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

    def _trim_plus_underscore(self, mystr):
        mystr = mystr.strip()
        mystr = re.sub(r"\s+", '_', mystr)
        return mystr

    def _parse(self, name):
        content = self._get_content(name) + '\0'
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
        json_content={}
        feature = key = value = ''
        nElement = state = 0
        multiplier = 1

        for char_ in content:
            if state == 0:
                # Initial State
                if char_.isdigit():
                    feature = self._trim_plus_underscore(feature)
                    nElement = int(char_)
                    state = 1
                elif char_ == '=':
                    aux = re.split('\\s', feature.strip(), 1)
                    feature = self._trim_plus_underscore(aux[0])
                    tmp = feature.lower()
                    if tmp in self.SPECIAL_WORDS:
                        # Special case for front panel and power supply
                        aux = re.split('\\s', aux[1], 1)
                        feature = (feature + '_' + 
                                   self._trim_plus_underscore(aux[0]))
                    key = self._trim_plus_underscore(aux[1])
                    state = 2
                else:
                    feature = feature + char_
            elif state == 1:
                # Digit found in state 0.
                if char_ == '=':
                    key = self._trim_plus_underscore(key)
                    # Handle case of no explicit key defined
                    key = 'part' if not key else key
                    state = 2
                elif char_.isdigit():
                    # Handle numbers of more than one digit
                    if not key:
                        multiplier = multiplier*10
                        nElement = (int(char_) * multiplier) + nElement
                elif char_ == '\n' or char_ == '\0':
                    # If line is truncated, ignore feature and restart state
                    feature = key = value = ''
                    nElement = state = 0
                    nBy = 1
                else:
                    key = key + char_
            elif state == 2:
                # Last stage will process value assigned to feature key
                # If value available, feature is processed into json
                # If no value, feature is ignored
                if char_ == '\n' or char_ == '\0':
                    pdb.set_trace()
                    value = self._trim_plus_underscore(value)
                    if value:
                        # Process JSON
                        jc = json_content.get(feature)
                        if jc:
                            if len(jc) >= nElement:
                                jc[nElement - 1][key] = value
                            else:
                                while len(jc) 
                                jc.append({key: value})
                        else:
                            json_content[feature] = [{key: value}]

                    # Return to initial state
                    feature = key = value = ''
                    nElement = state = 0
                    nBy=1
                else:
                    value = value + char_
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
class CliffTxt2Json(command.Command):
    '''Parse text or log files into json format'''

    def get_parser(self, prog_name):
        parser = super(CliffTxt2Json, self).get_parser(prog_name)
        ArgumentParser(None, parser)
        return parser

    def take_action(self, parsed_args):
        main(parsed_args)


def main(opts=None):
    # Parse arguments
    if opts is None:
        opts = ArgumentParser().parse_args(opts)
    # Create commands instance
    parse_txt2json = Text2Json(opts)
    # Run parsed subcommand function
    raise SystemExit(getattr(parse_txt2json, opts.func)())


if __name__ == "__main__":
    start_time = time.time()
    main()
    println("--- %s seconds ---" % (time.time() - start_time))

