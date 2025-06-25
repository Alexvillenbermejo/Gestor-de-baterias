import sqlite3

conn = sqlite3.connect('baterias.db')
c = conn.cursor()
c.execute('SELECT coche_id, fecha FROM revisiones ORDER BY fecha DESC LIMIT 5')
print(c.fetchall())
conn.close()
