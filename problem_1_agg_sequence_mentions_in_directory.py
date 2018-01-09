
# -*- coding: utf-8 -*-

import argparse
import configparser
import logging
import os

from utilities.execution_modes import ExecutionType
import utilities.fileutils as fileutils


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
cmd_arg_parser = fileutils.make_cmd_arg_parser("problem_1: aggregates occurrences of Sequence/Accessions and outputs as a csv to the specified folder.", config)

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



logger.info("matchlist called with file directory: {} output file: {} sequenceColumn: {}, addColumn: {}".format(file_directory,
                                                                                                                    output_path,
                                                                                                                    config["DATA DESCRIPTOR"]["sequenceColumn"],
                                                                                                                    config["DATA DESCRIPTOR"]["addColumn"]))

# (folder path, output file path, name of the peptide sequence column, name of the protein group accessions column)
matched_dataframes_by_length = fileutils.aggregate_sequence_occurence_by_length(file_directory, config["DATA DESCRIPTOR"]["sequenceColumn"], config["DATA DESCRIPTOR"]["addColumn"])

#Exporting the final dataframes back into a csv file.
for sequence_length, matched_dataframe in matched_dataframes_by_length.items():
    exportfile = os.path.join(output_path, "sequence_length_{}_matched_csv_list".format(sequence_length))
    print("exportfile was {}".format(exportfile))
    if exe_mode == ExecutionType.PRODUCTION:
        fileutils.write_dataframe_to_csv(matched_dataframe, exportfile)


