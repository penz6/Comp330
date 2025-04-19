"""
Module to generate DataFrames of high- and low-performing students
aggregated across all course sections.

Provides:
  - Lists.goodList: returns students earning "A" or "A-"
  - Lists.badList: returns students earning "F" or "D-"
"""

from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
import pandas as pd

class Lists:
    """
    Utility filters to extract subsets of student records by performance.

    Methods:
        goodList(runFile): DataFrame of top-performing students.
        badList(runFile): DataFrame of bottom-performing students.
    """

    def goodList(runFile):
        """
        Collect and return students with top grades ("A", "A-").

        Workflow:
          1. Parse run file to get group identifiers.
          2. Determine section filenames via grpReader.
          3. Bulk read section DataFrames with fileReader.
          4. Filter rows where Grade is "A" or "A-".
          5. Concatenate and return the result.

        Args:
            runFile (str): Path to the run file defining group/sections.

        Returns:
            pandas.DataFrame: Combined records of students earning "A" or "A-".
        """
        grpList = runReader(runFile)
        #strip the run filepath and append group
        #get all the sec files
        secList = grpReader(runFile,grpList)
        #get all the sec data frames
        dataList = fileReader.bulkReadSEC(runFile,secList)
        #get the better list
        goodListDF = pd.DataFrame()
        for dataframe in dataList:
            filtered_df = dataframe[dataframe["Grade"].isin(["A", "A-"])].copy()
            goodListDF = pd.concat([goodListDF, filtered_df], ignore_index=True)
            goodListDF = goodListDF.drop_duplicates()
        return(goodListDF)
            

    def badList(runFile):
        """
        Collect and return students with bottom grades ("F", "D-").

        Workflow:
          1. Parse run file to get group identifiers.
          2. Determine section filenames via grpReader.
          3. Bulk read section DataFrames with fileReader.
          4. Filter rows where Grade is "F" or "D-".
          5. Concatenate and return the result.

        Args:
            runFile (str): Path to the run file defining group/sections.

        Returns:
            pandas.DataFrame: Combined records of students earning "F" or "D-".
        """
        grpList = runReader(runFile)
        #strip the run filepath and append group
        #get all the sec files
        secList = grpReader(runFile,grpList)
        #get all the sec data frames
        dataList = fileReader.bulkReadSEC(runFile,secList)
        #get the better list
        badListDF = pd.DataFrame()
        for dataframe in dataList:
            filtered_df = dataframe[dataframe["Grade"].isin(["F", "D-","D","D+"])].copy()
            badListDF = pd.concat([badListDF, filtered_df], ignore_index=True)
            badListDF = badListDF.drop_duplicates()
        return(badListDF)