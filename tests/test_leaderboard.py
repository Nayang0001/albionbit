import unittest

from database.database import db
from database.models import Adventure
from services.leaderboard_service import LeaderboardService

db.crear_tablas()


class LeaderboardTests(unittest.TestCase):

    def setUp(self):
        db.cursor.execute("DELETE FROM adventures")
        db.cursor.execute("DELETE FROM adventure_results")
        db.conn.commit()

    def test_ranking_aggregates_completed_adventures(self):
        aventura = Adventure(
            guild_id=1,
            leader_id=42,
            tipo="PvE",
            contenido="HCE",
            descripcion="Test",
            finalizada=True,
            loot_total=100,
            silver_total=200,
        )

        servicio = LeaderboardService()
        servicio.registrar_resultado(aventura, 100, 200)

        ranking = servicio.obtener_ranking(guild_id=1, tipo="PvE")

        self.assertEqual(len(ranking), 1)
        self.assertEqual(ranking[0]["leader_id"], 42)
        self.assertEqual(ranking[0]["aventuras"], 1)
        self.assertEqual(ranking[0]["loot_total"], 100.0)
        self.assertEqual(ranking[0]["silver_total"], 200.0)


if __name__ == "__main__":
    unittest.main()
