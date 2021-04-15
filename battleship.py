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

        grid = Grid(master=self, mouse_highlight=True)
        grid.pack(expand=tk.YES, fill=tk.BOTH)

        grid.on_cell_click = lambda row, col: grid.set_content(row, col, 'hello world')

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

        grid = Grid(master=self, mouse_highlight=False)
        grid.pack(expand=tk.YES, fill=tk.BOTH)

    def on_shot_complete(self, func: callable):
        """Register a callback will be invoked when a shot has been
        taken on the grid.

        Args:
            func: A no-args callable.
        """
        self._on_shot_complete = func


class Grid(tk.Canvas):

    cell_length = GRID_WIDTH / 11

    def __init__(self, mouse_highlight: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configure(
            width=GRID_WIDTH,
            height=GRID_HEIGHT,
            bg='#8c8c8c',
        )

        self._draw_gridlines()

        self._highlighted = None

        def highlight(event):
            coords = self._row_col(event.x, event.y)
            if coords is not None:
                self._clear_highlight()
                self._highlight_cell(*coords)

        if mouse_highlight:
            self.bind('<Motion>', highlight)

        # The on-click handler takes two args for row and col.
        self.on_cell_click: callable = None

        def click(event):
            if self.on_cell_click is not None:
                coords = self._row_col(event.x, event.y)
                if coords is not None:
                    self.on_cell_click(*coords)

        self.bind('<ButtonRelease-1>', click)

    def _draw_gridlines(self):
        # Draw the vertical grid lines
        for i in range(1, 11):
            x = self.cell_length * i
            width = 1 if i != 1 else 3
            mid = self.cell_length // 2
            self.create_line(x, 0, x, GRID_HEIGHT, fill='silver', width=width)
            self.create_text((x + mid, mid), text=f'{i}', fill='#f2f2f2')

        row_char = ord('A') - 1

        # Draw the horizontal grid lines
        for i in range(1, 11):
            y = self.cell_length * i
            width = 1 if i != 1 else 3
            mid = self.cell_length // 2
            self.create_line(0, y, GRID_WIDTH, y, fill='silver', width=width)
            self.create_text((mid, y + mid), text=f'{chr(row_char + i)}', fill='#f2f2f2')

    def _row_col(self, x, y):
        """Get the row, col for the specified x, y position or None if x, y invalid."""
        row = chr(int((ord('A') - 1) + y // self.cell_length))
        col = int(x // self.cell_length)

        if 10 >= col >= 1 and 'J' >= row >= 'A':
            return row, col

        return None

    def _highlight_cell(self, row, col):
        """Highlight the cell specified by row, col."""
        cell = self._cell(row, col)
        self._highlighted = self.create_rectangle(*cell, outline='red', width=2)

    def _clear_highlight(self):
        """Clear any existing cell highlight."""
        if self._highlighted is not None:
            self.delete(self._highlighted)
            self._highlighted = None

    def _cell(self, row, col):
        """Return the bbox of the cell with the specified row and col."""
        row_map = {}
        row_char = ord('A')

        for i in range(1, 11):
            row_map[chr(row_char)] = i
            row_char += 1

        x1 = col * self.cell_length
        y1 = row_map[row] * self.cell_length
        x2 = x1 + self.cell_length
        y2 = y1 + self.cell_length

        return x1, y1, x2, y2

    def set_content(self, row, col, content):
        print('Setting content for', row, col, content)


if __name__ == '__main__':
    root = tk.Tk()
    root.resizable(width=False, height=False)
    root.title('Battleship')

    game_frame = GameFrame(master=root)
    game_frame.pack(expand=tk.YES, fill=tk.BOTH)

    root.mainloop()
