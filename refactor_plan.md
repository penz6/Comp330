# Modularization & Refactor Plan

This document walks through how to break the existing monolithic zscore_calculator.py (and related GPA/statistics code) into clean, focused modules. You’ll end up with reusable packages for parsing, reading, calculating, filtering, and reporting.

---

## 1. Identify Responsibilities

In **zscore_calculator.py** we currently have:

1. Grade → numeric GPA conversion  
2. Section‐level stats (mean & count)  
3. Group‐level stats (mean & stddev)  
4. Z‑score & p‑value calculation  
5. Significance test  
6. File‐I/O: locate & read `.SEC` files via `FileReader`  
7. Aggregation & JSON‑ready output  
8. CLI/API arguments (unused imports: `argparse`, `json`)

Each of these can become its own module.

---

## 2. Proposed Package Layout

```
Comp330/
├─ parsers/
│   └─ section.py          # parse raw SEC rows → structured records
│
├─ readers/
│   └─ sec_reader.py       # load .SEC file → pandas.DataFrame
│
├─ calculators/
│   ├─ gpa.py              # letter_to_gpa, calculate_section_stats, calculate_group_stats
│   └─ stats.py            # compute_z_score, compute_p_value, is_significant
│
├─ reporters/
│   └─ analyzer.py         # analyze_sections → results list & DataFrame
│
└─ cli.py                  # entry point: parse args, call analyzer, output JSON/print
```

---

## 3. Step‑by‑Step Refactor

1. **Move GPA logic → calculators/gpa.py**  
   - Copy `letter_to_gpa`, `calculate_section_stats`, `calculate_group_stats`.  
   - Export as public functions.  

2. **Move Z‑score logic → calculators/stats.py**  
   - Copy `compute_z_score`, `compute_p_value`, `is_significant`.  

3. **Extract file reading → readers/sec_reader.py**  
   - Wrap `from FileReader import fileReader.readSEC` (or reimplement with pandas).  
   - Provide `def load_section(path: str) → DataFrame`.  

4. **Create parser (optional) → parsers/section.py**  
   - If `.SEC` has custom headers/footers, parse raw lines into rows.  
   - Return a list of dicts or DataFrame‐ready data.  

5. **Assemble analysis → reporters/analyzer.py**  
   - Import `load_section`, GPA & stats functions.  
   - Rewrite `analyze_sections(...)` here.  
   - Remove `argparse`, `json`—leave formatting to CLI.  

6. **Build CLI → cli.py**  
   - Use `argparse` to accept `--sections`, `--threshold`, etc.  
   - Call `reporters.analyzer.analyze_sections`, then `print(json.dumps(...))`.  

7. **Update imports & remove dead code**  
   - In each module, only import its direct dependencies.  
   - Drop unused imports in zscore_calculator.py (after refactor, it goes away).  

8. **Write tests**  
   - For `calculators/gpa.py`: test edge cases (empty grades, excluded grades).  
   - For `calculators/stats.py`: zero‐std, large z, p‐value correctness.  
   - For `readers/sec_reader.py`: mock file with headers.  
   - For `reporters/analyzer.py`: end‐to‐end small dataset.  

---

## 4. Dependency Graph

```
cli.py
 └─ reporters/analyzer.py
     ├─ readers/sec_reader.py
     │   └─ parsers/section.py   (optional)
     ├─ calculators/gpa.py
     └─ calculators/stats.py
```

- Parsers have no dependencies.  
- Readers depend on parsers.  
- Calculators are independent of I/O.  
- Analyzer ties readers + calculators together.  
- CLI ties everything and handles user I/O.

---

## 5. Benefits

- **Single Responsibility** per module  
- **Reusability**: use GPA/stats code in GUI, web, batch jobs  
- **Testability**: unit tests for each module  
- **Maintainability**: small files, clear imports  
- **Scalability**: easy to add new calculators (e.g., t‑tests) or parsers (new file types)

---

### Next Steps

1. Scaffold the folder structure.  
2. Move functions one module at a time, updating imports.  
3. Run tests at each step.  
4. Remove the old zscore_calculator.py once fully migrated.