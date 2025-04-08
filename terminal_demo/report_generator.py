"""
Report Generator Module

This module provides functions to generate various reports from GPA data.
"""

import os
import pandas as pd
from gpa_calculator import identify_good_list, identify_work_list, perform_z_test

def generate_section_report(course_id, credit_hours, stats):
    """
    Generates a report for a single section.
    
    Parameters:
    course_id (str): Section identifier
    credit_hours (float): Credit hours for the section
    stats (dict): Dictionary with GPA statistics
    
    Returns:
    str: Formatted section report
    """
    report = [
        f"Report for Section: {course_id}",
        f"Credit Hours: {credit_hours}",
        "-" * 40,
        f"Number of Students: {stats['count']}",
        f"Average GPA: {stats['mean']:.2f}",
        f"Median GPA: {stats['median']:.2f}",
        f"Standard Deviation: {stats['std_dev']:.2f}",
        f"Range: {stats['min']:.1f} - {stats['max']:.1f}",
        "-" * 40
    ]
    
    # Add grade distribution
    grade_counts = stats['data']['Grade'].value_counts().sort_index()
    report.append("Grade Distribution:")
    for grade, count in grade_counts.items():
        percentage = count / stats['count'] * 100
        report.append(f"  {grade}: {count} ({percentage:.1f}%)")
    
    return "\n".join(report)

def generate_group_report(group_name, group_stats):
    """
    Generates a report for a group of sections.
    
    Parameters:
    group_name (str): Group identifier
    group_stats (dict): Dictionary with group statistics
    
    Returns:
    str: Formatted group report
    """
    aggregate = group_stats['aggregate']
    sections = group_stats['sections']
    
    report = [
        f"Group Report: {group_name}",
        "=" * 50,
        f"Number of Sections: {len(sections)}",
        f"Total Students: {aggregate['count']}",
        f"Group Average GPA: {aggregate['mean']:.2f}",
        f"Group Median GPA: {aggregate['median']:.2f}",
        f"Group Standard Deviation: {aggregate['std_dev']:.2f}",
        f"Range: {aggregate['min']:.1f} - {aggregate['max']:.1f}",
        "=" * 50,
        "\nSection Summary:",
        "-" * 50
    ]
    
    # Add section summaries
    section_rows = []
    for course_id, section_data in sections.items():
        stats = section_data['stats']
        section_rows.append({
            'Section': course_id,
            'Credits': section_data['credit_hours'],
            'Students': stats['count'],
            'Mean GPA': f"{stats['mean']:.2f}",
            'Median': f"{stats['median']:.2f}",
            'StdDev': f"{stats['std_dev']:.2f}"
        })
    
    # Convert to DataFrame for pretty printing
    section_df = pd.DataFrame(section_rows)
    report.append(section_df.to_string(index=False))
    
    # Add Z-test results
    if aggregate['std_dev'] > 0:
        report.append("\nZ-test Analysis:")
        report.append("-" * 50)
        for course_id, section_data in sections.items():
            stats = section_data['stats']
            z_score, p_value = perform_z_test(
                stats['mean'], 
                aggregate['mean'], 
                aggregate['std_dev']
            )
            significance = "Significant" if p_value < 0.05 else "Not Significant"
            direction = "Above" if z_score > 0 else "Below"
            report.append(f"{course_id}: {direction} average by {abs(z_score):.2f} standard deviations (p={p_value:.4f}) - {significance}")
    
    return "\n".join(report)

def generate_run_report(run_name, run_data):
    """
    Generates a report for an entire run.
    
    Parameters:
    run_name (str): Run identifier
    run_data (dict): Dictionary with group data
    
    Returns:
    str: Formatted run report
    """
    report = [
        f"Run Report: {run_name}",
        "=" * 60,
        f"Number of Groups: {len(run_data)}",
        "=" * 60,
    ]
    
    # Calculate overall statistics
    all_students = []
    for group_name, group_stats in run_data.items():
        all_students.append(group_stats['aggregate']['data'])
    
    if all_students:
        combined_df = pd.concat(all_students, ignore_index=True)
        
        report.extend([
            f"Total Students: {len(combined_df)}",
            f"Overall Average GPA: {combined_df['GPA'].mean():.2f}",
            f"Overall Median GPA: {combined_df['GPA'].median():.2f}",
            f"Overall Range: {combined_df['GPA'].min():.1f} - {combined_df['GPA'].max():.1f}",
            "=" * 60,
            "\nGroup Summary:",
            "-" * 60
        ])
        
        # Add group summaries
        group_rows = []
        for group_name, group_stats in run_data.items():
            agg = group_stats['aggregate']
            group_rows.append({
                'Group': group_name,
                'Sections': len(group_stats['sections']),
                'Students': agg['count'],
                'Mean GPA': f"{agg['mean']:.2f}",
                'Median': f"{agg['median']:.2f}",
                'StdDev': f"{agg['std_dev']:.2f}"
            })
            
        group_df = pd.DataFrame(group_rows)
        report.append(group_df.to_string(index=False))
    else:
        report.append("No data available for this run.")
    
    return "\n".join(report)

def generate_good_list_report(group_name, group_stats, threshold=3.5):
    """
    Generates a report of students on the Good List.
    
    Parameters:
    group_name (str): Group identifier
    group_stats (dict): Dictionary with group statistics
    threshold (float): GPA threshold for Good List
    
    Returns:
    str: Formatted Good List report
    """
    df = group_stats['aggregate']['data']
    good_list = identify_good_list(df, threshold)
    
    report = [
        f"Good List Report: {group_name}",
        f"Students with GPA >= {threshold}",
        "=" * 60,
        f"Number of Students: {len(good_list)} out of {len(df)} ({len(good_list)/len(df)*100:.1f}%)",
        "-" * 60
    ]
    
    if not good_list.empty:
        # Prepare data for display
        display_df = good_list[['LastName', 'FirstName', 'CourseID', 'GPA']].copy()
        display_df['GPA'] = display_df['GPA'].apply(lambda x: f"{x:.2f}")
        
        # Group by course
        for course, students in display_df.groupby('CourseID'):
            report.append(f"\nCourse: {course} ({len(students)} students)")
            report.append("-" * 40)
            
            # Format student list without the CourseID column
            student_list = students[['LastName', 'FirstName', 'GPA']]
            report.append(student_list.to_string(index=False))
    else:
        report.append("No students meet the Good List criteria.")
    
    return "\n".join(report)

def generate_work_list_report(group_name, group_stats, threshold=2.0):
    """
    Generates a report of students on the Work List.
    
    Parameters:
    group_name (str): Group identifier
    group_stats (dict): Dictionary with group statistics
    threshold (float): GPA threshold for Work List
    
    Returns:
    str: Formatted Work List report
    """
    df = group_stats['aggregate']['data']
    work_list = identify_work_list(df, threshold)
    
    report = [
        f"Work List Report: {group_name}",
        f"Students with GPA <= {threshold}",
        "=" * 60,
        f"Number of Students: {len(work_list)} out of {len(df)} ({len(work_list)/len(df)*100:.1f}%)",
        "-" * 60
    ]
    
    if not work_list.empty:
        # Prepare data for display
        display_df = work_list[['LastName', 'FirstName', 'CourseID', 'GPA']].copy()
        display_df['GPA'] = display_df['GPA'].apply(lambda x: f"{x:.2f}")
        
        # Group by course
        for course, students in display_df.groupby('CourseID'):
            report.append(f"\nCourse: {course} ({len(students)} students)")
            report.append("-" * 40)
            
            # Format student list without the CourseID column
            student_list = students[['LastName', 'FirstName', 'GPA']]
            report.append(student_list.to_string(index=False))
    else:
        report.append("No students meet the Work List criteria.")
    
    return "\n".join(report)

def save_report_to_file(report_text, file_path):
    """
    Saves a report to a text file.
    
    Parameters:
    report_text (str): The report content
    file_path (str): Path where the report should be saved
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(report_text)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False
