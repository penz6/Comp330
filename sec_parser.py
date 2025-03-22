"""
SEC File Parser for GPA Analysis Tool

This module provides functionality to parse .SEC files containing student records
as part of the GPA Analysis Tool. It serves as the first layer in processing the 
hierarchical data structure (sections → groups → runs) described in the project.

The parser extracts course information, student data, and calculates initial GPA
values that will be aggregated at higher levels by other components of the system.
"""

import pandas as pd
import os
import re

def parse_sec_file(file_path):
    """
    Parse a .SEC file and return its contents as a pandas DataFrame.
    
    This function serves as the entry point for processing section data in the
    GPA Analysis Tool's hierarchical structure. Section data is the fundamental
    unit that will later be grouped and analyzed in runs.
    
    Parameters:
    file_path (str): Path to the .SEC file
    
    Returns:
    pandas.DataFrame: DataFrame containing the course info and student records
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if file has .SEC extension
    if not file_path.upper().endswith('.SEC'):
        raise ValueError(f"File must have .SEC extension: {file_path}")
    
    # Initialize data structures
    course_info = {}
    student_records = []
    
    # Read file
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Parse header line (course ID and credit hours)
        if lines:
            header = lines[0].strip().split()
            if len(header) >= 2:
                course_info['course_id'] = header[0]
                course_info['credit_hours'] = float(header[1])
            else:
                raise ValueError(f"Invalid header format in file: {file_path}")
        
        # Parse student records
        for line in lines[1:]:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Use regex to properly parse quoted, comma-separated values
            pattern = r'"([^"]*)"'
            values = re.findall(pattern, line)
            
            if len(values) >= 3:
                # Split full name into first and last
                name_parts = values[0].split(',')
                last_name = name_parts[0].strip()
                first_name = name_parts[1].strip() if len(name_parts) > 1 else ""
                
                # Create student record
                student = {
                    'last_name': last_name,
                    'first_name': first_name,
                    'student_id': values[1],
                    'grade': values[2]
                }
                student_records.append(student)
    
    # Create DataFrame from student records
    df = pd.DataFrame(student_records)
    
    # Add course information to each row
    for key, value in course_info.items():
        df[key] = value
    
    # Extract section information from filename
    # This will be used when aggregating sections into groups
    file_basename = os.path.basename(file_path)
    section_id = file_basename.split('.')[0]
    df['section_id'] = section_id
    
    # For compatibility with the hierarchical structure mentioned in README
    # - Sections are part of Groups, which are part of Runs
    df['source_file'] = file_basename
    
    return df

def calculate_gpa(grade):
    """
    Convert letter grade to GPA value.
    
    This function implements the core GPA calculation logic mentioned in the README,
    translating letter grades to their numerical equivalents for further analysis.
    
    Parameters:
    grade (str): Letter grade (A, A-, B+, etc.)
    
    Returns:
    float: GPA value
    """
    # Standard 4.0 scale grade mapping
    grade_map = {
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
    return grade_map.get(grade, 0.0)

def calculate_section_stats(df):
    """
    Calculate GPA statistics for a section.
    
    This function provides section-level analytics as mentioned in the README,
    serving as the foundation for higher-level aggregation at group and run levels.
    
    Parameters:
    df (pandas.DataFrame): DataFrame containing student records
    
    Returns:
    dict: Dictionary with section statistics
    """
    # Add GPA column
    df['gpa'] = df['grade'].apply(calculate_gpa)
    
    # Calculate weighted GPA based on credit hours
    credit_hours = df['credit_hours'].iloc[0] if not df.empty else 0
    weighted_gpa = df['gpa'].mean()
    
    # Prepare statistics that will be used in reporting functionality
    stats = {
        'section_id': df['section_id'].iloc[0] if not df.empty else 'Unknown',
        'course_id': df['course_id'].iloc[0] if not df.empty else 'Unknown',
        'credit_hours': credit_hours,
        'student_count': len(df),
        'mean_gpa': weighted_gpa,
        'min_gpa': df['gpa'].min() if not df.empty else 0,
        'max_gpa': df['gpa'].max() if not df.empty else 0,
        'total_quality_points': (df['gpa'] * credit_hours).sum() if not df.empty else 0
    }
    
    return stats

def process_section_file(file_path):
    """
    Process a section file completely - parse data and calculate statistics.
    
    This is a convenience function that combines parsing and statistics calculation,
    making it easier to integrate this module with the Group and Run processors
    that will be developed as mentioned in the README.
    
    Parameters:
    file_path (str): Path to the .SEC file
    
    Returns:
    tuple: (DataFrame with parsed data, Dictionary with section statistics)
    """
    df = parse_sec_file(file_path)
    stats = calculate_section_stats(df)
    return df, stats




# Example usage with detailed explanations
if __name__ == "__main__":
    print("SEC FILE PARSER DEMONSTRATION")
    print("=" * 50)
    print("This module processes .SEC files containing student records and course information.")
    print("Below are examples of how to use the parser functions in your code.\n")
    
    # Example 1: Process a single file
    sample_file = r"C:\Users\Alex\Desktop\CLASS - CODE\Comp330\COMSC330_POC_Data\Sections\COMSC110.01S25.SEC"
    print(f"EXAMPLE 1: Processing a single section file")
    print(f"File: {sample_file}")
    
    try:
        # Basic usage - parse file and get statistics
        section_data, section_stats = process_section_file(sample_file)
        
        print("\nRESULTS:")
        print(f"Successfully parsed file with {len(section_data)} student records")
        
        # Show how to access the DataFrame columns
        print("\n1. Accessing the DataFrame columns:")
        print(f"Available columns: {', '.join(section_data.columns.tolist())}")
        print("\nFirst 3 students:")
        for i, row in section_data.head(3).iterrows():
            print(f"  Student: {row['first_name']} {row['last_name']}, ID: {row['student_id']}, Grade: {row['grade']}, GPA: {row['gpa']}")
        
        # Show how to access the statistics dictionary
        print("\n2. Accessing section statistics:")
        for key, value in section_stats.items():
            print(f"  {key}: {value}")
        
        # Show common data operations
        print("\n3. Common data operations:")
        print(f"  Average GPA: {section_data['gpa'].mean():.2f}")
        print(f"  Number of A grades: {len(section_data[section_data['grade'] == 'A'])}")
        print(f"  Grade distribution:")
        grade_counts = section_data['grade'].value_counts()
        for grade, count in grade_counts.items():
            print(f"    {grade}: {count} students")
    
    except FileNotFoundError:
        print("ERROR: File not found. Please check the file path.")
        print("TIP: Make sure the file exists and the path is correct.")
    except ValueError as e:
        print(f"ERROR: Invalid file format - {str(e)}")
        print("TIP: Ensure the file is a properly formatted .SEC file.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred - {str(e)}")
    
    # Example 2: How to process multiple files
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Processing multiple section files")
    
    # List of sample files (adjust paths as needed)
    sample_files = [
        r"C:\Users\Alex\Desktop\CLASS - CODE\Comp330\COMSC330_POC_Data\Sections\COMSC110.01S25.SEC",
        r"C:\Users\Alex\Desktop\CLASS - CODE\Comp330\COMSC330_POC_Data\Sections\COMSC330.01S25.SEC"
    ]
    
    print("Processing multiple files and combining results:")
    all_section_data = []
    all_section_stats = []
    
    for file_path in sample_files:
        try:
            print(f"\nProcessing: {os.path.basename(file_path)}")
            df, stats = process_section_file(file_path)
            all_section_data.append(df)
            all_section_stats.append(stats)
            print(f"Success: Found {len(df)} students with average GPA {stats['mean_gpa']:.2f}")
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {str(e)}")
    
    # Combine all data (useful for group or run processing)
    if all_section_data:
        combined_data = pd.concat(all_section_data, ignore_index=True)
        print(f"\nCombined data: {len(combined_data)} total student records")
        print(f"Overall average GPA: {combined_data['gpa'].mean():.2f}")
    
    print("\n" + "=" * 50)
    print("USAGE NOTES:")
    print("1. The 'section_data' DataFrame contains all student and course information")
    print("2. The 'section_stats' dictionary contains pre-calculated statistics")
    print("3. Use section_data.columns to see all available data fields")
    print("4. This module is the first step in the GPA Analysis Tool's process flow")
    print("5. The parsed data can be passed to Group (.GRP) and Run (.RUN) processors")
