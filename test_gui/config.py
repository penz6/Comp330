"""
Configuration settings for the Grade Analysis Tool GUI.
"""

from pandastable import config

# Fonts
TITLE_FONT = ("Arial", 18, "bold")
BUTTON_FONT = ("Arial", 11)
INFO_FONT = ("Arial", 10, "italic")

# Padding
DEFAULT_PADDING = 10

# Pandastable options
options = config.load_options()

def configure_table_options():
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
    # Don't try to apply options globally, we'll apply them to each table when created
    return options
