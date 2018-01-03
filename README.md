# Data-science-Strong-Lab-Code

##Prior Documentation
Problem #1:
 The code will list out all the Peptides sequences, its corresponding “Protein Group Accessions”, and the number of times the peptide was listed within the folder. 
For example, if the peptide GQPLWLEH was listed 3 times within the folder of files the final data frame will have a row that would look like this:
Sequence	Protein Group Accessions	Occurrence 
GQPLWLEH	Q9P217	3

Note: The code will only read in the csv files within the folder. To save an excel file as a csv file, you must be on the proper sheet within the excel file, click save as, and save as a “CSV UTF-8 (Comma Delimited) (*.csv)”. 
To run: 
In the fourth line of code, when calling the function, there are 4 inputs needed within the parenthesis. Each input needs to be separated with a comma. 
First Input: The path to the folder placed in quotation marks.
Example:  
Second Input: The path to the csv file where the final data frame will be exported into, placed in quotation marks. The csv file should be blank and already exist somewhere on the computer.
Example:  
Third Input: The name of the column that includes all the peptide sequences. This is just in case the column name changes over time. In the data you gave us, the column name that had all the peptide sequences was named “Sequence”.
Example:  
Fourth Input: The name of the “Protein Group Accessions” column. Again, this is just in case the column name ever changes. In the data you gave us, the addition column that you wanted was named “Protein Group Accessions”.
Example:  
After all the inputs, the fourth/last line of code (where the function is being called) should look like this: 
 
After running the code, a data frame should be printed out and it should be exported into the blank csv file that was given. 





Problem #2:
 The code will list out all the Peptides sequences and its corresponding “Protein Group Accessions” only if it doesn’t match the anchor position constraints. 
To run: 
In the fourth/final line of code, when calling the function, there are 5 inputs needed within the parenthesis. Each input needs to be separated with a comma. 
First Input: The regular expressions pattern. The pattern is already written as a comment into the code, so it is easy to copy and paste.
Pattern for HLA-A11:        r'\b.[VIFY][MLFYIA]\w+[LIYVF].[KR]\b'
Pattern for HLA-A24:        r'\b.[YF]\w+[LFI]\b'
Example:   for HLA-A11
Second Input: The last line of data from the csv file minus 2. For example in this file, the last line of data is 2567 but because of the column name and the fact that the index starts at 0, we need to subtract 2 from that number to get 2565.
 
Example: “2565”
Third Input: The path to the csv file where the final data frame will be exported into, placed in quotation marks. The csv file should be blank and already exist somewhere on the computer.
Example:  
Fourth Input: The name of the column that includes all the peptide sequences. This is just in case the column name changes over time. In the data you gave us, the column name that had all the peptide sequences was named “Sequence”.
Example:  
Fifth Input: The name of the “Protein Group Accessions” column. Again, this is just in case the column name ever changes. In the data you gave us, the addition column that you wanted was named “Protein Group Accessions”.
Example:  
After all the inputs, the fourth/last line of code (where the function is being called) should look like this: 
 
Note: Make the input changes to the last line of code before running any of the lines of code. After the final line of code runs, a window should pop up on your screen asking for a file to be selected. Once the file is selected, the final data frame will appear and be export into the csv file from input 3. 

##Original Problem Statement
Certainly! We have developed a method to determine peptide/MHC targets presented by cell lines/transformed cells and (hopefully) primary tumors. We use an easily purifiable, soluble HLA/B2M dimer that is transduced into cells via a lentivirus cell expression platform. The HLA is purified and bound peptides are separated and purified away from the HLA and run through MS. The information we get back from MS consists of ~ 2000-4000 peptides per run. They have been filtered for high confidence and are 8 to 14 amino acids long. In the list will be self peptides and cancer neoantigens. So far I have data from HLA alleles A2, A11, and A24 in HEK293 cells that have been transduced with HPV and MCV oncoproteins and from caski (HPV), siha (HPV), raji (EBV), and ocim1 (AML) cell lines. We are working on primary AML tumor samples now. I will attach an example of the excel spread sheet containing the data that we get from the MS facilities.

I would like to have code that would allow us to sort the data in the following ways:

1. Given a set of peptides from n experiments, which peptides are in common between all or between a given subset. For example, I would like to find out that peptide 1 is found in data sets a, b and c, whereas peptide 2 is found in data sets b and c. We would typically be sorting through about 50 data sets at a time to begin with.

2. Each HLA allele will have preferred anchor motifs. For instance, HLA-A24 likes to have a Y or F at position 2 and a F or I at the C term position. Given the preferred peptide motif, sort out all peptides that do not follow this pattern. Regardless of the peptide length (8-14-mers), the position of the anchors remains the same. For example both a 9-mer and a 14-mer will prefer a F at position 2 and a I at the C-term. When doing MEME analysis on the peptide lists we see a lot of information not presented in literature about the binding preference of a given allele. We'd like to explore this more.

3. We will be looking at the effects of certain drugs and viral evasion proteins on the peptide repertoire and we would like a way to compare two groups and to find the differences that are statistically relevant. At this point I'm not exactly sure how to go about this- I probably will need to talk to a biostatistician. For one, I am not sure how to define or determine stochasticity within a group. Maybe you have some ideas?
