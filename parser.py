import json
import sqlite3
import glob
import os

def create_database():
    if os.path.exists('jitendex.db'):
        os.remove('jitendex.db')
    conn = sqlite3.connect('jitendex.db')
    c = conn.cursor()

    # Create tables
    c.execute('''
        CREATE TABLE terms (
            id INTEGER PRIMARY KEY,
            term TEXT,
            reading TEXT,
            popularity INTEGER,
            sequence INTEGER UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE definitions (
            id INTEGER PRIMARY KEY,
            term_id INTEGER,
            definition TEXT,
            FOREIGN KEY (term_id) REFERENCES terms(id)
        )
    ''')

    conn.commit()
    conn.close()

def parse_and_insert_data():
    conn = sqlite3.connect('jitendex.db')
    c = conn.cursor()

    for file_path in glob.glob('term_bank_*.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
            for entry in data:
                term, reading, _, _, popularity, definitions, sequence, _ = entry

                # Insert into terms table
                try:
                    c.execute("INSERT INTO terms (term, reading, popularity, sequence) VALUES (?, ?, ?, ?)",
                              (term, reading, popularity, sequence))
                    term_id = c.lastrowid

                    # Insert into definitions table
                    for definition_item in definitions:
                        if isinstance(definition_item, dict) and definition_item.get('type') == 'structured-content':
                            # This is a simplified extraction.
                            # We might need a more robust way to handle the structured content.
                            glossary_items = []
                            def extract_glossary(content):
                                if isinstance(content, list):
                                    for item in content:
                                        extract_glossary(item)
                                elif isinstance(content, dict):
                                    if content.get('tag') == 'li' and 'content' in content:
                                        if isinstance(content['content'], list):
                                            glossary_items.append(" ".join(map(str, content['content'])))
                                        elif isinstance(content['content'], dict):
                                            extract_glossary(content['content'])
                                        else:
                                            glossary_items.append(str(content['content']))
                                    if 'content' in content:
                                        extract_glossary(content['content'])

                            extract_glossary(definition_item['content'])
                            for gloss in glossary_items:
                                c.execute("INSERT INTO definitions (term_id, definition) VALUES (?, ?)",
                                          (term_id, gloss))
                except sqlite3.IntegrityError as e:
                    print(f"Error inserting entry with sequence {sequence}: {e}")


    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    # We need to download and unzip the data first
    # This script assumes the term_bank_*.json files are in the same directory
    # You can re-download and unzip the data from https://jitendex.org/pages/downloads.html
    # and place the term_bank_*.json files in the same directory as this script.
    # parse_and_insert_data()
    print("Database created successfully. To populate it, download the Jitendex data and uncomment the call to parse_and_insert_data().")
