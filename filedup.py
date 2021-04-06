# -*- coding: utf-8 -*-
"""
Improvements and ideas TODO
1. This is written on Windows, make sure it works on osx/linux too (paths and concating files to paths)
2. How about including timestamp of when the hash was calculated in order to do a file change monitor
3. How about including file sizes so we can report on big file duplicates or order by size.
"""
import hashlib
import sqlite3
import glob
import os
import pathlib
import sys

# if Windows db is in AppData/Local
# if mac / linux put it in .filedup

home = str(pathlib.Path.home())

platform = sys.platform
if platform == 'win32':
    home_path = home + '/AppData/Local/'
else:
    home_path = home + '/.filedup/'


DATABASE_FILE = home_path + 'filedup.db'
WINDOW = 1000 # tuning for fetchmany


def get_file_hash(filename, block_size=65536):
    file_hash=hashlib.sha256()
    try:
        with open(filename, 'rb') as f:
            fb = f.read(block_size)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = f.read(block_size)
    except Exception as e:
        print("ERROR: {}".format(e))
        return None
    return file_hash.hexdigest()

class MyDB(object):

    def __init__(self):
        self._db_connection = sqlite3.connect(DATABASE_FILE)
        self._db_cur = self._db_connection.cursor()

    def query(self, query, params):
        return self._db_cur.execute(query, params)
    
    def commit(self):
        self._db_connection.commit()

    def __del__(self):
        self._db_connection.close()


def initialise_db(db):
    if len(db.query("select name from sqlite_master WHERE type='table' and name='files'", []).fetchall()) > 0:
        db.query('''drop table files''', [])
    if len(db.query("select name from sqlite_master WHERE type='table' and name='file_hashes'", []).fetchall()) > 0:
        db.query('''drop table file_hashes''', [])
    db.query('''create table file_hashes
             (id integer primary key, hash char(64))''',
             [])
    db.query('''create table files
             (id integer primary key, 
             file_path text, 
             hash_id integer,
             FOREIGN KEY (hash_id) REFERENCES file_hashes (id))''',
             [])
    
def open_db():
    return MyDB()

def query(query):
    db = open_db()
    output = db.query(query, [])
    return output.fetchall()

def insert_hash(db, hash):
    db.query('''INSERT INTO file_hashes (hash) VALUES (?)''', (hash,))

def get_hash_id(db, hash):    
    result = db.query("select id from file_hashes where hash = ?", (hash,)).fetchone()
    if result is None: return None
    if len(result) > 1: print('Found more than one hash_id for this hash {}'.format(hash))
    return result[0]

def insert_file(db, filename):
    # Is file already in DB?
    if len(db.query("select id from files where file_path = ?", (filename,)).fetchall()) > 0:
        # file already in DB
        print('File {} already in DB'.format(filename))
    else:
        hash = get_file_hash(filename)
        if not hash: return
        # Is hash already in DB?
        hash_id = get_hash_id(db, hash)
        if hash_id is None:
            # Hash not in DB
            insert_hash(db, hash)
            hash_id = get_hash_id(db, hash)
        print('filename={}, hash_id={}'.format(filename, hash_id))
        db.query('''INSERT INTO files (file_path, hash_id) VALUES (?,?)''', (filename, hash_id))

def get_file_names(pattern, recurse=False):
    output = []
    files=glob.glob(pattern)
    print('DEBUG pattern: {}'.format(pattern))
    for file in files:
        print('DEBUG file: {}'.format(file))
        if os.path.isdir(file) and recurse:
            output = output + get_file_names(file+'/*', recurse=True)
        elif os.path.isfile(file): output.append(file)
    return output

def get_file_from_id(id):
    db = open_db()
    cur = db.query("select file_path from files where id=?", (id,))
    return cur.fetchall()

def delete_file_from_db(id):
    db = open_db()
    db.query("delete from files where id in (?)", (id,))
    db.commit()
    
def populate(pattern):
    db = open_db()
    for file in get_file_names(pattern, recurse=True):
        insert_file(db, file)
        db.commit()

def get_duplicates():
    db = open_db()
    duplicates = db.query("select hash_id, count(hash_id) from files group by hash_id having count(hash_id) > 1", [])
    return duplicates.fetchall()

def delete_duplicates():
    db = open_db()
    for i in get_duplicates():
        result = db.query("select file_path, hash_id from files where hash_id = ?", (i[0],))
        files = result.fetchall()

        print('1', files[0])
        print('2', files[1])
        choice = input("1/2: ")
        if choice not in ('1','2','q'): continue
        if choice == 'q': break
        if choice == '1':
            print("deleting file {}".format(files[0][0]))
            os.remove(files[0][0])
        if choice == '2':
            print("deleting file {}".format(files[1][0]))
            os.remove(files[1][0])

def report():
    db = open_db()
    duplicates = db.query("select hash_id, count(hash_id) from files group by hash_id having count(hash_id) > 1", [])
    for hash_id in duplicates.fetchall():
        result = db.query("select file_path, hash_id from files where hash_id = ?", (hash_id[0],))
        files = result.fetchall()
        print(files)

def deleted_files():
    # check if file in db really exists
    db = open_db()
    to_delete = []
    cur = db.query("select id, file_path from files", [])
    data = cur.fetchmany(WINDOW)
    while data:
        for id, file in data:
            if not os.path.isfile(file):
                to_delete.append(id)
        data = cur.fetchmany(WINDOW)
    return to_delete

def redundant_hashes():
    # for each hash, check it has a corresponding file, if not delete it from DB
    output = []
    db = open_db()
    cur = db.query("select id from file_hashes where id not in (select hash_id from files)", [])
    data = cur.fetchall()
    for tup in data:
        for item in tup:
            output.append(item)
    return output
 
def delete_redundant_hashes():
    db = open_db()
    for hash in redundant_hashes():
        db.query("delete from file_hashes where id = ?", (hash,))
    db.commit()

# typical workflow:

# 1. delete duplicates
# >> file_dup.delete_duplicates()
# 2. clean up
# >> for i in file_dup.deleted_files(): file_dup.delete_file_from_db(i)
#
