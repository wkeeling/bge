"""This is the Battleship Game Engine.

This module contains the components required to run a game of Battleship.

2-player usage:

>>> game = Game()
>>>
>>> grid = game.create_grid('John')
>>> grid.add_ship(destroyer, ('A', 1), ('A', 2))
>>> grid.add_ship(submarine, ('D', 9), ('E', 9), ('F', 9))
>>> grid.add_ship(cruiser, ('J', 8), ('J', 9), ('J', 10))
>>> grid.add_ship(battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
>>> grid.add_ship(carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
>>>
>>> grid = game.create_grid('Jane')
>>> grid.add_ship(destroyer, ('B', 2), ('B', 3))
>>> grid.add_ship(submarine, ('B', 6), ('C', 6), ('D', 6))
>>> grid.add_ship(cruiser, ('F', 1), ('G', 1), ('H', 1))
>>> grid.add_ship(battleship, ('J', 3), ('J', 4), ('J', 5), ('J', 6))
>>> grid.add_ship(carrier, ('C', 9), ('D', 9), ('E', 9), ('F', 9), ('G', 9))
>>>
>>> hit, *_ = game.shoot('Jane', ('A', 1))  # John is shooting at Jane
>>> hit
False
>>> hit, *_ = game.shoot('John', ('E', 9))  # Jane is shooting at John
>>> hit
True

Single player usage:

>>> game = Game()
>>>
>>> grid = game.create_grid('John')
>>> grid.add_ship(destroyer, ('A', 1), ('A', 2))
>>> grid.add_ship(submarine, ('D', 9), ('E', 9), ('F', 9))
>>> grid.add_ship(cruiser, ('J', 8), ('J', 9), ('J', 10))
>>> grid.add_ship(battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
>>> grid.add_ship(carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
>>>
>>> hit, *_ = game.shoot(COMPUTER, ('A', 1))  # John is shooting at the computer
>>> hit
False
>>> hit, *_ = game.shoot('John')  # The computer is shooting at John, target coord is computed
>>> hit
False
"""
from __future__ import annotations
import itertools
import random
from typing import Optional, Union

Coord = tuple[str, int]

# When only one human player, the computer uses this name
# for player 2.
COMPUTER = 'Computer'

# Pass this as the target_coord argument to shoot() when the
# target is to be automatically computed.
AUTO = object()


class Game:
    """Maintains the state of a game of Battleship, coordinating player
    turns and shooting.

    After creating their grids, clients call shoot() in turn.
    """

    def __init__(self):
        self.players: dict[str, Grid] = {}

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

        return grid

    def shoot(self,
              target_player: str,
              target_coord: Union[Coord, AUTO] = AUTO) -> tuple[bool, set[Ship], Grid]:
        """Make a shot on the specified player's grid.

        The value of the target coordinate should be specified as a tuple
        containing the row and column. Alternatively, if the constant AUTO
        is supplied (the default), the coordinate will be computed based on
        the current state of the target grid.

        Args:
            target_player: the name of the player being targeted.
            target_coord: the grid coordinate being targeted or the value of
                the constant AUTO for automatic computation of the coordinate.
        Returns:
            a 3-tuple containing:
                a boolean for a hit/miss
                a set containing the remaning ships afloat
                the target player's Grid instance
        """
        if not self.players:
            raise RuntimeError('Need to create at least one grid')

        if len(self.players) == 1:
            self._create_player2()

        if not all(len(g.ships) == len(all_ships) for g in self.players.values()):
            raise RuntimeError('Not all ships have been positioned')

        try:
            target_grid = self.players[target_player]
        except KeyError:
            raise KeyError(
                f"No such player '{target_player}' - valid players are {list(self.players.keys())}")

        if target_coord not in target_grid:
            raise InvalidCoordinate(f'Invalid grid coordinate {target_coord}')

        hit = target_grid.receive_shot(target_coord)
        remaining_ships = target_grid.ships_afloat()

        return hit, remaining_ships, target_grid

    def _create_player2(self):
        """Create player 2 when only one human player."""
        grid = self.create_grid(COMPUTER)

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
                                    f"the size of the ship '{ship}'")

        rows, cols = list(zip(*coords))

        if rows.count(rows[0]) == len(rows):
            # Row is the same, so check cols are consecutive
            if sorted(cols) != list(range(min(cols), max(cols) + 1)):
                raise InvalidCoordinate(f"Coordinate columns are not consecutive for '{ship}'")
        elif cols.count(cols[0]) == len(cols):
            # Col is the same, so check rows are consecutive
            rows = [ord(r) for r in rows]
            if sorted(rows) != list(range(min(rows), max(rows) + 1)):
                raise InvalidCoordinate(f"Coordinate rows are not consecutive for '{ship}'")

        for coord in coords:
            if coord not in self or coord in self._all_ship_coords():
                # Ship extends off the grid or uses the same coordinate as
                # an already positioned ship.
                raise InvalidCoordinate(f"Invalid position for '{ship}'")

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

    def ships_sunk(self) -> set:
        """Return the ships that have been sunk.

        Returns:
            a set of the ships that have been sunk.
        """
        return set(self.ships.keys()) - self.ships_afloat()

    def _all_ship_coords(self) -> set:
        """Return the union of coordinates taken up by all ships."""
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
destroyer = Ship(name='Destroyer', size=2)
submarine = Ship(name='Submarine', size=3)
cruiser = Ship(name='Cruiser', size=3)
battleship = Ship(name='Battleship', size=4)
carrier = Ship(name='Carrier', size=5)

all_ships = {
    destroyer,
    submarine,
    cruiser,
    battleship,
    carrier
}
