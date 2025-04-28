import sqlite3

# Conectarse a (o crear) la base de datos
conn = sqlite3.connect('liga_mtg.db')
cursor = conn.cursor()

# Crear tabla de Mazos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mazos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Open_id TEXT NOT NULL,
        jugador TEXT NOT NULL,
        nombre_mazo TEXT NOT NULL,
        cartas_lista TEXT DEFAULT NULL,
        elo REAL DEFAULT 1200,
        imagen_url TEXT
    )
''')

# Crear tabla de Partidas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS partidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mazo_1_id INTEGER NOT NULL,
        mazo_2_id INTEGER NOT NULL,
        resultado_mazo_1 INTEGER NOT NULL,
        fecha TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (mazo_1_id) REFERENCES mazos(id),
        FOREIGN KEY (mazo_2_id) REFERENCES mazos(id)
    )
''')

# Guardar cambios y cerrar
conn.commit()
conn.close()

print("Base de datos creada correctamente.")
