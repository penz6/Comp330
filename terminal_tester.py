#!/usr/bin/env python3
# terminal_tester.py - Command-line interface to test grade analysis functionality

import os
import sys
from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
from GoodAndBadList import Lists
import pandas as pd
from zscore_calculator import analyze_sections

class TerminalTester:
    def __init__(self):
        self.run_file = None
        self.grp_files = None
        self.sec_files = None
        self.top_performers = None
        self.bottom_performers = None
        self.sec_data = None
        self.zscore_results = None
        self.handlers = {
            '1': self.load_run,
            '2': self.display_groups,
            '3': self.display_sections,
            '4': self.display_top_performers,
            '5': self.display_bottom_performers,
            '6': self.export_data,
            '7': self.read_sec_file,
            '8': self.perform_zscore,
            '9': self.exit_program
        }


    def display_menu(self):
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
        print("8. Perform Z-score analysis")
        print("9. Exit")
        print("="*50)
        return input("Select an option (1-9): ")


    def find_run_files(self, base_dir="C:\\Users\\Alex\\Desktop\\CLASS - CODE\\Comp330\\COMSC330_POC_Data"):
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


    def export_to_html(self, df, file_type):
        """Export a dataframe to HTML file."""
        if df is None or df.empty:
            print("No data to export!")
            return
        
        filename = f"{file_type}_export.html"
        df.to_html(filename)
        print(f"Data exported to {os.path.abspath(filename)}")


    def load_run(self):
        """Load a RUN file."""
        available_runs = self.find_run_files()
        
        if not available_runs:
            print("No RUN files found in the data directory!")
            custom_path = input("Would you like to enter a custom path? (y/n): ")
            if custom_path.lower() == 'y':
                file_path = input("Enter the path to your .RUN file: ")
                if not file_path.lower().endswith('.run'):
                    print("Error: Please provide a valid .RUN file!")
                    return
                
                self.run_file = file_path
                print(f"Successfully loaded RUN file: {self.run_file}")
            return
        
        print("\nAvailable RUN files:")
        for i, run in enumerate(available_runs, 1):
            print(f"{i}. {os.path.basename(run)} ({run})")
        
        try:
            selection = input("\nSelect a file number or enter a custom path: ")
            if selection.isdigit() and 1 <= int(selection) <= len(available_runs):
                self.run_file = available_runs[int(selection) - 1]
            else:
                # Assume it's a custom path
                if not selection.lower().endswith('.run'):
                    print("Error: Please provide a valid .RUN file!")
                    return
                self.run_file = selection
                
            print(f"Successfully loaded RUN file: {self.run_file}")
        except Exception as e:
            print(f"Error loading RUN file: {e}")


    def display_groups(self):
        """Display groups from the loaded RUN file."""
        if not self.run_file:
            print("Error: Please load a RUN file first (option 1)!")
            return
            
        try:
            self.grp_files = runReader(self.run_file)
            print("\nGroups from RUN file:")
            for i, grp in enumerate(self.grp_files, 1):
                print(f"{i}. {os.path.basename(grp)}")
        except Exception as e:
            print(f"Error reading groups: {e}")


    def display_sections(self):
        """Display sections from the loaded groups."""
        if not self.grp_files:
            print("Error: Please load groups first (option 2)!")
            return
            
        try:
            self.sec_files = grpReader(self.run_file, self.grp_files)
            print("\nSections from group files:")
            for i, sec in enumerate(self.sec_files, 1):
                print(f"{i}. {sec}")
        except Exception as e:
            print(f"Error reading sections: {e}")


    def display_top_performers(self):
        """Display top performers (A, A-) from the loaded RUN file."""
        if not self.run_file:
            print("Error: Please load a RUN file first (option 1)!")
            return
            
        try:
            print("Loading top performers (A, A-)...")
            self.top_performers = Lists.goodList(self.run_file)
            
            if self.top_performers.empty:
                print("No top performers found!")
            else:
                print(f"\nFound {len(self.top_performers)} top performers:")
                pd.set_option('display.max_rows', None)
                print(self.top_performers)
                pd.reset_option('display.max_rows')
        except Exception as e:
            print(f"Error getting top performers: {e}")


    def display_bottom_performers(self):
        """Display bottom performers (F, D-) from the loaded RUN file."""
        if not self.run_file:
            print("Error: Please load a RUN file first (option 1)!")
            return
            
        try:
            print("Loading bottom performers (F, D-)...")
            self.bottom_performers = Lists.badList(self.run_file)
            
            if self.bottom_performers.empty:
                print("No bottom performers found!")
            else:
                print(f"\nFound {len(self.bottom_performers)} bottom performers:")
                pd.set_option('display.max_rows', None)
                print(self.bottom_performers)
                pd.reset_option('display.max_rows')
        except Exception as e:
            print(f"Error getting bottom performers: {e}")


    def export_data(self):
        """Export data to HTML files."""
        print("\nExport options:")
        print("1. Export top performers")
        print("2. Export bottom performers")
        print("3. Export SEC file data")
        print("4. Export Z-score analysis")
        print("5. Cancel Export")
        export_choice = input("Select data to export (1-5): ")
        
        if export_choice == '1':
            if self.top_performers is None:
                print("Error: Please load top performers first (option 4)!")
                return
            self.export_to_html(self.top_performers, "top_performers")
        elif export_choice == '2':
            if self.bottom_performers is None:
                print("Error: Please load bottom performers first (option 5)!")
                return
            self.export_to_html(self.bottom_performers, "bottom_performers")
        elif export_choice == '3':
            if self.sec_data is None:
                print("Error: Please read a SEC file first (option 7)!")
                return
            self.export_to_html(self.sec_data, "sec_data")
        elif export_choice == '4':
            if self.zscore_results is None:
                print("Error: Please perform Z-score analysis first (option 8)!")
                return
            self.export_to_html(self.zscore_results, "zscore_analysis")
        elif export_choice == '5':
            print("Export cancelled.")
            return
        else:
            print("Invalid export option!")


    def read_sec_file(self):
        """Read an individual SEC file and display its data."""
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
                return
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
                    return
                file_path = selection
        
        try:
            print(f"Reading SEC file: {file_path}")
            self.sec_data = fileReader.readSEC(file_path)
            
            if self.sec_data.empty:
                print("No data found in the SEC file!")
            else:
                print("\nSEC file data:")
                pd.set_option('display.max_rows', None)
                print(self.sec_data)
                pd.reset_option('display.max_rows')
        except Exception as e:
            print(f"Error reading SEC file: {e}")


    def perform_zscore(self):
        """Perform Z-score analysis on the loaded data."""
        if not self.run_file:
            print("Error: Please load a RUN file first (option 1)!")
            return
        
        if not self.grp_files:
            print("Error: Please load groups first (option 2)!")
            return
            
        if not self.sec_files:
            print("Error: Please load sections first (option 3)!")
            return
            
        try:
            print("Performing Z-score analysis...")
            # Set significance threshold
            threshold = 1.96  # Default value (95% confidence)
            custom_threshold = input("Enter significance threshold (default is 1.96): ")
            if custom_threshold.strip() and custom_threshold.replace('.', '', 1).isdigit():
                threshold = float(custom_threshold)
            
            # Run the analysis
            result_data, self.zscore_results = analyze_sections(self.run_file, self.grp_files, self.sec_files, threshold)
            
            # Display results
            if not result_data:
                print("No results found!")
            else:
                print(f"\nFound {len(result_data)} sections to analyze:")
                print("\nStatistical Summary:")
                print(f"Group GPA: {result_data[0]['group_gpa']}")
                print(f"Group Std Dev: {result_data[0]['group_std']}")
                
                # Print all section results
                print("\nSection Z-score Analysis:")
                print("-" * 80)
                print(f"{'Section':<15} {'GPA':<6} {'Count':<6} {'Z-score':<10} {'P-value':<10} {'Significant':<10}")
                print("-" * 80)
                
                for result in result_data:
                    z_score = result['z_score']
                    p_value = result['p_value']
                    z_display = f"{z_score:.2f}" if isinstance(z_score, (int, float)) else z_score
                    p_display = f"{p_value:.4f}" if isinstance(p_value, (int, float)) else p_value
                    
                    print(f"{result['section']:<15} {result['section_gpa']:<6} {result['section_count']:<6} {z_display:<10} {p_display:<10} {'Yes' if result['significant'] else 'No':<10}")
        
        except Exception as e:
            print(f"Error performing Z-score analysis: {e}")


    def exit_program(self):
        print("Exiting program. Goodbye!")
        sys.exit(0)


    def invalid_option(self):
        print("Invalid option! Please select a number between 1 and 9.")


    def run(self):
        while True:
            choice = self.display_menu()
            handler = self.handlers.get(choice, self.invalid_option)
            handler()
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    TerminalTester().run()