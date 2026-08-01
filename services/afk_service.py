"""Persistencia del registro AFK del servidor."""

from database.database import db


class AfkService:
    def establecer_afk(
        self,
        guild_id: int,
        user_id: int,
        user_name: str,
        reason: str,
        updated_by: int,
    ) -> None:
        db.conn.execute(
            """
            INSERT INTO afk_records (guild_id, user_id, user_name, reason, is_afk, updated_by, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                user_name = excluded.user_name,
                reason = excluded.reason,
                is_afk = 1,
                updated_by = excluded.updated_by,
                updated_at = CURRENT_TIMESTAMP
            """,
            (guild_id, user_id, user_name, reason, updated_by),
        )
        db.conn.commit()

    def editar_estado(
        self,
        guild_id: int,
        user_id: int,
        user_name: str,
        is_afk: bool,
        updated_by: int,
        reason: str | None = None,
    ) -> bool:
        current = db.conn.execute(
            "SELECT reason FROM afk_records WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        ).fetchone()
        if current is None:
            return False

        db.conn.execute(
            """
            UPDATE afk_records
            SET user_name = ?, reason = ?, is_afk = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
            WHERE guild_id = ? AND user_id = ?
            """,
            (user_name, reason.strip() if reason else current["reason"], int(is_afk), updated_by, guild_id, user_id),
        )
        db.conn.commit()
        return True

    def obtener_afk_activos(self, guild_id: int):
        return db.conn.execute(
            """
            SELECT user_id, user_name, reason, updated_by, updated_at
            FROM afk_records
            WHERE guild_id = ? AND is_afk = 1
            ORDER BY updated_at DESC, user_name COLLATE NOCASE
            """,
            (guild_id,),
        ).fetchall()
