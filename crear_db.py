# crea_db.py
import sqlite3

conn = sqlite3.connect('baterias.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS coches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bastidor TEXT NOT NULL,
    plaza TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS revisiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coche_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    foto TEXT,
    FOREIGN KEY (coche_id) REFERENCES coches (id)
)
''')

conn.commit()
conn.close()
print("Base de datos creada.")
