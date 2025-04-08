#group parser
def grpReader(filepath,grpFileArray):
    #empty list
    files = []
    #sec file path
    secPath = filepath.split("/Run")[0]+"/Sections/"
    for filename in grpFileArray:
        with open(filename, 'r') as file:
            next(file)  # Skip the first title line
            for line in file:
                 files.append(line.rstrip())
    return files

