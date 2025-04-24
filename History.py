import pandas as pd
import os

class HistoryManager:
    """
    Manages the persistence of student lists across program runs.
    Tracks students who appear on Good List (A/A- grades) and Work List (D+/D/D-/F grades).
    """

    def __init__(self, good_file="good_list.csv", work_file="work_list.csv"):
        """
        Initialize the HistoryManager with file paths for good and work lists.
        """
        self.folder = "historical_lists"
        os.makedirs(self.folder, exist_ok=True)
        self.good_file = os.path.join(self.folder, good_file)
        self.work_file = os.path.join(self.folder, work_file)

    def update_list(self, new_data, file_path):
        """
        Update a CSV file with new data, avoiding duplicates by student ID.
        Returns: (updated_dataframe, list_of_duplicate_ids)
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
        Returns: (updated_dataframe, list_of_duplicate_ids)
        """
        return self.update_list(good_list, self.good_file)

    def update_work_list(self, work_list):
        """
        Update the Work List CSV with new student data.
        Returns: (updated_dataframe, list_of_duplicate_ids)
        """
        return self.update_list(work_list, self.work_file)

    def get_good_list(self):
        """
        Retrieve the current Good List from CSV.
        Returns: pd.DataFrame or empty DataFrame if file doesn't exist
        """
        if os.path.exists(self.good_file):
            return pd.read_csv(self.good_file)
        return pd.DataFrame()

    def get_work_list(self):
        """
        Retrieve the current Work List from CSV.
        Returns: pd.DataFrame or empty DataFrame if file doesn't exist
        """
        if os.path.exists(self.work_file):
            return pd.read_csv(self.work_file)
        return pd.DataFrame()

    def check_student_history(self, student_id):
        """
        Check if a student has previously appeared on Good or Work Lists.
        Returns: dict with keys 'good_list' and 'work_list'
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
