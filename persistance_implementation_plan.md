# Persistence Implementation Plan

This document describes how to persist Good/Bad student lists and Z‑score analysis data into a SQL database.

---

## 1. Goals

- Store top (“A”, “A-”) and bottom (“F”, “D-”) performer records.
- Persist section statistics (mean GPA, count).
- Persist group statistics (mean, stddev).
- Persist Z‑score test results per section (z_score, p_value, significance).
- Enable querying, reporting, and reuse across runs.

---

## 2. Technology Stack

- Python ORM: SQLAlchemy
- Database: SQLite (development) / PostgreSQL (production)
- Migrations: Alembic
- Connection URL via environment variable or config file

---

## 3. Data Model

```sql
-- Tables
Students (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  fname        TEXT NOT NULL,
  lname        TEXT NOT NULL,
  student_id   TEXT NOT NULL UNIQUE
);

Sections (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT NOT NULL UNIQUE,
  mean_gpa     REAL NOT NULL,
  count        INTEGER NOT NULL
);

Groups (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT NOT NULL UNIQUE,
  mean_gpa     REAL NOT NULL,
  stddev       REAL NOT NULL
);

Performances (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  section_id   INTEGER NOT NULL REFERENCES Sections(id),
  student_id   INTEGER NOT NULL REFERENCES Students(id),
  grade        TEXT NOT NULL,
  category     TEXT CHECK(category IN ('good','bad')) NOT NULL
);

ZScores (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  section_id   INTEGER NOT NULL REFERENCES Sections(id),
  z_score      REAL,
  p_value      REAL,
  significant  BOOLEAN,
  threshold    REAL,
  timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Step‑by‑Step Implementation

1. Install dependencies  
   ```bash
   pip install sqlalchemy alembic
   ```

2. Define ORM models in `persistence/models.py`.  
3. Configure database URL and engine in `persistence/db.py`.  
4. Create Alembic migration scripts to generate tables.  
5. Extend `GoodAndBadList` and `zscore_calculator` to call a new `persistence/service.py`:
   - Insert or update `Students`, `Sections`, `Groups`.  
   - Bulk insert `Performances` entries with category “good”/“bad”.  
   - Insert a new `ZScores` record per analysis run.  
6. Add a CLI or API endpoint to replay or query persisted data.

---

## 5. Integration Points

- After building `goodListDF` / `badListDF`, call `service.persist_performances(df, section_name, category)`.
- After computing each section’s stats and Z‑score, call `service.persist_section_stats(...)` and `service.persist_zscore(...)`.

---

## 6. Sample Usage

```python
from persistence import service

# persist students and their performance
service.persist_performances(goodListDF, section_name='COMSC101_SEC1', category='good')

# persist section summary
service.persist_section_stats('COMSC101_SEC1', mean_gpa, count)

# persist group stats
service.persist_group_stats('Fall2023_GroupA', group_mean, group_std)

# persist z-score
service.persist_zscore('COMSC101_SEC1', z_score, p_value, significant, threshold)
```

---

## 7. Next Steps

- Scaffold `persistence/` package.  
- Write unit tests for `service` functions.  
- Update documentation.  
- Run migrations and validate data flows.  

