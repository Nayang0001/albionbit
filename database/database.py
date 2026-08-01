import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "albion.db"

SCHEMA = BASE_DIR / "schema.sql"


class Database:

    def __init__(self):

        self.conn = sqlite3.connect(DATABASE)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    def crear_tablas(self):

        with open(SCHEMA, "r", encoding="utf8") as archivo:

            self.conn.executescript(

                archivo.read()

            )

            self.conn.execute("""

            CREATE TABLE IF NOT EXISTS adventure_results (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id INTEGER,

                leader_id INTEGER,

                tipo TEXT,

                adventure_id TEXT UNIQUE,

                loot_total REAL DEFAULT 0,

                silver_total REAL DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )

            """)

            self.conn.commit()


db = Database()
