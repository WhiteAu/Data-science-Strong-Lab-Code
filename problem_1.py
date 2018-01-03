
# -*- coding: utf-8 -*-

import argparse
import configparser
import logging
import os

from utilities.execution_modes import ExecutionType
from utilities.fileutils import matchlist


X_FEATURE = 'x'

formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

logger = logging.getLogger()
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)

logger.setLevel(logging.DEBUG)

EXECUTION_TYPE_TO_LOGGER_LEVEL = {
    ExecutionType.TEST : logging.DEBUG,
    ExecutionType.PRODUCTION : logging.DEBUG, #change to INFO when done
    }





config = configparser.ConfigParser()
configFilePath = 'config'
config.read(configFilePath)


cmd_arg_parser = argparse.ArgumentParser("problem_1: aggregates occurrences of Sequence/Accessions and outputs as a csv to the specified folder.")
cmd_arg_parser.add_argument('-t', action="store_true", default=False,
                            dest="is_test",
                            help="Set mode to test. There will be additional debug information and no computationally expensive functions will be run.")
cmd_arg_parser.add_argument('--folder',
                            action="store",
                            dest="file_dir",
                            help="Load CSV's from supplied directory.  by default this defaults to {}".format(config['DEFAULT']['input']))
cmd_arg_parser.add_argument('--output',
                            action="store",
                            dest="output_dir",
                            help="Target file and location to write results out to. by default this defaults to {}".format(config['DEFAULT']['output']))


cmd_args = cmd_arg_parser.parse_args()

if cmd_args.is_test == True:
    exe_mode = ExecutionType.TEST
else:
    exe_mode = ExecutionType.PRODUCTION

logger.setLevel(EXECUTION_TYPE_TO_LOGGER_LEVEL[exe_mode])

file_directory = config['DEFAULT']['input']
if cmd_args.file_dir != None:
    file_directory = cmd_args.file_dir
output_path = config['DEFAULT']['output']
if cmd_args.output_dir != None:
    output_path= cmd_args.output_dir


script_path = os.path.dirname(os.path.realpath(__file__))


if exe_mode == ExecutionType.PRODUCTION:

    logger.info("matchlist called with file directory: {} output file: {} sequenceColumn: {}, addColumn: {}".format(file_directory,
                                                                                                                    output_path,
                                                                                                                    config["DATA DESCRIPTOR"]["sequenceColumn"],
                                                                                                                    config["DATA DESCRIPTOR"]["addColumn"]))

    # (folder path, output file path, name of the peptide sequence column, name of the protein group accessions column)
    matchlist(file_directory, output_path, config["DATA DESCRIPTOR"]["sequenceColumn"],
              config["DATA DESCRIPTOR"]["addColumn"])

