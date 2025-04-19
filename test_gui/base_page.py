"""
Base class for all pages in the Grade Analysis Tool GUI application.
"""

import tkinter as tk
from tkinter import ttk
# Use absolute imports
from test_gui.config import TITLE_FONT, DEFAULT_PADDING

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
        if hasattr(self.controller, 'home_icon') and self.controller.home_icon:
            home_btn = ttk.Button(
                button_bar,
                image=self.controller.home_icon,
                command=lambda: self.controller.show_frame_by_name('DashBoard')
            )
        else:
            home_btn = ttk.Button(
                button_bar,
                text="Home",
                command=lambda: self.controller.show_frame_by_name('DashBoard')
            )
        home_btn.pack(side=tk.LEFT, padx=5)

        return button_bar

    def update(self):
        """Force the frame to update visually."""
        self.update_idletasks()
