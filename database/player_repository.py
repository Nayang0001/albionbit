from database.database_manager import db


class PlayerRepository:

    def obtener(self, discord_id):

        db.cursor.execute(

            """
            SELECT *

            FROM jugadores

            WHERE discord_id=?
            """,

            (discord_id,)

        )

        return db.cursor.fetchone()

    def crear(self, discord_id, nombre):

        db.cursor.execute(

            """

            INSERT OR IGNORE INTO jugadores(

                discord_id,

                nombre

            )

            VALUES(?,?)

            """,

            (

                discord_id,

                nombre

            )

        )

        db.conn.commit()

    def cambiar_nombre(

        self,

        discord_id,

        nombre

    ):

        db.cursor.execute(

            """

            UPDATE jugadores

            SET nombre=?

            WHERE discord_id=?

            """,

            (

                nombre,

                discord_id

            )

        )

        db.conn.commit()


player_repository = PlayerRepository()
