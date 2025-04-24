# GPA Analysis Tool

The **GPA Analysis Tool** is a Python-based solution designed to process and analyze academic performance data across sections, groups, and runs. It includes functionalities for file parsing, GPA calculation, identifying performance outliers, statistical analysis (Z-scores), and provides multiple interfaces (command-line and graphical) for interaction. Development has explored different approaches for GUI and CLI implementations, as well as database persistence.

This project was developed to meet a specific set of requirements outlined in a course setting (COMSC 330). This README details the project's current capabilities and how they align with those requirements.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Requirements from Slides](#key-requirements-from-slides)
- [Alignment with Requirements](#alignment-with-requirements)
- [Features](#features)
- [Current Status](#current-status)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Persistence](#persistence)
- [Documentation and Plans](#documentation-and-plans)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The GPA Analysis Tool is designed to process academic data files (`.SEC`, `.GRP`, `.RUN`) to calculate GPAs, identify performance trends, perform statistical comparisons, and report findings. The project includes multiple interface implementations and experiments with data persistence.

---

## Key Requirements from Slides
| Req # | Name                             | Description                                                                                                                                    |
|-------|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 1     | Section GPA Calculation          | Go through sections and figure out each section GPA.                                                                                           |
| 2     | Grade Count Display              | Easy to see display of the number of each grade per section.                                                                                   |
| 3     | Group Sections                   | Be able to group sections together.                                                                                                            |
| 4     | Section Comparison               | Compare each section’s GPA relative to its group.                                                                                              |
| 5     | Section Significance – Z-test    | Identify if a section is significantly different (|z| >= 2) based on the group GPA.                                                             |
| 6     | Group Significance – Z-test      | For multiple groups, test if a group’s GPA is significantly different from all groups combined.                                                |
| 7     | Good List                        | List students with one or more A or A– grades.                                                                                                 |
| 8     | Work List                        | List students with one or more D+, D, D–, or F grades.                                                                                         |
| 9     | Save Lists                       | Save Good list and Work list as separate files.                                                                                                |
| 10    | History – Appeared Before        | Determine if a student has appeared on either list in the past.                                                                                |
| 11    | Comprehensive Report             | Produce a single report encompassing all analyses.                                                                                             |
| 12    | Grade Handling Rules             | F counts as zero points; I, W, P, NP are excluded from GPA calculation.                                                                        |
| 13    | File Parsing                     | Handle `.SEC`, `.GRP`, and `.RUN` formats as specified.                                                                                        |
| 14    | Data Handling                    | Data stability within a run; groups/sections can change between runs; handle empty or malformed files and last‐line quirks.                     |

## Alignment with Requirements
| Req # | Name                          | Status       | Progress                                                                                                              |
|-------|-------------------------------|--------------|-----------------------------------------------------------------------------------------------------------------------|
| 1     | Section GPA Calculation       | Done         | Implemented in `zscore_calculator.py`, `terminal_demo/gpa_calculator.py`, and `test_gui/stats_utils.py`.            |
| 2     | Grade Count Display           | Started      | CLI shows distribution; GUI needs a clear per-section grade breakdown.                                                |
| 3     | Group Sections                | Done         | Parsers (`run_parser.py`, `grp_parser.py`) correctly group sections.                                                  |
| 4     | Section Comparison            | Done         | Z-score logic compares section GPA to group average.                                                                  |
| 5     | Section Significance – Z-test | Started         | `is_significant` uses |z| >= 2.0;  threshold.                                                             |
| 6     | Group Significance – Z-test   | Not Started  | No implementation for comparing group means against overall run GPA.                                                  |
| 7     | Good List                     | Done         | `GoodAndBadList.py` and CLI/GUI functions identify A/A– students.                                                     |
| 8     | Work List                     | Done         | `GoodAndBadList.py` and CLI/GUI functions identify D+/D–/F students.                                                  |
| 9     | Save Lists                    | Started         | `History.py` saves lists to CSV; persistence tested in `test_persistence.py`.                                         |
| 10    | History – Appeared Before     | Started         | CSV history and DB schema allow setup possibilities.                                                            |
| 11    | Comprehensive Report          | Started      | `report_generator.py` and GUIs cover most content; need one unified document output.                                  |
| 12    | Grade Handling Rules          | Done         | GPA logic excludes I/W/P/NP and includes F as zero.                                                                   |
| 13    | File Parsing                  | Done         | Parsers handle `.SEC`, `.GRP`, and `.RUN` as specified.                                                               |
| 14    | Data Handling                 | Done         | Hierarchical loading with basic error checks for file issues.                                                         |

---

## Features

### Implemented (Reflecting Capabilities for Requirements):
- **File Parsing & Data Loading:** Full parsing and hierarchical loading of `.SEC`, `.GRP`, and `.RUN` files.
- **GPA Calculation:** Logic to convert grades to GPA (handling exclusions) and compute section and group averages.
- **Performer Identification:** Functions to identify and list students meeting "Good" (A/A-) and "Work" (F, D-, D, D+) list criteria.
- **Z-score Analysis:** Calculation of Z-scores and p-values for Section vs. Group comparisons, including significance testing (primarily against |z| >= 2 or p < 0.05).
- **Reporting & Display:** Text report generation (CLI, including grade distribution in `terminal_demo`) and interactive table display (GUI) for analysis results and student lists.
- **History Tracking:** Demonstrated history tracking for students on Good/Work lists via CSV (`History.py`) and database persistence capabilities (`test_persistence.py`).
- **Database Persistence (Proof-of-Concept):** Functionality to store key data (Students, Sections, Groups, Performances, Z-scores) in an SQLite database, tested via `test_persistence.py`. Not integrated into main workflows.
- **User Interfaces:** Multiple functional command-line (`terminal_tester.py`, `terminal_demo/`) and graphical interfaces (`MainGUI.py`, `test_gui/`).

---

## Current Status

The project successfully implements most of the core data processing and analysis requirements outlined in the course slideshow. This includes file parsing, GPA calculation, Good/Work lists, Section vs. Group Z-score analysis, history tracking capabilities, and reporting/display through multiple interfaces.

Database persistence for analysis results and student data has been implemented and tested (`test_persistence.py`), but it is **not integrated** into the main GUI/CLI application workflows; it exists as a standalone demonstration of the capability.

The main functional requirement identified as **not currently implemented** is the statistical test for comparing *individual Group GPAs* against the *overall Run GPA*. Additionally, the per-section grade count display (Req 2) is only available in one of the CLI implementations.

The repository structure shows different development paths (main directory modules, `terminal_demo/`, `test_gui/`), likely reflecting iterative development or parallel work. Documentation in `docs/` outlines plans for potential refactoring and further persistence work.

---

## Directory Structure

The project is organized as follows:

- **`penz6-comp330/`**: The root directory.
    - **`README.md`**: This file.
    - **Core Modules**: `FileReader.py`, `GoodAndBadList.py`, `grp_parser.py`, `History.py`, `run_parser.py`, `terminal_tester.py`, `zscore_calculator.py`. These contain foundational parsing, filtering, calculation, history tracking (CSV), and a simple CLI tester.
    - **`LICENSE`**: Project license file (Apache 2.0).
    - **`MainGUI.py`**: A primary Tkinter GUI implementation.
    - **`test.db`**: SQLite database file created and used by `test_persistence.py`.
    - **`test_persistence.py`**: Script demonstrating database schema creation and data persistence logic using SQLite.
    - **`COMSC330_POC_Data/`**: Directory containing sample academic data files.
        - **`Groups/`**: Sample `.GRP` files.
        - **`Runs/`**: Sample `.RUN` files.
        - **`Sections/`**: Sample `.SEC` files.
    - **`docs/`**: Documentation directory containing design plans.
        - `persistance_implementation_plan.md`: Plan for database persistence using SQLAlchemy.
        - `posible_DB_schema.md`: Alternative database schema ideas.
        - `refactor_plan.md`: Plan for modularizing and refactoring the codebase.
    - **`terminal_demo/`**: Contains a more structured command-line interface application and related modules (`gpa_calculator.py`, `report_generator.py`, parsers, `main.py`).
    - **`test_gui/`**: Contains another, potentially more refactored, Tkinter GUI implementation and related modules (`app.py`, `base_page.py`, `config.py`, `pages.py`, `stats_utils.py`, `test_GUI.py`).

---

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd penz6-comp330
    ```

2.  **Python Requirements:**
    The project requires Python 3.x and several libraries. Install dependencies using pip:
    ```bash
    pip install pandas scipy pandastable sv_ttk Pillow
    # Optional (if exploring persistence further based on docs):
    # pip install sqlalchemy alembic
    ```
    *Note: `scipy` is used for Z-score calculations.*

3.  **Data Files:**
    Ensure the `COMSC330_POC_Data/` directory is present in the root of the project, containing the sample `.GRP`, `.RUN`, and `.SEC` files. The scripts are configured to find this data directory relative to their location.

---

## Usage

There are multiple ways to interact with the tool. Run these commands from the root directory (`penz6-comp330/`):

1.  **Terminal Tester (Simple CLI):**
    ```bash
    python terminal_tester.py
    ```
    Provides a menu to test loading files, displaying lists, and Z-score analysis.

2.  **Terminal Demo (Structured CLI):**
    ```bash
    python terminal_demo/main.py
    ```
    Provides a different menu-driven CLI focused on processing run files and generating text reports.

3.  **Main GUI:**
    ```bash
    python MainGUI.py
    ```
    Launches a graphical interface for selecting a `.RUN` file and viewing Good/Bad lists. Requires `tkinter`, `pandastable`, `sv_ttk`, `Pillow`.

4.  **Test GUI (Alternative/Refactored GUI):**
    ```bash
    python test_gui/test_GUI.py
    ```
    Launches another GUI implementation with features like file selection, performer lists, student search/filtering, and basic Z-score analysis display. Requires `tkinter`, `pandastable`, `sv_ttk`, `Pillow`, `scipy`.

---

## Persistence

The project includes a tested implementation for persisting data to an SQLite database (`test.db`). The `test_persistence.py` script creates the necessary tables (Students, Sections, Groups, Performances, ZScores) and demonstrates inserting data derived from processing a `.RUN` file.

**This persistence functionality is currently a proof-of-concept and is not integrated into the main application interfaces (CLIs or GUIs).**

To run the persistence test and populate/re-create `test.db`:
```bash
# Ensure you are in the penz6-comp330 root directory
python test_persistence.py
```

---

## Documentation and Plans

The `docs/` directory contains markdown documents outlining design decisions and potential future directions:

- **`persistance_implementation_plan.md`**: Details a strategy for integrating database persistence more formally using SQLAlchemy.
- **`posible_DB_schema.md`**: Explores alternative database schema designs.
- **`refactor_plan.md`**: Proposes a plan for modularizing and cleaning up the codebase structure for better maintainability and reusability.

These documents provide insight into the development process and potential improvements.

---

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/YourFeature`)
6. Open a Pull Request

---

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---

This GPA Analysis Tool was developed as part of the COMSC 330 course project at RWU, Roger Williams University.