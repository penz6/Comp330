#!/usr/bin/env python3
# terminal_tester.py - Command-line interface to test grade analysis functionality

import os
import sys
from pathlib import Path
from run_parser import runReader
from grp_parser import grpReader
from FileReader import fileReader
from GoodAndBadList import Lists
from History import HistoryManager  # Import the HistoryManager class
import pandas as pd
from zscore_calculator import analyze_sections

class TerminalTester:
    def __init__(self):
        """
        Initialize the TerminalTester class with default attributes for file paths,
        dataframes, and handlers for menu options. This sets up the internal state
        for managing loaded files, analysis results, and user interactions.
        """
        self.run_file = None
        self.grp_files = None
        self.sec_files = None
        self.top_performers = None
        self.bottom_performers = None
        self.sec_data = None
        self.zscore_results = None
        # Initialize the HistoryManager
        self.history = HistoryManager()
        self.handlers = {
            '1': self.load_run,
            '2': self.display_groups,
            '3': self.display_sections,
            '4': self.display_top_performers,
            '5': self.display_bottom_performers,
            '6': self.export_data,
            '7': self.read_sec_file,
            '8': self.perform_zscore,
            '9': self.manage_history,  # Add new handler for history management
            '10': self.auto_process,   # New handler for auto-processing
            '0': self.exit_program     # Changed from 9 to 0 to accommodate new option
        }


    def display_menu(self):
        """
        Display the main menu to the user, outlining all available options for
        interacting with the grade analysis tool. Prompts the user to select an
        option and returns their input for further processing.

        Returns:
            str: The user's menu selection as a string.
        """
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
        print("9. Manage student history")
        print("10. Auto-Process full pipeline")  # New option
        print("0. Exit")
        print("="*50)
        return input("Select an option (0-10): ")  # Updated range


    def find_run_files(self, base_dir=None):
        """
        Search for all '.run' files within the specified base directory and its
        subdirectories. If no directory is provided, defaults to the 'COMSC330_POC_Data'
        folder relative to the script location.

        Args:
            base_dir (str or Path, optional): The directory to search for RUN files.

        Returns:
            list: A list of absolute file paths to found RUN files.
        """
        if base_dir is None:
            # Default to a directory relative to the script location
            base_dir = Path(__file__).parent / "COMSC330_POC_Data"
        else:
            base_dir = Path(base_dir)

        run_files = []
        if not base_dir.exists():
            print(f"Warning: Base directory '{base_dir}' does not exist.")
            return run_files

        # Accept .run, .run.txt, .RUN.txt (case-insensitive)
        for file in base_dir.rglob("*"):
            if file.is_file():
                fname = file.name.lower()
                if fname.endswith('.run') or fname.endswith('.run.txt'):
                    run_files.append(str(file.resolve()))

        return run_files


    def export_to_html(self, df, file_type):
        """
        Export the provided pandas DataFrame to an HTML file. The filename is
        determined by the file_type argument. Notifies the user of the export
        location or if there is no data to export.

        Args:
            df (pd.DataFrame): The DataFrame to export.
            file_type (str): A descriptor for the type of data being exported,
                             used in the output filename.
        """
        if df is None or df.empty:
            print("No data to export!")
            return
        
        filename = f"{file_type}_export.html"
        df.to_html(filename)
        print(f"Data exported to {os.path.abspath(filename)}")


    def load_run(self):
        """
        Prompt the user to select or provide the path to a RUN file. Lists all
        available RUN files found in the data directory, or allows for manual
        entry of a custom path. Updates the internal state with the selected file.
        """
        # Accept .run, .run.txt, .RUN.txt
        def is_run_file(filename):
            fname = filename.lower()
            return fname.endswith('.run') or fname.endswith('.run.txt')

        available_runs = []
        # Search for .run, .run.txt files
        for file in self.find_run_files():
            if is_run_file(file):
                available_runs.append(file)
        
        if not available_runs:
            print("No RUN files found in the data directory!")
            custom_path = input("Would you like to enter a custom path? (y/n): ")
            if custom_path.lower() == 'y':
                file_path = input("Enter the path to your .RUN file: ")
                if not is_run_file(file_path):
                    print("Error: Please provide a valid .RUN file (.run or .run.txt)!")
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
                if not is_run_file(selection):
                    print("Error: Please provide a valid .RUN file (.run or .run.txt)!")
                    return
                self.run_file = selection
                print(f"Successfully loaded RUN file: {self.run_file}")
        except Exception as e:
            print(f"Error loading RUN file: {e}")


    def display_groups(self):
        """
        Display all group files associated with the currently loaded RUN file.
        Requires that a RUN file has been loaded. Lists each group file found,
        or notifies the user if an error occurs.
        """
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
        """
        Display all section files associated with the loaded group files.
        Requires that group files have been loaded. Lists each section file found,
        or notifies the user if an error occurs.
        """
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
        """
        Display a list of top-performing students (grades A and A-) from the
        loaded RUN file. Requires that a RUN file has been loaded. Shows the
        results in a formatted table or notifies the user if no data is found.
        """
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
                # Ask if user wants to update the history
                update_history = input("\nUpdate Good List history with these students? (y/n): ")
                if update_history.lower() == 'y':
                    updated_df, already_on_list = self.history.update_good_list(self.top_performers)
                    if already_on_list:
                        print(f"\n{len(already_on_list)} students were already on the Good List.")
                    print(f"Good List updated with {len(self.top_performers) - len(already_on_list)} new students.")
        except Exception as e:
            print(f"Error getting top performers: {e}")


    def display_bottom_performers(self):
        """
        Display a list of bottom-performing students (grades F and D-) from the
        loaded RUN file. Requires that a RUN file has been loaded. Shows the
        results in a formatted table or notifies the user if no data is found.
        """
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
                # Ask if user wants to update the history
                update_history = input("\nUpdate Work List history with these students? (y/n): ")
                if update_history.lower() == 'y':
                    updated_df, already_on_list = self.history.update_work_list(self.bottom_performers)
                    if already_on_list:
                        print(f"\n{len(already_on_list)} students were already on the Work List.")
                    print(f"Work List updated with {len(self.bottom_performers) - len(already_on_list)} new students.")
        except Exception as e:
            print(f"Error getting bottom performers: {e}")


    def export_data(self):
        """
        Present export options to the user for saving various data sets to HTML files.
        Allows exporting of top performers, bottom performers, SEC file data, or
        Z-score analysis results. Handles user selection and validates that the
        relevant data has been loaded before exporting.
        """
        print("\nExport options:")
        print("1. Export top performers")
        print("2. Export bottom performers")
        print("3. Export SEC file data")
        print("4. Export Z-score analysis")
        print("5. Export historical Good List")  # New option
        print("6. Export historical Work List")  # New option
        print("7. Cancel Export")
        export_choice = input("Select data to export (1-7): ")
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
            good_list = self.history.get_good_list()
            if good_list.empty:
                print("Error: No historical Good List data found!")
                return
            self.export_to_html(good_list, "historical_good_list")
        elif export_choice == '6':
            work_list = self.history.get_work_list()
            if work_list.empty:
                print("Error: No historical Work List data found!")
                return
            self.export_to_html(work_list, "historical_work_list")
        elif export_choice == '7':
            print("Export cancelled.")
            return
        else:
            print("Invalid export option!")


    def read_sec_file(self):
        """
        Prompt the user to select or provide the path to a SEC file. Lists all
        available SEC files found in the data directory, or allows for manual
        entry of a custom path. Reads and displays the SEC file data in a table,
        or notifies the user if no data is found.
        """
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
        """
        Perform Z-score statistical analysis on the loaded section data. Prompts
        the user for a significance threshold, runs the analysis, and displays
        a summary of results including group GPA, standard deviation, and
        section-level Z-scores and significance. Requires that RUN, group, and
        section files have been loaded.
        """
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
                print(f"{'Section':<45} {'GPA':<6} {'Count':<6} {'Z-score':<10} {'P-value':<10} {'Significant':<10}")
                print("-" * 80)
                
                # Path shortening logic to enshure more readable output
                def shorten_section_path(section_path):
                    marker = "COMSC330_POC_Data"
                    idx = section_path.find(marker)
                    if idx != -1:
                        return section_path[idx:]
                    return section_path

                for result in result_data:
                    z_score = result['z_score']
                    p_value = result['p_value']
                    z_display = f"{z_score:.2f}" if isinstance(z_score, (int, float)) else z_score
                    p_display = f"{p_value:.4f}" if isinstance(p_value, (int, float)) else p_value
                    section_short = shorten_section_path(result['section'])
                    print(f"{section_short:<45} {result['section_gpa']:<6} {result['section_count']:<6} {z_display:<10} {p_display:<10} {'Yes' if result['significant'] else 'No':<10}")
        
        except Exception as e:
            print(f"Error performing Z-score analysis: {e}")


    def manage_history(self):
        """
        Provide options for managing student history data, including viewing historical
        lists and checking individual student history.
        """
        print("\nHistory Management Options:")
        print("1. View historical Good List")
        print("2. View historical Work List")
        print("3. Check student history")
        print("4. Return to main menu")
        history_choice = input("Select an option (1-4): ")
        if history_choice == '1':
            good_list = self.history.get_good_list()
            if good_list.empty:
                print("No historical Good List data found!")
            else:
                print(f"\nHistorical Good List ({len(good_list)} students):")
                pd.set_option('display.max_rows', None)
                print(good_list)
                pd.reset_option('display.max_rows')
        elif history_choice == '2':
            work_list = self.history.get_work_list()
            if work_list.empty:
                print("No historical Work List data found!")
            else:
                print(f"\nHistorical Work List ({len(work_list)} students):")
                pd.set_option('display.max_rows', None)
                print(work_list)
                pd.reset_option('display.max_rows')
        elif history_choice == '3':
            student_id = input("Enter student ID to check: ")
            try:
                student_id = int(student_id)
                history = self.history.check_student_history(student_id)
                print(f"\nHistory for Student ID: {student_id}")
                print(f"Previously on Good List: {'Yes' if history['good_list'] else 'No'}")
                print(f"Previously on Work List: {'Yes' if history['work_list'] else 'No'}")
            except ValueError:
                print("Error: Please enter a valid numeric student ID!")
        elif history_choice == '4':
            return
        else:
            print("Invalid option!")


    def exit_program(self):
        """
        Exit the program gracefully, displaying a goodbye message and terminating
        the script execution.
        """
        print("Exiting program. Goodbye!")
        sys.exit(0)


    def invalid_option(self):
        """
        Notify the user that an invalid menu option was selected and prompt them
        to choose a valid option.
        """
        print("Invalid option! Please select a number between 0 and 10.")  # Updated range


    def auto_process(self):
        """
        Run the entire data processing pipeline in sequence:
        1) Prompt user for RUN file path or list + pick
        2) Load groups
        3) Load sections
        4) Compute/display top performers
        5) Compute/display bottom performers
        6) Read first SEC file in data directory
        7) Perform Z-score analysis (default threshold)
        
        This method automates the steps that would otherwise require multiple
        menu selections and confirmations.
        """
        print("\n" + "="*50)
        print("Auto-Processing Pipeline")
        print("="*50)
        
        try:
            # 1. Load RUN file
            print("[1/7] Searching for RUN files...")
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
                else:
                    print("Auto-process cancelled: No RUN file selected.")
                    return
            else:
                print("\nAvailable RUN files:")
                for i, run in enumerate(available_runs, 1):
                    print(f"{i}. {os.path.basename(run)} ({run})")
                selection = input("\nSelect a file number or enter a custom path: ")
                if selection.isdigit() and 1 <= int(selection) <= len(available_runs):
                    self.run_file = available_runs[int(selection) - 1]
                else:
                    if not selection.lower().endswith('.run'):
                        print("Error: Please provide a valid .RUN file!")
                        return
                    self.run_file = selection
            print(f"Successfully loaded RUN file: {self.run_file}")

            # 2. Load groups
            print("[2/7] Loading groups...")
            self.grp_files = runReader(self.run_file)
            print(f"Loaded {len(self.grp_files)} group files.")

            # 3. Load sections
            print("[3/7] Loading sections...")
            self.sec_files = grpReader(self.run_file, self.grp_files)
            print(f"Loaded {len(self.sec_files)} section files.")

            # 4. Process top performers
            print("[4/7] Processing top performers (A, A-)...")
            self.top_performers = Lists.goodList(self.run_file)
            if self.top_performers.empty:
                print("No top performers found!")
            else:
                print(f"Top performers: {len(self.top_performers)} students")
                # Ensure 'id' column exists for update_good_list
                if 'id' not in self.top_performers.columns:
                    # Try to find a likely column (case-insensitive)
                    id_col = next((col for col in self.top_performers.columns if col.lower() == 'id'), None)
                    if id_col:
                        self.top_performers = self.top_performers.rename(columns={id_col: 'id'})
                if 'id' not in self.top_performers.columns:
                    print("Error: Top performers data missing 'id' column. Skipping Good List update.")
                else:
                    updated_df, already_on_list = self.history.update_good_list(self.top_performers)
                    print(f"Good List updated: {len(self.top_performers) - len(already_on_list)} new, {len(already_on_list)} already on list")

            # 5. Process bottom performers
            print("[5/7] Processing bottom performers (F, D-)...")
            self.bottom_performers = Lists.badList(self.run_file)
            if self.bottom_performers.empty:
                print("No bottom performers found!")
            else:
                print(f"Bottom performers: {len(self.bottom_performers)} students")
                # Ensure 'id' column exists for update_work_list
                if 'id' not in self.bottom_performers.columns:
                    id_col = next((col for col in self.bottom_performers.columns if col.lower() == 'id'), None)
                    if id_col:
                        self.bottom_performers = self.bottom_performers.rename(columns={id_col: 'id'})
                if 'id' not in self.bottom_performers.columns:
                    print("Error: Bottom performers data missing 'id' column. Skipping Work List update.")
                else:
                    updated_df, already_on_list = self.history.update_work_list(self.bottom_performers)
                    print(f"Work List updated: {len(self.bottom_performers) - len(already_on_list)} new, {len(already_on_list)} already on list")

            # 6. Read first SEC file
            print("[6/7] Loading SEC file data...")
            data_dir = "COMSC330_POC_Data"
            sec_files_found = []
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if file.lower().endswith('.sec'):
                        sec_files_found.append(os.path.join(root, file))
            if not sec_files_found:
                print("No SEC files found in the data directory. Skipping SEC file processing.")
            else:
                file_path = sec_files_found[0]
                print(f"Reading SEC file: {file_path}")
                self.sec_data = fileReader.readSEC(file_path)
                if self.sec_data.empty:
                    print("No data found in the SEC file!")
                else:
                    print(f"SEC data loaded: {len(self.sec_data)} rows")

            # 7. Perform Z-score analysis
            print("[7/7] Performing Z-score analysis...")
            if not self.run_file or not self.grp_files or not self.sec_files:
                print("Missing required data for Z-score analysis. Skipping.")
            else:
                threshold = 1.96
                result_data, self.zscore_results = analyze_sections(self.run_file, self.grp_files, self.sec_files, threshold)
                if not result_data:
                    print("No Z-score results found!")
                else:
                    print(f"Z-score analysis completed: {len(result_data)} sections analyzed")
                    print(f"Group GPA: {result_data[0]['group_gpa']}")
                    print(f"Group Std Dev: {result_data[0]['group_std']}")

            print("\n" + "="*50)
            print("Auto-Processing Complete!")
            print("="*50)

        except Exception as e:
            print(f"Auto-processing error: {e}")
            print("Auto-processing pipeline aborted.")

    def run(self):
        """
        Main loop for the terminal tester. Continuously displays the menu,
        processes user input, and invokes the appropriate handler for each
        selected option until the user chooses to exit.
        """
        while True:
            choice = self.display_menu()
            handler = self.handlers.get(choice, self.invalid_option)
            handler()
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    TerminalTester().run()