# this file should use the sec_parser,
# the code here shouls read the group file and parse it into, 
# a list of sec_files to be passed to the sec_parser
# for parsing.
# the sec_parser should then return the data extracted from the sec files. 
# the grp_parser should then perform the same operations as 
# the sec_parser, but for the group of sec files now.

# We could also refactor these 2 parsers into a more modular
# design, there are some commonalities between the two parsers.

# this will be a more detailed process, if we end up going with the 
# refactor plan. 

# This behavior also needs to extend to the run parser, 
# this will be used by the run_parser to parse the run files.

# We also need to work out the details of the actual data format. 

# there are different ways to represent the data, 
# we need to consider the calculation of the data when defining 
# the data format.