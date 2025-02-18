# Penn Potter 2/13/25

import pandas as pd

# data frame we read the data into
df = pd.DataFrame(columns=["Last", "First", "ID#", "Grade"])

name = 'HW 2 Test Files/COMPSC230.03F24.SEC'
#Read the file
def readRUN(name):
    if name.split(".")[2] == "RUN":
        # iterate through the file
        with open(name, 'r') as file:
            for line in file:
                data = line.strip()
                data = data.split(",")
                # What are we on again?
                round = 1
                # For each grade in data
                for row in data:
                    # append to data frame
                    df.loc[:, round] = row
                    round+=1
        return df

    else:
        # a bad thing happened
        raise Exception("Wrong File Type Passed")
    