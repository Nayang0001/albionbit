import sqlite3


class Database:

    def __init__(self):

        self.conn = sqlite3.connect(
            "albion.db"
        )

        self.cursor = self.conn.cursor()

        self.crear_tablas()

    def crear_tablas(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS aventuras(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            guild_id INTEGER,

            leader_id INTEGER,

            tipo TEXT,

            contenido TEXT,

            descripcion TEXT,

            canal_id INTEGER,

            mensaje_id INTEGER

        )

        """)

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS jugadores(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            discord_id INTEGER UNIQUE,

            nombre TEXT

        )

        """)

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS roles(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            aventura_id INTEGER,

            nombre TEXT,

            jugador_id INTEGER

        )

        """)

        self.conn.commit()


db = Database()
