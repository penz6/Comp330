import pandas as pd


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
        if name.split(".")[2] == "SEC":
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
    def bulkReadSEC(filePath,secFileList):
        secPath = filePath.split("/Run")[0]+"/Sections/"
        secList = []
        for secFile in secFileList:
            secList.append(fileReader.readSEC(secPath+secFile))
        return secList
        