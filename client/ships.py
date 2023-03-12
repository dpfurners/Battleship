from typing import Literal


class Ship:
    def __init__(self, amount: int, name: str, coords: tuple[int, int],
                 direction: Literal["horizontal", "vertical"] = "horizontal"):
        self.hits: int = 0
        self.name: str = name
        self.amount: int = amount
        self.coords: tuple[int, int] = coords
        self.direction: Literal["horizontal", "vertical"] = direction
        self.ship_parts: list[tuple[int, int]] = [(0, 0)]

    @classmethod
    def new_ship(cls, pos):
        return cls(0, "Default", pos, "horizontal")

    def __repr__(self):
        return f"<Ship {self.name} {self.coords} {self.direction} {self.ship_parts}>"


class Cruiser(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new_ship(cls, coords: tuple[int, int], direction: Literal["horizontal", "vertical"] = "vertical"):
        shp = cls(2, "Cruiser", coords, direction)
        shp.ship_parts = \
            [
                coords,
                (coords[0], coords[1] + 1)
            ] if direction == "horizontal" else \
                [
                    coords,
                    (coords[0] + 1, coords[1])
                ]
        return shp


class Frigate(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new_ship(cls,  coords: tuple[int, int], direction: Literal["horizontal", "vertical"] = "vertical"):
        shp = cls(3, "Frigate", coords, direction)
        shp.ship_parts = \
            [
                coords,
                (coords[0], coords[1] + 1),
                (coords[0], coords[1] + 2)
            ] if direction == "horizontal" else \
                [
                    coords,
                    (coords[0] + 1, coords[1]),
                    (coords[0] + 2, coords[1])
                ]
        return shp


class AircraftCarrier(Ship):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def new_ship(cls,  coords: tuple[int, int], direction: Literal["horizontal", "vertical"] = "vertical"):
        shp = cls(5, "AircraftCarrier", coords, direction)
        shp.ship_parts = \
            [
                coords,
                (coords[0], coords[1] + 1),
                (coords[0] + 1, coords[1] + 1),
                (coords[0] + 1, coords[1] + 2),
                (coords[0] + 1, coords[1] + 3)
            ] if direction == "horizontal" else \
                [
                    coords,
                    (coords[0] + 1, coords[1]),
                    (coords[0] + 1, coords[1] - 1),
                    (coords[0] + 2, coords[1] - 1),
                    (coords[0] + 3, coords[1] - 1)
                ]
        return shp