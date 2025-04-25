import os
import pandas as pd
from FileReader import fileReader
from zscore_calculator import letter_to_gpa

def calculate_average_gpa(df):
    """
    Compute average GPA for a given DataFrame of grades.
    """
    gpas = [letter_to_gpa(g) for g in df['Grade']]
    mean_gpa = sum(gpas) / len(gpas)
    return mean_gpa, len(gpas)

def average_gpa_report(run_file, sec_files):
    """
    Load section files, compute average GPA summarize results.

    Returns:
        DataFrame: Summary of average GPA per section.
        float: Group-level average GPA.
    """
    base_dir = os.path.dirname(os.path.dirname(run_file))
    sections_path = os.path.join(base_dir, "Sections")
    
    section_data = []
    all_gpas = []

    for sec_file in sec_files:
        full_path = os.path.join(sections_path, sec_file)
      
        df = fileReader.readSEC(full_path)
        avg_gpa, count = calculate_average_gpa(df)
        gpas = [letter_to_gpa(g) for g in df['Grade']]
        all_gpas.extend(gpas)

        section_data.append({
            'Section': sec_file,
            'Average GPA': round(avg_gpa, 3),
            'Total Grades': count
        })

    group_avg_gpa = round(sum(all_gpas) / len(all_gpas), 3) 

    df_summary = pd.DataFrame(section_data)
    return df_summary, group_avg_gpa


