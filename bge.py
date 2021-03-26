"""This is the Battleship Game Engine.

This module contains the components required to run a game of Battleship.

Usage:

>>> game = Game()
>>>
>>> grid = game.create_grid('John')
>>> grid.add_ship(destroyer, ('A', 1), Orientation.E)
>>> grid.add_ship(submarine, ('D', 9), Orientation.S)
>>> grid.add_ship(cruiser, ('J', 10), Orientation.W)
>>> grid.add_ship(battleship, ('I', 3), Orientation.N)
>>> grid.add_ship(carrier, ('C', 2), Orientation.E)
>>>
>>> grid = game.create_grid('Jane')
>>> grid.add_ship(destroyer, ('B', 2), Orientation.E)
>>> grid.add_ship(submarine, ('B', 6), Orientation.S)
>>> grid.add_ship(cruiser, ('F', 1), Orientation.S)
>>> grid.add_ship(battleship, ('J', 3), Orientation.E)
>>> grid.add_ship(carrier, ('G', 9), Orientation.N)
>>>
>>> game.current_player
>>> 'John'
>>> game.shoot(('A', 1))  # John is shooting at Jane
>>>
"""
from __future__ import annotations
import itertools
from enum import Enum
from typing import Optional

Coord = tuple[str, int]


class Game:
    """Maintains the state of a game of Battleship, coordinating player
    turns and shooting.

    After creating their grids, clients call shoot() in turn, based on the
    value of current_player.
    """

    def __init__(self):
        self.players: dict[str, Grid] = {}
        self.current_player: Optional[str] = None
        self._player_seq = None

    def create_grid(self, player_name: str) -> Grid:
        """Creates a grid for a player, adding that player to the game.

        Args:
            player_name: the name of the player.
        Returns:
            the player's Grid.
        """
        if len(self.players) == 2:
            raise RuntimeError('Game already has two players')

        grid = Grid()

        self.players[player_name] = grid
        self._player_seq = itertools.cycle(self.players.keys())
        self.current_player = next(self._player_seq)

        return grid

    def shoot(self, coord: Coord):
        """Make a shot on the opponent's grid.

        Args:
            coord: the grid coordinate as (row, col).
        Returns:
            a tuple containing a boolean for a hit/miss,
            a set of the remaning ships and a matrix representing
            the current state of the grid.
        """
        opponent = self.players.keys() - self.current_player

        if coord not in opponent:
            raise InvalidCoordinate(f'Invalid grid coordinate {coord}')

        hit = opponent.receive_shot(coord)
        remaining_ships = opponent.ships_afloat()

        if len(remaining_ships) > 0:
            # Switch to the other player
            self.current_player = next(self._player_seq)

        return hit, remaining_ships, opponent.as_matrix


class Grid:
    """A Grid holds the position of a player's ships and the position of
    the shots that have been received from the opponent player.

    When a Grid is first created it holds no ships and ships must be added
    via the add_ship() method.

    An opponent makes a shot on the grid by calling receive_shot() and
    passing in the coordinate of the shot.
    """
    # The number of spaces making up the width and height of the grid.
    size: int = 10

    def __init__(self):
        # The locations of the ships on the grid.
        # A ship's location is a list of grid coordinates the ship fills.
        self.ships: dict[Ship, list[Coord]] = {}

        # The shots that have been targeted at this grid to date.
        self.shots: set[Coord] = set()

    def add_ship(self, ship: Ship, start: Coord, orientation: Orientation) -> None:
        """Add a ship to the grid checking that the position is valid based on the
        grid's current state.

        Args:
            ship: the ship to position.
            start: the coordinate of the start of the ship.
            orientation: the orientation of the ship from the start coordinate.
        Raises:
            InvalidCoordinate: if the position of the ship is not fully on the
                grid, or if it intersects with an existing ship on the grid.
        """
        if orientation == Orientation.N:
            row_inc, col_inc = -1, 0
        elif orientation == Orientation.E:
            row_inc, col_inc = 0, 1
        elif orientation == Orientation.S:
            row_inc, col_inc = 1, 0
        elif orientation == Orientation.W:
            row_inc, col_inc = 0, -1
        else:
            raise RuntimeError(f'Invalid orientation: {orientation}')

        coords = []

        for i in range(ship.size):
            coord = (chr(ord(start[0]) + (i * row_inc)), start[1] + (i * col_inc))

            if coord not in self or coord in self._all_ship_coords():
                # Ship extends off the board or intersects an existing ship's position
                raise InvalidCoordinate(f'Invalid position for {ship.name}')

            coords.append(coord)

        self.ships[ship] = coords

    def receive_shot(self, coord: Coord) -> bool:
        """Receive a shot from the opponent player and return whether
        the shot hit a ship.

        Args:
            coord: The coordinate of the shot.
        Returns:
            True if the shot was a hit, False if it was a miss.
        """
        if coord in self.shots:
            raise InvalidCoordinate(f'Shot at {coord} has previously been made')

        self.shots.add(coord)

        return coord in self._all_ship_coords()

    def as_matrix(self) -> list[list[Optional[bool]]]:
        """Return a matrix of the current state of the grid.

        The value of a cell in the matrix can be one of True, False, None.
        True indicates a hit, False indicates a miss and None indicates
        that the cell has yet to be targeted.

        Returns:
            the matrix as a list of lists.
        """
        matrix = []

        for i in range(self.size):
            row = []

            for j in range(self.size):
                coord = (chr(ord('A') + i), j + 1)
                if coord in self.shots:
                    row.append(coord in self._all_ship_coords())
                else:
                    row.append(None)

            matrix.append(row)

        return matrix

    def ships_afloat(self) -> set:
        """Return the ships that have not yet been sunk, i.e. any ships
        that still have locations without shots.

        Returns:
            a set of the remaining ships afloat.
        """
        remaining_ships = set(self.ships.keys())

        for ship, location in self.ships.items():
            if self.shots.issuperset(set(location)):
                remaining_ships.remove(ship)

        return remaining_ships

    def _all_ship_coords(self) -> set:
        """Return the set of coordinates taken up by all ships."""
        return set(itertools.chain(*self.ships.values()))

    def __contains__(self, coord: Coord):
        min_row, min_col = ('A', 1)
        max_row, max_col = (chr(ord('A') + self.size - 1), self.size)

        return min_row <= coord[0] <= max_row and min_col <= coord[1] <= max_col


class Orientation(Enum):
    """Used to represent the orientation of a ship on the grid."""
    N = 1
    E = 2
    S = 3
    W = 4


class InvalidCoordinate(Exception):
    """Indicates that a coordinate is not valid on the grid."""


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
        return self.name == other.name and self.size == other.size

    def __hash__(self):
        return hash((self.name, self.size))


# The five ships permitted by the game.
carrier = Ship(name='Carrier', size=5)
battleship = Ship(name='Battleship', size=4)
cruiser = Ship(name='Cruiser', size=3)
submarine = Ship(name='Submarine', size=3)
destroyer = Ship(name='Destroyer', size=2)
