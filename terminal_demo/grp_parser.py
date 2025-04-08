"""
Group File Parser Module

This module parses .GRP files which contain a group name and references to section files.
"""

import os

def parse_grp_file(file_path):
    """
    Parses a .GRP file and returns the group name and a list of section file references.

    Parameters:
    file_path (str): Path to the .GRP file

    Returns:
    tuple: (group_name, section_files) where group_name is a string and section_files is a list of strings

    Raises:
    FileNotFoundError: If the file does not exist.
    ValueError: If the file does not have a .GRP extension or has invalid format.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if file has .GRP extension
    if not file_path.upper().endswith('.GRP'):
        raise ValueError(f"File must have .GRP extension: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
            
            if not lines:
                raise ValueError(f"Empty GRP file: {file_path}")
            
            # First line is the group name
            group_name = lines[0]
            
            # Remaining lines are section file references
            section_files = lines[1:]
            
            return group_name, section_files
            
    except Exception as e:
        raise ValueError(f"Error reading or parsing file {file_path}: {str(e)}")

def get_sections_from_grp(grp_file, sections_dir):
    """
    Gets the full paths to all section files referenced in a group file.

    Parameters:
    grp_file (str): Path to the .GRP file
    sections_dir (str): Directory containing section files

    Returns:
    list: List of full paths to section files
    """
    group_name, section_files = parse_grp_file(grp_file)
    
    # Create full paths to section files
    section_paths = []
    for section_file in section_files:
        section_path = os.path.join(sections_dir, section_file)
        section_paths.append(section_path)
    
    return group_name, section_paths

if __name__ == "__main__":
    # Example usage
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file_path = os.path.join(script_dir, "COMSC330_POC_Data", "Groups", "COMSC110.GRP")
    sections_dir = os.path.join(script_dir, "COMSC330_POC_Data", "Sections")
    
    print(f"Processing group file: {sample_file_path}")
    print("-" * 30)
    
    try:
        group_name, section_paths = get_sections_from_grp(sample_file_path, sections_dir)
        print(f"Group Name: {group_name}")
        print("Section Files:")
        for path in section_paths:
            print(f"  - {path}")
    except Exception as e:
        print(f"Error: {e}")