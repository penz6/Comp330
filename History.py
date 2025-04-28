import pandas as pd
import os

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
        Update a CSV file with new student data, avoiding duplicates by student ID.

        Args:
            new_data (pd.DataFrame): DataFrame containing new student records. Must include an 'id' column.
            file_path (str): Path to the CSV file to update.

        Returns:
            tuple:
                - updated_dataframe (pd.DataFrame): The DataFrame after merging new and existing data.
                - list_of_duplicate_ids (list): List of student IDs from new_data that were already present in the file.

        Side Effects:
            Writes the updated DataFrame to the specified CSV file.
            Creates the file if it does not exist.
        """
        already_on_list = []
        if os.path.exists(file_path):
            existing = pd.read_csv(file_path)
            new_entries = new_data[~new_data['ID'].isin(existing['id'])]
            already_on_list = new_data[new_data['ID'].isin(existing['id'])]['id'].tolist()
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
            good_list (pd.DataFrame): DataFrame of students to add to the Good List. Must include an 'id' column.

        Returns:
            tuple:
                - updated_dataframe (pd.DataFrame): The Good List after update.
                - list_of_duplicate_ids (list): IDs from good_list already present in the Good List.

        Side Effects:
            Writes to the Good List CSV file.
        """
        return self.update_list(good_list, self.good_file)

    def update_work_list(self, work_list):
        """
        Update the Work List CSV with new student data.

        Args:
            work_list (pd.DataFrame): DataFrame of students to add to the Work List. Must include an 'id' column.

        Returns:
            tuple:
                - updated_dataframe (pd.DataFrame): The Work List after update.
                - list_of_duplicate_ids (list): IDs from work_list already present in the Work List.

        Side Effects:
            Writes to the Work List CSV file.
        """
        return self.update_list(work_list, self.work_file)

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

        Side Effects:
            Reads from the Good and Work List CSV files if they exist.
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
