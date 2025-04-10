"""
Main application class for the Grade Analysis Tool GUI.
Manages the main window, pages, and navigation.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk as sv
import pandas as pd

# Using absolute imports instead of relative imports
from test_gui.config import BUTTON_FONT, options, configure_table_options

# The PAGE_CLASSES will be imported after we define the pages class
# to avoid circular imports
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

        # Configure table options - but don't apply them globally
        self.table_options = configure_table_options()

        # Store current file path and last loaded file for caching checks
        self.filepath = ""
        self.last_loaded_file = None

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

        # Import page classes here to avoid circular imports
        from test_gui.pages import PAGE_CLASSES
        
        # Create all pages using the PAGE_CLASSES dictionary
        for name, Page in PAGE_CLASSES.items():
            page_instance = Page(container, self)
            self.frames[name] = page_instance  # Store by name

        # Show initial page (HomePage)
        self.show_frame_by_name('HomePage')

        # Add an example data method for testing
        self.example_data_loaded = False

    def load_icons(self):
        """Load and prepare icons for the application."""
        # Define icon paths relative to the script location might be safer
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.dirname(script_dir)  # Assumes icons are in parent dir

        home_icon_path = os.path.join(icon_dir, "home.png")
        export_icon_path = os.path.join(icon_dir, "export.png")
        search_icon_path = os.path.join(icon_dir, "search.png")

        self.home_icon = None
        self.export_icon = None
        self.search_icon = None  # Keep track even if not used currently

        try:
            if os.path.exists(home_icon_path):
                self.home_icon = tk.PhotoImage(file=home_icon_path)
                self.home_icon = self.home_icon.subsample(3, 3)

            if os.path.exists(export_icon_path):
                self.export_icon = tk.PhotoImage(file=export_icon_path)
                self.export_icon = self.export_icon.subsample(3, 3)

            if os.path.exists(search_icon_path):
                self.search_icon = tk.PhotoImage(file=search_icon_path)
                self.search_icon = self.search_icon.subsample(3, 3)

        except Exception as e:
            messagebox.showwarning("Icon Warning", f"Could not load one or more icons: {str(e)}\nThe application will use text buttons instead.")
            # Ensure icons are None if loading failed
            self.home_icon = None
            self.export_icon = None
            self.search_icon = None

    def show_frame_by_name(self, page_name, **kwargs):
        """
        Show the specified page by name and hide all others.

        Args:
            page_name: The string name of the page class to display
            **kwargs: Additional arguments to pass to the page's prepare method
        """
        if page_name not in self.frames:
            print(f"Error: Page '{page_name}' not found.")
            return

        # Hide all frames first
        for frame in self.frames.values():
            frame.pack_forget()

        # Get the frame to show
        frame = self.frames[page_name]

        # Prepare the frame with any data it needs
        if hasattr(frame, "prepare"):
            try:
                frame.prepare(**kwargs)
            except Exception as e:
                messagebox.showerror("Page Load Error", f"Error preparing page '{page_name}': {e}")
                return  # Stop if prepare fails

        # Show the frame
        frame.pack(fill="both", expand=True)
        frame.tkraise()  # Bring the frame to the front

    def set_filepath(self, filepath):
        """Set the current file path."""
        self.filepath = filepath
        # Reset last loaded file when a new file is explicitly set
        self.last_loaded_file = None

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
        if df is None or df.empty:
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
                df.to_html(file_path, index=False)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                # Ensure openpyxl is installed for Excel export
                try:
                    import openpyxl
                    df.to_excel(file_path, index=False)
                except ImportError:
                    messagebox.showerror("Export Error", "Please install the 'openpyxl' library to export to Excel.\nRun: pip install openpyxl")
                    return

            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def load_example_data(self):
        """
        Loads example data for testing when no file is available.
        """
        # Create sample data with multiple sections
        data = {
            'FName': ['John', 'Jane', 'Bob', 'Alice', 'Tom', 'Sarah', 
                      'Mike', 'Lisa', 'David', 'Emma', 'Ryan', 'Olivia'],
            'LName': ['Smith', 'Doe', 'Johnson', 'Williams', 'Brown', 'Jones',
                     'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Wilson'],
            'ID': ['001', '002', '003', '004', '005', '006', 
                   '007', '008', '009', '010', '011', '012'],
            'Grade': ['A', 'B+', 'C', 'A-', 'F', 'B', 
                      'A', 'A-', 'B+', 'D', 'C+', 'B-'],
            'CourseID': ['COMSC110.01', 'COMSC110.01', 'COMSC110.01', 'COMSC110.01',
                        'COMSC110.02', 'COMSC110.02', 'COMSC110.02', 'COMSC110.02',
                        'COMSC210.01', 'COMSC210.01', 'COMSC210.01', 'COMSC210.01'],
            'CreditHours': [4.0, 4.0, 4.0, 4.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
        }
        
        # Convert to DataFrame
        example_df = pd.DataFrame(data)
        
        # Add GPA column based on grades
        grade_to_gpa = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        example_df['GPA'] = example_df['Grade'].map(grade_to_gpa)
        
        # Save the example data
        self.example_data = example_df
        self.example_data_loaded = True
        
        # Return the example data
        return example_df

def run_app():
    """Creates and runs the main application."""
    app = ImprovedGradeGUI()
    app.mainloop()
