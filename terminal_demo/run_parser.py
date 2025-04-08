"""
Run File Parser Module

This module parses .RUN files which contain a run name and references to group files.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from terminal_demo.grp_parser import get_sections_from_grp

def parse_run_file(file_path):
    """
    Parses a .RUN file and returns the run name and a list of group file references.

    Parameters:
    file_path (str): Path to the .RUN file

    Returns:
    tuple: (run_name, group_files) where run_name is a string and group_files is a list of strings

    Raises:
    FileNotFoundError: If the file does not exist.
    ValueError: If the file does not have a .RUN extension or has invalid format.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if file has .RUN extension
    if not file_path.upper().endswith('.RUN'):
        raise ValueError(f"File must have .RUN extension: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
            
            if not lines:
                raise ValueError(f"Empty RUN file: {file_path}")
            
            # First line is the run name
            run_name = lines[0]
            
            # Remaining lines are group file references
            group_files = lines[1:]
            
            return run_name, group_files
            
    except Exception as e:
        raise ValueError(f"Error reading or parsing file {file_path}: {str(e)}")

def get_groups_from_run(run_file, groups_dir, sections_dir):
    """
    Gets all groups and their section files referenced in a run file.

    Parameters:
    run_file (str): Path to the .RUN file
    groups_dir (str): Directory containing group files
    sections_dir (str): Directory containing section files

    Returns:
    tuple: (run_name, groups_data) where groups_data is a dictionary mapping 
           group names to lists of section file paths
    """
    run_name, group_files = parse_run_file(run_file)
    
    # Process each group file
    groups_data = {}
    for group_file in group_files:
        group_path = os.path.join(groups_dir, group_file)
        try:
            group_name, section_paths = get_sections_from_grp(group_path, sections_dir)
            
            # Verify that each section file exists before adding to groups_data
            valid_section_paths = []
            for path in section_paths:
                if os.path.exists(path):
                    valid_section_paths.append(path)
                else:
                    print(f"Warning: Section file not found: {path}")
            
            # Only add the group if it has valid section files
            if valid_section_paths:
                groups_data[group_name] = valid_section_paths
            else:
                print(f"Warning: No valid section files found for group: {group_name}")
                
        except Exception as e:
            print(f"Error processing group file {group_file}: {e}")
            # Continue processing other groups rather than failing completely
            continue
    
    return run_name, groups_data

if __name__ == "__main__":
    # Example usage
    sample_file_path = r"COMSC330_POC_Data\Runs\SPRING25.RUN"
    groups_dir = r"COMSC330_POC_Data\Groups"
    sections_dir = r"COMSC330_POC_Data\Sections"
    
    print(f"Processing run file: {sample_file_path}")
    print("-" * 30)
    
    try:
        run_name, groups_data = get_groups_from_run(sample_file_path, groups_dir, sections_dir)
        print(f"Run Name: {run_name}")
        print("Groups and Sections:")
        for group_name, section_paths in groups_data.items():
            print(f"Group: {group_name}")
            for path in section_paths:
                print(f"  - {path}")
    except Exception as e:
        print(f"Error: {e}")
