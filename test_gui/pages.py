"""
Page implementations for the Grade Analysis Tool GUI.
Includes HomePage, DashBoard, SearchStudents, and PerformerPage.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pandastable import Table, TableModel, config
import pandas as pd
import numpy as np

# Assuming GoodAndBadList is in the parent directory
import sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from GoodAndBadList import Lists

# Use absolute imports
from test_gui.base_page import BasePage
from test_gui.config import TITLE_FONT, BUTTON_FONT, INFO_FONT, DEFAULT_PADDING, options
from test_gui.stats_utils import perform_z_test, calculate_section_stats, compare_section_to_group

class HomePage(BasePage):
    """
    Home page for the application.
    Allows users to select a run file to begin analysis.
    """
    def create_widgets(self):
        # Create header
        self.create_header("Welcome to the Grade Analysis Tool")

        # Create main content frame
        content = tk.Frame(self)
        content.pack(expand=True, fill=tk.BOTH, padx=DEFAULT_PADDING*2, pady=DEFAULT_PADDING*2)

        # App description
        description = (
            "This tool allows you to analyze student grades across different "
            "course sections and groups. To begin, select a .RUN file to process."
        )
        desc_label = tk.Label(
            content,
            text=description,
            wraplength=600,
            justify=tk.CENTER,
            pady=DEFAULT_PADDING*2
        )
        desc_label.pack(fill=tk.X)

        # File selection button
        select_file_btn = ttk.Button(
            content,
            text="Select Run File",
            command=self.select_file,
            style="TButton"
        )
        select_file_btn.pack(pady=DEFAULT_PADDING*2)

        # File path display
        self.file_var = tk.StringVar()
        self.file_var.set("No file selected")
        file_label = tk.Label(
            content,
            textvariable=self.file_var,
            font=INFO_FONT
        )
        file_label.pack(pady=DEFAULT_PADDING)

    def select_file(self):
        """Handle file selection and validation."""
        filepath = filedialog.askopenfilename(
            title="Select Run File",
            filetypes=[("Run files", "*.RUN"), ("All files", "*.*")]
        )

        if not filepath:
            return  # User cancelled

        # Update file path display
        self.file_var.set(f"Selected: {os.path.basename(filepath)}")

        # Validate file
        try:
            # Check if file has .run extension (case insensitive)
            if not filepath.lower().endswith('.run'):
                raise ValueError("File must have a .RUN extension")

            # Set the filepath in controller and navigate to dashboard
            self.controller.set_filepath(filepath)
            self.controller.show_frame_by_name('DashBoard')

        except Exception as e:
            messagebox.showerror("File Error", f"Error with selected file: {str(e)}")
            self.file_var.set("No valid file selected")


class DashBoard(BasePage):
    """
    Dashboard page showing options for various reports and analyses.
    """
    def create_widgets(self):
        # Create header
        self.create_header("Grade Analysis Dashboard")

        # Create main content frame
        content = tk.Frame(self)
        content.pack(expand=True, fill=tk.BOTH, padx=DEFAULT_PADDING*2, pady=DEFAULT_PADDING*2)

        # Create button frame
        btn_frame = tk.Frame(content)
        btn_frame.pack(expand=True, pady=DEFAULT_PADDING*3)

        # Create navigation buttons with descriptions
        self.create_nav_button(
            btn_frame,
            "View Top Performers",
            "View students with the highest grades (A/A-)",
            lambda: self.controller.show_frame_by_name('PerformerPage', performer_type="top")
        )

        self.create_nav_button(
            btn_frame,
            "View Lowest Performers",
            "View students with the lowest grades (F/D-)",
            lambda: self.controller.show_frame_by_name('PerformerPage', performer_type="bottom")
        )

        self.create_nav_button(
            btn_frame,
            "Search & Filter Students",
            "Search and filter students by various criteria",
            lambda: self.controller.show_frame_by_name('SearchStudents')
        )

        # Display current file
        file_frame = tk.Frame(self)
        file_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

        self.file_label = tk.Label(
            file_frame,
            text=f"Current file: {os.path.basename(self.controller.get_filepath()) if self.controller.get_filepath() else 'None'}",
            font=INFO_FONT
        )
        self.file_label.pack(side=tk.LEFT)

        # Add button to select different file
        change_file_btn = ttk.Button(
            file_frame,
            text="Change File",
            command=lambda: self.controller.show_frame_by_name('HomePage')
        )
        change_file_btn.pack(side=tk.RIGHT, padx=DEFAULT_PADDING)

    def prepare(self, **kwargs):
        """Update file information when showing the dashboard."""
        if hasattr(self, 'file_label'):
            filepath = self.controller.get_filepath()
            filename = os.path.basename(filepath) if filepath else "No file selected"
            self.file_label.config(text=f"Current file: {filename}")

    def create_nav_button(self, parent, title, description, command):
        """Create a navigation button with description."""
        # Create a frame for each button with its description
        frame = tk.Frame(parent, bd=1, relief=tk.GROOVE)
        frame.pack(fill=tk.X, padx=DEFAULT_PADDING*2, pady=DEFAULT_PADDING)

        # Button title
        title_label = tk.Label(frame, text=title, font=BUTTON_FONT)
        title_label.pack(anchor=tk.W, padx=DEFAULT_PADDING, pady=(DEFAULT_PADDING, 0))

        # Description
        desc_label = tk.Label(frame, text=description, font=INFO_FONT, wraplength=500)
        desc_label.pack(anchor=tk.W, padx=DEFAULT_PADDING*2, pady=(0, DEFAULT_PADDING))

        # Button
        button = ttk.Button(frame, text="Open", command=command)
        button.pack(anchor=tk.E, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)


class SearchStudents(BasePage):
    """
    Page for searching and filtering students across all sections.
    Implements the functionality that was missing in the original implementation.
    """
    def create_widgets(self):
        # Create button bar with navigation buttons
        button_bar = self.create_button_bar()

        # Add export button
        if self.controller.export_icon:
            export_btn = ttk.Button(
                button_bar,
                image=self.controller.export_icon,
                command=lambda: self.export_data()
            )
        else:
            export_btn = ttk.Button(
                button_bar,
                text="Export",
                command=lambda: self.export_data()
            )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Page title
        self.create_header("Search & Filter Students")

        # Create search options frame
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

        # Search by name
        name_label = tk.Label(search_frame, text="Name:")
        name_label.pack(side=tk.LEFT, padx=(0, 5))

        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(search_frame, textvariable=self.name_var, width=20)
        name_entry.pack(side=tk.LEFT, padx=(0, DEFAULT_PADDING))

        # Filter by grade
        grade_label = tk.Label(search_frame, text="Grade:")
        grade_label.pack(side=tk.LEFT, padx=(DEFAULT_PADDING, 5))

        self.grade_var = tk.StringVar()
        grades = ["All"] + list(sorted(["A+", "A", "A-", "B+", "B", "B-",
                                        "C+", "C", "C-", "D+", "D", "D-", "F"]))
        grade_combo = ttk.Combobox(search_frame, textvariable=self.grade_var,
                                  values=grades, width=5, state="readonly")
        grade_combo.current(0)  # Set default to "All"
        grade_combo.pack(side=tk.LEFT, padx=(0, DEFAULT_PADDING))

        # Search button
        search_btn = ttk.Button(
            search_frame,
            text="Search",
            command=self.apply_filters
        )
        search_btn.pack(side=tk.LEFT, padx=DEFAULT_PADDING)

        # Reset button
        reset_btn = ttk.Button(
            search_frame,
            text="Reset",
            command=self.reset_filters
        )
        reset_btn.pack(side=tk.LEFT)

        # Create status frame
        self.status_frame = tk.Frame(self)
        self.status_frame.pack(fill=tk.X, padx=DEFAULT_PADDING, pady=(0, DEFAULT_PADDING))

        self.status_var = tk.StringVar()
        self.status_var.set("No data loaded yet")
        status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                               font=INFO_FONT, anchor=tk.W)
        status_label.pack(fill=tk.X)

        # Create table frame
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

        # Initialize variables
        self.df = None  # Full DataFrame
        self.filtered_df = None  # Filtered DataFrame
        self.table = None  # Table widget

    def prepare(self, **kwargs):
        """Load student data from all sections."""
        filepath = self.controller.get_filepath()
        if not filepath:
            self.status_var.set("No file selected.")
            # Clear existing table if present
            if self.table:
                self.table.destroy()
                self.table = None
            self.df = None
            self.filtered_df = None
            return

        # Avoid reloading if data is already present and file hasn't changed
        if (hasattr(self.controller, 'last_loaded_file') and 
            self.df is not None and 
            self.controller.last_loaded_file == filepath):
            self.status_var.set(f"Showing {len(self.filtered_df)} of {len(self.df)} students")
            self.update_table()  # Ensure table is shown
            return

        try:
            self.status_var.set("Loading data...")
            self.update()  # Force UI update

            # Load all student data
            self.df = self.load_all_students(filepath)
            if hasattr(self.controller, 'last_loaded_file'):
                self.controller.last_loaded_file = filepath  # Track loaded file

            if self.df is None or self.df.empty:
                self.status_var.set("No student data found in the selected file.")
                if self.table:
                    self.table.destroy()
                    self.table = None
                self.filtered_df = None
                return

            # Store full copy for filtering and reset filters
            self.filtered_df = self.df.copy()
            self.name_var.set("")
            self.grade_var.set("All")

            # Update status
            self.status_var.set(f"Loaded {len(self.df)} student records. Apply filters or search.")

            # Create the table
            self.update_table()

        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Error loading data: {str(e)}")
            self.status_var.set("Error loading data.")
            self.df = None
            self.filtered_df = None
            if self.table:
                self.table.destroy()
                self.table = None

    def load_all_students(self, filepath):
        """
        Load all student data from the run file.
        Combines good and bad lists as a placeholder for a full data load method.
        """
        try:
            # This is a workaround - ideally we would have a proper method to load all students
            good_df = Lists.goodList(filepath)
            bad_df = Lists.badList(filepath)

            # Combine both datasets
            if good_df is not None and bad_df is not None:
                all_df = pd.concat([good_df, bad_df], ignore_index=True)
                # If any duplicates, keep only one copy
                all_df = all_df.drop_duplicates(subset=['FName', 'LName', 'ID'])  # Assuming these define unique student
            elif good_df is not None:
                all_df = good_df.drop_duplicates(subset=['FName', 'LName', 'ID'])
            elif bad_df is not None:
                all_df = bad_df.drop_duplicates(subset=['FName', 'LName', 'ID'])
            else:
                all_df = pd.DataFrame()  # Return empty DataFrame if both fail

            return all_df
        except Exception as e:
            print(f"Error in load_all_students: {e}")  # Log error
            # Return empty dataframe
            return pd.DataFrame()

    def apply_filters(self):
        """Apply search and filter criteria to the data."""
        if self.df is None or self.df.empty:
            self.status_var.set("No data loaded to filter.")
            return

        # Start with the full dataset
        filtered = self.df.copy()

        # Apply name filter (case insensitive)
        name_filter = self.name_var.get().strip().lower()
        if name_filter:
            # Filter by either first or last name
            try:
                name_mask = (
                    filtered['FName'].str.lower().str.contains(name_filter, na=False) |
                    filtered['LName'].str.lower().str.contains(name_filter, na=False)
                )
                filtered = filtered[name_mask]
            except KeyError:
                messagebox.showerror("Filter Error", "FName or LName column not found in data.")
                return

        # Apply grade filter
        grade_filter = self.grade_var.get()
        if grade_filter != "All":
            try:
                filtered = filtered[filtered['Grade'] == grade_filter]
            except KeyError:
                messagebox.showerror("Filter Error", "Grade column not found in data.")
                return

        # Update filtered data
        self.filtered_df = filtered

        # Update status
        count = len(filtered)
        self.status_var.set(f"Found {count} matching student{'s' if count != 1 else ''}")

        # Update the table
        self.update_table()

    def reset_filters(self):
        """Reset all filters."""
        self.name_var.set("")
        self.grade_var.set("All")

        # Reset filtered data to full dataset
        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.status_var.set(f"Showing all {len(self.df)} students")
            self.update_table()
        else:
            self.status_var.set("No data loaded.")
            if self.table:
                self.table.destroy()
                self.table = None

    def update_table(self):
        """Update the displayed table with current filtered data."""
        # Remove existing table if any
        if self.table:
            self.table.destroy()
            self.table = None  # Ensure reference is cleared

        if self.filtered_df is None or self.filtered_df.empty:
            # If no data, display a message instead of an empty table
            no_data_label = tk.Label(self.table_frame, text="No data to display.", font=INFO_FONT)
            no_data_label.pack(expand=True)
            # Store reference to clear it later
            self.table = no_data_label
            return

        # Create new table with correct options
        try:
            self.table = Table(
                self.table_frame,
                dataframe=self.filtered_df,
                showtoolbar=False,
                showstatusbar=True,
                editable=False
            )
            
            # Apply the configured options to this table instance
            for key, value in options.items():
                setattr(self.table, key, value)
                
            self.table.autoResizeColumns()
            self.table.show()
        except Exception as e:
            messagebox.showerror("Table Error", f"Could not display data table: {e}")
            self.status_var.set("Error displaying table.")

    def export_data(self):
        """Export the currently filtered data."""
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showinfo("Export", "No data to export.")
            return

        self.controller.export_to_file(self.filtered_df, "student_search_results")


class PerformerPage(BasePage):
    """
    Page for displaying either top or bottom performers.
    Combines the functionality of TopPerformers and BottomPerformers from the original.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.df = None  # Will hold the data
        self.performer_type = "top"  # Default
        self.loaded_performer_type = None  # Track what type was loaded

    def create_widgets(self):
        # Create button bar with navigation buttons
        button_bar = self.create_button_bar()

        # Add export button
        if self.controller.export_icon:
            export_btn = ttk.Button(
                button_bar,
                image=self.controller.export_icon,
                command=self.export_data
            )
        else:
            export_btn = ttk.Button(
                button_bar,
                text="Export",
                command=self.export_data
            )
        export_btn.pack(side=tk.LEFT, padx=5)

        # Add analysis button
        analysis_btn = ttk.Button(
            button_bar,
            text="Z-Score Analysis",
            command=self.show_z_score_analysis
        )
        analysis_btn.pack(side=tk.LEFT, padx=5)

        # Create title (will be set in prepare)
        self.title_var = tk.StringVar()
        self.title_var.set("Student Performance")
        self.title_label = tk.Label(self, textvariable=self.title_var, font=TITLE_FONT)
        self.title_label.pack(pady=DEFAULT_PADDING)

        # Create status label
        self.status_var = tk.StringVar()
        self.status_var.set("Loading data...")
        status_label = tk.Label(self, textvariable=self.status_var, font=INFO_FONT)
        status_label.pack(pady=(0, DEFAULT_PADDING))

        # Create table container
        self.table_frame = tk.Frame(self)
        self.table_frame.pack(fill="both", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)

        # Table will be created in prepare method
        self.table = None

    def prepare(self, **kwargs):
        """
        Prepare the page with the appropriate data.

        Args:
            performer_type: Either "top" or "bottom"
        """
        self.performer_type = kwargs.get("performer_type", "top")

        # Set page title
        if self.performer_type == "top":
            self.title_var.set("Top Performing Students")
            grade_types = "A/A-"
        else:
            self.title_var.set("Students Needing Improvement")
            grade_types = "F/D-"

        # Get file path
        filepath = self.controller.get_filepath()
        if not filepath:
            self.status_var.set("No file selected.")
            if self.table:
                self.table.destroy()
                self.table = None
            self.df = None
            return

        # Avoid reloading if data is already present for this type and file
        if (hasattr(self.controller, 'last_loaded_file') and
            self.df is not None and
            self.controller.last_loaded_file == filepath and
            hasattr(self, 'loaded_performer_type') and
            self.loaded_performer_type == self.performer_type):
            self.status_var.set(f"Showing {len(self.df)} student{'s' if len(self.df) != 1 else ''} with grades of {grade_types}")
            self.update_table()  # Ensure table is shown
            return

        # Load data
        try:
            self.status_var.set("Loading data...")
            self.update()  # Force UI update

            if self.performer_type == "top":
                self.df = Lists.goodList(filepath)
            else:
                self.df = Lists.badList(filepath)

            if hasattr(self.controller, 'last_loaded_file'):
                self.controller.last_loaded_file = filepath  # Track loaded file
            self.loaded_performer_type = self.performer_type  # Track loaded type

            if self.df is None:  # Handle case where Lists might return None
                self.df = pd.DataFrame()  # Use empty DataFrame

            # Update status
            student_count = len(self.df)
            self.status_var.set(
                f"Found {student_count} student{'s' if student_count != 1 else ''} "
                f"with grades of {grade_types}"
            )

            # Create table
            self.update_table()

        except Exception as e:
            messagebox.showerror("Data Error", f"Error loading data: {str(e)}")
            self.status_var.set("Error loading data.")
            self.df = None
            if self.table:
                self.table.destroy()
                self.table = None

    def update_table(self):
        """Create or update the table display."""
        # Remove existing table if any
        if self.table:
            self.table.destroy()
            self.table = None  # Ensure reference is cleared

        if self.df is None or self.df.empty:
            # If no data, display a message instead of an empty table
            no_data_label = tk.Label(self.table_frame, text="No data to display.", font=INFO_FONT)
            no_data_label.pack(expand=True)
            # Store reference to clear it later
            self.table = no_data_label
            return

        # Create new table with correct options
        try:
            self.table = Table(
                self.table_frame,
                dataframe=self.df,
                showtoolbar=False,
                showstatusbar=True,
                editable=False
            )
            
            # Apply the configured options to this table instance
            for key, value in options.items():
                setattr(self.table, key, value)
                
            self.table.autoResizeColumns()
            self.table.show()
        except Exception as e:
            messagebox.showerror("Table Error", f"Could not display data table: {e}")
            self.status_var.set("Error displaying table.")

    def export_data(self):
        """Export the currently displayed data."""
        if self.df is None or self.df.empty:
            messagebox.showinfo("Export", "No data to export.")
            return

        # Get appropriate filename based on title
        if "Top" in self.title_var.get():
            default_name = "top_performers"
        else:
            default_name = "lowest_performers"

        self.controller.export_to_file(self.df, default_name)

    def show_z_score_analysis(self):
        """
        Show a window with Z-score analysis comparing sections to the group average.
        """
        if self.df is None or self.df.empty:
            messagebox.showinfo("Analysis", "No data available for analysis.")
            return
            
        # Create a new top-level window for the analysis
        analysis_window = tk.Toplevel(self)
        analysis_window.title("Z-Score Section Analysis")
        analysis_window.geometry("600x400")
        
        # Add a frame for the content
        content_frame = tk.Frame(analysis_window)
        content_frame.pack(fill="both", expand=True, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # Get all unique course IDs
        try:
            if 'CourseID' not in self.df.columns:
                messagebox.showerror("Analysis Error", "CourseID column not found in data.")
                analysis_window.destroy()
                return
                
            course_ids = self.df['CourseID'].unique()
            
            # If no course IDs, show message
            if len(course_ids) == 0:
                no_data_label = tk.Label(
                    content_frame, 
                    text="No course sections found for analysis.", 
                    font=INFO_FONT
                )
                no_data_label.pack(pady=50)
                return
                
            # Create a section to show the overall statistics
            overall_frame = tk.LabelFrame(content_frame, text="Overall Statistics")
            overall_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
            
            # Calculate overall statistics
            overall_stats = calculate_section_stats(self.df)
            
            # Display overall statistics
            overall_label = tk.Label(
                overall_frame,
                text=f"Number of Students: {overall_stats['count']}\n"
                     f"Average GPA: {overall_stats['mean']:.2f}\n"
                     f"Standard Deviation: {overall_stats['std_dev']:.2f}",
                justify=tk.LEFT,
                padx=DEFAULT_PADDING,
                pady=DEFAULT_PADDING
            )
            overall_label.pack(anchor=tk.W)
            
            # Create a scrollable frame for the sections
            canvas = tk.Canvas(content_frame)
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # For each course ID, create a section in the analysis
            for course_id in sorted(course_ids):
                # Create a frame for this section
                section_frame = tk.LabelFrame(scrollable_frame, text=f"Section: {course_id}")
                section_frame.pack(fill="x", padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
                
                # Get section data
                section_df = self.df[self.df['CourseID'] == course_id]
                
                # Compare to overall
                comparison = compare_section_to_group(section_df, self.df)
                
                # Build the display text
                section_text = (
                    f"Students: {comparison['section_stats']['count']}\n"
                    f"Average GPA: {comparison['section_stats']['mean']:.2f}\n"
                    f"Z-Score: {comparison['z_score']:.2f}\n"
                    f"P-Value: {comparison['p_value']:.4f}\n"
                    f"Interpretation: {comparison['interpretation']}"
                )
                
                # Add a label with the section info
                section_label = tk.Label(
                    section_frame,
                    text=section_text,
                    justify=tk.LEFT,
                    padx=DEFAULT_PADDING,
                    pady=DEFAULT_PADDING
                )
                section_label.pack(anchor=tk.W)
                
                # Color-code based on significance and direction
                if comparison['is_significant']:
                    if comparison['z_score'] > 0:  # Above average
                        section_frame.config(bg="#d4edda")  # Light green
                        section_label.config(bg="#d4edda")
                    else:  # Below average
                        section_frame.config(bg="#f8d7da")  # Light red
                        section_label.config(bg="#f8d7da")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error performing analysis: {str(e)}")
            analysis_window.destroy()

# Dictionary to map page names to classes for easy lookup
PAGE_CLASSES = {
    'HomePage': HomePage,
    'DashBoard': DashBoard,
    'SearchStudents': SearchStudents,
    'PerformerPage': PerformerPage,
}
