
# coding: utf-8

# In[ ]:

import pandas as pd
import os


# In[ ]:

def csv_files(folderpath):
    filelist = []
    directory = os.fsencode(folderpath)
    os.chdir(directory)
    #Adding all the csv files from a folder into a list
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".csv"):
            filelist.append(filename)
    return filelist


# In[ ]:

def matchlist(folderpath, exportfile, sequenceColumn, addColumn):
    #calling the first function
    filelist = csv_files(folderpath)
    new_df = []
    #Reads in the content of the csv files from the list and adds the content into a new list.
    for file in filelist:
        df1 = pd.read_csv(file)
        new_df.append(df1)
    #Merging the dataframes together and adding the occurences of each peptide.
    final_df = pd.concat(new_df).groupby([sequenceColumn,addColumn])            .agg({sequenceColumn:'size'})            .rename(columns={sequenceColumn:'Occurence'})            .reset_index()            .sort_values(by=['Occurence',addColumn], ascending=[False,True])
    #Exporting the final dataframe back into a csv file.
    final_df.to_csv(exportfile, encoding='utf-8', index=False)
    return final_df


# In[ ]:

#(folder path, output file path, name of the peptide sequence column, name of the protein group accessions column)
matchlist("C:/Users/Sujatha/Desktop/HLA_A11", "C:/Users/Sujatha/Desktop/example 2.csv", "Sequence", "Protein Group Accessions")

