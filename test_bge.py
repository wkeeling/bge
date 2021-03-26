import pytest

import bge


class TestGame:

    def test_create_grid_one_player(self):
        game = bge.Game()

        game.create_grid('John')

        assert len(game.players) == 1
        assert game.current_player == 'John'

    def test_create_grid_two_players(self):
        game = bge.Game()

        game.create_grid('John')
        game.create_grid('Jane')

        assert len(game.players) == 2
        assert game.current_player == 'John'

    def test_raise_exception_missing_ships(self):
        pytest.fail('Implement')

    def test_shoot_hit(self):
        game = bge.Game()
        grid = game.create_grid('John')
        grid.add_ship(bge.destroyer, ('A', 1), bge.Orientation.E)
        grid.add_ship(bge.submarine, ('D', 9), bge.Orientation.S)
        grid.add_ship(bge.cruiser, ('J', 10), bge.Orientation.W)
        grid.add_ship(bge.battleship, ('I', 3), bge.Orientation.N)
        grid.add_ship(bge.carrier, ('C', 2), bge.Orientation.E)
        grid = game.create_grid('Jane')
        grid.add_ship(bge.destroyer, ('B', 2), bge.Orientation.E)
        grid.add_ship(bge.submarine, ('B', 6), bge.Orientation.S)
        grid.add_ship(bge.cruiser, ('F', 1), bge.Orientation.S)
        grid.add_ship(bge.battleship, ('J', 3), bge.Orientation.E)
        grid.add_ship(bge.carrier, ('G', 9), bge.Orientation.N)

        # John shoots at Jane
        hit, num_ships, matrix = game.shoot(('A', 1))

        assert not hit


class TestGrid:

    def test_add_ship(self):
        grid = bge.Grid()

        grid.add_ship(bge.battleship, ('A', 1), bge.Orientation.E)

        assert len(grid.ships) == 1
        assert grid.ships[bge.battleship] == [
            ('A', 1),
            ('A', 2),
            ('A', 3),
            ('A', 4),
        ]

    def test_add_ship_off_grid(self):
        grid = bge.Grid()

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('A', 5), bge.Orientation.N)

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('E', 10), bge.Orientation.E)

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('J', 5), bge.Orientation.S)

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('E', 1), bge.Orientation.W)

    def test_add_ship_intersect_existing_ship(self):
        grid = bge.Grid()

        grid.add_ship(bge.battleship, ('E', 3), bge.Orientation.E)

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.cruiser, ('C', 6), bge.Orientation.S)

    def test_add_ship_invalid_orientation(self):
        grid = bge.Grid()

        with pytest.raises(RuntimeError):
            grid.add_ship(bge.cruiser, ('C', 6), 'NW')

    def test_receive_shot_hit(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), bge.Orientation.E)

        hit = grid.receive_shot(('A', 2))

        assert hit

    def test_receive_shot_miss(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 2), bge.Orientation.E)

        hit = grid.receive_shot(('A', 4))

        assert not hit

    def test_receive_shot_duplicate(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 2), bge.Orientation.E)
        grid.receive_shot(('A', 2))

        with pytest.raises(bge.InvalidCoordinate):
            grid.receive_shot(('A', 2))

    def test_as_matrix(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), bge.Orientation.E)
        grid.add_ship(bge.submarine, ('D', 9), bge.Orientation.S)
        grid.add_ship(bge.cruiser, ('J', 10), bge.Orientation.W)
        grid.add_ship(bge.battleship, ('I', 3), bge.Orientation.N)
        grid.add_ship(bge.carrier, ('C', 2), bge.Orientation.E)
        grid.receive_shot(('A', 1))
        grid.receive_shot(('B', 3))
        grid.receive_shot(('C', 2))
        grid.receive_shot(('C', 5))
        grid.receive_shot(('C', 6))
        grid.receive_shot(('E', 1))
        grid.receive_shot(('H', 2))
        grid.receive_shot(('H', 6))
        grid.receive_shot(('I', 3))
        grid.receive_shot(('J', 5))
        grid.receive_shot(('J', 10))

        matrix = grid.as_matrix()

        assert matrix == [
            #  1     2     3     4     5     6     7     8     9    10
            [True, None, None, None, None, None, None, None, None, None],    # A
            [None, None, False, None, None, None, None, None, None, None],   # B
            [None, True, None, None, True, True, None, None, None, None],    # C
            [None, None, None, None, None, None, None, None, None, None],    # D
            [False, None, None, None, None, None, None, None, None, None],   # E
            [None, None, None, None, None, None, None, None, None, None],    # F
            [None, None, None, None, None, None, None, None, None, None],    # G
            [None, False, None, None, None, False, None, None, None, None],  # H
            [None, None, True, None, None, None, None, None, None, None],    # I
            [None, None, None, None, False, None, None, None, None, True],   # J
        ]

    def test_ships_afloat(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), bge.Orientation.E)
        grid.add_ship(bge.submarine, ('D', 9), bge.Orientation.S)
        grid.shots.update({
            ('A', 2),
            ('D', 9),
            ('E', 9),
            ('F', 9),
        })

        assert grid.ships_afloat() == {bge.destroyer}

    def test_all_ship_coords(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), bge.Orientation.E)
        grid.add_ship(bge.submarine, ('D', 9), bge.Orientation.S)

        assert grid._all_ship_coords() == {
            ('A', 1),
            ('A', 2),
            ('D', 9),
            ('E', 9),
            ('F', 9),
        }

    def test_contains(self):
        grid = bge.Grid()

        for i in range(ord('A'), ord('A') + grid.size):
            for j in range(1, grid.size + 1):
                assert (chr(i), j) in grid

        assert ('J', 11) not in grid
        assert ('K', 1) not in grid


class TestShip:

    def test_ship_equality(self):
        assert bge.cruiser == bge.cruiser
        assert bge.cruiser == bge.Ship('Cruiser', 3)
        assert not bge.cruiser == bge.carrier
