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
