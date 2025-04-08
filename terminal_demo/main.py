"""
GPA Analysis Tool - Main Application

This module provides a command-line interface for the GPA Analysis Tool,
allowing users to process run files, calculate GPAs, and generate reports.
"""

import os
import sys
from run_parser import get_groups_from_run
from gpa_calculator import calculate_group_gpa
from report_generator import (
    generate_section_report, 
    generate_group_report, 
    generate_run_report,
    generate_good_list_report,
    generate_work_list_report,
    save_report_to_file
)

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a formatted header."""
    clear_screen()
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)
    print()

def get_data_directories():
    """
    Gets the base directory and subdirectories for data files.
    
    Returns:
    tuple: (base_dir, runs_dir, groups_dir, sections_dir)
    """
    # Check if we're in the expected directory structure
    current_dir = os.getcwd()
    
    # Try to find the data directory
    data_dir = os.path.join(current_dir, "COMSC330_POC_Data")
    if not os.path.exists(data_dir):
        # If not found, prompt user for the path
        print("Data directory not found in the current location.")
        data_dir = input("Please enter the path to the data directory: ")
        
        if not os.path.exists(data_dir):
            print(f"Error: Directory not found: {data_dir}")
            sys.exit(1)
    
    # Set up subdirectories
    runs_dir = os.path.join(data_dir, "Runs")
    groups_dir = os.path.join(data_dir, "Groups")
    sections_dir = os.path.join(data_dir, "Sections")
    
    # Verify directories exist
    for directory in [runs_dir, groups_dir, sections_dir]:
        if not os.path.exists(directory):
            print(f"Error: Required directory not found: {directory}")
            sys.exit(1)
    
    return data_dir, runs_dir, groups_dir, sections_dir

def list_files(directory, extension):
    """
    Lists all files with the given extension in a directory.
    
    Parameters:
    directory (str): Directory to search
    extension (str): File extension to filter by
    
    Returns:
    list: List of matching files
    """
    return [f for f in os.listdir(directory) if f.upper().endswith(extension.upper())]

def select_file(directory, extension, prompt):
    """
    Prompts the user to select a file from the directory.
    
    Parameters:
    directory (str): Directory containing the files
    extension (str): File extension to filter by
    prompt (str): Message to display to the user
    
    Returns:
    str: Path to the selected file
    """
    files = list_files(directory, extension)
    
    if not files:
        print(f"No {extension} files found in {directory}")
        return None
    
    print(prompt)
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(files):
                return os.path.join(directory, files[choice-1])
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Please enter a valid number")

def process_run(run_file, groups_dir, sections_dir):
    """
    Processes a run file and calculates GPAs for all groups and sections.
    
    Parameters:
    run_file (str): Path to the run file
    groups_dir (str): Directory containing group files
    sections_dir (str): Directory containing section files
    
    Returns:
    tuple: (run_name, run_data) where run_data is a dictionary with group statistics
    """
    print(f"Processing run file: {os.path.basename(run_file)}")
    
    # Verify the directories exist
    for dir_path, dir_name in [(groups_dir, "Groups"), (sections_dir, "Sections")]:
        if not os.path.exists(dir_path):
            print(f"Warning: {dir_name} directory not found: {dir_path}")
            print("Creating directory...")
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
                return None, {}
    
    try:
        run_name, groups_data = get_groups_from_run(run_file, groups_dir, sections_dir)
        
        # Check if we got any groups back
        if not groups_data:
            print("Warning: No valid groups found in the run file.")
            return run_name, {}
        
        # Process each group
        run_results = {}
        for group_name, section_paths in groups_data.items():
            print(f"  Processing group: {group_name}")
            
            # Check if we have any sections to process
            if not section_paths:
                print(f"  Warning: No valid section files found for group: {group_name}")
                continue
                
            group_stats = calculate_group_gpa(section_paths)
            
            # Only add groups with data
            if group_stats['sections']:
                run_results[group_name] = group_stats
            else:
                print(f"  Warning: No data processed for group: {group_name}")
        
        return run_name, run_results
        
    except Exception as e:
        print(f"Error processing run file: {e}")
        return None, {}

def show_main_menu():
    """
    Displays the main menu and returns the user's choice.
    
    Returns:
    int: User's menu choice
    """
    print_header("GPA ANALYSIS TOOL")
    print("1. Process Run File")
    print("2. View Reports Menu")
    print("3. Exit")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= 3:
                return choice
            else:
                print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")

def show_reports_menu():
    """
    Displays the reports menu and returns the user's choice.
    
    Returns:
    int: User's menu choice
    """
    print_header("REPORTS MENU")
    print("1. Run Summary Report")
    print("2. Group Reports")
    print("3. Good List Reports")
    print("4. Work List Reports")
    print("5. Return to Main Menu")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= 5:
                return choice
            else:
                print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")

def save_or_display_report(report_text, default_filename):
    """
    Asks the user whether to save or display the report.
    
    Parameters:
    report_text (str): The report content
    default_filename (str): Default filename for saving the report
    """
    print("\nReport generated.")
    print("1. Display report")
    print("2. Save to file")
    print("3. Both")
    print("4. Cancel")
    
    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if choice == 1:
                print("\n" + report_text)
                input("\nPress Enter to continue...")
                break
            elif choice == 2:
                filename = input(f"Enter filename [{default_filename}]: ") or default_filename
                if save_report_to_file(report_text, filename):
                    print(f"Report saved to {filename}")
                input("\nPress Enter to continue...")
                break
            elif choice == 3:
                print("\n" + report_text)
                filename = input(f"\nEnter filename [{default_filename}]: ") or default_filename
                if save_report_to_file(report_text, filename):
                    print(f"Report saved to {filename}")
                input("\nPress Enter to continue...")
                break
            elif choice == 4:
                break
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")

def main():
    """Main application function."""
    # Get data directories
    data_dir, runs_dir, groups_dir, sections_dir = get_data_directories()
    
    # State to store processed run data
    current_run_name = None
    current_run_data = None
    
    while True:
        choice = show_main_menu()
        
        if choice == 1:  # Process Run File
            run_file = select_file(runs_dir, ".RUN", "\nSelect a run file to process:")
            
            if run_file:
                try:
                    current_run_name, current_run_data = process_run(run_file, groups_dir, sections_dir)
                    
                    if not current_run_data:
                        print("\nWarning: No valid data was processed from the run file.")
                        print("Possible causes:")
                        print("- Missing section files")
                        print("- Invalid group files")
                        print("- File format errors")
                        print("\nPlease check your data directory and try again.")
                    else:
                        print(f"\nRun '{current_run_name}' processed successfully.")
                        print(f"Processed {len(current_run_data)} groups.")
                    
                    input("\nPress Enter to continue...")
                except Exception as e:
                    print(f"\nError processing run: {e}")
                    input("\nPress Enter to continue...")
        
        elif choice == 2:  # View Reports Menu
            if not current_run_data:
                print("\nNo run data available. Please process a run file first.")
                input("\nPress Enter to continue...")
                continue
            
            report_choice = show_reports_menu()
            
            if report_choice == 1:  # Run Summary Report
                report = generate_run_report(current_run_name, current_run_data)
                save_or_display_report(report, f"run_report_{current_run_name}.txt")
            
            elif report_choice == 2:  # Group Reports
                if not current_run_data:
                    print("\nNo run data available.")
                    input("\nPress Enter to continue...")
                    continue
                
                print_header("SELECT GROUP FOR REPORT")
                groups = list(current_run_data.keys())
                
                for i, group in enumerate(groups, 1):
                    print(f"{i}. {group}")
                
                try:
                    group_choice = int(input("\nEnter your choice: "))
                    if 1 <= group_choice <= len(groups):
                        group_name = groups[group_choice-1]
                        group_stats = current_run_data[group_name]
                        report = generate_group_report(group_name, group_stats)
                        save_or_display_report(report, f"group_report_{group_name}.txt")
                except ValueError:
                    print("Invalid choice. Returning to menu.")
                    input("\nPress Enter to continue...")
            
            elif report_choice == 3:  # Good List Reports
                if not current_run_data:
                    print("\nNo run data available.")
                    input("\nPress Enter to continue...")
                    continue
                
                print_header("SELECT GROUP FOR GOOD LIST REPORT")
                groups = list(current_run_data.keys())
                
                for i, group in enumerate(groups, 1):
                    print(f"{i}. {group}")
                
                try:
                    group_choice = int(input("\nEnter your choice: "))
                    if 1 <= group_choice <= len(groups):
                        group_name = groups[group_choice-1]
                        group_stats = current_run_data[group_name]
                        
                        threshold = input("\nEnter GPA threshold (default: 3.5): ")
                        threshold = float(threshold) if threshold else 3.5
                        
                        report = generate_good_list_report(group_name, group_stats, threshold)
                        save_or_display_report(report, f"good_list_{group_name}.txt")
                except ValueError:
                    print("Invalid choice. Returning to menu.")
                    input("\nPress Enter to continue...")
            
            elif report_choice == 4:  # Work List Reports
                if not current_run_data:
                    print("\nNo run data available.")
                    input("\nPress Enter to continue...")
                    continue
                
                print_header("SELECT GROUP FOR WORK LIST REPORT")
                groups = list(current_run_data.keys())
                
                for i, group in enumerate(groups, 1):
                    print(f"{i}. {group}")
                
                try:
                    group_choice = int(input("\nEnter your choice: "))
                    if 1 <= group_choice <= len(groups):
                        group_name = groups[group_choice-1]
                        group_stats = current_run_data[group_name]
                        
                        threshold = input("\nEnter GPA threshold (default: 2.0): ")
                        threshold = float(threshold) if threshold else 2.0
                        
                        report = generate_work_list_report(group_name, group_stats, threshold)
                        save_or_display_report(report, f"work_list_{group_name}.txt")
                except ValueError:
                    print("Invalid choice. Returning to menu.")
                    input("\nPress Enter to continue...")
            
            # Option 5 returns to the main menu automatically
        
        elif choice == 3:  # Exit
            print("\nThank you for using the GPA Analysis Tool. Goodbye!")
            break

if __name__ == "__main__":
    main()
