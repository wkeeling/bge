"""This is the Battleship Game Engine.

This module contains the components required to run a game of Battleship.
Clients should call start_game() to begin a new game.
"""
from __future__ import annotations
from enum import Enum

Coord = tuple[str, int]


def start_game() -> Game:
    """Start a new game of Battleship."""
    return Game()


class Game:
    """Maintains state for a two player game of Battleship."""

    def __init__(self):
        self.player1: Grid = Grid()
        self.player2: Grid = Grid()


class Grid:
    """A Grid holds a player's ships and the shots that have been received
    from the opponent player via them invoking the shoot() method.
    """
    # The number of spaces making up the width and height of the grid.
    size: int = 10

    def __init__(self):
        # The locations of the ships on the grid.
        # A ship's location is a list of grid coordinates the ship fills.
        self.ships: dict[Ship, list[Coord]] = {}

        # The shots that have been targeted at this grid to date.
        self.shots: list[Coord] = []

        # The coordinates representing the top left and bottom right spaces
        # on the grid based on the grid's size.
        self._top_left = ('A', 1)
        self._bottom_right = (chr(ord('A') + self.size - 1), self.size)

    def position(self, ship: Ship, start: Coord, orientation: Orientation):
        """Position a ship on the grid checking that the position is
        valid based on the grid's current state.

        Where a position is not valid, InvalidPosition will be raised.

        Args:
            ship: the ship to position.
            start: the coordinate of the start of the ship.
            orientation: the orientation of the ship from the start coordinate.
        Raises:
            InvalidPosition: if the position of the ship is not fully on the
                grid, or if it intersects with an existing ship on the grid.
        """
        # if orientation == Orientation.N:


    def shoot(self, coord: Coord):
        """Make a shot on the grid.

        Args:
            coord: the targeted grid coordinate as (row, col).
        """


class Orientation(Enum):
    """Used to represent the orientation of a ship on the grid."""
    N = 1
    E = 2
    S = 3
    W = 4


class InvalidPosition(Exception):
    """Indicates that a ship has been placed in an invalid position
    on the grid.
    """


class Ship:
    """Represents a battleship.

    Battleships have a name and a size which determines how many grid
    spaces they take up.
    """

    def __init__(self, name: str, size: int):
        self.name = name
        # The number of grid spaces this ship uses
        self.size = size

    def __eq__(self, other: Ship) -> bool:
        if not isinstance(other, Ship):
            return False
        if other == self:
            return True
        return self.name == other.name and self.size == other.size

    def __hash__(self):
        return hash((self.name, self.size))


# The five ships permitted by the game.
carrier = Ship(name='Carrier', size=5)
battleship = Ship(name='Battleship', size=4)
cruiser = Ship(name='Cruiser', size=3)
submarine = Ship(name='Submarine', size=3)
destroyer = Ship(name='Destroyer', size=2)
