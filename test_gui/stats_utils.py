"""
Statistical Utilities Module for Grade Analysis Tool

This module provides statistical functions for analyzing grade data,
such as z-tests for comparing section GPAs to group averages.
"""

import scipy.stats as stats
import numpy as np
import pandas as pd

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
    # Handle edge cases to avoid division by zero
    if group_std == 0 or np.isnan(group_std) or np.isnan(section_gpa) or np.isnan(group_mean):
        return 0, 1.0  # No difference / not significant
    
    # Calculate Z-score
    z_score = (section_gpa - group_mean) / group_std
    
    # Get two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    return z_score, p_value

def calculate_section_stats(df, section_id=None):
    """
    Calculate statistics for a section or filtered DataFrame.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing student data with GPA column
    section_id (str, optional): If provided, filters the DataFrame for this section
    
    Returns:
    dict: Statistics including mean, median, std_dev, etc.
    """
    # Filter by section if section_id is provided
    if section_id is not None and 'CourseID' in df.columns:
        section_df = df[df['CourseID'] == section_id]
    else:
        section_df = df
    
    # If no data or no GPA column, return empty stats
    if section_df.empty or 'GPA' not in section_df.columns:
        return {
            'mean': np.nan,
            'median': np.nan,
            'std_dev': np.nan,
            'count': 0,
            'min': np.nan,
            'max': np.nan,
            'data': section_df
        }
    
    return {
        'mean': section_df['GPA'].mean(),
        'median': section_df['GPA'].median(),
        'std_dev': section_df['GPA'].std(),
        'count': len(section_df),
        'min': section_df['GPA'].min(),
        'max': section_df['GPA'].max(),
        'data': section_df
    }

def compare_section_to_group(section_df, group_df):
    """
    Compare a section's performance to the overall group.
    
    Parameters:
    section_df (pd.DataFrame): DataFrame containing section student data
    group_df (pd.DataFrame): DataFrame containing all group student data
    
    Returns:
    dict: Comparison statistics including z-score and p-value
    """
    # Calculate statistics
    section_stats = calculate_section_stats(section_df)
    group_stats = calculate_section_stats(group_df)
    
    # Perform z-test
    z_score, p_value = perform_z_test(
        section_stats['mean'],
        group_stats['mean'],
        group_stats['std_dev']
    )
    
    return {
        'section_stats': section_stats,
        'group_stats': group_stats,
        'z_score': z_score,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'direction': 'above' if z_score > 0 else 'below',
        'interpretation': get_significance_interpretation(z_score, p_value)
    }

def get_significance_interpretation(z_score, p_value):
    """
    Get a human-readable interpretation of z-score and p-value.
    
    Parameters:
    z_score (float): Z-score from comparison
    p_value (float): P-value from comparison
    
    Returns:
    str: Interpretation of results
    """
    if p_value >= 0.05:
        return "Not significantly different from average"
    
    direction = "above" if z_score > 0 else "below"
    magnitude = abs(z_score)
    
    if magnitude < 1.0:
        strength = "slightly"
    elif magnitude < 2.0:
        strength = "moderately"
    elif magnitude < 3.0:
        strength = "considerably"
    else:
        strength = "extremely"
    
    return f"Significantly {strength} {direction} average (p={p_value:.4f})"
