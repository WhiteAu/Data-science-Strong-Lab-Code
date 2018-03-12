import argparse
import collections
import logging
import os
import random

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
        sequence_dfs[key] = create_aggregate_sequence_dataframe(df, sequenceColumn, FILE_NAME_HEADER)

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


def aggregate_and_pivot_dataframe_by_secondary_column(frame, primary, secondary, agg_col_name='Occurrence'):
    '''
    Take some frame, and make a pivoted (long) table of the aggregate of the primary column by the secondary column

    :param frame:
    :param primary:
    :param secondary:
    :return:
    '''


    pivot_frame = frame.groupby([primary, secondary]) \
        .agg({primary: 'size'}) \
        .rename(columns={primary: agg_col_name}) \
        .reset_index() \
        .pivot(index=primary, columns=secondary, values=agg_col_name) \
        .fillna(0) \
        .reset_index()

    return pivot_frame

def make_empty_pivot_frame(frame, primary, secondary,):
    some_dumb_hash = str(random.randint(10000000, 99999999))
    hashed_zero_col_name = "".join(["zeroes", some_dumb_hash])
    dummy_frame = frame
    dummy_frame[hashed_zero_col_name] = 0
    pivot_frame = frame.pivot(index=primary, columns=secondary, values=hashed_zero_col_name)

    return pivot_frame

def make_columns_from_dict(dict, primary_col_name="primary", secondary_col_name="secondary"):
    '''
    given a dict of key : [values] return a dataframe representation of all key:value tuples

    :param dict:
    :param primary_col_name:
    :param secondary_col_name:
    :return:
    '''
    df = pd.DataFrame([(key, item) for key, val in dict.items() for item in val])

    df.rename(columns={0:primary_col_name, 1:secondary_col_name}, inplace=True)
    df.set_index(primary_col_name)

    return df

def create_aggregate_dataframe(frame, primary, columnName="Occurrence"):
    grouped_sequence_frame = frame.groupby([primary])
    grouped_sequence_frame = grouped_sequence_frame.agg({primary: 'size'}) \
                                                   .rename(columns={primary: columnName}) \
                                                   .reset_index()

    return grouped_sequence_frame

def create_aggregate_sequence_dataframe(frame : pd.DataFrame, sequenceColumn, addColumn, *args, **kwargs) -> pd.DataFrame:

    grouped_sequence_frame = create_aggregate_dataframe(frame, sequenceColumn, columnName='Occurrence')


    agg_frame = aggregate_and_pivot_dataframe_by_secondary_column(frame, sequenceColumn, addColumn, agg_col_name='Occurrence')

    final_frame = pd.merge(grouped_sequence_frame, agg_frame, on=sequenceColumn, how='left')

    return final_frame

def make_full_occurrence_dataframe(frame, seq_to_regex_dict, pattern_list, sequenceColumn, *args, **kwargs):
    '''
    guarantee that no-appearance columns occur in a dataframe
    :return:
    '''
    dummy_shell_dict = {seq: pattern_list for seq in seq_to_regex_dict.keys()}
    pre_pivot_columns = make_columns_from_dict(dummy_shell_dict,
                                               primary_col_name=sequenceColumn,
                                               secondary_col_name="Pattern")

    occurence_columns = make_columns_from_dict(seq_to_regex_dict,
                                               primary_col_name=sequenceColumn,
                                               secondary_col_name="Pattern")

    aggregated_occurrence_df = create_aggregate_dataframe(occurence_columns, sequenceColumn, columnName='Occurrence')
    pivoted_df = make_empty_pivot_frame(pre_pivot_columns, sequenceColumn, "Pattern")

    # populate the shell dataframe with occurence
    for key, patterns in seq_to_regex_dict.items():
        for pattern in patterns:
            pivoted_df.loc[key, pattern] = 1

    final_frame = pd.merge(aggregated_occurrence_df, pivoted_df.reset_index(), on=sequenceColumn, how='left')

    return final_frame


def openfiles():
    root = Tk()
    files = filedialog.askopenfilenames(parent=root, title='Select a file and click open')
    filepath = root.tk.splitlist(files)
    return filepath

def make_file_referenced_df_from_csv(filename, sequenceColumn, *args, **kwargs):
    column_list = [FILE_NAME_HEADER, sequenceColumn]
    if "addColumn" in kwargs.keys():
        column_list.append(kwargs['addColumn'])
    new_df = pd.read_csv(filename)
    new_df[FILE_NAME_HEADER] = os.path.split(filename)[1]
    new_df = new_df[column_list]

    return new_df

def create_anchor_match_dataframes(pattern_list, input_dir, sequenceColumn, *args, **kwargs):
    #calling the first function
    #filegroup = openfiles()
    filelist = return_filetype_list(input_dir, filetype=".csv")
    matchlist = {}
    logger.info("returned filegroup was {}".format(filelist))
    #Reading in the chosen csv file, selecting necessary columns, and adding it to a list
    for file in filelist:
        logger.info("returned file was {}".format(file))
        filename = os.path.split(file)[1]
        logger.info("split filename was {}".format(filename))
        matchlist[filename] = make_file_referenced_df_from_csv(file, sequenceColumn, *args, **kwargs)
    #Return peptide sequences that doesn't match the regex pattern
    all_list = []
    some_list = []
    none_list = []
    for filename, df in matchlist.items():
        all, some, none_df = create_match_dataframes(pattern_list, df, sequenceColumn)
        all[FILE_NAME_HEADER] = filename
        some[FILE_NAME_HEADER] = filename
        none_df[FILE_NAME_HEADER] = filename

        all_list.append(all)
        some_list.append(some)
        none_list.append(none_df)

    all_composite = pd.concat(all_list)
    some_composite = pd.concat(some_list)
    none_composite = pd.concat(none_list)

    return all_composite, some_composite, none_composite

def create_match_dataframes(pattern_list, df, sequenceColumn, all_criteria="pattern"):
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

    all_match_sequences = {sequence:values  for sequence, values in some_match_sequences.items()
                           if values == match_against}

    all_df = df[df[sequenceColumn].isin(all_match_sequences.keys())]
    if not all_df.empty:
        all_df = make_full_occurrence_dataframe(all_df, all_match_sequences, pattern_list, sequenceColumn)
    some_df = df[df[sequenceColumn].isin(some_match_sequences.keys())]
    if not some_df.empty:
        some_df = make_full_occurrence_dataframe(some_df, some_match_sequences, pattern_list, sequenceColumn)
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
    print("the collapsed dataframe head: {}".format(collapsed_frame.head))

    write_dataframe_to_csv(collapsed_frame, exportfile)


def write_sieved_dataframe_to_csv(dataframe, outputpath, filename):
    sieved_filename = "".join("sieved_", filename )

    exportfile = os.path.join(outputpath, sieved_filename)
    write_dataframe_to_csv(dataframe, exportfile)

def write_dataframe_to_csv_with_path(dataframe, path, filename):
    exportfile = os.path.join(path, filename)
    return write_dataframe_to_csv(dataframe, exportfile)

def write_dataframe_to_csv(dataframe, filename):
    if not filename.endswith(".csv"):
        filename = "".join([filename, ".csv"])
    logger.info("writing csv output to file: {}".format(filename))
    dataframe.to_csv(filename, encoding='utf-8', index=False)