from database.database_manager import db


class AdventureRepository:

    def guardar(self, aventura):

        db.cursor.execute(

            """

            INSERT INTO aventuras(

                guild_id,

                leader_id,

                tipo,

                contenido,

                descripcion,

                canal_id,

                mensaje_id

            )

            VALUES(?,?,?,?,?,?,?)

            """,

            (

                aventura.guild_id,

                aventura.leader_id,

                aventura.tipo,

                aventura.contenido,

                aventura.descripcion,

                aventura.canal_id,

                aventura.mensaje_id

            )

        )

        db.conn.commit()

        aventura.id = db.cursor.lastrowid

        return aventura


repository = AdventureRepository()
