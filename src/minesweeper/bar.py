from __future__ import annotations
import curses
from typing import Literal

import configuration as conf


class Bar:
    """The object representing the top bar of the application."""
    def __init__(self, window: curses.window) -> None:
        # the window the Bar will be drawn on.
        self.window = window

    def update(self, unmarked_mines: int, game_state: Literal[0, 1, 2, 3])\
            -> None:
        pass

    def mouse_press(self, y: int, x: int) -> None:
        pass

    def mouse_release(self, y: int, x: int) -> None:
        pass
