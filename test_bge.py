import pytest

import bge


class TestGame:

    @pytest.fixture
    def game(self):
        game = bge.Game()
        grid = game.create_grid('John')
        grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
        grid.add_ship(bge.submarine, ('D', 9), ('E', 9), ('F', 9))
        grid.add_ship(bge.cruiser, ('J', 8), ('J', 9), ('J', 10))
        grid.add_ship(bge.battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
        grid.add_ship(bge.carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
        grid = game.create_grid('Jane')
        grid.add_ship(bge.destroyer, ('B', 2), ('B', 3))
        grid.add_ship(bge.submarine, ('B', 6), ('C', 6), ('D', 6))
        grid.add_ship(bge.cruiser, ('F', 1), ('G', 1), ('H', 1))
        grid.add_ship(bge.battleship, ('J', 3), ('J', 4), ('J', 5), ('J', 6))
        grid.add_ship(bge.carrier, ('C', 9), ('D', 9), ('E', 9), ('F', 9), ('G', 9))
        return game

    def test_create_grid_one_player(self):
        game = bge.Game()

        game.create_grid('John')

        assert len(game.players) == 1

    def test_create_grid_two_players(self, game):
        assert len(game.players) == 2

    def test_raise_exception_missing_grid(self):
        game = bge.Game()

        with pytest.raises(RuntimeError):
            game.shoot('John', ('A', 1))

    def test_raise_exception_missing_ships(self, game):
        game.players['John'].ships.pop(bge.submarine)

        with pytest.raises(RuntimeError):
            game.shoot('John', ('A', 1))

    def test_creates_player2(self, game):
        game.players.pop('Jane')  # Remove existing player 2

        game.shoot(bge.COMPUTER, ('A', 1))  # Computer will assume player 2

        assert len(game.players) == 2
        assert bge.COMPUTER in game.players

    def test_shoot_hit(self, game):
        hit, *_ = game.shoot('Jane', ('B', 2))

        assert hit

    def test_shoot_miss(self, game):
        hit, *_ = game.shoot('Jane', ('A', 2))

        assert not hit

    def test_shoot_sinks_ship(self, game):
        # Sink Jane's destroyer
        game.shoot('Jane', ('B', 2))
        _, remaining, _ = game.shoot('Jane', ('B', 3))

        assert len(remaining) == 4
        assert bge.destroyer not in remaining

    def test_shoot_raise_exception_invalid_coord(self, game):
        with pytest.raises(bge.InvalidCoordinate):
            game.shoot('John', ('A', 12))

    def test_shoot_invalid_player(self, game):
        with pytest.raises(KeyError):
            game.shoot('Jim', ('B', 2))


class TestGrid:

    def test_add_ship(self):
        grid = bge.Grid()

        grid.add_ship(bge.battleship, ('A', 1), ('A', 2), ('A', 3), ('A', 4))

        assert len(grid.ships) == 1
        assert grid.ships[bge.battleship] == (
            ('A', 1),
            ('A', 2),
            ('A', 3),
            ('A', 4),
        )

    def test_add_ship_off_grid(self):
        grid = bge.Grid()

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('C', 5), ('B', 5), ('A', 5), (chr(ord('A') - 1), 5))

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('E', 8), ('E', 9), ('E', 10), ('E', 11))

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('H', 5), ('I', 5), ('J', 5), ('K', 5))

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.battleship, ('E', 3), ('E', 2), ('E', 1), ('E', 0))

    def test_add_ship_intersect_existing_ship(self):
        grid = bge.Grid()

        grid.add_ship(bge.battleship, ('E', 3), ('E', 4), ('E', 5), ('E', 6))

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.cruiser, ('C', 6), ('D', 6), ('E', 6))

    def test_add_ship_unequal_number_coords(self):
        grid = bge.Grid()

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.cruiser, ('C', 4), ('C', 5), ('C', 6), ('C', 7))

    def test_add_ship_non_consecutive_coords(self):
        grid = bge.Grid()

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.cruiser, ('C', 6), ('C', 4), ('C', 7))

        with pytest.raises(bge.InvalidCoordinate):
            grid.add_ship(bge.cruiser, ('A', 1), ('C', 1), ('D', 1))

    def test_receive_shot_hit(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))

        hit = grid.receive_shot(('A', 2))

        assert hit

    def test_receive_shot_miss(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 2), ('A', 3))

        hit = grid.receive_shot(('A', 4))

        assert not hit

    def test_receive_shot_duplicate(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 2), ('A', 3))
        grid.receive_shot(('A', 2))

        with pytest.raises(bge.InvalidCoordinate):
            grid.receive_shot(('A', 2))

    def test_as_matrix(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
        grid.add_ship(bge.submarine, ('D', 8), ('D', 9), ('D', 10))
        grid.add_ship(bge.cruiser, ('J', 8), ('J', 9), ('J', 10))
        grid.add_ship(bge.battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
        grid.add_ship(bge.carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
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
        grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
        grid.add_ship(bge.submarine, ('D', 9), ('E', 9), ('F', 9))
        grid.shots.update({
            ('A', 2),
            ('D', 9),
            ('E', 9),
            ('F', 9),
        })

        assert grid.ships_afloat() == {bge.destroyer}

    def test_all_ship_coords(self):
        grid = bge.Grid()
        grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
        grid.add_ship(bge.submarine, ('D', 9), ('E', 9), ('F', 9))

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
