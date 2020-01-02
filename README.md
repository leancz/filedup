file_dup
========

Edit filedup.py and change the path of DATABASE_FILE to be where you want it.

Start Python and:

: import filedup

Initialise the database

: db = filedup.open_db()

: filedup.initialise_db(db)

: db.commit()

: del db

Scan a directory for files and record files and hashes in database

: filedup.populate('D:')

Report on duplicates

: filedup.report()


