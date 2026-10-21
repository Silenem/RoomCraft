import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tsp import City, load_cities, solve_tsp


class SolverTests(unittest.TestCase):
    def assert_closed_tour(self, route, count):
        self.assertEqual(route[0], 0)
        self.assertEqual(route[-1], 0)
        self.assertEqual(sorted(route[:-1]), list(range(count)))

    def test_square_has_perimeter_four(self):
        # Input order crosses the square, so it is not already optimal.
        cities = [City("A", 0, 0), City("C", 1, 1), City("B", 1, 0), City("D", 0, 1)]
        route, length = solve_tsp(cities)
        self.assert_closed_tour(route, 4)
        self.assertAlmostEqual(length, 4.0)

    def test_right_triangle(self):
        route, length = solve_tsp([City("A", 0, 0), City("B", 3, 0), City("C", 0, 4)])
        self.assert_closed_tour(route, 3)
        self.assertAlmostEqual(length, 12.0)

    def test_one_city(self):
        self.assertEqual(solve_tsp([City("A", 8, -3)]), ([0, 0], 0.0))

    def test_two_cities_include_return_trip(self):
        self.assertEqual(solve_tsp([City("A", 0, 0), City("B", 3, 4)]), ([0, 1, 0], 10.0))

    def test_coincident_cities(self):
        route, length = solve_tsp([City("A", 2, 2), City("B", 2, 2), City("C", 2, 2)])
        self.assert_closed_tour(route, 3)
        self.assertEqual(length, 0.0)

    def test_invalid_inputs(self):
        cases = [
            [],
            [City(str(i), i, 0) for i in range(11)],
            [City("A", 0, 0), City("A", 1, 1)],
            [City(" ", 0, 0)],
            [City("A", math.inf, 0)],
            [City("A", math.nan, 0)],
            [City("A", True, 0)],
            [City("A", "1", 0)],
            [City("A", 1e308, 0), City("B", -1e308, 0)],
        ]
        for cities in cases:
            with self.subTest(cities=cities), self.assertRaises(ValueError):
                solve_tsp(cities)

    def test_load_rejects_invalid_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for data in ({"name": "A"}, [{"name": "A", "x": 0}], [123]):
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.subTest(data=data), self.assertRaises(ValueError):
                    load_cities(path)

    def test_command_line_example(self):
        script = Path(__file__).resolve().parents[1] / "tsp.py"
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Route: A -> B -> C -> D -> A", result.stdout)
        self.assertIn("Distance: 4.000000", result.stdout)


if __name__ == "__main__":
    unittest.main()
