Battleship Game Engine
======================


**2 Player Usage**

.. code:: python

    >>> from pprint import pprint
    >>> import bge
    >>>
    >>> game = bge.Game()
    >>>
    >>> grid = game.create_grid('John')
    >>> grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
    >>> grid.add_ship(bge.submarine, ('D', 9), ('E', 9), ('F', 9))
    >>> grid.add_ship(bge.cruiser, ('J', 8), ('J', 9), ('J', 10))
    >>> grid.add_ship(bge.battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
    >>> grid.add_ship(bge.carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
    >>>
    >>> grid = game.create_grid('Jane')
    >>> grid.add_ship(bge.destroyer, ('B', 2), ('B', 3))
    >>> grid.add_ship(bge.submarine, ('B', 6), ('C', 6), ('D', 6))
    >>> grid.add_ship(bge.cruiser, ('F', 1), ('G', 1), ('H', 1))
    >>> grid.add_ship(bge.battleship, ('J', 3), ('J', 4), ('J', 5), ('J', 6))
    >>> grid.add_ship(bge.carrier, ('C', 9), ('D', 9), ('E', 9), ('F', 9), ('G', 9))
    >>>
    >>> hit, remaining, grid = game.shoot('Jane', ('A', 1))  # John is shooting at Jane
    >>> hit
    False
    >>> pprint(grid.as_matrix())
    [[False, None, None, None, None, None, None, None, None, None],  # No hit at A1
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None]]
    >>>
    >>> hit, remaining, grid = game.shoot('John', ('E', 9))  # Jane is shooting at John
    >>> hit
    True
    >>> pprint(grid.as_matrix())
    [[None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, True, None],  # Hit at E9!
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None]]

**Single Player Usage**

.. code:: python

    >>> from pprint import pprint
    >>> import bge
    >>>
    >>> game = bge.Game()
    >>>
    >>> grid = game.create_grid('John')
    >>> grid.add_ship(bge.destroyer, ('A', 1), ('A', 2))
    >>> grid.add_ship(bge.submarine, ('D', 9), ('E', 9), ('F', 9))
    >>> grid.add_ship(bge.cruiser, ('J', 8), ('J', 9), ('J', 10))
    >>> grid.add_ship(bge.battleship, ('F', 3), ('G', 3), ('H', 3), ('I', 3))
    >>> grid.add_ship(bge.carrier, ('C', 2), ('C', 3), ('C', 4), ('C', 5), ('C', 6))
    >>>
    >>> hit, remaining, grid = game.shoot(bge.COMPUTER, ('A', 1))  # John is shooting at the computer
    >>> hit
    False
    >>> hit, remaining, grid = game.shoot('John')  # Trigger computer to shoot at John, target coord is computed
    >>> hit
    False
    >>> pprint(grid.as_matrix())
    [[None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, False, None, None, None],  # Computer targeted C7 - a miss
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None],
     [None, None, None, None, None, None, None, None, None, None]]
    >>> # Alternate back and forth...
