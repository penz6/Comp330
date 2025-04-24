import pandas as pd
import os

class HistoryManager:
    """
    Handles persistent tracking of students who appear on the Good List (A/A- grades)
    and Work List (D+/D/D-/F grades) across program runs. Lists are stored as CSV files
    in the 'historical_lists' directory. Provides methods to update, retrieve, and check
    student history for both lists.

    Attributes:
        good_file (str): Path to the Good List CSV file.
        work_file (str): Path to the Work List CSV file.
        folder (str): Directory where historical lists are stored.
    """

    def __init__(self, good_file="good_list.csv", work_file="work_list.csv"):
        """
        Initialize the HistoryManager, ensuring the historical_lists directory exists,
        and set file paths for the Good List and Work List CSVs.

        Args:
            good_file (str): Filename for the Good List CSV (default: 'good_list.csv').
            work_file (str): Filename for the Work List CSV (default: 'work_list.csv').
        """
        self.folder = "historical_lists"
        os.makedirs(self.folder, exist_ok=True)
        self.good_file = os.path.join(self.folder, good_file)
        self.work_file = os.path.join(self.folder, work_file)

    def update_list(self, new_data, file_path):
        """
        Update a CSV file with new student data, avoiding duplicates by student ID.

        Args:
            new_data (pd.DataFrame): DataFrame containing new student records (must include 'id' column).
            file_path (str): Path to the CSV file to update.

        Returns:
            tuple:
                - updated (pd.DataFrame): The updated DataFrame containing all unique students.
                - already_on_list (list): List of student IDs that were already present in the file.
        """
        already_on_list = []
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)
            new_entries = new_data[~new_data['id'].isin(existing['id'])]
            already_on_list = new_data[new_data['id'].isin(existing['id'])]['id'].tolist()
            updated = pd.concat([existing, new_entries], ignore_index=True)
        else:
            updated = new_data
            print(f"🆕 Creating new file: {file_path}")
        updated.to_csv(file_path, index=False)
        return updated, already_on_list

    def update_good_list(self, good_list):
        """
        Update the Good List CSV with new student data.

        Args:
            good_list (pd.DataFrame): DataFrame of students to add to the Good List (must include 'id' column).

        Returns:
            tuple:
                - updated (pd.DataFrame): The updated Good List DataFrame.
                - already_on_list (list): List of student IDs already present in the Good List.
        """
        return self.update_list(good_list, self.good_file)

    def update_work_list(self, work_list):
        """
        Update the Work List CSV with new student data.

        Args:
            work_list (pd.DataFrame): DataFrame of students to add to the Work List (must include 'id' column).

        Returns:
            tuple:
                - updated (pd.DataFrame): The updated Work List DataFrame.
                - already_on_list (list): List of student IDs already present in the Work List.
        """
        return self.update_list(work_list, self.work_file)

    def get_good_list(self):
        """
        Retrieve the current Good List from CSV.

        Returns:
            pd.DataFrame: DataFrame containing all students on the Good List,
                          or an empty DataFrame if the file does not exist.
        """
        if os.path.exists(self.good_file):
            return pd.read_csv(self.good_file)
        return pd.DataFrame()

    def get_work_list(self):
        """
        Retrieve the current Work List from CSV.

        Returns:
            pd.DataFrame: DataFrame containing all students on the Work List,
                          or an empty DataFrame if the file does not exist.
        """
        if os.path.exists(self.work_file):
            return pd.read_csv(self.work_file)
        return pd.DataFrame()

    def check_student_history(self, student_id):
        """
        Check if a student has previously appeared on the Good List or Work List.

        Args:
            student_id: The unique ID of the student to check (type should match 'id' column in lists).

        Returns:
            dict: Dictionary with boolean values:
                - 'good_list': True if student is in the Good List, else False.
                - 'work_list': True if student is in the Work List, else False.
        """
        history = {
            'good_list': False,
            'work_list': False
        }
        if os.path.exists(self.good_file):
            good_list = pd.read_csv(self.good_file)
            history['good_list'] = student_id in good_list['id'].values
        if os.path.exists(self.work_file):
            work_list = pd.read_csv(self.work_file)
            history['work_list'] = student_id in work_list['id'].values
        return history
