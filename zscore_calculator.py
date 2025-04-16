"""
zscore_calculator.py

Provides simple Z-score calculations for section vs. group GPA comparisons,
plus a command-line interface that outputs results in JSON.
"""

from scipy.stats import norm
import argparse
import json
import pandas as pd
import os

def letter_to_gpa(grade):
    """
    Convert letter grade to GPA value.
    F grade = 0.0 points (included in GPA)
    I, W, P, NP grades are excluded from GPA calculations
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
    Compute the Z-score: (sample_mean - population_mean) / population_std.
    Raises ValueError if population_std is zero.
    """
    if population_std == 0:
        raise ValueError("Population standard deviation cannot be zero.")
    return (sample_mean - population_mean) / population_std


def compute_p_value(z_score: float) -> float:
    """
    Compute two-tailed p-value for a given Z-score.
    """
    return 2 * (1 - norm.cdf(abs(z_score)))


def is_significant(z_score: float, threshold: float = 2.0) -> bool:
    """
    Returns True if z≤-2 or z≥2 (or custom threshold).
    """
    return abs(z_score) >= threshold

def calculate_section_stats(section_df):
    """Calculate GPA statistics for a section."""
    if section_df.empty:
        return 0, 0
    
    # Convert grades to GPA values and filter out excluded grades
    gpas = [letter_to_gpa(grade) for grade in section_df['Grade']]
    gpas = [gpa for gpa in gpas if gpa is not None]  # Filter out None values (excluded grades)
    
    # Calculate mean GPA
    mean_gpa = sum(gpas) / len(gpas) if gpas else 0
    
    return mean_gpa, len(gpas)

def calculate_group_stats(section_dfs):
    """Calculate group-level GPA statistics."""
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
    Analyze sections using z-scores.
    Z-scores of ≤-2 or ≥2 are considered significant by default.
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
                'section_gpa': round(sec_mean, 2),
                'section_count': sec_count,
                'group_gpa': round(group_mean, 2),
                'group_std': round(group_std, 2),
                'z_score': round(z_score, 2),
                'p_value': round(p_value, 4),
                'significant': significant,
                'performance': 'Above Average' if z_score > 0 else 'Below Average' if z_score < 0 else 'Average'
            })
        except ValueError as e:
            # Handle division by zero
            results.append({
                'section': sec_name,
                'section_gpa': round(sec_mean, 2),
                'section_count': sec_count,
                'group_gpa': round(group_mean, 2),
                'group_std': round(group_std, 2),
                'z_score': 'N/A',
                'p_value': 'N/A',
                'significant': False,
                'error': str(e)
            })
    
    # Sort results by z-score (absolute value)
    results.sort(key=lambda x: abs(x['z_score']) if isinstance(x['z_score'], (int, float)) else 0, reverse=True)
    
    return results, pd.DataFrame(results)

