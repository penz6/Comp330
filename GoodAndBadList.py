from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
import pandas as pd

class Lists:
    #good list
    def goodList(runFile):
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
        return(goodListDF)
            

    def badList(runFile):
        grpList = runReader(runFile)
        #strip the run filepath and append group
        #get all the sec files
        secList = grpReader(runFile,grpList)
        #get all the sec data frames
        dataList = fileReader.bulkReadSEC(runFile,secList)
        #get the better list
        badListDF = pd.DataFrame()
        for dataframe in dataList:
            filtered_df = dataframe[dataframe["Grade"].isin(["F", "D-"])].copy()
            badListDF = pd.concat([badListDF, filtered_df], ignore_index=True)
        return(badListDF)