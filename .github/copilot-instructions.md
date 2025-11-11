# Jitendex Parser - AI Agent Instructions

## Project Overview

This is a Python-based data parser that converts Jitendex Japanese dictionary data (JSON format) into a SQLite database optimized for Flutter mobile apps. The database is pre-built and committed to the repo for direct use by Flutter developers.

## Architecture

**Two-table normalized schema:**

- `terms`: Japanese terms with readings, popularity scores, and unique sequence IDs
- `definitions`: English definitions linked via foreign key to terms (one-to-many)

**Key files:**

- `parser.py`: Main ETL script - parses `term_bank_*.json` files, handles structured-content extraction
- `verify_db.py`: Simple integrity checker - counts terms/definitions
- `jitendex.db`: Pre-built artifact (ignored in git via `.gitignore`)

## Critical Workflows

**Running the parser:**

1. Download Jitendex Yomitan data from https://jitendex.org/pages/downloads.html
2. Extract `term_bank_*.json` files to repo root
3. Uncomment `parse_and_insert_data()` call in `parser.py` main block
4. Run: `python parser.py`
5. Database is recreated from scratch (existing file deleted)

**Verifying output:**

```bash
python verify_db.py
```

## Project-Specific Patterns

**Structured content parsing:** The parser handles Yomitan's nested structured-content format (dicts with 'tag': 'li') by recursively extracting glossary items. When modifying definition extraction logic, preserve the recursive `extract_glossary()` pattern.

**Error handling:** Uses `sqlite3.IntegrityError` catch for duplicate sequence violations - prints warnings but continues processing. This is intentional for partial data recovery.

**Database initialization:** Always deletes existing DB before creation (`os.remove('jitendex.db')`). There's no migration or incremental update logic.

## Data Model Details

**Entry format (from Yomitan JSON):**

```python
[term, reading, _, _, popularity, definitions, sequence, _]
#   0       1    2  3      4           5           6      7
```

**Structured-content extraction:** Definitions can be plain strings OR complex dicts. The parser specifically looks for `{'type': 'structured-content', 'content': [...]}` and recursively finds `<li>` tags to extract individual glossary entries.

## Flutter Integration

The SQLite database is designed for read-only querying in Flutter apps via `sqflite`. Common query pattern (documented in README):

```sql
SELECT t.term, t.reading, d.definition
FROM terms t
INNER JOIN definitions d ON t.id = d.term_id
WHERE t.term = ?
```

When modifying the schema, ensure Flutter compatibility (no JSON columns or advanced SQLite features not supported by `sqflite`).

## Dependencies

- Python 3 standard library only (`json`, `sqlite3`, `glob`, `os`)
- No `requirements.txt` - deliberately kept dependency-free
- Target platform: any system with Python 3.x

## Conventions

- Database file is both an artifact AND documentation (committed to repo for user convenience)
- Parser script has safety-commented main execution - prevents accidental runs without data files
- No logging framework - uses simple `print()` statements for error reporting
- No unit tests - verification is manual via `verify_db.py`
