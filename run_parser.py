import os

#run parser
def runReader(runFile):
    #inital zero
    lines = []
    #Get base directory and construct groups path using proper OS path functions
    base_dir = os.path.dirname(os.path.dirname(runFile))
    grpPath = os.path.join(base_dir, "Groups")
    
    with open(runFile, 'r') as file:
        next(file)  # Skip the first title line
        for line in file:
            lines.append(os.path.join(grpPath, line.rstrip()))
    return lines


# # needed to fix the path handling so it works on all OS
# # replaced string splitting with os.path.join