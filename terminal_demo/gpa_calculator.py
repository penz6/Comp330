"""
GPA Calculator Module

This module provides functions to convert letter grades to GPA values,
calculate weighted GPAs, and perform statistical analysis on grades.
"""

import re
import pandas as pd
import numpy as np
import os
from sec_parser import format_sec_data_as_csv

# Grade to GPA mapping
GRADE_TO_GPA = {
    'A+': 4.0,
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    'D': 1.0,
    'D-': 0.7,
    'F': 0.0
}

def parse_sec_header(file_path):
    """
    Parses the header of a .SEC file to get the course ID and credit hours.
    
    Parameters:
    file_path (str): Path to the .SEC file
    
    Returns:
    tuple: (course_id, credit_hours)
    """
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            # Extract course ID and credit hours
            parts = first_line.split()
            if len(parts) >= 2:
                course_id = parts[0]
                credit_hours = float(parts[1])
                return course_id, credit_hours
            else:
                raise ValueError(f"Invalid SEC file header: {first_line}")
    except Exception as e:
        raise ValueError(f"Error reading SEC file header {file_path}: {str(e)}")

def convert_csv_to_dataframe(csv_data):
    """
    Converts CSV data string to a pandas DataFrame.
    
    Parameters:
    csv_data (str): CSV data as a string
    
    Returns:
    pd.DataFrame: DataFrame containing student data
    """
    import io
    return pd.read_csv(io.StringIO(csv_data))

def add_gpa_column(df):
    """
    Adds a GPA column to the DataFrame based on letter grades.
    
    Parameters:
    df (pd.DataFrame): DataFrame with a 'Grade' column
    
    Returns:
    pd.DataFrame: DataFrame with added 'GPA' column
    """
    # Create a copy to avoid modifying the original
    df_copy = df.copy()
    # Convert letter grades to GPA values
    df_copy['GPA'] = df_copy['Grade'].map(lambda x: GRADE_TO_GPA.get(x, np.nan))
    return df_copy

def calculate_section_gpa(file_path):
    """
    Calculates GPA statistics for a section file.
    
    Parameters:
    file_path (str): Path to the .SEC file
    
    Returns:
    tuple: (course_id, credit_hours, gpa_stats) where gpa_stats is a dictionary
           containing mean, median, std_dev, count, min, max
    """
    # Parse section header for course ID and credit hours
    course_id, credit_hours = parse_sec_header(file_path)
    
    # Parse student data
    csv_data = format_sec_data_as_csv(file_path)
    df = convert_csv_to_dataframe(csv_data)
    
    # Add GPA column
    df = add_gpa_column(df)
    
    # Calculate statistics
    gpa_stats = {
        'mean': df['GPA'].mean(),
        'median': df['GPA'].median(),
        'std_dev': df['GPA'].std(),
        'count': len(df),
        'min': df['GPA'].min(),
        'max': df['GPA'].max(),
        'data': df
    }
    
    return course_id, credit_hours, gpa_stats

def calculate_group_gpa(section_files):
    """
    Calculates aggregate GPA statistics for a group of sections.
    
    Parameters:
    section_files (list): List of paths to .SEC files
    
    Returns:
    dict: Dictionary with aggregate statistics and individual section stats
    """
    all_students = []
    section_stats = {}
    
    for section_file in section_files:
        try:
            # Verify the file exists before trying to process it
            if not os.path.exists(section_file):
                print(f"Warning: Section file does not exist: {section_file}")
                continue
                
            course_id, credit_hours, stats = calculate_section_gpa(section_file)
            section_stats[course_id] = {
                'credit_hours': credit_hours,
                'stats': stats
            }
            
            # Add course_id and credit_hours to each student record
            df = stats['data'].copy()
            df['CourseID'] = course_id
            df['CreditHours'] = credit_hours
            all_students.append(df)
        except Exception as e:
            print(f"Error processing section {section_file}: {e}")
            # Continue with other sections rather than failing completely
    
    # Combine all student data
    if all_students:
        combined_df = pd.concat(all_students, ignore_index=True)
        
        # Calculate aggregate statistics
        aggregate_stats = {
            'mean': combined_df['GPA'].mean(),
            'median': combined_df['GPA'].median(),
            'std_dev': combined_df['GPA'].std(),
            'count': len(combined_df),
            'min': combined_df['GPA'].min(),
            'max': combined_df['GPA'].max(),
            'data': combined_df
        }
    else:
        aggregate_stats = {
            'mean': np.nan,
            'median': np.nan,
            'std_dev': np.nan,
            'count': 0,
            'min': np.nan,
            'max': np.nan,
            'data': pd.DataFrame()
        }
    
    return {
        'aggregate': aggregate_stats,
        'sections': section_stats
    }

def identify_good_list(df, threshold=3.5):
    """
    Identifies students for the Good List (GPA >= threshold).
    
    Parameters:
    df (pd.DataFrame): DataFrame with student data including GPA
    threshold (float): GPA threshold for Good List, default 3.5
    
    Returns:
    pd.DataFrame: DataFrame with students on the Good List
    """
    return df[df['GPA'] >= threshold].sort_values('GPA', ascending=False)

def identify_work_list(df, threshold=2.0):
    """
    Identifies students for the Work List (GPA <= threshold).
    
    Parameters:
    df (pd.DataFrame): DataFrame with student data including GPA
    threshold (float): GPA threshold for Work List, default 2.0
    
    Returns:
    pd.DataFrame: DataFrame with students on the Work List
    """
    return df[df['GPA'] <= threshold].sort_values('GPA')

def perform_z_test(section_gpa, group_mean, group_std):
    """
    Performs a Z-test to compare a section's average GPA to the group average.
    
    Parameters:
    section_gpa (float): Section's average GPA
    group_mean (float): Group's average GPA
    group_std (float): Group's standard deviation
    
    Returns:
    tuple: (z_score, p_value)
    """
    import scipy.stats as stats
    
    # Calculate Z-score
    z_score = (section_gpa - group_mean) / group_std
    
    # Get two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    return z_score, p_value

if __name__ == "__main__":
    # Example usage
    sample_file_path = r"COMSC330_POC_Data\Sections\COMSC110.01S25.SEC"
    
    print(f"Calculating GPA for section: {sample_file_path}")
    print("-" * 30)
    
    try:
        course_id, credit_hours, stats = calculate_section_gpa(sample_file_path)
        print(f"Course ID: {course_id}")
        print(f"Credit Hours: {credit_hours}")
        print(f"Average GPA: {stats['mean']:.2f}")
        print(f"Median GPA: {stats['median']:.2f}")
        print(f"Standard Deviation: {stats['std_dev']:.2f}")
        print(f"Number of Students: {stats['count']}")
        
        # Show Good List
        good_list = identify_good_list(stats['data'])
        print(f"\nGood List ({len(good_list)} students):")
        if not good_list.empty:
            print(good_list[['LastName', 'FirstName', 'GPA']])
        
        # Show Work List
        work_list = identify_work_list(stats['data'])
        print(f"\nWork List ({len(work_list)} students):")
        if not work_list.empty:
            print(work_list[['LastName', 'FirstName', 'GPA']])
        
    except Exception as e:
        print(f"Error: {e}")
