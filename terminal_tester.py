#!/usr/bin/env python3
# terminal_tester.py - Command-line interface to test grade analysis functionality

import os
import sys
from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
from GoodAndBadList import Lists
import pandas as pd

def display_menu():
    """Display the main menu options to the user."""
    print("\n" + "="*50)
    print("PGUA^2 Grade Analyzer - Terminal Tester")
    print("="*50)
    print("1. Load a RUN file")
    print("2. Display all groups from RUN file")
    print("3. Display all sections from groups")
    print("4. Display top performers (A, A-)")
    print("5. Display bottom performers (F, D-)")
    print("6. Export data to HTML")
    print("7. Read individual SEC file")
    print("8. Exit")
    print("="*50)
    return input("Select an option (1-8): ")

def find_run_files(base_dir="C:\\Users\\Alex\\Desktop\\CLASS - CODE\\Comp330\\COMSC330_POC_Data"):
    """Find all RUN files in the base directory and its subdirectories."""
    run_files = []
    
    # Check if the base directory exists
    if not os.path.exists(base_dir):
        print(f"Warning: Base directory '{base_dir}' does not exist.")
        return run_files
    
    # Walk through the directory tree and find .RUN files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.run'):
                run_files.append(os.path.join(root, file))
    
    return run_files

def export_to_html(df, file_type):
    """Export a dataframe to HTML file."""
    if df is None or df.empty:
        print("No data to export!")
        return
    
    filename = f"{file_type}_export.html"
    df.to_html(filename)
    print(f"Data exported to {os.path.abspath(filename)}")

def main():
    """Main program function."""
    run_file = None
    grp_files = None
    sec_files = None
    top_performers = None
    bottom_performers = None
    sec_data = None
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            # Load RUN file
            available_runs = find_run_files()
            
            if not available_runs:
                print("No RUN files found in the data directory!")
                custom_path = input("Would you like to enter a custom path? (y/n): ")
                if custom_path.lower() == 'y':
                    file_path = input("Enter the path to your .RUN file: ")
                    if not file_path.lower().endswith('.run'):
                        print("Error: Please provide a valid .RUN file!")
                        continue
                    
                    run_file = file_path
                    print(f"Successfully loaded RUN file: {run_file}")
                continue
            
            print("\nAvailable RUN files:")
            for i, run in enumerate(available_runs, 1):
                print(f"{i}. {os.path.basename(run)} ({run})")
            
            try:
                selection = input("\nSelect a file number or enter a custom path: ")
                if selection.isdigit() and 1 <= int(selection) <= len(available_runs):
                    run_file = available_runs[int(selection) - 1]
                else:
                    # Assume it's a custom path
                    if not selection.lower().endswith('.run'):
                        print("Error: Please provide a valid .RUN file!")
                        continue
                    run_file = selection
                    
                print(f"Successfully loaded RUN file: {run_file}")
            except Exception as e:
                print(f"Error loading RUN file: {e}")
        
        elif choice == '2':
            # Display groups
            if not run_file:
                print("Error: Please load a RUN file first (option 1)!")
                continue
                
            try:
                grp_files = runReader(run_file)
                print("\nGroups from RUN file:")
                for i, grp in enumerate(grp_files, 1):
                    print(f"{i}. {os.path.basename(grp)}")
            except Exception as e:
                print(f"Error reading groups: {e}")
        
        elif choice == '3':
            # Display sections
            if not grp_files:
                print("Error: Please load groups first (option 2)!")
                continue
                
            try:
                sec_files = grpReader(run_file, grp_files)
                print("\nSections from group files:")
                for i, sec in enumerate(sec_files, 1):
                    print(f"{i}. {sec}")
            except Exception as e:
                print(f"Error reading sections: {e}")
        
        elif choice == '4':
            # Display top performers
            if not run_file:
                print("Error: Please load a RUN file first (option 1)!")
                continue
                
            try:
                print("Loading top performers (A, A-)...")
                top_performers = Lists.goodList(run_file)
                
                if top_performers.empty:
                    print("No top performers found!")
                else:
                    print(f"\nFound {len(top_performers)} top performers:")
                    pd.set_option('display.max_rows', None)
                    print(top_performers)
                    pd.reset_option('display.max_rows')
            except Exception as e:
                print(f"Error getting top performers: {e}")
        
        elif choice == '5':
            # Display bottom performers
            if not run_file:
                print("Error: Please load a RUN file first (option 1)!")
                continue
                
            try:
                print("Loading bottom performers (F, D-)...")
                bottom_performers = Lists.badList(run_file)
                
                if bottom_performers.empty:
                    print("No bottom performers found!")
                else:
                    print(f"\nFound {len(bottom_performers)} bottom performers:")
                    pd.set_option('display.max_rows', None)
                    print(bottom_performers)
                    pd.reset_option('display.max_rows')
            except Exception as e:
                print(f"Error getting bottom performers: {e}")
        
        elif choice == '6':
            # Export data
            print("\nExport options:")
            print("1. Export top performers")
            print("2. Export bottom performers")
            print("3. Export SEC file data")
            export_choice = input("Select data to export (1-3): ")
            
            if export_choice == '1':
                if top_performers is None:
                    print("Error: Please load top performers first (option 4)!")
                    continue
                export_to_html(top_performers, "top_performers")
            elif export_choice == '2':
                if bottom_performers is None:
                    print("Error: Please load bottom performers first (option 5)!")
                    continue
                export_to_html(bottom_performers, "bottom_performers")
            elif export_choice == '3':
                if sec_data is None:
                    print("Error: Please read a SEC file first (option 7)!")
                    continue
                export_to_html(sec_data, "sec_data")
            else:
                print("Invalid export option!")
        
        elif choice == '7':
            # Read individual SEC file
            data_dir = "COMSC330_POC_Data"
            sec_files_found = []
            
            # Find all SEC files in the data directory
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.lower().endswith('.sec'):
                        sec_files_found.append(os.path.join(root, file))
            
            if not sec_files_found:
                print("No SEC files found in the data directory!")
                file_path = input("Enter the path to your .SEC file: ")
                if not file_path.lower().endswith('.sec'):
                    print("Error: Please provide a valid .SEC file!")
                    continue
            else:
                print("\nAvailable SEC files:")
                for i, sec in enumerate(sec_files_found, 1):
                    print(f"{i}. {os.path.basename(sec)} ({sec})")
                
                selection = input("\nSelect a file number or enter a custom path: ")
                if selection.isdigit() and 1 <= int(selection) <= len(sec_files_found):
                    file_path = sec_files_found[int(selection) - 1]
                else:
                    # Assume it's a custom path
                    if not selection.lower().endswith('.sec'):
                        print("Error: Please provide a valid .SEC file!")
                        continue
                    file_path = selection
            
            try:
                print(f"Reading SEC file: {file_path}")
                sec_data = fileReader.readSEC(file_path)
                
                if sec_data.empty:
                    print("No data found in the SEC file!")
                else:
                    print("\nSEC file data:")
                    pd.set_option('display.max_rows', None)
                    print(sec_data)
                    pd.reset_option('display.max_rows')
            except Exception as e:
                print(f"Error reading SEC file: {e}")
        
        elif choice == '8':
            # Exit
            print("Exiting program. Goodbye!")
            sys.exit(0)
        
        else:
            print("Invalid option! Please select a number between 1 and 8.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()