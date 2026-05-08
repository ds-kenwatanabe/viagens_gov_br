import unittest
from decimal import Decimal

from src.geocode import _geocode_location


class GeocodeAliasTest(unittest.TestCase):
    def test_uses_local_coordinate_alias_before_nominatim(self):
        cache = {}
        location = {
            "local_texto": "Washington",
            "cidade": "Washington",
            "estado": "DC",
            "pais": "Estados Unidos",
        }

        latitude, longitude, confidence, source = _geocode_location(
            location,
            user_agent=None,
            cache=cache,
            delay_seconds=0,
        )

        self.assertEqual(latitude, Decimal("38.907192"))
        self.assertEqual(longitude, Decimal("-77.036871"))
        self.assertEqual(confidence, Decimal("1"))
        self.assertEqual(source, "local")
        self.assertEqual(cache["Washington, DC, Estados Unidos"][3], "local")

    def test_unknown_location_without_user_agent_is_cached_as_local_miss(self):
        cache = {}
        location = {
            "local_texto": "Cidade Teste",
            "cidade": "Cidade Teste",
            "estado": None,
            "pais": "Pais Teste",
        }

        latitude, longitude, confidence, source = _geocode_location(
            location,
            user_agent=None,
            cache=cache,
            delay_seconds=0,
        )

        self.assertIsNone(latitude)
        self.assertIsNone(longitude)
        self.assertEqual(confidence, Decimal("0"))
        self.assertEqual(source, "local")
        self.assertEqual(cache["Cidade Teste, Pais Teste"][3], "local")


if __name__ == "__main__":
    unittest.main()
