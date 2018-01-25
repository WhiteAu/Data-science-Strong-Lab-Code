# coding: utf-8

import argparse
import configparser
import logging
import os

from utilities.execution_modes import ExecutionType
import utilities.fileutils as fileutils



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
cmd_arg_parser = fileutils.make_cmd_arg_parser("problem_2: screens a given directories' CSV files for compliance with a given regular expression", config)

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


#(regex pattern, number of rows with data minus 2, name of the peptide sequence column, name of the protein group accessions column)
#pattern for HLA-A11 is r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'
#pattern for HLA-A24 is r'\b.[YF]\w+[LFI]\b'
all, some, none = fileutils.create_anchor_match_dataframes([r'^[FL]',r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'],
                                                             file_directory,
                                                             config["DATA DESCRIPTOR"]["sequenceColumn"],
                                                             config["DATA DESCRIPTOR"]["addColumn"])
logger.info("returned dataframes were: all{}\nsome {}\nnone {}".format(all, some, none))


if exe_mode == ExecutionType.PRODUCTION:
    logger.info("writing output to {}".format(output_path))
    fileutils.write_dataframe_to_csv_with_path(all, output_path, "sieved_compilation_problem_2_all")
    fileutils.write_dataframe_to_csv_with_path(some, output_path, "sieved_compilation_problem_2_some")
    fileutils.write_dataframe_to_csv_with_path(none, output_path, "sieved_compilation_problem_2_none")




