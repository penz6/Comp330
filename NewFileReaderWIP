import pandas as pd

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
        # iterate through the file
        with open(name, 'r') as file:
            for line in file:
                temp_list = line.split(",")
                #counter for templist
                tempcounter = 0
                #for the item in the temp list
                for item in temp_list:
                    #append to list
                    dictionary[tempcounter].append(item.rstrip())
                    #increment tempcount
                    tempcounter+=1
        #return
        return data 
                    
    else:
        # a bad thing happened
        raise Exception("Wrong File Type Passed")

# Define the data
#data = {
  #  'Name': ["Adams, Emily", "Black, John", "Collins, Sarah", "Diaz, Michael", "Evans, Olivia", "Foster, Liam"],
 #   'ID': [345678, 567123, 789456, 345987, 654321, 321654],
  #  'Grade': ['A', 'B+', 'C+', 'A-', 'B', 'C']
#}

# Create a DataFrame
df = pd.DataFrame(readSEC("COMSC210.02S25.SEC"))



# Display the updated DataFrame
print(df)
