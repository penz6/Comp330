#!/usr/bin/env python3
# TerminalGUI.py - GUI interface for grade analysis functionality

"""
Lets try to add some debug statements, as of now the good and work list did not save properly becasue of an ID issue could you create some statemtns that will output the status of certian calls to the terminal so i can have more detailed debugging of the GUI behavior.

Dont try to fix the described saving issue, we will use the outputs froo the debug that yoou create to do that.

Only Create these debug statemts inside the TerminalGUI file for now.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import sv_ttk as sv
import pandas as pd
from pandastable import Table, TableModel, config
import json
import threading
import queue

# Add debug utility imports
import datetime
import traceback

# Attempt to import project modules, handle potential import errors
try:
    from run_parser import runReader
    from grp_parser import grpReader
    from FileReader import fileReader
    from GoodAndBadList import Lists
    from History import HistoryManager
    from zscore_calculator import analyze_sections
except ImportError as e:
    messagebox.showerror("Import Error", f"Failed to import required module: {e}\nMake sure all project files are in the correct location.")
    sys.exit(1)

# Add debug utility function
def debug_print(category, message, data=None):
    """Print formatted debug information to the terminal"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[DEBUG][{timestamp}][{category}] {message}")
    if data is not None:
        if isinstance(data, pd.DataFrame):
            print(f"  DataFrame info: {len(data)} rows, {list(data.columns)} columns")
            print(f"  Column types: {data.dtypes}")
            if 'id' in data.columns or 'ID' in data.columns:
                id_col = 'id' if 'id' in data.columns else 'ID'
                print(f"  ID column '{id_col}' sample: {data[id_col].head(3).tolist()}")
                print(f"  ID column type: {data[id_col].dtype}")
        else:
            print(f"  {data}")

class TerminalGUIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PGUA^2 Grade Analyzer - GUI")
        self.geometry("1000x700")
        sv.set_theme("dark")
        self.current_theme = "dark"

        # Initialize state variables
        self.run_file = None
        self.grp_files = None
        self.sec_files = None
        self.top_performers = None
        self.bottom_performers = None
        self.sec_data = None
        self.zscore_results = None
        self.history = HistoryManager()
        debug_print("INIT", "HistoryManager initialized", self.history)
        self.recent_files = self._load_recent_files()
        self.search_var = tk.StringVar()
        
        # Configure pandastable style for dark theme
        self.options = config.load_options()
        self.options.update({
            'cellbackgr': '#2b2b2b', 'textcolor': '#ffffff', 'grid_color': '#444444',
            'rowselectedcolor': '#44475a', 'colheadercolor': '#1e1e1e',
            'colheaderfg': '#ffffff', 'fontsize': 10, 'rowheight': 22
        })

        # Main layout frames
        self.menu_frame = ttk.Frame(self, padding="10")
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add toolbar at the top
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Add search functionality
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.LEFT, padx=5)
        search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar, text="Find", command=self.search_table).pack(side=tk.LEFT, padx=5)
        
        # Add theme toggle button
        ttk.Button(self.toolbar, text="Toggle Theme", command=self.toggle_theme).pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.toolbar, text="Refresh", command=self.refresh_display).pack(side=tk.RIGHT, padx=5)
        
        self.display_frame = ttk.Frame(self.main_frame, padding="10")
        self.display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.table = None # Placeholder for pandastable

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self._create_menu()
        
        # Set up keyboard shortcuts
        self.bind("<Control-o>", lambda e: self.load_run())
        self.bind("<Control-e>", lambda e: self.export_data())
        self.bind("<Control-g>", lambda e: self.display_groups())
        self.bind("<Control-s>", lambda e: self.display_sections())
        self.bind("<Control-t>", lambda e: self.display_performers(top=True))
        self.bind("<Control-b>", lambda e: self.display_performers(top=False))
        self.bind("<Control-z>", lambda e: self.perform_zscore())
        self.bind("<Control-a>", lambda e: self.auto_process())
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Control-f>", lambda e: search_entry.focus_set())
        
        # For operations that might take time
        self.task_queue = queue.Queue()
        self.check_queue()

    def _create_menu(self):
        """Creates the buttons in the left-side menu frame."""
        ttk.Label(self.menu_frame, text="Menu", font=("Arial", 16, "bold")).pack(pady=10)

        menu_items = [
            ("Load RUN File (Ctrl+O)", self.load_run),
            ("Display Groups (Ctrl+G)", self.display_groups),
            ("Display Sections (Ctrl+S)", self.display_sections),
            ("Top Performers (Ctrl+T)", lambda: self.display_performers(top=True)),
            ("Bottom Performers (Ctrl+B)", lambda: self.display_performers(top=False)),
            ("Export Data (Ctrl+E)", self.export_data),
            ("Read SEC File", self.read_sec_file),
            ("Z-Score Analysis (Ctrl+Z)", self.perform_zscore),
            ("Manage History", self.manage_history),
            ("Auto-Process (Ctrl+A)", self.auto_process),
            ("Help (F1)", self.show_help),
            ("Exit", self.quit)
        ]

        for text, command in menu_items:
            ttk.Button(self.menu_frame, text=text, command=command, width=20).pack(pady=5, fill=tk.X)
            
        # Add recent files section
        ttk.Separator(self.menu_frame).pack(fill=tk.X, pady=10)
        ttk.Label(self.menu_frame, text="Recent Files").pack(pady=5)
        
        self.recent_files_frame = ttk.Frame(self.menu_frame)
        self.recent_files_frame.pack(fill=tk.X)
        self._update_recent_files_menu()
        
    def _update_recent_files_menu(self):
        """Updates the recent files menu items"""
        for widget in self.recent_files_frame.winfo_children():
            widget.destroy()
            
        for file_path in self.recent_files[:5]:  # Show up to 5 recent files
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                button = ttk.Button(
                    self.recent_files_frame, 
                    text=file_name,
                    command=lambda path=file_path: self._open_recent_file(path)
                )
                button.pack(fill=tk.X, pady=2)
                
    def _open_recent_file(self, file_path):
        """Opens a file from the recent files list"""
        self.run_file = file_path
        self._add_recent_file(file_path)
        self._show_message("RUN File Loaded", f"Successfully loaded:\n{os.path.basename(self.run_file)}")
        # Reset dependent data
        self.grp_files = None
        self.sec_files = None
        self.top_performers = None
        self.bottom_performers = None
        self.zscore_results = None
        self._clear_display()
        self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
                
    def _load_recent_files(self):
        """Load recent files from JSON file"""
        config_path = Path.home() / ".pgua_recent_files.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
        
    def _save_recent_files(self):
        """Save recent files to JSON file"""
        config_path = Path.home() / ".pgua_recent_files.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(self.recent_files, f)
        except Exception as e:
            print(f"Error saving recent files: {e}")
            
    def _add_recent_file(self, filepath):
        """Add a file to recent files list"""
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        self.recent_files.insert(0, filepath)
        if len(self.recent_files) > 10:  # Keep only 10 most recent
            self.recent_files = self.recent_files[:10]
        self._save_recent_files()
        self._update_recent_files_menu()

    def _clear_display(self):
        """Clears the right-side display frame."""
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.table = None

    def _display_dataframe(self, df, title="Data"):
        """Displays a pandas DataFrame in the display frame using pandastable."""
        self._clear_display()
        if df is None or df.empty:
            ttk.Label(self.display_frame, text=f"No {title} data to display.").pack(pady=20)
            return

        ttk.Label(self.display_frame, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        
        # Display summary info if available
        if not df.empty:
            info_frame = ttk.Frame(self.display_frame)
            info_frame.pack(fill=tk.X, pady=5)
            ttk.Label(info_frame, text=f"Rows: {len(df)}, Columns: {len(df.columns)}").pack(side=tk.LEFT, padx=5)
            
        table_frame = ttk.Frame(self.display_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.table = Table(table_frame, dataframe=df, showtoolbar=True, showstatusbar=True, editable=False)
        config.apply_options(self.options, self.table) # Apply theme options
        self.table.show()
        
    def search_table(self):
        """Search the current table for the search term"""
        if self.table is None:
            self._show_message("Search", "No data to search.")
            return
            
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            self._show_message("Search", "Please enter a search term.")
            return
            
        df = self.table.model.df
        
        # Convert all columns to string and check if they contain the search term
        found = False
        for col in df.columns:
            df_str = df[col].astype(str).str.lower()
            matches = df_str.str.contains(search_term)
            if matches.any():
                found = True
                self.table.setSelectedRow(matches[matches].index[0])
                break
                
        if not found:
            self._show_message("Search", f"No matches found for '{search_term}'")
        else:
            self.status_var.set(f"Found match for '{search_term}'")

    def _show_message(self, title, message, msg_type="info"):
        """Shows a message box."""
        if msg_type == "error":
            messagebox.showerror(title, message)
            self.status_var.set(f"Error: {message[:50]}...")
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
            self.status_var.set(f"Warning: {message[:50]}...")
        else:
            messagebox.showinfo(title, message)
            self.status_var.set(f"Info: {message[:50]}...")

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.current_theme == "dark":
            sv.set_theme("light")
            self.current_theme = "light"
            self.options.update({
                'cellbackgr': '#ffffff', 'textcolor': '#000000', 'grid_color': '#cccccc',
                'rowselectedcolor': '#e6e6e6', 'colheadercolor': '#f0f0f0',
                'colheaderfg': '#000000'
            })
        else:
            sv.set_theme("dark")
            self.current_theme = "dark"
            self.options.update({
                'cellbackgr': '#2b2b2b', 'textcolor': '#ffffff', 'grid_color': '#444444',
                'rowselectedcolor': '#44475a', 'colheadercolor': '#1e1e1e',
                'colheaderfg': '#ffffff'
            })
            
        # Update table if exists
        if self.table:
            config.apply_options(self.options, self.table)
            self.table.redraw()
            
        self.status_var.set(f"Theme changed to {self.current_theme}")

    def refresh_display(self):
        """Refresh the current display"""
        if self.table:
            self.table.redraw()
        self.status_var.set("Display refreshed")
        
    def show_help(self):
        """Show help information"""
        help_window = tk.Toplevel(self)
        help_window.title("PGUA² Grade Analyzer Help")
        help_window.geometry("600x500")
        sv.set_theme(self.current_theme)
        
        help_text = """
        PGUA² Grade Analyzer - Help
        
        Keyboard Shortcuts:
        - Ctrl+O: Load RUN file
        - Ctrl+G: Display Groups
        - Ctrl+S: Display Sections
        - Ctrl+T: Show Top Performers
        - Ctrl+B: Show Bottom Performers
        - Ctrl+E: Export Data
        - Ctrl+Z: Perform Z-Score Analysis
        - Ctrl+A: Run Auto-Process
        - Ctrl+F: Focus on search box
        - F1: Show this help
        
        Basic Usage:
        1. Load a RUN file using "Load RUN File"
        2. View Groups and Sections
        3. Check Top/Bottom performers
        4. Perform Z-Score analysis
        
        Tables can be sorted by clicking on column headers.
        Use the search box to find specific data in tables.
        """
        
        text_area = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text_area.insert(tk.END, help_text)
        text_area.config(state=tk.DISABLED)
        
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)
    
    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a background thread with progress updates"""
        def thread_target():
            try:
                self.status_var.set("Processing...")
                result = func(*args, **kwargs)
                self.task_queue.put((lambda: self.status_var.set("Ready")))
                return result
            except Exception as e:
                self.task_queue.put((lambda: self._show_message("Error", str(e), "error")))
                return None
                
        thread = threading.Thread(target=thread_target)
        thread.daemon = True
        thread.start()
        
    def check_queue(self):
        """Check for completed tasks"""
        try:
            while True:
                task = self.task_queue.get_nowait()
                task()
                self.task_queue.task_done()
        except queue.Empty:
            pass
        self.after(100, self.check_queue)

    def load_run(self):
        """Prompts user to select a RUN file."""
        # Define file types for the dialog
        filetypes = (
            ('RUN files', '*.run'),
            ('Text files', '*.run.txt'),
            ('All files', '*.*')
        )
        # Default directory (can be adjusted)
        initial_dir = Path(__file__).parent / "COMSC330_POC_Data"
        if not initial_dir.exists():
            initial_dir = Path.home()

        filepath = filedialog.askopenfilename(
            title="Select a RUN file",
            initialdir=str(initial_dir),
            filetypes=filetypes
        )
        if filepath:
            fname_lower = filepath.lower()
            if fname_lower.endswith('.run') or fname_lower.endswith('.run.txt'):
                self.run_file = filepath
                self._add_recent_file(filepath)  # Add to recent files
                self._show_message("RUN File Loaded", f"Successfully loaded:\n{os.path.basename(self.run_file)}")
                # Reset dependent data
                self.grp_files = None
                self.sec_files = None
                self.top_performers = None
                self.bottom_performers = None
                self.zscore_results = None
                self._clear_display() # Clear display after loading new file
                self.status_var.set(f"Loaded: {os.path.basename(self.run_file)}")
            else:
                self._show_message("Error", "Invalid file type. Please select a .run or .run.txt file.", "error")
                self.run_file = None

    def display_groups(self):
        """Displays groups found in the loaded RUN file."""
        if not self.run_file:
            self._show_message("Error", "Please load a RUN file first.", "error")
            return
        try:
            self.grp_files = runReader(self.run_file)
            self._clear_display()
            ttk.Label(self.display_frame, text="Groups Found:", font=("Arial", 14, "bold")).pack(pady=10)
            if self.grp_files:
                listbox = tk.Listbox(self.display_frame, width=80, height=15, bg="#2b2b2b", fg="#ffffff", selectbackground="#44475a")
                listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
                for grp in self.grp_files:
                    listbox.insert(tk.END, os.path.basename(grp))
                self._show_message("Groups", f"Found {len(self.grp_files)} group files.")
            else:
                ttk.Label(self.display_frame, text="No group files found.").pack(pady=20)
        except Exception as e:
            self._show_message("Error Reading Groups", f"An error occurred: {e}", "error")
            self.grp_files = None

    def display_sections(self):
        """Displays sections found from the loaded groups."""
        if not self.run_file:
            self._show_message("Error", "Please load a RUN file first.", "error")
            return
        if not self.grp_files:
             # Attempt to load groups if not already loaded
            try:
                self.grp_files = runReader(self.run_file)
                if not self.grp_files:
                    self._show_message("Error", "No groups found in the RUN file. Cannot load sections.", "error")
                    return
            except Exception as e:
                self._show_message("Error Reading Groups", f"Failed to load groups automatically: {e}", "error")
                return

        try:
            self.sec_files = grpReader(self.run_file, self.grp_files)
            self._clear_display()
            ttk.Label(self.display_frame, text="Sections Found:", font=("Arial", 14, "bold")).pack(pady=10)
            if self.sec_files:
                listbox = tk.Listbox(self.display_frame, width=80, height=15, bg="#2b2b2b", fg="#ffffff", selectbackground="#44475a")
                listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
                for sec in self.sec_files:
                    listbox.insert(tk.END, sec) # Display full path or relative path as needed
                self._show_message("Sections", f"Found {len(self.sec_files)} section files.")
            else:
                 ttk.Label(self.display_frame, text="No section files found.").pack(pady=20)
        except Exception as e:
            self._show_message("Error Reading Sections", f"An error occurred: {e}", "error")
            self.sec_files = None

    def display_performers(self, top=True):
        """Displays top or bottom performers."""
        if not self.run_file:
            self._show_message("Error", "Please load a RUN file first.", "error")
            return

        list_type = "Top" if top else "Bottom"
        list_func = Lists.goodList if top else Lists.badList
        history_update_func = self.history.update_good_list if top else self.history.update_work_list
        history_list_name = "Good List" if top else "Work List"

        debug_print("PERFORMERS", f"Starting {list_type} performers display", {"run_file": self.run_file})

        try:
            debug_print("PERFORMERS", f"Calling {list_func.__name__} function")
            performers_df = list_func(self.run_file)
            debug_print("PERFORMERS", f"{list_type} performers data loaded", performers_df)
            
            if top:
                self.top_performers = performers_df
            else:
                self.bottom_performers = performers_df

            self._display_dataframe(performers_df, f"{list_type} Performers")

            if not performers_df.empty:
                # Check all columns case-insensitively for ID
                debug_print("ID_CHECK", "Looking for ID column", {"columns": list(performers_df.columns)})
                id_cols = [col for col in performers_df.columns if col.lower() == 'id']
                debug_print("ID_CHECK", f"Found ID columns: {id_cols}")
                
                # Ensure 'id' column exists for history update
                id_col = next((col for col in performers_df.columns if col.lower() == 'id'), None)
                if not id_col:
                    debug_print("ERROR", f"ID column missing in {list_type} performers data", performers_df.columns)
                    self._show_message("Warning", f"Cannot update history: '{list_type} Performers' data is missing an 'id' column.", "warning")
                    return

                # Rename if necessary (case-insensitive match)
                if id_col != 'id':
                    debug_print("ID_RENAME", f"Renaming column '{id_col}' to 'id'", 
                               {"before_dtype": performers_df[id_col].dtype, "sample": performers_df[id_col].head(3)})
                    performers_df = performers_df.rename(columns={id_col: 'id'})
                    debug_print("ID_RENAME", "After renaming", 
                               {"has_id_col": 'id' in performers_df.columns, 
                                "dtype": performers_df['id'].dtype if 'id' in performers_df.columns else None})
                    if top: self.top_performers = performers_df
                    else: self.bottom_performers = performers_df

                debug_print("HISTORY", f"Before updating {history_list_name}", 
                           {"df_shape": performers_df.shape, 
                            "id_sample": performers_df['id'].head(3) if 'id' in performers_df.columns else None})

                update = messagebox.askyesno("Update History", f"Update {history_list_name} history with these {len(performers_df)} students?")
                if update:
                    debug_print("HISTORY", f"Updating {history_list_name}", {"id_col_exists": 'id' in performers_df.columns})
                    try:
                        updated_df, already_on_list = history_update_func(performers_df)
                        debug_print("HISTORY", f"{history_list_name} update result", 
                                   {"updated_df_shape": updated_df.shape if updated_df is not None else None, 
                                    "already_on_list_count": len(already_on_list)})
                        new_count = len(performers_df) - len(already_on_list)
                        self._show_message("History Updated", f"{history_list_name} updated.\nNew students added: {new_count}\nAlready on list: {len(already_on_list)}")
                    except Exception as update_err:
                        debug_print("ERROR", f"Error updating {history_list_name}", 
                                    {"error": str(update_err), "traceback": traceback.format_exc()})
                        self._show_message(f"History Update Error", f"Failed to update {history_list_name}: {update_err}", "error")

        except Exception as e:
            debug_print("ERROR", f"Error in display_performers({top})", 
                       {"error": str(e), "traceback": traceback.format_exc()})
            self._show_message(f"Error Loading {list_type} Performers", f"An error occurred: {e}", "error")
            if top: self.top_performers = None
            else: self.bottom_performers = None

    def export_data(self):
        """Provides options to export data to HTML."""
        export_options = {
            "Top Performers": self.top_performers,
            "Bottom Performers": self.bottom_performers,
            "SEC Data": self.sec_data,
            "Z-Score Analysis": self.zscore_results,
            "Historical Good List": self.history.get_good_list(),
            "Historical Work List": self.history.get_work_list()
        }

        # Create a simple dialog for selection
        dialog = tk.Toplevel(self)
        dialog.title("Export Data")
        dialog.geometry("300x300")
        sv.set_theme("dark") # Apply theme to dialog

        ttk.Label(dialog, text="Select data to export:").pack(pady=10)

        listbox = tk.Listbox(dialog, selectmode=tk.SINGLE, exportselection=False, bg="#2b2b2b", fg="#ffffff", selectbackground="#44475a")
        for key in export_options.keys():
            listbox.insert(tk.END, key)
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def on_export():
            selection_index = listbox.curselection()
            if not selection_index:
                self._show_message("Export Error", "Please select an item to export.", "warning")
                return

            selected_key = listbox.get(selection_index[0])
            df_to_export = export_options[selected_key]

            if df_to_export is None or df_to_export.empty:
                self._show_message("Export Error", f"No data available for '{selected_key}'.", "warning")
                return

            filename_suggestion = f"{selected_key.lower().replace(' ', '_')}_export.html"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=filename_suggestion,
                title=f"Save {selected_key} as HTML"
            )

            if filepath:
                try:
                    df_to_export.to_html(filepath, index=False)
                    self._show_message("Export Successful", f"Data exported to:\n{filepath}")
                    dialog.destroy()
                except Exception as e:
                    self._show_message("Export Error", f"Failed to export data: {e}", "error")

        ttk.Button(dialog, text="Export Selected", command=on_export).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)


    def read_sec_file(self):
        """Prompts user to select a SEC file and displays its content."""
        filetypes = (('SEC files', '*.sec'), ('All files', '*.*'))
        initial_dir = Path(__file__).parent / "COMSC330_POC_Data"
        if not initial_dir.exists(): initial_dir = Path.home()

        filepath = filedialog.askopenfilename(
            title="Select a SEC file",
            initialdir=str(initial_dir),
            filetypes=filetypes
        )
        if filepath:
            if filepath.lower().endswith('.sec'):
                try:
                    self.sec_data = fileReader.readSEC(filepath)
                    self._display_dataframe(self.sec_data, f"SEC Data: {os.path.basename(filepath)}")
                except Exception as e:
                    self._show_message("Error Reading SEC File", f"An error occurred: {e}", "error")
                    self.sec_data = None
            else:
                self._show_message("Error", "Invalid file type. Please select a .sec file.", "error")

    def perform_zscore(self):
        """Performs Z-score analysis."""
        if not self.run_file or not self.grp_files or not self.sec_files:
             # Check and try to load dependencies if missing
            if not self.run_file:
                self._show_message("Error", "Please load a RUN file first.", "error")
                return
            if not self.grp_files:
                self.display_groups() # Attempt to load groups
                if not self.grp_files: return # Exit if still no groups
            if not self.sec_files:
                self.display_sections() # Attempt to load sections
                if not self.sec_files: return # Exit if still no sections

        try:
            threshold_str = simpledialog.askstring("Z-Score Threshold", "Enter significance threshold (e.g., 1.96 for 95%):", initialvalue="1.96")
            if threshold_str is None: return # User cancelled

            try:
                threshold = float(threshold_str)
            except ValueError:
                self._show_message("Error", "Invalid threshold value. Please enter a number.", "error")
                return

            result_data, self.zscore_results = analyze_sections(self.run_file, self.grp_files, self.sec_files, threshold)

            if self.zscore_results is None or self.zscore_results.empty:
                 self._show_message("Z-Score Analysis", "No results generated from the analysis.")
            else:
                # Display summary info if available
                summary_text = ""
                if result_data:
                    summary_text = f"Group GPA: {result_data[0].get('group_gpa', 'N/A'):.2f}, Group Std Dev: {result_data[0].get('group_std', 'N/A'):.2f}"

                self._display_dataframe(self.zscore_results, f"Z-Score Analysis Results\n{summary_text}")

        except Exception as e:
            self._show_message("Z-Score Error", f"An error occurred during Z-score analysis: {e}", "error")
            self.zscore_results = None

    def manage_history(self):
        """Opens a new window for history management."""
        debug_print("HISTORY", "Opening history management window")
        history_window = tk.Toplevel(self)
        history_window.title("Student History Management")
        history_window.geometry("700x500")
        sv.set_theme("dark") # Apply theme

        notebook = ttk.Notebook(history_window)

        # Frame for Good List
        good_list_frame = ttk.Frame(notebook, padding="10")
        notebook.add(good_list_frame, text='Good List History')
        good_list_df = self.history.get_good_list()
        debug_print("HISTORY", "Retrieved good list history", good_list_df)
        if good_list_df.empty:
            ttk.Label(good_list_frame, text="Good List history is empty.").pack(pady=20)
        else:
            good_table_frame = ttk.Frame(good_list_frame)
            good_table_frame.pack(fill=tk.BOTH, expand=True)
            good_table = Table(good_table_frame, dataframe=good_list_df, showtoolbar=False, showstatusbar=True, editable=False)
            config.apply_options(self.options, good_table)
            good_table.show()

        # Frame for Work List
        work_list_frame = ttk.Frame(notebook, padding="10")
        notebook.add(work_list_frame, text='Work List History')
        work_list_df = self.history.get_work_list()
        debug_print("HISTORY", "Retrieved work list history", work_list_df)
        if work_list_df.empty:
            ttk.Label(work_list_frame, text="Work List history is empty.").pack(pady=20)
        else:
            work_table_frame = ttk.Frame(work_list_frame)
            work_table_frame.pack(fill=tk.BOTH, expand=True)
            work_table = Table(work_table_frame, dataframe=work_list_df, showtoolbar=False, showstatusbar=True, editable=False)
            config.apply_options(self.options, work_table)
            work_table.show()

        # Frame for checking individual student
        check_student_frame = ttk.Frame(notebook, padding="10")
        notebook.add(check_student_frame, text='Check Student')

        ttk.Label(check_student_frame, text="Enter Student ID:").pack(side=tk.LEFT, padx=5)
        student_id_entry = ttk.Entry(check_student_frame, width=15)
        student_id_entry.pack(side=tk.LEFT, padx=5)
        result_label = ttk.Label(check_student_frame, text="")
        result_label.pack(side=tk.LEFT, padx=10)

        def check_student():
            try:
                student_id = int(student_id_entry.get())
                debug_print("HISTORY", f"Checking student history for ID: {student_id}")
                history_info = self.history.check_student_history(student_id)
                debug_print("HISTORY", "Student history check result", history_info)
                result_text = f"Student {student_id}: Good List: {'Yes' if history_info['good_list'] else 'No'}, Work List: {'Yes' if history_info['work_list'] else 'No'}"
                result_label.config(text=result_text)
            except ValueError:
                result_label.config(text="Invalid ID. Please enter a number.")
            except Exception as e:
                debug_print("ERROR", f"Error checking student history", {"error": str(e)})
                result_label.config(text=f"Error checking history: {e}")

        ttk.Button(check_student_frame, text="Check", command=check_student).pack(side=tk.LEFT, padx=5)

        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def auto_process(self):
        """Runs the full processing pipeline automatically."""
        debug_print("AUTO", "Starting auto-process workflow")
        self._show_message("Auto-Process", "Starting automatic processing pipeline...")
        self.status_var.set("Auto-processing started...")

        # 1. Load RUN file (reuse existing method, but handle cancellation)
        self.load_run()
        if not self.run_file:
            debug_print("AUTO", "Auto-process cancelled: No RUN file selected")
            self._show_message("Auto-Process", "Auto-process cancelled: No RUN file selected.", "warning")
            return

        progress_steps = 7
        current_step = 1

        def update_status(message):
            nonlocal current_step
            debug_print("AUTO", f"Step {current_step}/{progress_steps}: {message}")
            self.status_var.set(f"[{current_step}/{progress_steps}] {message}")
            self._show_message("Auto-Process Status", f"[{current_step}/{progress_steps}] {message}")
            current_step += 1
            self.update_idletasks() # Update GUI

        try:
            # 2. Load groups
            update_status("Loading groups...")
            self.grp_files = runReader(self.run_file)
            if not self.grp_files: raise Exception("No groups found.")
            update_status(f"Loaded {len(self.grp_files)} group files.")

            # 3. Load sections
            self.sec_files = grpReader(self.run_file, self.grp_files)
            if not self.sec_files: raise Exception("No sections found.")
            update_status(f"Loaded {len(self.sec_files)} section files.")

            # 4. Process top performers
            update_status("Processing top performers...")
            self.top_performers = Lists.goodList(self.run_file)
            debug_print("AUTO", "Top performers processed", self.top_performers)
            if self.top_performers.empty:
                update_status("No top performers found.")
            else:
                update_status(f"Found {len(self.top_performers)} top performers.")
                # Attempt history update (optional, could be made configurable)
                debug_print("AUTO", "Looking for ID column in top performers", {"columns": list(self.top_performers.columns)})
                id_col = next((col for col in self.top_performers.columns if col.lower() == 'id'), None)
                if id_col:
                    if id_col != 'id': 
                        debug_print("AUTO", f"Renaming column '{id_col}' to 'id' in top performers", 
                                   {"before_type": self.top_performers[id_col].dtype})
                        self.top_performers = self.top_performers.rename(columns={id_col: 'id'})
                        debug_print("AUTO", "After renaming", 
                                   {"has_id_column": 'id' in self.top_performers.columns,
                                    "id_dtype": self.top_performers['id'].dtype if 'id' in self.top_performers.columns else None})
                    
                    debug_print("AUTO", "Updating good list history", 
                               {"id_column_sample": self.top_performers['id'].head(3) if 'id' in self.top_performers.columns else None})
                    try:
                        updated_df, already_on_list = self.history.update_good_list(self.top_performers)
                        debug_print("AUTO", "Good list update results", 
                                   {"updated_df_rows": len(updated_df) if updated_df is not None else 0,
                                    "already_on_list": len(already_on_list)})
                        update_status(f"Good List updated ({len(self.top_performers) - len(already_on_list)} new).")
                    except Exception as update_err:
                        debug_print("ERROR", "Failed to update good list", 
                                  {"error": str(update_err), "traceback": traceback.format_exc()})
                        update_status(f"Error updating Good List: {update_err}")
                else:
                    debug_print("AUTO", "No ID column found in top performers", {"columns": list(self.top_performers.columns)})
                    update_status("Skipping Good List history update (no 'id' column).")

            # 5. Process bottom performers
            update_status("Processing bottom performers...")
            self.bottom_performers = Lists.badList(self.run_file)
            debug_print("AUTO", "Bottom performers processed", self.bottom_performers)
            if self.bottom_performers.empty:
                update_status("No bottom performers found.")
            else:
                update_status(f"Found {len(self.bottom_performers)} bottom performers.")
                 # Attempt history update
                debug_print("AUTO", "Looking for ID column in bottom performers", {"columns": list(self.bottom_performers.columns)})
                id_col = next((col for col in self.bottom_performers.columns if col.lower() == 'id'), None)
                if id_col:
                    if id_col != 'id': 
                        debug_print("AUTO", f"Renaming column '{id_col}' to 'id' in bottom performers", 
                                   {"before_type": self.bottom_performers[id_col].dtype})
                        self.bottom_performers = self.bottom_performers.rename(columns={id_col: 'id'})
                        debug_print("AUTO", "After renaming", 
                                   {"has_id_column": 'id' in self.bottom_performers.columns,
                                    "id_dtype": self.bottom_performers['id'].dtype if 'id' in self.bottom_performers.columns else None})
                    
                    debug_print("AUTO", "Updating work list history", 
                               {"id_column_sample": self.bottom_performers['id'].head(3) if 'id' in self.bottom_performers.columns else None})
                    try:
                        updated_df, already_on_list = self.history.update_work_list(self.bottom_performers)
                        debug_print("AUTO", "Work list update results", 
                                   {"updated_df_rows": len(updated_df) if updated_df is not None else 0,
                                    "already_on_list": len(already_on_list)})
                        update_status(f"Work List updated ({len(self.bottom_performers) - len(already_on_list)} new).")
                    except Exception as update_err:
                        debug_print("ERROR", "Failed to update work list", 
                                  {"error": str(update_err), "traceback": traceback.format_exc()})
                        update_status(f"Error updating Work List: {update_err}")
                else:
                    debug_print("AUTO", "No ID column found in bottom performers", {"columns": list(self.bottom_performers.columns)})
                    update_status("Skipping Work List history update (no 'id' column).")

            # 6. Read first SEC file (optional, find one automatically)
            update_status("Loading first available SEC file...")
            sec_file_to_read = None
            data_dir = Path(__file__).parent / "COMSC330_POC_Data"
            if data_dir.exists():
                for file in data_dir.rglob("*.sec"):
                    sec_file_to_read = str(file)
                    break # Found the first one

            if sec_file_to_read:
                self.sec_data = fileReader.readSEC(sec_file_to_read)
                update_status(f"Loaded SEC data from {os.path.basename(sec_file_to_read)} ({len(self.sec_data)} rows).")
            else:
                update_status("No SEC files found in data directory. Skipping SEC load.")
                self.sec_data = None

            # 7. Perform Z-score analysis
            update_status("Performing Z-score analysis (threshold 1.96)...")
            threshold = 1.96
            result_data, self.zscore_results = analyze_sections(self.run_file, self.grp_files, self.sec_files, threshold)
            if not result_data:
                update_status("No Z-score results found.")
            else:
                update_status(f"Z-score analysis complete ({len(result_data)} sections).")

            self._show_message("Auto-Process Complete", "Automatic processing finished successfully!")
            self.status_var.set("Auto-processing completed successfully")
            # Optionally display final results, e.g., Z-scores
            if self.zscore_results is not None and not self.zscore_results.empty:
                 self._display_dataframe(self.zscore_results, "Z-Score Analysis Results")


        except Exception as e:
            debug_print("ERROR", "Auto-process error", {"error": str(e), "traceback": traceback.format_exc()})
            self._show_message("Auto-Process Error", f"Pipeline stopped due to error:\n{e}", "error")
            self.status_var.set(f"Auto-process error: {str(e)[:50]}...")


if __name__ == "__main__":
    # Ensure History files exist before starting
    try:
        debug_print("STARTUP", "Initializing history files")
        HistoryManager() # This will create files if they don't exist
    except Exception as e:
         debug_print("ERROR", "History initialization failed", {"error": str(e)})
         messagebox.showerror("History Init Error", f"Could not initialize history files: {e}")
         sys.exit(1)

    debug_print("STARTUP", "Starting TerminalGUIApp")
    app = TerminalGUIApp()
    app.mainloop()
