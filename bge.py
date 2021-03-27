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
'John'
>>> hit, *_ = game.shoot(('A', 1))  # John is shooting at Jane
>>> hit
False
>>> game.current_player
'Jane'
>>> hit, *_ = game.shoot(('E', 9))  # Jane is shooting at John
>>> hit
True
"""
from __future__ import annotations
import itertools
import random
from typing import Optional

Coord = tuple[str, int]

# When only one human player, the computer uses this name
# for player 2.
PLAYER2_NAME = 'Computer'


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

        A maximum of two grids can be created, one for each player.
        Where a single grid is created, the computer assumes the role
        of the other player.

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

    def shoot(self, coord: Coord) -> tuple[bool, set[Ship], list[list[Optional[bool]]]]:
        """Make a shot on the opponent's grid.

        Args:
            coord: the grid coordinate being targeted.
        Returns:
            a 3-tuple containing:
                a boolean for a hit/miss
                a set containing the remaning ships afloat
                a matrix representing the current state of the grid. Each cell in the
                matrix has a value of True|False|None where True means hit, False
                means miss and None means yet to be targeted.
        """
        if not self.players:
            raise RuntimeError('Need to create at least one grid')

        if len(self.players) == 1:
            self._create_player2()

        if not all(len(g.ships) == len(all_ships) for g in self.players.values()):
            raise RuntimeError('Not all ships have been positioned')

        players = list(self.players)
        players.remove(self.current_player)
        opponent_grid = self.players[players[0]]

        if coord not in opponent_grid:
            raise InvalidCoordinate(f'Invalid grid coordinate {coord}')

        hit = opponent_grid.receive_shot(coord)
        remaining_ships = opponent_grid.ships_afloat()

        if len(remaining_ships) > 0:
            # Switch to the other player
            self.current_player = next(self._player_seq)

        return hit, remaining_ships, opponent_grid.as_matrix()

    def _create_player2(self):
        """Create player 2 when only one human player."""
        grid = self.create_grid(PLAYER2_NAME)

        ships = set(all_ships)

        while ships:
            ship = ships.pop()

            # Randomly position each ship on the grid
            while True:
                # Create a random start coordinate
                row = random.choice([chr(c) for c in range(ord('A'), ord('A') + grid.size)])
                col = random.choice(range(1, 11))
                # Randomly select the direction to generate the coordinates in
                row_inc, col_inc = random.choice(((0, 1), (1, 0)))
                coords = []

                for i in range(ship.size):
                    # Generate the ship coordinates
                    coords.append((chr(ord(row) + (i * row_inc)), col + (i * col_inc)))

                try:
                    grid.add_ship(ship, *coords)
                    break
                except InvalidCoordinate:
                    continue


class Grid:
    """A Grid holds the position of a player's ships and the position of
    the shots that have been received from the opponent player.

    When a Grid is first created it holds no ships and ships must be added
    via the add_ship() method.

    An opponent makes a shot on the grid by calling it's receive_shot()
    method and passing in the shot coordinates.
    """
    # The number of spaces making up the width and height of the grid.
    size: int = 10

    def __init__(self):
        # The locations of the ships on the grid.
        # A ship's location consists of the grid coordinates the ship fills.
        self.ships: dict[Ship, tuple[Coord]] = {}

        # The shots that have been targeted at this grid to date.
        self.shots: set[Coord] = set()

    def add_ship(self, ship: Ship, *coords: Coord) -> None:
        """Add a ship to the grid checking that the position is valid based on the
        grid's current state.

        Args:
            ship: the ship to position.
            coords: the coordinates of the ship.
        Raises:
            InvalidCoordinate: if the supplied coordinates do not correspond to the
                size of the ship, or are not consecutive within a row or column,
                or are off the grid, or are the same as a coordinate used by an
                already positioned ship.
        """
        if len(coords) != ship.size:
            raise InvalidCoordinate('The number of coordinates do not correspond to '
                                    f'the size of the ship {ship}')

        rows, cols = list(zip(*coords))

        if rows.count(rows[0]) == len(rows):
            # Row is the same, so check cols are consecutive
            if sorted(cols) != list(range(min(cols), max(cols) + 1)):
                raise InvalidCoordinate(f'Coordinate columns are not consecutive for {ship}')
        elif cols.count(cols[0]) == len(cols):
            # Col is the same, so check rows are consecutive
            rows = [ord(r) for r in rows]
            if sorted(rows) != list(range(min(rows), max(rows) + 1)):
                raise InvalidCoordinate(f'Coordinate rows are not consecutive for {ship}')

        for coord in coords:
            if coord not in self or coord in self._all_ship_coords():
                # Ship extends off the grid or uses the same coordinate as
                # an already positioned ship.
                raise InvalidCoordinate(f'Invalid position for {ship}')

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
        """Return the ships that have not yet been sunk, i.e. the ships
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Ship(name='{self.name}', size={self.size})"


# The five ships permitted by the game.
carrier = Ship(name='Carrier', size=5)
battleship = Ship(name='Battleship', size=4)
cruiser = Ship(name='Cruiser', size=3)
submarine = Ship(name='Submarine', size=3)
destroyer = Ship(name='Destroyer', size=2)

all_ships = {
    destroyer,
    submarine,
    cruiser,
    battleship,
    carrier
}
