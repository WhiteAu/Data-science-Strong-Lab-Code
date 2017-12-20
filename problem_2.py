
# coding: utf-8

# In[ ]:

import pandas as pd
import os
from tkinter import filedialog
from tkinter import *


# In[ ]:

#Used to set up and open the file path.
def openfiles():
    root = Tk()
    files = filedialog.askopenfilenames(parent=root, title='Select a file and click open')
    filepath = root.tk.splitlist(files)
    return filepath


# In[ ]:

def combinedlist(pattern, exportfile, sequenceColumn, addColumn):
    #calling the first function
    filegroup = openfiles()
    matchlist = {}
    #Reading in the chosen csv file, selecting necessary columns, and adding it to a list
    for file in filegroup:
        new_df = pd.read_csv(file)
        filename = os.path.split(file)[1]
        new_df["File Name 1"] = filename
        new_df = new_df[["File Name 1", sequenceColumn, addColumn]]
        matchlist[filename] = new_df
    #Return peptide sequences that doesn't match the regex pattern
    sieved_dataframes = {}
    for filename, df in matchlist.iteritems:
        sieved_df = df[~df.Sequence.str.contains(pattern)]

        write_sieved_dataframe_to_csv(sieved_dataframes, exportfile, filename)

        sieved_dataframes[filename] = sieved_df
    return sieved_dataframes


def write_sieved_dataframe_to_csv(dataframe, outputpath, filename):
    sieved_filename = "".join("sieved_", filename )


    dataframe.to_csv(exportfile, encoding='utf-8', index=False)



# In[ ]:

#(regex pattern, number of rows with data minus 2, name of the peptide sequence column, name of the protein group accessions column)
#pattern for HLA-A11 is r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'
#pattern for HLA-A24 is r'\b.[YF]\w+[LFI]\b'
combinedlist(r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b', 2565, "C:/Users/Sujatha/Desktop/example 2.csv", "Sequence", "Protein Group Accessions")


# In[ ]:



