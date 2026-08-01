from database.database import db


class LeaderboardService:

    def registrar_resultado(self, aventura, loot_total=None, silver_total=None):
        adventure_id = str(getattr(aventura, "id", "") or "")
        if not adventure_id:
            return None

        if loot_total is None:
            loot_total = getattr(aventura, "loot_total", 0.0) or 0.0
        if silver_total is None:
            silver_total = getattr(aventura, "silver_total", 0.0) or 0.0

        tipo_valor = (getattr(aventura, "tipo", "") or "").strip().upper()
        if tipo_valor not in {"PVE", "PVP"}:
            tipo_valor = "PVE" if "PVE" in tipo_valor else "PVP" if "PVP" in tipo_valor else tipo_valor

        db.cursor.execute(
            "SELECT id FROM adventure_results WHERE adventure_id = ?",
            (adventure_id,)
        )
        fila = db.cursor.fetchone()

        if fila is None:
            db.cursor.execute(
                """
                INSERT INTO adventure_results (
                    guild_id,
                    leader_id,
                    tipo,
                    adventure_id,
                    loot_total,
                    silver_total
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    getattr(aventura, "guild_id", 0),
                    getattr(aventura, "leader_id", 0),
                    tipo_valor,
                    adventure_id,
                    float(loot_total or 0),
                    float(silver_total or 0),
                ),
            )
        else:
            db.cursor.execute(
                """
                UPDATE adventure_results
                SET guild_id = ?,
                    leader_id = ?,
                    tipo = ?,
                    loot_total = ?,
                    silver_total = ?
                WHERE adventure_id = ?
                """,
                (
                    getattr(aventura, "guild_id", 0),
                    getattr(aventura, "leader_id", 0),
                    tipo_valor,
                    float(loot_total or 0),
                    float(silver_total or 0),
                    adventure_id,
                ),
            )

        db.conn.commit()
        return True

    def actualizar_totales(self, adventure_id, loot_total, silver_total):
        if not adventure_id:
            return False

        db.cursor.execute(
            """
            UPDATE adventure_results
            SET loot_total = ?, silver_total = ?
            WHERE adventure_id = ?
            """,
            (float(loot_total or 0), float(silver_total or 0), str(adventure_id)),
        )
        db.conn.commit()
        return db.cursor.rowcount > 0

    def obtener_ranking(self, guild_id, tipo=None, limit=10):
        query = """
            SELECT leader_id, COUNT(*) AS aventuras, SUM(loot_total) AS loot_total, SUM(silver_total) AS silver_total
            FROM adventure_results
            WHERE guild_id = ?
        """
        params = [guild_id]

        if tipo is not None and str(tipo).strip():
            tipo_valor = str(tipo).strip().upper()
            if tipo_valor in {"PVP", "PVE"}:
                query += " AND tipo = ?"
                params.append(tipo_valor)

        query += " GROUP BY leader_id ORDER BY aventuras DESC, loot_total DESC, silver_total DESC LIMIT ?"
        params.append(limit)

        db.cursor.execute(query, params)
        filas = db.cursor.fetchall()

        return [
            {
                "leader_id": fila[0],
                "aventuras": fila[1],
                "loot_total": float(fila[2] or 0),
                "silver_total": float(fila[3] or 0),
            }
            for fila in filas
        ]
