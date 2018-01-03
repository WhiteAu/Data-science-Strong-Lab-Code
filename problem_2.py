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


cmd_arg_parser = argparse.ArgumentParser("problem_2: screens a given directories' CSV files for compliance with a given regular expression")
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


#(regex pattern, number of rows with data minus 2, name of the peptide sequence column, name of the protein group accessions column)
#pattern for HLA-A11 is r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'
#pattern for HLA-A24 is r'\b.[YF]\w+[LFI]\b'
sieved_dataframes = fileutils.combinedlist(r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b',  "Sequence", "Protein Group Accessions")
logger.info("returned dataframes were: {}".format(sieved_dataframes))

if exe_mode == ExecutionType.PRODUCTION:
    logger.info("writing output to {}".format(output_path))
    fileutils.write_sieved_dataframe_dict_to_csv(sieved_dataframes, output_path, "problem_2_example")



