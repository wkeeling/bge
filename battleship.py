"""This module provides an example frontend for the Battleship Game Engine."""

import tkinter as tk

import bge

GRID_WIDTH = 500
GRID_HEIGHT = 500


class GameFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        game = bge.Game()

        my_ship_grid = MyShipFrame(game, master=self)
        my_ship_grid.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH, padx=(0, 20))

        enemy_ship_grid = EnemyShipFrame(game, master=self)
        enemy_ship_grid.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.BOTH)


class EnemyShipFrame(tk.Frame):

    def __init__(self, game: bge.Game, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game
        self._on_shot_complete = None

        title = tk.Label(master=self, text='Enemy Ships', font=('Arial', 18))
        title.pack()

        grid = Grid(master=self)
        grid.pack(expand=tk.YES, fill=tk.BOTH)

    def on_shot_complete(self, func: callable):
        """Register a callback will be invoked when a shot has been
        taken on the grid.

        Args:
            func: A no-args callable.
        """
        self._on_shot_complete = func


class MyShipFrame(tk.Frame):

    def __init__(self, game: bge.Game, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game = game
        self._on_shot_complete = None

        title = tk.Label(master=self, text='My Ships', font=('Arial', 18))
        title.pack()

        grid = Grid(master=self)
        grid.pack(expand=tk.YES, fill=tk.BOTH)

    def on_shot_complete(self, func: callable):
        """Register a callback will be invoked when a shot has been
        taken on the grid.

        Args:
            func: A no-args callable.
        """
        self._on_shot_complete = func


class Grid(tk.Canvas):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(
            width=GRID_WIDTH,
            height=GRID_HEIGHT,
            bg='#8c8c8c',
        )

        cell_length = GRID_WIDTH / 11

        for i in range(1, 11):
            x = cell_length * i
            width = 1 if i != 1 else 3
            self.create_line(x, 0, x, GRID_HEIGHT, fill='silver', width=width)
            self.create_text(
                (x + (cell_length // 2), (cell_length // 2)), text=f'{i}', fill='#f2f2f2'
            )

        row_char = ord('A') - 1

        for i in range(1, 11):
            y = cell_length * i
            width = 1 if i != 1 else 3
            self.create_line(0, y, GRID_WIDTH, y, fill='silver', width=width)
            self.create_text(
                ((cell_length // 2), y + (cell_length // 2)), text=f'{chr(row_char + 1)}', fill='#f2f2f2'
            )
            row_char += 1


if __name__ == '__main__':
    root = tk.Tk()
    # root.geometry('1000x520')
    root.resizable(width=False, height=False)
    root.title('Battleship')

    game_frame = GameFrame(master=root)
    game_frame.pack(expand=tk.YES, fill=tk.BOTH)

    root.mainloop()
