import pandas as pd
import os

# File paths
good_file = "good_list.csv"
work_file = "work_list.csv"

# Sample DataFrames — use your real ones with at least an 'id' column
# good_list = pd.DataFrame([{"id": 101, "name": "Alice", "grade": 90}, {"id": 102, "name": "Bob", "grade": 85}])
# work_list = pd.DataFrame([{"id": 103, "name": "Diana", "grade": 60}, {"id": 104, "name": "Charlie", "grade": 65}])

# Lists to track duplicates
already_on_good_list = []
already_on_work_list = []

# ------------- GOOD LIST -------------
if os.path.exists(good_file):
    # Load existing CSV
    existing_good = pd.read_csv(good_file)

    # Filter: keep only new students based on 'id'
    new_good = good_list[~good_list['id'].isin(existing_good['id'])]
    already_on_good_list = good_list[good_list['id'].isin(existing_good['id'])]['id'].tolist()

    # Combine and overwrite file
    updated_good = pd.concat([existing_good, new_good], ignore_index=True)
else:
    # File doesn't exist — use new data
    updated_good = good_list
    print(f"🆕 Creating new file: {good_file}")

# Save to CSV
updated_good.to_csv(good_file, index=False)

# ------------- WORK LIST -------------
if os.path.exists(work_file):
    existing_work = pd.read_csv(work_file)
    new_work = work_list[~work_list['id'].isin(existing_work['id'])]
    already_on_work_list = work_list[work_list['id'].isin(existing_work['id'])]['id'].tolist()
    updated_work = pd.concat([existing_work, new_work], ignore_index=True)
else:
    updated_work = work_list
    print(f"🆕 Creating new file: {work_file}")

# Save to CSV
updated_work.to_csv(work_file, index=False)


"""
Nice work!

To use this code outside of this file we should try to make it a function.


import pandas as pd
import os

class HistoryManager:
    ##### Constructor #####
    def __init__(self, good_file="good_list.csv", work_file="work_list.csv"):
        self.good_file = good_file
        self.work_file = work_file

    
    ##### Update List #####
    def update_list(self, new_data, file_path):
        `Update a CSV file with new data, avoiding duplicates by 'id'.`
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

    ##### Update Good List (using update_list) #####
    def update_good_list(self, good_list):
        return self.update_list(good_list, self.good_file)

    ##### Update Work List (using update_list) #####
    def update_work_list(self, work_list):
        return self.update_list(work_list, self.work_file)


        
------------- Example Usage -------------

# elsewhere in the code
from History import HistoryManager

# Assume good_list and work_list are pandas DataFrames with at least an 'id' column
hm = HistoryManager()
updated_good, dup_good = hm.update_good_list(good_list)
updated_work, dup_work = hm.update_work_list(work_list)


Keep crushing! 
"""
