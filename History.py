import pandas as pd
import os



"""
Some changes are needed to satisfy the requirements of the task at hand.

To start we need to more effectivly manage histroy between runs. 

To do this we will create a new column ini the CSV that will....
1. Store the name of the class the student is being evaluated on.
2. If executing a run adds a student to the good list, 
    running it again with another run where the same student is on the good list,
    will not add them again but add data into this new column, this column
    will be added to for each run the student is on the good list.

    for example, 
    FirstName,LastName,id,Grade,sections
    SEkhyny, Jywo,AMAldQk,A, <name of the section the student is in that added it to the list>
    

"""

class HistoryManager:
    """
    Manages the persistence of student lists across program runs.

    Tracks students who appear on:
      - Good List: students with A/A- grades.
      - Work List: students with D+/D/D-/F grades.

    Lists are stored as CSV files in a dedicated folder. Provides methods to update, retrieve,
    and check student history in these lists.
    """

    def __init__(self, good_file="good_list.csv", work_file="work_list.csv"):
        """
        Initialize the HistoryManager with file paths for good and work lists.

        Args:
            good_file (str): Filename for the Good List CSV (default: "good_list.csv").
            work_file (str): Filename for the Work List CSV (default: "work_list.csv").

        Side Effects:
            Creates the storage folder if it does not exist.
            Sets up file paths for list storage.
        """
        self.folder = "historical_lists"
        os.makedirs(self.folder, exist_ok=True)
        self.good_file = os.path.join(self.folder, good_file)
        self.work_file = os.path.join(self.folder, work_file)

    def update_list(self, new_data, file_path):
        """
        Update a CSV file with new student data, tracking grade and section history.

        Args:
            new_data (pd.DataFrame): DataFrame containing new student records.
                                     Must include 'id', 'Grade', and 'section_source' columns.
            file_path (str): Path to the CSV file to update.

        Returns:
            tuple: (updated_dataframe, list_of_updated_or_existing_ids)
                   - updated_dataframe: The full DataFrame written back to the CSV.
                   - list_of_updated_or_existing_ids: IDs of students who were already in the list
                     (either updated or just present).
        """
        updated_or_existing_ids = []
        new_records_list = []

        # Define expected columns in the history CSV
        history_columns = ['FirstName', 'LastName', 'id', 'grades', 'sections']

        if os.path.exists(file_path):
            try:
                existing = pd.read_csv(file_path)
                # Ensure required columns exist, fill NaN sections/grades with empty string
                if 'sections' not in existing.columns:
                    existing['sections'] = ''
                if 'grades' not in existing.columns:
                    existing['grades'] = ''
                existing['sections'] = existing['sections'].fillna('')
                existing['grades'] = existing['grades'].fillna('')
                
                # Ensure 'id' column is of a consistent type (string) for reliable matching
                existing['id'] = existing['id'].astype(str)
                new_data['id'] = new_data['id'].astype(str)

            except pd.errors.EmptyDataError:
                print(f"Warning: History file {file_path} is empty. Creating new structure.")
                existing = pd.DataFrame(columns=history_columns)
            except Exception as e:
                print(f"Error reading history file {file_path}: {e}. Starting fresh.")
                existing = pd.DataFrame(columns=history_columns)
        else:
            print(f"🆕 Creating new history file: {file_path}")
            existing = pd.DataFrame(columns=history_columns)

        # Process each new record
        for _, new_row in new_data.iterrows():
            student_id = new_row['id']
            new_grade = new_row['Grade']
            new_section = new_row['section_source']

            # Check if student exists
            match = existing[existing['id'] == student_id]

            if not match.empty:
                # Student exists, update their record
                existing_idx = match.index[0]
                updated_or_existing_ids.append(student_id)

                # Get current history, handle potential NaN/None
                current_sections_str = str(existing.at[existing_idx, 'sections'])
                current_grades_str = str(existing.at[existing_idx, 'grades'])

                current_sections = current_sections_str.split(',') if current_sections_str else []
                current_grades = current_grades_str.split(',') if current_grades_str else []

                # Create a unique identifier for the grade/section pair
                entry_identifier = f"{new_section}:{new_grade}"
                
                # Check if this specific section/grade combo is already recorded
                # Simple check: is the section already listed? More robust check needed if grade matters per section.
                # For now, just append if the section isn't listed.
                # A more complex approach might store pairs like "SEC1:A,SEC2:A-"
                if new_section not in current_sections:
                    current_sections.append(new_section)
                    current_grades.append(new_grade) # Append corresponding grade

                    # Update the DataFrame
                    existing.at[existing_idx, 'sections'] = ','.join(filter(None, current_sections)) # Filter removes empty strings
                    existing.at[existing_idx, 'grades'] = ','.join(filter(None, current_grades))
                # Optional: Add logic here if you want to update the grade for an *existing* section entry

            else:
                # Student is new, create a new record
                new_record = {
                    'FirstName': new_row.get('FirstName', ''), # Use .get for safety
                    'LastName': new_row.get('LastName', ''),
                    'id': student_id,
                    'grades': new_grade,
                    'sections': new_section
                }
                # Ensure the new record has all necessary columns, even if empty
                for col in history_columns:
                    if col not in new_record:
                        new_record[col] = ''
                new_records_list.append(new_record)

        # Combine existing (potentially updated) data with completely new records
        if new_records_list:
            new_records_df = pd.DataFrame(new_records_list, columns=history_columns)
            updated = pd.concat([existing, new_records_df], ignore_index=True)
        else:
            updated = existing

        # Ensure final DataFrame has the correct columns in order
        updated = updated.reindex(columns=history_columns)
        
        # Save the updated DataFrame
        try:
            updated.to_csv(file_path, index=False)
        except Exception as e:
            print(f"Error writing updated history to {file_path}: {e}")
            # Decide how to handle write error - maybe return existing data?
            return existing, updated_or_existing_ids

        return updated, updated_or_existing_ids

    def update_good_list(self, good_list_data):
        """
        Update the Good List CSV with new student data, tracking history.

        Args:
            good_list_data (pd.DataFrame): DataFrame of students to add/update in the Good List.
                                           Must include 'id', 'Grade', 'section_source'.

        Returns:
            tuple: (updated_dataframe, list_of_updated_or_existing_ids)
        """
        # Remove the section_name argument, data comes from the dataframe
        return self.update_list(good_list_data, self.good_file)

    def update_work_list(self, work_list_data):
        """
        Update the Work List CSV with new student data, tracking history.

        Args:
            work_list_data (pd.DataFrame): DataFrame of students to add/update in the Work List.
                                           Must include 'id', 'Grade', 'section_source'.

        Returns:
            tuple: (updated_dataframe, list_of_updated_or_existing_ids)
        """
        # Remove the section_name argument, data comes from the dataframe
        return self.update_list(work_list_data, self.work_file)

    def get_good_list(self):
        """
        Retrieve the current Good List from CSV.

        Returns:
            pd.DataFrame: DataFrame containing the Good List.
                - If the file does not exist, returns an empty DataFrame.

        Side Effects:
            Reads from the Good List CSV file if it exists.
        """
        if os.path.exists(self.good_file):
            return pd.read_csv(self.good_file)
        return pd.DataFrame()

    def get_work_list(self):
        """
        Retrieve the current Work List from CSV.

        Returns:
            pd.DataFrame: DataFrame containing the Work List.
                - If the file does not exist, returns an empty DataFrame.

        Side Effects:
            Reads from the Work List CSV file if it exists.
        """
        if os.path.exists(self.work_file):
            return pd.read_csv(self.work_file)
        return pd.DataFrame()

    def check_student_history(self, student_id):
        """
        Check if a student has previously appeared on the Good or Work Lists.

        Args:
            student_id: The student ID to check (should match the type used in the 'id' column).

        Returns:
            dict: Dictionary with keys:
                - 'good_list' (bool): True if student_id is in the Good List, else False.
                - 'work_list' (bool): True if student_id is in the Work List, else False.
                - 'good_details' (dict): {'grades': str, 'sections': str} if on good list, else None
                - 'work_details' (dict): {'grades': str, 'sections': str} if on work list, else None

        Side Effects:
            Reads from the Good and Work List CSV files if they exist.
        """
        history = {
            'good_list': False,
            'work_list': False,
            'good_details': None,
            'work_details': None
        }
        student_id_str = str(student_id) # Ensure comparison is string-based

        if os.path.exists(self.good_file):
            try:
                good_list = pd.read_csv(self.good_file)
                good_list['id'] = good_list['id'].astype(str) # Ensure consistent type
                match = good_list[good_list['id'] == student_id_str]
                if not match.empty:
                    history['good_list'] = True
                    details = match.iloc[0]
                    history['good_details'] = {
                        'grades': details.get('grades', ''),
                        'sections': details.get('sections', '')
                    }
            except Exception as e:
                print(f"Error reading good list for history check: {e}")

        if os.path.exists(self.work_file):
            try:
                work_list = pd.read_csv(self.work_file)
                work_list['id'] = work_list['id'].astype(str) # Ensure consistent type
                match = work_list[work_list['id'] == student_id_str]
                if not match.empty:
                    history['work_list'] = True
                    details = match.iloc[0]
                    history['work_details'] = {
                        'grades': details.get('grades', ''),
                        'sections': details.get('sections', '')
                    }
            except Exception as e:
                print(f"Error reading work list for history check: {e}")

        return history
