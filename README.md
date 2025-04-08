# GPA Analysis Tool

The **GPA Analysis Tool** is a Python-based solution being developed to compute and analyze GPAs across academic sections, groups, and runs. This tool will process academic data files to generate reports highlighting key performance insights.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Current Progress](#current-progress)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Development Roadmap](#development-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

The GPA Analysis Tool is designed to:

- **Process Hierarchical Data:** Navigate and analyze data organized in sections, groups, and runs.
- **Parse Academic Files:** Read and process `.GRP`, `.RUN`, and `.SEC` files containing student records.
- **Calculate GPAs:** Compute weighted grade point averages across different academic units.
- **Generate Reports:** Create summaries of academic performance data.

---

## Current Progress

The project is in early development stages:

- ✅ SEC file reader implementation completed
- ⏳ Group and Run file readers under development
- ⏳ GPA calculation logic pending implementation
- ⏳ Reporting functionality planned for future development

---

## Features

### Implemented:
- **SEC File Processing:** 
  - Read and parse section files containing student records
  - Parse data into structured format using pandas DataFrame

### Planned:
- **Complete File Processing:** 
  - Support for `.GRP` and `.RUN` files
  - Handle data in a hierarchical structure (sections → groups → runs)
  
- **GPA Computation:**
  - Calculate weighted GPAs based on credit hours
  - Aggregate statistics at section, group, and run levels
  
- **Basic Reporting:**
  - Generate plain text reports with summary statistics
  - Include performance metrics for different academic units

---

## Directory Structure

The project expects a data directory structure containing:

- **Groups/**  
  Contains group definition files (`.GRP`) that associate sections with groups.

- **Runs/**  
  Contains run definition files (`.RUN`) that associate groups with analysis runs.

- **Sections/**  
  Contains section data files (`.SEC`) with student records and grades.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/penz6/Comp330.git
   cd Comp330
   ```

2. **Python Requirements:**

   The project requires:
   - Python 3.x
   - pandas library

   Install dependencies:
   ```bash
   pip install pandas
   ```

---

## Usage

The project is currently under development and not fully functional. For testing the SEC file reader:

```python
from FileReader import fileReader

# Read a SEC file
df = fileReader.readSEC('path/to/your/file.data.SEC')
print(df)
```

Full usage instructions will be provided as more functionality is implemented.

---

## Development Roadmap

1. **Phase 1 (In Progress):** 
   - Complete file readers for all data types
   - Establish data structure relationships

2. **Phase 2 (Planned):**
   - Implement GPA calculation algorithms
   - Create basic aggregation methods

3. **Phase 3 (Planned):**
   - Develop reporting functionality
   - Add data visualization options

---

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request with a description of your enhancements

---

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

---

This GPA Analysis Tool is being developed as part of the Comp330 course project at Loyola University Chicago.