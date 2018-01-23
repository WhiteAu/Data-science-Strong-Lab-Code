import argparse
import collections
import logging
import os

import pandas as pd

from tkinter import filedialog, Tk
from typing import List


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

FILE_NAME_HEADER = "File Name"

def make_cmd_arg_parser(description, configparser):


    cmd_arg_parser = argparse.ArgumentParser(description)
    cmd_arg_parser.add_argument('-t', action="store_true", default=False,
                                dest="is_test",
                                help="Set mode to test. There will be additional debug information and no computationally expensive functions will be run.")
    cmd_arg_parser.add_argument('--folder',
                                action="store",
                                dest="file_dir",
                                help="Load CSV's from supplied directory.  by default this defaults to {}".format(
                                    configparser['DEFAULT']['input']))
    cmd_arg_parser.add_argument('--output',
                                action="store",
                                dest="output_dir",
                                help="Target file and location to write results out to. by default this defaults to {}".format(
                                    configparser['DEFAULT']['output']))

    return cmd_arg_parser


def return_filetype_list(folderpath, filetype=".csv"):
    '''
    Returns a list of all files that match a given filetype

    :param folderpath: the absolute path to the folder to check
    :param filetype: the file suffikey to check and return. Defaults to .csv
    :return: a list of filename strings
    '''
    filelist = []
    #directory = os.fsencode(folderpath)

    #Adding all the csv files from a folder into a list
    for file in os.listdir(folderpath):
        #filename = os.fsdecode(file)
        if file.endswith(filetype):
            filelist.append(os.path.sep.join([folderpath, file]))
    return filelist


def aggregate_sequence_occurence_by_length(folderpath, sequenceColumn, *args, **kwargs):
    '''

    :param folderpath: path to the directory containing the csv's to aggregate

    :param sequenceColumn: the name of the sequence column
    :return: a copy of the aggregate dataframe
    '''
    #calling the first function
    filelist = return_filetype_list(folderpath, filetype=".csv")
    aggregate_df = []
    #Reads in the content of the csv files from the list and adds the content into a new list.
    for file in filelist:
        df1 = pd.read_csv(file)
        filename = os.path.split(file)[1]
        if "abs_path" in kwargs.keys():
            filename = file
        df1[FILE_NAME_HEADER] = filename
        aggregate_df.append(df1)

    aggregate_df = pd.concat(aggregate_df)
    #re-split dataframe by sequence length
    sequence_dfs = split_df_by_col_length(aggregate_df, sequenceColumn)

    # Merging the dataframes together and adding the occurences of each peptide.
    for key, df in sequence_dfs.items():
        sequence_dfs[key] = create_aggregate_dataframe(df, sequenceColumn, FILE_NAME_HEADER)

    return sequence_dfs

def split_df_by_col_length(df, column_to_split):
    length_col ="_".join([column_to_split, 'length'])
    logger.info("{} called with column: {}".format(__name__, column_to_split))
    logger.info("Length Column is {}".format(length_col))
    logger.info("split column head: {}".format(df[column_to_split].head()))
    df[length_col] = df[column_to_split].str.len()

    split_dfs = split(df, length_col)

    return split_dfs


def split(df, group):
    gb = df.groupby(group)
    #return [gb.get_group(x) for x in gb.groups]
    return {key: gb.get_group(key) for key in gb.groups}



def create_aggregate_dataframe(frame : pd.DataFrame, sequenceColumn, addColumn, *args, **kwargs) -> pd.DataFrame:

    grouped_sequence_frame = frame.groupby([sequenceColumn])
    grouped_sequence_frame = grouped_sequence_frame.agg({sequenceColumn: 'size'})\
                                                   .rename(columns={sequenceColumn: 'Occurrence'})\
                                                   .reset_index()



    agg_frame = frame.groupby([sequenceColumn, addColumn]) \
                                 .agg({sequenceColumn: 'size'}) \
                                 .rename(columns={sequenceColumn: 'Occurrence'}) \
                                 .reset_index() \
                                 .pivot(index=sequenceColumn, columns=addColumn, values='Occurrence') \
                                 .fillna(0) \
                                 .reset_index()


    final_frame = pd.merge(grouped_sequence_frame, agg_frame, on=sequenceColumn, how='left')

    print(final_frame)
    return final_frame

def openfiles():
    root = Tk()
    files = filedialog.askopenfilenames(parent=root, title='Select a file and click open')
    filepath = root.tk.splitlist(files)
    return filepath

def make_file_referenced_df_from_csv(filename, sequenceColumn, addColumn):
    new_df = pd.read_csv(filename)
    new_df[FILE_NAME_HEADER] = os.path.split(filename)[1]
    new_df = new_df[[FILE_NAME_HEADER, sequenceColumn, addColumn]]

    return new_df

def create_anchor_match_dataframes(pattern_list, sequenceColumn, addColumn):
    #calling the first function
    filegroup = openfiles()
    matchlist = {}
    logger.info("returned filegroup was {}".format(filegroup))
    #Reading in the chosen csv file, selecting necessary columns, and adding it to a list
    for file in filegroup:
        logger.info("returned file was {}".format(file))
        filename = os.path.split(file)[1]
        logger.info("split filename was {}".format(filename))
        matchlist[filename] = make_file_referenced_df_from_csv(file, sequenceColumn, addColumn)
    #Return peptide sequences that doesn't match the regex pattern
    sieved_dataframes = {}
    for filename, df in matchlist.items():
        all, some, none_df = create_match_dataframe(pattern_list, df, sequenceColumn)
        all[FILE_NAME_HEADER] = filename
        some[FILE_NAME_HEADER] = filename
        none_df[FILE_NAME_HEADER] = filename


    return sieved_dataframes

def create_match_dataframe(pattern_list, df, sequenceColumn, all_criteria="pattern"):
    sequenceList = set(df[sequenceColumn].unique())
    some_match_sequences = collections.defaultdict(set)
    none_match_sequences = set(df[sequenceColumn].unique())

    for pattern in pattern_list:
        sieved_df = df[df[sequenceColumn].str.contains(pattern)]
        for sequence in sieved_df[sequenceColumn].unique():
            some_match_sequences[sequence].add(pattern)
            none_match_sequences.discard(sequence)

    match_against = set(pattern_list)
    if all_criteria == "sequence":
        match_against = sequenceList

    all_match_sequences = [sequence for sequence, values in some_match_sequences.items()
                           if values == match_against]

    all_df = df[df[sequenceColumn].isin(all_match_sequences)]
    some_df = df[df[sequenceColumn].isin(some_match_sequences.keys())]
    none_df = df[df[sequenceColumn].isin(none_match_sequences)]


    return all_df, some_df, none_df


def write_sieved_dataframe_dict_to_csv(df_dict, outputpath, filename):
    sieved_filename = "".join(["sieved_compilation_", filename])

    exportfile = os.path.join(outputpath, sieved_filename)

    collapsed_frame = pd.DataFrame()
    for name, df in df_dict.items():
        named_df = df
        named_df[FILE_NAME_HEADER] = name
        collapsed_frame.append(named_df)

    write_dataframe_to_csv(collapsed_frame, exportfile)


def write_sieved_dataframe_to_csv(dataframe, outputpath, filename):
    sieved_filename = "".join("sieved_", filename )

    exportfile = os.path.join(outputpath, sieved_filename)
    write_dataframe_to_csv(dataframe, exportfile)


def write_dataframe_to_csv(dataframe, filename):
    if not filename.endswith(".csv"):
        filename = "".join([filename, ".csv"])
    logger.info("writing csv output to file: {}".format(filename))
    dataframe.to_csv(filename, encoding='utf-8', index=False)