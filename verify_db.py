
import sqlite3

conn = sqlite3.connect('jitendex.db')
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM terms')
term_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM definitions')
definition_count = c.fetchone()[0]

conn.close()

print(f"Number of terms: {term_count}")
print(f"Number of definitions: {definition_count}")
