"""Find an exact shortest round trip through up to ten cities."""

import argparse
import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path


MAX_CITIES = 10


@dataclass(frozen=True)
class City:
    name: str
    x: float
    y: float


def validate_cities(cities: list[City]) -> None:
    if not 1 <= len(cities) <= MAX_CITIES:
        raise ValueError(f"Provide between 1 and {MAX_CITIES} cities.")
    for city in cities:
        if not isinstance(city.name, str) or not city.name.strip():
            raise ValueError("Every city must have a non-empty name.")
        for coordinate in (city.x, city.y):
            if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                raise ValueError("Coordinates must be numbers.")
            try:
                finite = math.isfinite(coordinate)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("Coordinates must be finite numbers.")
    if len({city.name for city in cities}) != len(cities):
        raise ValueError("City names must be unique.")


def solve_tsp(cities: list[City]) -> tuple[list[int], float]:
    """Return a closed route of city indices and its Euclidean length.

    Fix city 0 as the start and examine all permutations of the others.
    This covers every possible cycle and therefore finds a global optimum
    under floating-point arithmetic. Ties keep the first examined route.
    """
    validate_cities(cities)
    distances = [
        [math.hypot(a.x - b.x, a.y - b.y) for b in cities]
        for a in cities
    ]
    if any(not math.isfinite(distance) for row in distances for distance in row):
        raise ValueError("Coordinates are too large to calculate distances.")

    best_route = []
    best_length = math.inf
    for permutation in itertools.permutations(range(1, len(cities))):
        route = [0, *permutation, 0]
        try:
            length = math.fsum(distances[a][b] for a, b in zip(route, route[1:]))
        except OverflowError as error:
            raise ValueError("Route length is too large to calculate.") from error
        if length < best_length:
            best_route, best_length = route, length
    return best_route, best_length


def load_cities(path: Path) -> list[City]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("The JSON file must contain a list of cities.")
    cities = []
    for item in data:
        if not isinstance(item, dict) or set(item) != {"name", "x", "y"}:
            raise ValueError("Each city must contain exactly these fields: name, x, y.")
        cities.append(City(**item))
    validate_cities(cities)
    return cities


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, nargs="?",
        default=Path(__file__).parent / "examples" / "cities.json",
        help="JSON file with city names and Cartesian coordinates",
    )
    args = parser.parse_args()
    try:
        cities = load_cities(args.input)
        route, length = solve_tsp(cities)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Route: " + " -> ".join(cities[index].name for index in route))
    print(f"Distance: {length:.6f}")


if __name__ == "__main__":
    main()
