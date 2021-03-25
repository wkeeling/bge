import bge


def test_start_game_returns_game_instance():
    game = bge.start_game()

    assert isinstance(game, bge.Game)


def test_position_ship():
    grid = bge.Grid()

    grid.position(bge.battleship, ('A', 1), bge.Orientation.E)

    assert len(grid.ships) == 1
    assert grid.ships[bge.battleship] == [
        ('A', 1),
        ('A', 2),
        ('A', 3),
        ('A', 4),
    ]
