import unittest

from src.extract_locations import extract_locations


class ExtractLocationsTest(unittest.TestCase):
    def test_extracts_city_state_pattern(self):
        locations = extract_locations("Reuniao institucional em Manaus/AM.")

        self.assertEqual(
            locations[0],
            {
                "local_texto": "Manaus/AM",
                "cidade": "Manaus",
                "estado": "AM",
                "pais": "Brasil",
            },
        )

    def test_extracts_known_international_location(self):
        locations = extract_locations("Missao oficial em Lisboa para agenda bilateral.")

        self.assertIn(
            {
                "local_texto": "Lisboa",
                "cidade": "Lisboa",
                "estado": None,
                "pais": "Portugal",
            },
            locations,
        )


if __name__ == "__main__":
    unittest.main()
