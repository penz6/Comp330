import sys
import os
import pandas as pd

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import your main GPA processing module
import gpa_averages

# Mock replacement for fileReader.readSEC with expanded test data
def fake_readSEC(path):
    # Simulate two different section files with varying grades
    if 'section1' in path:
        return pd.DataFrame({'Grade': ['A', 'B+', 'B-', 'C+', 'F']})  # Avg: (4.0 + 3.3 + 2.7 + 2.3 + 0.0) / 5 = 2.46
    elif 'section2' in path:
        return pd.DataFrame({'Grade': ['A-', 'B', 'B', 'C-', 'D']})   # Avg: (3.7 + 3.0 + 3.0 + 1.7 + 1.0) / 5 = 2.48
    else:
        return pd.DataFrame({'Grade': []})

# Patch fileReader.readSEC in your module
gpa_averages.fileReader.readSEC = fake_readSEC

# Test section files
mock_section_files = ['section1.csv', 'section2.csv']
df, group_avg = gpa_averages.average_gpa_report(__file__, mock_section_files)

# Output the results
print("=== GPA Report Test ===")
print(df)
print("Group Average GPA:", group_avg)

# Perform assertions
len(df) == 2, "Expected two sections"
round(df.loc[df['Section'] == 'section1.csv', 'Average GPA'].values[0], 2) == 2.46, "Section 1 GPA incorrect" 
round(df.loc[df['Section'] == 'section2.csv', 'Average GPA'].values[0], 2) == 2.48, "Section 2 GPA incorrect"
round(group_avg, 2) == 2.47, "Group average GPA should be 2.47"

print("test passed")

