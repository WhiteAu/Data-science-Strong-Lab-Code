import os

import pandas as pd

from tkinter import filedialog, Tk
from typing import List

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
    agg_frame = pd.concat(frames).groupby([sequenceColumn, addColumn]) \
                                 .agg({sequenceColumn: 'size'}) \
                                 .rename(columns={sequenceColumn: 'Occurence'}) \
                                 .reset_index() \
                                 .sort_values(by=['Occurence', addColumn], ascending=[False, True]) \
                                 .reset_index(drop=True)
    return agg_frame

def openfiles():
    root = Tk()
    files = filedialog.askopenfilenames(parent=root, title='Select a file and click open')
    filepath = root.tk.splitlist(files)
    return filepath

def make_file_referenced_df_from_csv(filename, sequenceColumn, addColumn):
    new_df = pd.read_csv(filename)
    new_df["File Name 1"] = os.path.split(filename)[1]
    new_df = new_df[["File Name 1", sequenceColumn, addColumn]]

    return new_df

def combinedlist(pattern, exportpath, sequenceColumn, addColumn):
    #calling the first function
    filegroup = openfiles()
    matchlist = {}
    #Reading in the chosen csv file, selecting necessary columns, and adding it to a list
    for file in filegroup:
        filename = os.path.split(file)[1]
        matchlist[filename] = make_file_referenced_df_from_csv(filename, sequenceColumn, addColumn)
    #Return peptide sequences that doesn't match the regex pattern
    sieved_dataframes = {}
    for filename, df in matchlist.iteritems:
        sieved_df = df[~df.Sequence.str.contains(pattern)]

        write_sieved_dataframe_to_csv(sieved_dataframes, exportpath, filename)

        sieved_dataframes[filename] = sieved_df
    return sieved_dataframes


def write_sieved_dataframe_to_csv(dataframe, outputpath, filename):
    sieved_filename = "".join("sieved_", filename )

    exportfile = os.path.join(outputpath, sieved_filename)
    write_dataframe_to_csv(dataframe, exportfile)

def write_dataframe_to_csv(dataframe, filename):
    dataframe.to_csv(filename, encoding='utf-8', index=False)