import os

#group parser
def grpReader(filepath, grpFileArray):
    """
    Parses group files to extract section filenames.
    
    Args:
        filepath (str): Path to the run file.
        grpFileArray (list of str): List of group file names to read.
    
    Returns:
        list of str: List of section filenames extracted from the group files.
    """
    #empty list
    files = []
    #sec file path using OS path functions
    base_dir = os.path.dirname(os.path.dirname(filepath))
    secPath = os.path.join(base_dir, "Sections")
    
    for filename in grpFileArray:
        with open(filename, 'r') as file:
            next(file)  # Skip the first title line
            for line in file:
                files.append(line.rstrip())
    return files

# needed to fix the path handling so it works on all OS
# replaced string splitting with os.path.join