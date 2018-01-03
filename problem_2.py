
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

def combinedlist(pattern, datalen, exportfile, sequenceColumn, addColumn):
    #calling the first function
    filegroup = openfiles()
    matchlist = []
    #Reading in the chosen csv file, selecting necessary columns, and adding it to a list
    for file in filegroup:
        new_df = pd.read_csv(file)
        new_df["File Name"] = os.path.split(file)[1]
        new_df = new_df[["File Name", sequenceColumn, addColumn]]
        matchlist.append(new_df)
    #Return peptide sequences that doesn't match the regex pattern
    for df1 in matchlist:
        df1 = df1.loc[0:datalen]
    final_df = df1[~df1.Sequence.str.contains(pattern)]
    final_df.to_csv(exportfile, encoding='utf-8', index=False)
    return final_df


# In[ ]:

#(regex pattern, number of rows with data minus 2, name of the peptide sequence column, name of the protein group accessions column)
#pattern for HLA-A11 is r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'
#pattern for HLA-A24 is r'\b.[YF]\w+[LFI]\b'
combinedlist(r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b', 2565, "C:/Users/Sujatha/Desktop/example 2.csv", "Sequence", "Protein Group Accessions")


# In[ ]:



