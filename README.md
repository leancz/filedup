# file_dup

A set of functions for identifying duplicate files. I had a load of photos from various devices and always forgot to clean-up the device after downloading and had many duplicates in various directories. This helps me manage that.

## Installation
I assume you have Python, sqlite3 and sqlite3 for python installed. Copy the file filedup.py to a place in your Python path. Edit filedup.py and change the path of DATABASE_FILE to be where you want the database file to be located.

Initialise the database.
```python
import filedup
db = filedup.open_db()
filedup.initialise_db(db)
db.commit()
del db
```

## Usage
Scan a directory for files and record files and hashes in database

```python
filedup.populate('D:')
```

Report on duplicates

```python
filedup.report()
```


