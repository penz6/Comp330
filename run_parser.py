#run parser
def runReader(runFile):
    #inital zero
    lines = []
    #strip the run file path
    grpPath = runFile.split("/Run")[0]+"/Groups/"
    with open(runFile, 'r') as file:
        next(file)  # Skip the first title line
        for line in file:
            lines.append(grpPath+line.rstrip())
    return lines

