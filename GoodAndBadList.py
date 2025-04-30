"""
Module to generate DataFrames of high- and low-performing students
aggregated across all course sections.

Provides:
  - Lists.goodList: returns students earning "A" or "A-" with source section.
  - Lists.badList: returns students earning "F" or "D-" range with source section.
"""

from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
import pandas as pd
import os # Import os for basename

class Lists:
    """
    Utility filters to extract subsets of student records by performance.

    Methods:
        goodList(runFile): DataFrame of top-performing students with source section.
        badList(runFile): DataFrame of bottom-performing students with source section.
    """

    def goodList(runFile):
        """
        Collect and return students with top grades ("A", "A-"), including source section.

        Workflow:
          1. Parse run file to get group identifiers.
          2. Determine section filenames via grpReader.
          3. Bulk read section DataFrames with fileReader.
          4. For each section DataFrame, filter rows where Grade is "A" or "A-".
          5. Add a 'section_source' column with the base name of the .sec file.
          6. Concatenate filtered data from all sections.
          7. Drop duplicates based on 'id' and 'section_source' to handle potential re-reads.

        Args:
            runFile (str): Path to the run file defining group/sections.

        Returns:
            pandas.DataFrame: Combined records of students earning "A" or "A-",
                              including 'section_source' column.
        """
        grpList = runReader(runFile)
        secList = grpReader(runFile, grpList)
        
        # Get base directory for sections path
        base_dir = os.path.dirname(os.path.dirname(runFile))
        sections_path = os.path.join(base_dir, "Sections")

        all_good_students = []
        required_columns = ['Grade'] # 'id'/'ID' checked separately

        for sec_file_name in secList:
            full_path = os.path.join(sections_path, sec_file_name)
            try:
                dataframe = fileReader.readSEC(full_path)
                if dataframe.empty:
                    continue # Skip empty dataframes

                # --- Robustness Check ---
                # Check for 'id' or 'ID' column
                id_col = None
                if 'id' in dataframe.columns:
                    id_col = 'id'
                elif 'ID' in dataframe.columns:
                    id_col = 'ID'
                    dataframe = dataframe.rename(columns={'ID': 'id'}) # Rename to 'id' for consistency
                
                if id_col is None:
                    print(f"Warning: Section {sec_file_name} is missing 'id' or 'ID' column. Skipping.")
                    continue

                # Check for other required columns
                missing_cols = [col for col in required_columns if col not in dataframe.columns]
                if missing_cols:
                    print(f"Warning: Section {sec_file_name} is missing columns: {missing_cols}. Skipping.")
                    continue
                # --- End Robustness Check ---

                # Filter for good grades
                filtered_df = dataframe[dataframe["Grade"].isin(["A", "A-"])].copy()
                if not filtered_df.empty:
                    # Add the source section file name
                    filtered_df['section_source'] = os.path.basename(sec_file_name)
                    all_good_students.append(filtered_df)
            except Exception as e:
                print(f"Warning: Could not read or process section {sec_file_name}: {e}")

        if not all_good_students:
            # Return empty DataFrame with expected columns if no students found
            # Ensure 'id' is included here
            return pd.DataFrame(columns=['FirstName', 'LastName', 'id', 'Grade', 'section_source'])

        # Concatenate all found students
        goodListDF = pd.concat(all_good_students, ignore_index=True)
        
        # Drop duplicates - 'id' column should now reliably exist
        goodListDF = goodListDF.drop_duplicates(subset=['id', 'section_source'], keep='first')
        
        return goodListDF


    def badList(runFile):
        """
        Collect and return students with bottom grades ("F", "D-", "D", "D+"), including source section.

        Workflow:
          1. Parse run file to get group identifiers.
          2. Determine section filenames via grpReader.
          3. Bulk read section DataFrames with fileReader.
          4. For each section DataFrame, filter rows where Grade is "F", "D-", "D", or "D+".
          5. Add a 'section_source' column with the base name of the .sec file.
          6. Concatenate filtered data from all sections.
          7. Drop duplicates based on 'id' and 'section_source'.

        Args:
            runFile (str): Path to the run file defining group/sections.

        Returns:
            pandas.DataFrame: Combined records of students earning "F" or "D-" range,
                              including 'section_source' column.
        """
        grpList = runReader(runFile)
        secList = grpReader(runFile, grpList)

        # Get base directory for sections path
        base_dir = os.path.dirname(os.path.dirname(runFile))
        sections_path = os.path.join(base_dir, "Sections")

        all_bad_students = []
        required_columns = ['Grade'] # 'id'/'ID' checked separately

        for sec_file_name in secList:
            full_path = os.path.join(sections_path, sec_file_name)
            try:
                dataframe = fileReader.readSEC(full_path)
                if dataframe.empty:
                    continue # Skip empty dataframes

                # --- Robustness Check ---
                 # Check for 'id' or 'ID' column
                id_col = None
                if 'id' in dataframe.columns:
                    id_col = 'id'
                elif 'ID' in dataframe.columns:
                    id_col = 'ID'
                    dataframe = dataframe.rename(columns={'ID': 'id'}) # Rename to 'id' for consistency
                
                if id_col is None:
                    print(f"Warning: Section {sec_file_name} is missing 'id' or 'ID' column. Skipping.")
                    continue

                # Check for other required columns
                missing_cols = [col for col in required_columns if col not in dataframe.columns]
                if missing_cols:
                    print(f"Warning: Section {sec_file_name} is missing columns: {missing_cols}. Skipping.")
                    continue
                # --- End Robustness Check ---

                # Filter for bad grades
                filtered_df = dataframe[dataframe["Grade"].isin(["F", "D-", "D", "D+"])].copy()
                if not filtered_df.empty:
                    # Add the source section file name
                    filtered_df['section_source'] = os.path.basename(sec_file_name)
                    all_bad_students.append(filtered_df)
            except Exception as e:
                print(f"Warning: Could not read or process section {sec_file_name}: {e}")

        if not all_bad_students:
            # Return empty DataFrame with expected columns if no students found
            # Ensure 'id' is included here
            return pd.DataFrame(columns=['FirstName', 'LastName', 'id', 'Grade', 'section_source'])

        # Concatenate all found students
        badListDF = pd.concat(all_bad_students, ignore_index=True)

        # Drop duplicates - 'id' column should now reliably exist
        badListDF = badListDF.drop_duplicates(subset=['id', 'section_source'], keep='first')

        return badListDF