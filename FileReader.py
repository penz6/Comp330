import pandas as pd
import os

#new class
class fileReader:
        
    # read the file
    def readSEC(name):
        #define data
        data = {
        'FName': [],
        'LName': [],
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
        #Get base directory and construct sections path using proper OS path functions
        base_dir = os.path.dirname(os.path.dirname(filePath))
        secPath = os.path.join(base_dir, "Sections")
        
        secList = []
        for secFile in secFileList:
            secList.append(fileReader.readSEC(os.path.join(secPath, secFile)))
        return secList




# # # # needed to fix the path handling so it works on all OS
# # # # replaced string splitting with os.path.join