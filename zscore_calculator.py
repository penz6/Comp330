"""
zscore_calculator.py

Module to compute and analyze Z-scores for course section GPAs relative to group GPAs.

This module includes:
  - letter_to_gpa: convert letter grades to numeric GPA (with exclusions)
  - compute_z_score: calculate Z-score given sample and population stats
  - compute_p_value: compute two‐tailed p‐value for a Z‐score
  - is_significant: test if a Z‐score exceeds a threshold
  - calculate_section_stats: mean GPA and count of valid grades per section
  - calculate_group_stats: mean and stddev across sections
  - analyze_sections: load data, run analysis, return JSON‐ready results
"""


from scipy.stats import norm
import argparse
import json
import pandas as pd
import os


def letter_to_gpa(grade):
    """
    Convert a letter grade to its numeric GPA value.

    Excludes incomplete, withdrawal, pass, and non-pass grades.

    Args:
        grade (str): Letter grade (e.g., 'A', 'B+', 'NP').

    Returns:
        float or None: GPA value for valid grades; None for exclusions.
    """
    # Grades that should be excluded from GPA calculation
    excluded_grades = ["I", "W", "P", "NP"]
    
    # Return None for excluded grades to filter them out
    if grade in excluded_grades:
        return None
        
    # Standard GPA conversion for other grades
    conversion = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0  # F is worth 0 but included in GPA
    }
    return conversion.get(grade, 0.0)


def compute_z_score(sample_mean: float, population_mean: float, population_std: float) -> float:
    """
    Compute the Z-score for a sample mean.

    Uses formula: (sample_mean - population_mean) / population_std.

    Args:
        sample_mean (float): Sample mean (e.g., section GPA).
        population_mean (float): Population mean (e.g., group GPA).
        population_std (float): Population standard deviation.

    Returns:
        float: Calculated Z-score.

    Raises:
        ValueError: If population_std is zero.
    """
    if population_std == 0:
        raise ValueError("Population standard deviation cannot be zero.")
    return (sample_mean - population_mean) / population_std


def compute_p_value(z_score: float) -> float:
    """
    Calculate the two‐tailed p‐value from a Z-score.

    Args:
        z_score (float): Z-score value.

    Returns:
        float: Two‐tailed p‐value.
    """
    return 2 * (1 - norm.cdf(abs(z_score)))


def is_significant(z_score: float, threshold: float = 2.0) -> bool:
    """
    Determine if a Z-score is statistically significant.

    A Z-score is significant if |z_score| ≥ threshold.

    Args:
        z_score (float): Z-score value.
        threshold (float): Significance threshold (default 2.0).

    Returns:
        bool: True if significant, else False.
    """
    return abs(z_score) >= threshold


def calculate_section_stats(section_df):
    """
    Compute average GPA and count of valid grades for a section.

    Args:
        section_df (DataFrame): Must contain a 'Grade' column.

    Returns:
        tuple:
            mean_gpa (float): Average GPA of the section.
            count (int): Number of valid grades.
    """
    if section_df.empty:
        return 0, 0
    
    # Convert grades to GPA values and filter out excluded grades
    gpas = [letter_to_gpa(grade) for grade in section_df['Grade']]
    gpas = [gpa for gpa in gpas if gpa is not None]  # Filter out None values (excluded grades)
    
    # Calculate mean GPA
    mean_gpa = sum(gpas) / len(gpas) if gpas else 0
    
    return mean_gpa, len(gpas)


def calculate_group_stats(section_dfs):
    """
    Aggregate GPA data across sections to compute group statistics.

    Args:
        section_dfs (list of DataFrame): Each with a 'Grade' column.

    Returns:
        tuple:
            mean (float): Group mean GPA.
            std_dev (float): Group standard deviation.
    """
    all_gpas = []
    
    for df in section_dfs:
        if not df.empty:
            # Convert grades to GPA values and filter out excluded grades
            gpas = [letter_to_gpa(grade) for grade in df['Grade']]
            gpas = [gpa for gpa in gpas if gpa is not None]  # Filter out None values
            all_gpas.extend(gpas)
    
    if not all_gpas:
        return 0, 0
    
    # Calculate mean and standard deviation
    mean = sum(all_gpas) / len(all_gpas)
    variance = sum((x - mean) ** 2 for x in all_gpas) / len(all_gpas) if len(all_gpas) > 1 else 0
    std_dev = variance ** 0.5
    
    return mean, std_dev


def analyze_sections(run_file, grp_files, sec_files, threshold=2.0):
    """
    Load section files, compute Z-scores, and return analysis.

    Args:
        run_file (str): Path to this script (used to locate Sections folder).
        grp_files (list of str): Group‐level data files (currently unused).
        sec_files (list of str): Section filenames to analyze.
        threshold (float): Z-score threshold for significance (default 2.0).

    Returns:
        results (list of dict): Analysis per section, ready for JSON.
        DataFrame: Pandas DataFrame of results.
    """
    from FileReader import fileReader
    
    # Get base directory for sections path
    base_dir = os.path.dirname(os.path.dirname(run_file))
    sections_path = os.path.join(base_dir, "Sections")
    
    # Read all section files
    section_dfs = {}
    section_files = []
    
    for sec_file in sec_files:
        full_path = os.path.join(sections_path, sec_file)
        try:
            df = fileReader.readSEC(full_path)
            section_dfs[sec_file] = df
            section_files.append(df)
        except Exception as e:
            print(f"Error reading section {sec_file}: {e}")
    
    # Calculate group-level statistics
    group_mean, group_std = calculate_group_stats(section_files)
    
    # Calculate z-scores for each section
    results = []
    
    for sec_name, sec_df in section_dfs.items():
        sec_mean, sec_count = calculate_section_stats(sec_df)
        
        try:
            z_score = compute_z_score(sec_mean, group_mean, group_std)
            p_value = compute_p_value(z_score)
            significant = is_significant(z_score, threshold)
            
            results.append({
                'section': sec_name,
                'section_gpa': round(sec_mean, 3),
                'section_count': sec_count,
                'group_gpa': round(group_mean, 3),
                'group_std': round(group_std, 3),
                'z_score': round(z_score, 3),
                'p_value': round(p_value, 5),
                'significant': significant,
                'performance': 'Above Average' if z_score > 0 else 'Below Average' if z_score < 0 else 'Average'
            })
        except ValueError as e:
            # Handle division by zero
            results.append({
                'section': sec_name,
                'section_gpa': round(sec_mean, 3),
                'section_count': sec_count,
                'group_gpa': round(group_mean, 3),
                'group_std': round(group_std, 3),
                'z_score': 'N/A',
                'p_value': 'N/A',
                'significant': False,
                'error': str(e)
            })
    
    # Sort results by z-score (absolute value)
    results.sort(key=lambda x: abs(x['z_score']) if isinstance(x['z_score'], (int, float)) else 0, reverse=True)
    
    return results, pd.DataFrame(results)

