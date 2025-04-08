"""
Simplified SEC File Parser for CSV Output
This module parses a .SEC file and outputs student data in CSV format.
"""

import os
import re

def format_sec_data_as_csv(file_path):
    """
    Parses a .SEC file and returns the student data in a specific CSV format.

    Parameters:
    file_path (str): Path to the .SEC file

    Returns:
    str: A string containing the formatted data.
    
    Raises:
    FileNotFoundError: If the file does not exist.
    ValueError: If the file does not have a .SEC extension or has invalid format.
    """
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check if file has .SEC extension
    if not file_path.upper().endswith('.SEC'):
        raise ValueError(f"File must have .SEC extension: {file_path}")

    student_lines = []
    # Using a header that matches the data columns being extracted
    header = '"LastName","FirstName","StudentID","Grade"' 

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            # Skip header line (course info) - assuming it's always the first line
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
                    student_id = values[1]
                    grade = values[2]
                    
                    # Format the output line
                    formatted_line = f'"{last_name}","{first_name}","{student_id}","{grade}"'
                    student_lines.append(formatted_line)
                else:
                    # Handle lines that don't match the expected format if necessary
                    # For now, we'll just skip them
                    print(f"Warning: Skipping malformed line in {file_path}: {line}")
                    
    except Exception as e:
        raise ValueError(f"Error reading or parsing file {file_path}: {str(e)}")

    # Combine header and data lines
    csv_output = header + "\n" + "\n".join(student_lines)
    
    return csv_output

def print_formatted_data(file_path):
    """
    Helper method to call format_sec_data_as_csv and print the result.

    Parameters:
    file_path (str): Path to the .SEC file
    """
    try:
        csv_data = format_sec_data_as_csv(file_path)
        print(csv_data)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
if __name__ == "__main__":
    # Define the path to the SEC file you want to process
    # Make sure this path is correct for your system
    # This path is relative and assumes the current working directory is set correctly.
    # It may fail if the script is run from a different directory. Consider using an absolute path
    # or a path relative to the script's location:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file_path = os.path.join(script_dir, "..", "COMSC330_POC_Data", "Sections", "COMSC110.01S25.SEC")
    
    print(f"Processing file: {sample_file_path}")
    print("-" * 30)
    
    # Call the helper method to process the file and print the output
    print_formatted_data(sample_file_path)
    
    print("-" * 30)
    print("Processing complete.")
