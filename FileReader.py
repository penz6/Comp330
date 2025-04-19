"""
Module to load section (.sec) files into pandas DataFrames.

Provides:
  - fileReader: utility class with methods for reading single or multiple .sec files.
"""
import pandas as pd
import os

#new class
class fileReader:
    """
    Utility class for reading section data files.

    Methods:
        readSEC(name): Parse a single .sec file into a DataFrame.
        bulkReadSEC(filePath, secFileList): Parse multiple .sec files given a base path.
    """

    # read the file
    def readSEC(name):
        """
        Parse a section file (.sec) into a pandas DataFrame.

        Args:
            name (str): Full path to the .sec file.

        Returns:
            pandas.DataFrame: DataFrame with columns ['FName', 'LName', 'ID', 'Grade'].

        Raises:
            Exception: If file extension is not '.sec'.
            IOError: If the file cannot be opened or read.
        """
        #define data
        data = {
        'FirstName': [],
        'LastName': [],
        'ID': [],
        'Grade': []
        }
        #create a dictonary for the data
        dictionary = list(data.values())
        #if the correct file type
        if name.split(".")[-1].lower() == "sec":
            #counter to skip one
            skip_one = 0
            # iterate through the file
            with open(name, 'r') as file:
                for line in file:
                    skip_one+=1
                    #if first line
                    if skip_one == 1:
                        #nothing
                        print("Skipped")
                    else:
                        temp_list = line.split(",")
                        #counter for templist
                        tempcounter = 0
                        #for the item in the temp list
                        for item in temp_list:
                            #append to list
                            dictionary[tempcounter].append(item.strip('"\n'))
                            #increment tempcount
                            tempcounter+=1
            #return
            return pd.DataFrame(data)
                        
        else:
            # a bad thing happened
            raise Exception("Wrong File Type Passed")
            

    def bulkReadSEC(filePath, secFileList):
        """
        Load multiple section files relative to a run file path.

        Args:
            filePath (str): Path to the script file (used to locate the Sections directory).
            secFileList (list of str): List of .sec filenames to read.

        Returns:
            list of pandas.DataFrame: One DataFrame per section file in the order provided.
        """
        #Get base directory and construct sections path using proper OS path functions
        base_dir = os.path.dirname(os.path.dirname(filePath))
        secPath = os.path.join(base_dir, "Sections")
        
        secList = []
        for secFile in secFileList:
            secList.append(fileReader.readSEC(os.path.join(secPath, secFile)))
        return secList




# # # # needed to fix the path handling so it works on all OS
# # # # replaced string splitting with os.path.join