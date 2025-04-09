"""
Improved Grade Analyzer GUI Application

This module provides an enhanced graphical user interface for analyzing student grades
from .run, .grp, and .sec files. It builds upon the original MainGUI.py implementation
with improved structure, error handling, and user experience.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image
import sv_ttk as sv
from pandastable import Table, TableModel, config
from GoodAndBadList import Lists
import pandas as pd

# Global variables
options = config.load_options()
TITLE_FONT = ("Arial", 18, "bold")
BUTTON_FONT = ("Arial", 11)
INFO_FONT = ("Arial", 10, "italic")
DEFAULT_PADDING = 10

class ImprovedGradeGUI(tk.Tk):
    """
    Main application class for the Grade Analysis Tool.
    This class manages the application window and navigation between pages.
    """
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.title("Grade Analysis Tool")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Set theme
        sv.set_theme("dark")
        
        # Configure table options
        self.configure_table_options()
        
        # Store current file path
        self.filepath = ""
        
        # Create style for widgets
        style = ttk.Style()
        style.configure("TButton", font=BUTTON_FONT, padding=(10, 5))
        
        # Load icons
        self.load_icons()
        
        # Create main container
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create all pages
        for Page in (HomePage, DashBoard, SearchStudents, PerformerPage):
            page_instance = Page(container, self)
            self.frames[Page] = page_instance
            page_instance.pack(fill="both", expand=True)
        
        # Show initial page
        self.show_frame(HomePage)
    
    def configure_table_options(self):
        """Configure options for pandas tables."""
        options.update({
            'cellbackgr': '#2b2b2b',
            'textcolor': '#ffffff',
            'grid_color': '#444444',
            'rowselectedcolor': '#44475a',
            'font': 'TkDefaultFont',
            'fontsize': 12,
            'rowheight': 22,
            'colheadercolor': '#1e1e1e',
            'colheaderfg': '#ffffff',
        })
    
    def load_icons(self):
        """Load and prepare icons for the application."""
        try:
            # Home icon
            self.home_icon = tk.PhotoImage(file="home.png")
            self.home_icon = self.home_icon.subsample(3, 3)
            
            # Export icon
            self.export_icon = tk.PhotoImage(file="export.png") 
            self.export_icon = self.export_icon.subsample(3, 3)
            
            # Search icon
            self.search_icon = tk.PhotoImage(file="search.png") if os.path.exists("search.png") else None
            if self.search_icon:
                self.search_icon = self.search_icon.subsample(3, 3)
        except Exception as e:
            messagebox.showwarning("Icon Warning", f"Could not load one or more icons: {str(e)}\nThe application will use text buttons instead.")
            self.home_icon = None
            self.export_icon = None
            self.search_icon = None
    
    def show_frame(self, page_class, **kwargs):
        """
        Show the specified page and hide all others.
        
        Args:
            page_class: The class of the page to display
            **kwargs: Additional arguments to pass to the page's prepare method
        """
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Get the frame to show
        frame = self.frames[page_class]
        
        # Prepare the frame with any data it needs
        if hasattr(frame, "prepare"):
            frame.prepare(**kwargs)
        
        # Show the frame
        frame.pack(fill="both", expand=True)
    
    def set_filepath(self, filepath):
        """Set the current file path."""
        self.filepath = filepath
    
    def get_filepath(self):
        """Get the current file path."""
        return self.filepath
    
    def export_to_file(self, df, default_name="grade_report"):
        """
        Export a DataFrame to various file formats.
        
        Args:
            df: DataFrame to export
            default_name: Default file name (without extension)
        """
        if df.empty:
            messagebox.showinfo("Export Info", "No data to export.")
            return
            
        # Ask user for file type
        file_types = [
            ("HTML files", "*.html"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx")
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=file_types,
            initialfile=default_name
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Export based on file extension
            if file_path.endswith('.html'):
                df.to_html(file_path)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
                
            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")


class BasePage(tk.Frame):
    """
    Base class for all pages in the application.
    Provides common functionality and layout.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    
    def create_widgets(self):
        """Create the widgets for this page. Override in subclasses."""
        pass
    
    def prepare(self, **kwargs):
        """
        Prepare the page before displaying it.
        Override in subclasses that need to load data.
        
        Args:
            **kwargs: Additional arguments for page preparation
        """
        pass
    
    def create_header(self, title):
        """
        Create a standard header with title.
        
        Args:
            title: Title text to display
        
        Returns:
            The header frame
        """
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        title_label = tk.Label(header_frame, text=title, font=TITLE_FONT)
        title_label.pack(pady=DEFAULT_PADDING)
        
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill=tk.X, padx=DEFAULT_PADDING*2)
        
        return header_frame
    
    def create_button_bar(self):
        """
        Create a standard button bar at the top of the page.
        
        Returns:
            The button bar frame
        """
        button_bar = tk.Frame(self)
        button_bar.pack(fill=tk.X, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        # Add home button
        if self.controller.home_icon:
            home_btn = ttk.Button(
                button_bar,
                image=self.controller.home_icon,
                command=lambda: self.controller.show_frame(DashBoard)
            )
        else:
            home_btn = ttk.Button(
                button_bar,
                text="Home",
                command=lambda: self.controller.show_frame(DashBoard)
            )
        home_btn.pack(side=tk.LEFT, padx=5)
        
        return button_bar


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
            self.controller.show_frame(DashBoard)
            
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
            lambda: self.controller.show_frame(PerformerPage, performer_type="top")
        )
        
        self.create_nav_button(
            btn_frame,
            "View Lowest Performers",
            "View students with the lowest grades (F/D-)",
            lambda: self.controller.show_frame(PerformerPage, performer_type="bottom")
        )
        
        self.create_nav_button(
            btn_frame,
            "Search & Filter Students",
            "Search and filter students by various criteria",
            lambda: self.controller.show_frame(SearchStudents)
        )
        
        # Display current file
        file_frame = tk.Frame(self)
        file_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=DEFAULT_PADDING, pady=DEFAULT_PADDING)
        
        self.file_label = tk.Label(
            file_frame,
            text=f"Current file: {os.path.basename(self.controller.get_filepath())}",
            font=INFO_FONT
        )
        self.file_label.pack(side=tk.LEFT)
        
        # Add button to select different file
        change_file_btn = ttk.Button(
            file_frame,
            text="Change File",
            command=lambda: self.controller.show_frame(HomePage)
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
            return
        
        try:
            # Load all student data (we assume the Lists.goodList method gives us all data,
            # which is not ideal but seems to be what the original app expected)
            self.df = self.load_all_students(filepath)
            
            if self.df.empty:
                self.status_var.set("No student data found in the selected file.")
                return
                
            # Store full copy for filtering
            self.filtered_df = self.df.copy()
            
            # Update status
            self.status_var.set(f"Loaded {len(self.df)} student records")
            
            # Create the table
            self.update_table()
            
        except Exception as e:
            messagebox.showerror("Data Loading Error", f"Error loading data: {str(e)}")
            self.status_var.set("Error loading data.")
    
    def load_all_students(self, filepath):
        """
        Load all student data from the run file.
        Ideally, this would use a proper API to load all students,
        but for now we'll combine the good and bad lists.
        """
        # This is a workaround - ideally we would have a proper method to load all students
        good_df = Lists.goodList(filepath)
        bad_df = Lists.badList(filepath)
        
        # Combine both datasets
        all_df = pd.concat([good_df, bad_df], ignore_index=True)
        
        # If any duplicates, keep only one copy
        all_df = all_df.drop_duplicates()
        
        return all_df
    
    def apply_filters(self):
        """Apply search and filter criteria to the data."""
        if self.df is None or self.df.empty:
            return
            
        # Start with the full dataset
        filtered = self.df.copy()
        
        # Apply name filter (case insensitive)
        name_filter = self.name_var.get().strip().lower()
        if name_filter:
            # Filter by either first or last name
            name_mask = (
                filtered['FName'].str.lower().str.contains(name_filter, na=False) | 
                filtered['LName'].str.lower().str.contains(name_filter, na=False)
            )
            filtered = filtered[name_mask]
        
        # Apply grade filter
        grade_filter = self.grade_var.get()
        if grade_filter != "All":
            filtered = filtered[filtered['Grade'] == grade_filter]
        
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
    
    def update_table(self):
        """Update the displayed table with current filtered data."""
        # Remove existing table if any
        if self.table:
            self.table.destroy()
        
        if self.filtered_df is None or self.filtered_df.empty:
            # If no data, don't create a table
            return
            
        # Create new table
        self.table = Table(
            self.table_frame,
            dataframe=self.filtered_df,
            showtoolbar=False,
            showstatusbar=True,
            editable=False,
            config=options
        )
        config.apply_options(options, self.table)
        self.table.autoResizeColumns()
        self.table.show()
    
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
        performer_type = kwargs.get("performer_type", "top")
        
        # Set page title
        if performer_type == "top":
            self.title_var.set("Top Performing Students")
        else:
            self.title_var.set("Students Needing Improvement")
        
        # Get file path
        filepath = self.controller.get_filepath()
        if not filepath:
            self.status_var.set("No file selected.")
            return
        
        # Load data
        try:
            if performer_type == "top":
                self.df = Lists.goodList(filepath)
                grade_types = "A/A-"
            else:
                self.df = Lists.badList(filepath)
                grade_types = "F/D-"
            
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
    
    def update_table(self):
        """Create or update the table display."""
        # Remove existing table if any
        if self.table:
            self.table.destroy()
        
        if self.df is None or self.df.empty:
            return
            
        # Create new table
        self.table = Table(
            self.table_frame,
            dataframe=self.df,
            showtoolbar=False,
            showstatusbar=True,
            editable=False,
            config=options
        )
        config.apply_options(options, self.table)
        self.table.autoResizeColumns()
        self.table.show()
    
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


# Run the application when the script is executed directly
if __name__ == "__main__":
    app = ImprovedGradeGUI()
    app.mainloop()
