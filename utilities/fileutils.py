import logging
import os

import pandas as pd

from tkinter import filedialog, Tk
from typing import List


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

FILE_NAME_HEADER = "File Name"

def return_filetype_list(folderpath, filetype=".csv"):
    '''
    Returns a list of all files that match a given filetype

    :param folderpath: the absolute path to the folder to check
    :param filetype: the file suffix to check and return. Defaults to .csv
    :return: a list of filename strings
    '''
    filelist = []
    #directory = os.fsencode(folderpath)

    #Adding all the csv files from a folder into a list
    for file in os.listdir(folderpath):
        #filename = os.fsdecode(file)
        if file.endswith(filetype):
            filelist.append(file)
    return filelist


def matchlist(folderpath, exportfile, sequenceColumn, addColumn):
    '''

    :param folderpath: path to the directory containing the csv's to aggregate
    :param exportfile: the absolute path to the file to export aggregate dataframe to as a csv
    :param sequenceColumn: the name of the sequence column
    :param addColumn: the name of the column to aggregate
    :return: a copy of the aggregate dataframe
    '''
    #calling the first function
    filelist = return_filetype_list(folderpath, filetype=".csv")
    new_df = []
    #Reads in the content of the csv files from the list and adds the content into a new list.
    for file in filelist:
        df1 = pd.read_csv(file)
        new_df.append(df1)
    #Merging the dataframes together and adding the occurences of each peptide.
    final_df = create_aggregate_dataframe(new_df, sequenceColumn, addColumn)
    #Exporting the final dataframe back into a csv file.
    write_dataframe_to_csv(final_df, exportfile)


    return final_df

def create_aggregate_dataframe(frames : List[pd.DataFrame], sequenceColumn, addColumn, *args, **kwargs) -> pd.DataFrame:
    concat_frames = pd.concat(frames)
    grouped_sequence_frame = concat_frames.groupby([sequenceColumn])
    grouped_sequence_frame = grouped_sequence_frame.agg({sequenceColumn: 'size'})\
                                                   .rename(columns={sequenceColumn: 'Occurrence'})\
                                                   .reset_index()



    agg_frame = pd.concat(frames).groupby([sequenceColumn, addColumn]) \
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

def combinedlist(pattern, sequenceColumn, addColumn):
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
        sieved_df = df[~df.Sequence.str.contains(pattern)]

        sieved_dataframes[filename] = sieved_df

    return sieved_dataframes

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
    logger.info("writing csv output to file: {}".format(filename))
    dataframe.to_csv(filename, encoding='utf-8', index=False)