from __future__ import annotations
import curses
from math import log10
from typing import Literal

import configuration as conf


class Bar:
    """The object representing the top bar of the application."""
    def __init__(self, window: curses.window) -> None:
        # the window the Bar will be drawn on.
        self.window = window
        self.mines_digits: int = 0
        self.mines_offset: int = 0
        self.button_offset: int = 0
        self.timer_offset: int = 0
        self.timer_length: int = 0

        self.set_layout(999)  # TODO: change this dynamically

    def set_layout(self, max_mines: int) -> None:
        self.mines_digits = int(log10(max_mines)) + 1
        width: int = self.window.getmaxyx()[1]

        #            ║ 137 ☹ 13:37 ║
        if width >= 1 + self.mines_digits + 1 + 1 + 1 + 5 + 1:

            #          ║  137 ☹ 00:13:37  ║
            if width >= 2 + self.mines_digits + 1 + 1 + 1 + 8 + 2:
                self.timer_length = 8
                space = 2
            #          ║  137 ☹ 13:37  ║
            elif width >= 2 + self.mines_digits + 1 + 1 + 1 + 5 + 2:
                self.timer_length = 5
                space = 2
            #          ║ 137 ☹ 13:37 ║
            else:
                self.timer_length = 5
                space = 1

            self.timer_offset = width - space - self.timer_length
            self.mines_offset = space
            if self.mines_digits > self.timer_length:
                self.button_offset = max(
                    width // 2,  # half, moved to the right when even
                    self.mines_offset + self.mines_digits + 1  # at least 1
                    # space after mines
                )
            else:
                self.button_offset = min(
                    (width - 1) // 2,  # half, moved to the left when even
                    self.timer_offset - 2  # at least 1 space before timer
                )

        #            ║ 137 ☹ 00:13:37 ║

    def update(self, unmarked_mines: int, game_state: Literal[0, 1, 2, 3])\
            -> None:
        pass

    def mouse_press(self, y: int, x: int) -> None:
        pass

    def mouse_release(self, y: int, x: int) -> None:
        pass

    def timer_start(self) -> None:
        pass

    def timer_stop(self) -> None:
        pass

    def timer_reset(self) -> None:
        pass
