from __future__ import annotations
import curses
from itertools import product
from typing import TypeAlias, Literal, Generator, Any
from collections.abc import Iterable
from queue import LifoQueue
from random import choice, sample

from MyLib.ocurses.curses_utilities import addstr

import configuration as conf


UNTOUCHED: Literal['UNTOUCHED'] = 'UNTOUCHED'
DIRECTIONS: list[tuple[int, int]] = [
    (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)
]

Cell: TypeAlias = tuple[int, int]
Region: TypeAlias = Cell | Literal['UNTOUCHED']


def is_mine(number: int) -> bool:
    return number in (10, 12)


def is_pressable(number: int) -> bool:
    return number in (11, 12)


def is_covered(number: int) -> bool:
    return number > 8


def is_unflagged_mine(number: int) -> bool:
    return number == 12


def is_flagged(number: int) -> bool:
    return number in (9, 10)


# noinspection PyPep8Naming
class _DO_NOT_SET:
    pass


class _Boundary:
    """
    A dict-like object representing a choice of mine placement on the boundary.
    """
    def __init__(self) -> None:
        self._mines: dict[Cell, bool] = {}
        self._mine_count: int = 0

    def __repr__(self) -> str:
        return str(tuple(cell for cell in self._mines if self._mines[cell]))

    def __len__(self) -> int:
        return len(self._mines)

    def __iter__(self) -> Iterable[Cell, bool]:
        return iter(self._mines.items())

    def set_mine(self, y: int, x: int) -> None:
        self._mines[y, x] = True
        self._mine_count += 1

    def set_empty(self, y: int, x: int) -> None:
        self._mines[y, x] = False

    def get_number_of_mines(self) -> int:
        return self._mine_count

    def copy(self) -> _Boundary:
        new = _Boundary()
        new._mines = self._mines.copy()
        new._mine_count = self._mine_count
        return new

    def get(self, cell: Cell, default: Any = _DO_NOT_SET) -> Any:
        if default is _DO_NOT_SET:
            return self._mines.get(cell)
        return self._mines.get(cell, default)

    def delete(self, cell: Cell) -> None:
        del self._mines[cell]


class Minefield:

    def __init__(self, window: curses.window) -> None:
        # the window the Minefield will be drawn on. It has odd width and
        # squares will be on odd x-coordinates.
        self.window = window
        # the dimensions of the minefield, calculated from dimensions of window
        self.dimensions: tuple[int, int]
        # the current number of cells unexposed to the player
        self.covered: int
        # the total number of mines, costant
        self.total_mines: int
        # the total number of mines minus the number of flags placed
        self.unmarked_mines: int = 0
        # 2D array representing the state of the minefield:
        #   {0, ..., 8}           uncovered numbers, constant
        #   9                     flagged cell that is not mine
        #   10                    flagged mine
        #   11                    covered cell that is not mine
        #   12                    mine, can be repositioned, is always covered
        self.minefield: list[list[int]]
        # the set of cells that are flagged
        self.flags: set[Cell] = set()
        # 0: game not started; 1: playing; 2: EXPLOSION!; 3: player won
        self.game_state: Literal[0, 1, 2, 3] = 0

        # helper variables:
        # the set of cells in the UNTOUCHED region that are mine
        self.mine_cells: set[Cell]
        # the set of cells in the UNTOUCHED region that are not mine
        self.empty_cells: set[Cell]
        # the set of all regions that player can safely uncover
        self.possible: set[Region] = set()
        # keys are a set of all cells on the boundary, each cell has associated
        # the index of the direction to the uncovered cell it was accessed from
        self.normal_directions: dict[Cell, int] = dict()
        # the list of all possible boundaries given the uncovered cells
        self.all_boundaries: list[_Boundary] = []
        # boundaries[region] is a list of all boundaries that don't have the
        # region full of mines, ie those can be chosen from when player
        # uncovers a cell whe possible is empty
        self.boundaries: dict[Region, list[_Boundary]] = {
            UNTOUCHED: [_Boundary()]
        }
        # the list of boundaries that have at least one mine in the UNTOUCHED
        # region
        self.ue_boundaries: list[_Boundary] = []
        # the list of pressed cells (between press and release of a button)
        self.pressed: list[Cell] = []

        # initializing values
        maxy, maxx = window.getmaxyx()
        self.dimensions = (maxy, maxx // 2)
        self.covered = self.dimensions[0] * self.dimensions[1]
        self.total_mines = round(self.covered * conf.MINE_RATIO)

        all_coordinates: list[Cell] = list(product(
            range(self.dimensions[0]), range(self.dimensions[1])
        ))
        self.mine_cells = set(sample(all_coordinates, k=self.total_mines))
        self.empty_cells = set(all_coordinates) - self.mine_cells
        self.minefield = [
            [12 if (y, x) in self.mine_cells else 11
             for x in range(self.dimensions[1])]
            for y in range(self.dimensions[0])
        ]

        self.renderer = Renderer(
            self.window, self.dimensions, self.minefield, self.pressed
        )
        self.renderer.draw_minefield()

        # The commented code below could be used instead, with appropriate
        # changes, to track the number of neighbouring mines dynamically. It
        # might be faster.
        #
        # self.minefield = [
        #     [16] * self.dimensions[1] for _ in range(self.dimensions[0])
        # ]
        # for y, x in self.mine_cells:
        #     self.minefield[y][x] = 42
        #     for dy, dx in DIRECTIONS:
        #         if (0 <= y + dy < self.dimensions[0] and
        #                 0 <= x + dx < self.dimensions[1] and
        #                 self.minefield[y + dy][x + dx] != 42):
        #             self.minefield[y + dy][x + dx] += 1

    def mouse_uncover_press(self, y: int, x: int) -> None:
        """If the pressed cell is covered, redraw and save it."""
        # The parameters are the coordinates of on-screen character.
        celly, cellx = self._char_to_cell(y, x, True)
        if is_pressable(self.minefield[celly][cellx]):
            self.pressed = [(celly, cellx)]
            self.renderer.draw_pressed(celly, cellx)

    def mouse_uncover_release(self) -> None:
        """Uncover the previously pressed cell, analyze the information."""
        if self.pressed:
            self._uncover(*self.pressed[0])
            self.pressed = []

    def mouse_uncover_cancel(self) -> None:
        """Unpress previously pressed cell, do not uncover."""
        if self.pressed:
            self.renderer.draw_covered(*self.pressed[0])
            self.pressed = []

    def mouse_mark_press(self, y: int, x: int) -> None:
        """
        If uncovered, redraw and save all covered neighbours. Othervise mark.
        """
        # The parameters are the coordinates of on-screen character.
        celly, cellx = self._char_to_cell(y, x, False)
        if is_covered(self.minefield[celly][cellx]):
            if is_pressable(self.minefield[celly][cellx]):
                self.flags.add((celly, cellx))
                self.minefield[celly][cellx] -= 2
                self.renderer.draw_flag(celly, cellx)
            else:
                self.flags.remove((celly, cellx))
                self.minefield[celly][cellx] += 2
                self.renderer.draw_covered(celly, cellx)
        else:
            # TODO: press neighbours
            pass

    def mouse_mark_release(self) -> None:
        """If previously pressed cell has enough flags, uncover neighbours."""
        pass

    def mouse_mark_cancel(self) -> None:
        """Regraw neighbours of previously pressed cell. Do not uncover."""
        pass

    def _char_to_cell(self, chy: int, chx: int, uncover: bool) -> Cell:
        """Convert on-screen character coordinates to coordinates of a cell."""
        # offsety, offsetx = self.window.getbegyx()
        # y, x = chy - offsety, chx - offsetx
        # if x % 2:
        #     # exactly in the middle of a cell
        #     return y, x // 2
        # else:
        #     # between cells
        #     if x == self.window.getmaxyx()[1] - 1:
        #         # snaping away from the right boundary
        #         return y, x // 2 - 1
        #     if x == 0 or (y, x // 2 - 1) not in self.normal_directions:
        #         # snapping away from the left boundary or an untouched cell on
        #         # the left
        #         return y, x // 2
        #     if (y, x // 2) not in self.normal_directions:
        #         # snapping away from an untouched cell on the right
        #         return y, x // 2 - 1
        #     if uncover:
        #         # left-click
        #         if not is_pressable(self.minefield[y][x // 2 - 1]):
        #             # snapping away
        #             return y, x // 2
        #         if not is_pressable(self.minefield[y][x // 2]):
        #             return y, x // 2 - 1
        #         if (y, x // 2) in self.possible:
        #             return y, x // 2
        #         if (y, x // 2 - 1) in self.possible:
        #             return y, x // 2 - 1
        #     else:
        #         # right-click
        #         if not self.boundaries[y, x // 2]:
        #             return y, x // 2
        #         if not self.boundaries[y, x // 2 - 1]:
        #             return y, x // 2 - 1
        #     return y, x // 2

        offsety, offsetx = self.window.getbegyx()
        y, x = chy - offsety, chx - offsetx
        right = x // 2
        left = x // 2 - 1
        if x % 2:
            # exactly in the middle of a cell
            return y, x // 2
        elif uncover:  # between cells, left click

            # Snapping away borders
            if x == 0:
                return y, right
            if x == self.window.getmaxyx()[1] - 1:
                return y, left

            # Snapping away from flags and uncovered
            if not is_pressable(self.minefield[y][left]):
                return y, right
            if not is_pressable(self.minefield[y][right]):
                return y, left

            # Snapping towards possible
            pos_right = (y, right) if (y, right) in self.normal_directions \
                else UNTOUCHED
            if pos_right in self.possible:
                return y, right
            pos_left = (y, left) if (y, left) in \
                self.normal_directions else UNTOUCHED
            if pos_left in self.possible:
                return y, left

            # Snapping towards boundary
            if pos_right != UNTOUCHED:
                return y, right
            if pos_left != UNTOUCHED:
                return y, left

            # indecidable, snap right
            return y, right

        else:  # between cells, right click

            # Snapping away borders
            if x == 0:
                return y, right
            if x == self.window.getmaxyx()[1] - 1:
                return y, left

            # helper variables
            pos_right = (y, right) if (y, right) in self.normal_directions \
                else UNTOUCHED
            explosive_right = not self.boundaries[pos_right]
            pos_left = (y, left) if (y, left) in \
                self.normal_directions else UNTOUCHED
            explosive_left = not self.boundaries[pos_left]

            # Snapping away from flagged explosives
            if explosive_left and is_flagged(self.minefield[y][left]):
                return y, right
            if explosive_right and is_flagged(self.minefield[y][right]):
                return y, left

            # Snapping towards pressable explosives
            if explosive_right and is_pressable(self.minefield[y][right]):
                return y, right
            if explosive_left and is_pressable(self.minefield[y][left]):
                return y, left

            # Snapping away from pressable can-be-empty
            if not explosive_left and is_pressable(self.minefield[y][left]):
                return y, right
            if not explosive_right and is_pressable(self.minefield[y][right]):
                return y, left

            # Snapping towards flagged can-be-empty
            if not explosive_right and is_flagged(self.minefield[y][right]):
                return y, right
            if not explosive_left and is_flagged(self.minefield[y][left]):
                return y, left

            def is_chordable(celly: int, cellx: int) -> bool:
                """
                Return True if (celly, cellx) has enough flags and has a
                pressable neighbour.
                """
                flags = 0
                pressables = 0
                for dy, dx in DIRECTIONS:
                    ny, nx = celly + dy, cellx + dx
                    if (self.dimensions[0] > ny >= 0 <= nx <
                            self.dimensions[1]):
                        if is_flagged(self.minefield[ny][nx]):
                            flags += 1
                        elif is_pressable(self.minefield[ny][nx]):
                            pressables += 1
                return flags >= self.minefield[celly][cellx] and pressables > 0

            # Snapping towards chordable
            if is_chordable(y, right):
                return y, right
            if is_chordable(y, left):
                return y, left

            # indecidable, snap right
            return y, right

    def _uncover(self, y: int, x: int) -> None:
        """Handle left-click on (y, x)."""
        pos: Region
        if (y, x) in self.normal_directions:
            pos = (y, x)
        else:
            self._remove_from_untouched(y, x)
            pos = UNTOUCHED
        if pos in self.possible:
            self._uncover_safe(y, x)

        elif not self.boundaries[pos]:
            self._explode(y, x)

        elif self.possible:
            if not is_mine(self.minefield[y][x]):
                if pos == UNTOUCHED:
                    self._overwrite_minefield(choice(self.ue_boundaries),
                                              (y, x), True)
                else:
                    # the following 'if' has only debugging purpose. The code
                    # sometimes breaks here because the set is empty. But
                    # the problem seems to have been fixed.
                    # TODO: remove this debug 'if'
                    if not set(self.all_boundaries) - set(
                            self.boundaries[pos]):
                        raise AssertionError(
                            f'all_boundaries: {self.all_boundaries}'
                            f'boundaries({pos}): {self.boundaries[pos]}'
                            f'possible: {self.possible}'
                        )
                    self._overwrite_minefield(choice(tuple(
                        set(self.all_boundaries) - set(self.boundaries[pos])
                    )))
            self._explode(y, x)

        else:
            if is_mine(self.minefield[y][x]):
                self._overwrite_minefield(choice(self.boundaries[pos]),
                                          (y, x), False)
            self._uncover_safe(y, x)

    def _remove_from_untouched(self, y: int, x: int) -> None:
        """Remove (y, x) from mine_cells or empty_cells."""
        if (y, x) in self.empty_cells:
            self.empty_cells.remove((y, x))
        elif (y, x) in self.mine_cells:
            self.mine_cells.remove((y, x))

    def _uncover_safe(self, y: int, x: int) -> None:
        """Uncover (y, x) when known that it is empty."""
        pos: Region = (y, x) if (y, x) in self.normal_directions else UNTOUCHED
        new, old, inner_boundary = self._uncover_search((y, x))

        # cache possible boundaries, then update state
        possible_boundaries: list[_Boundary] = self.boundaries[pos]
        self._update_state(possible_boundaries, new, old, inner_boundary)

    def _uncover_search(self, *cells: Cell) -> tuple[list[Cell], list[Cell],
                                                     list[Cell]]:
        """
        Uncover each cell in cells. If some is zero, do a DFS to uncover whole
        chunk. Return the list of new cells on the boundary, the list of cells
        removed from the boundary and the list of new cells on the inner
        boundary. These impose further restrictions on the possible boundaries.
        """
        # each cell in cells must be pressable

        new: list[Cell] = []
        old: list[Cell] = []
        inner_boundary: list[Cell] = []
        zero_stack = LifoQueue()
        # we will use the fact that dictionaries are insertion-ordered
        # cell: (direction, number_of_mines)
        nonzero_queue: dict[Cell, tuple[int, int]] = {}
        for y, x in cells:
            if mines := self._count_mines(y, x):
                nonzero_queue[y, x] = (
                    self.normal_directions.get((y, x), 0), mines
                )
            else:
                zero_stack.put((y, x, self.normal_directions.get((y, x), 0)))

        # flagged cells will never be added to zero_stack or nonzero_queue

        # dfs to first uncover all zeroes
        while not zero_stack.empty():
            y, x, direction = zero_stack.get()
            if not is_covered(self.minefield[y][x]):
                # cell is already uncovered
                continue
            if self._uncover_cell(y, x, 0):
                old.append((y, x))

            for d in range(direction, direction + 8):
                ny, nx = y + DIRECTIONS[d][0], x + DIRECTIONS[d][1]
                if (self.dimensions[0] > ny >= 0 <= nx < self.dimensions[1]
                        and is_covered(self.minefield[ny][nx])):
                    if is_pressable(self.minefield[ny][nx]):
                        # (ny, nx) is inbounds and pressable, therefore can be
                        # uncovered
                        if mines := self._count_mines(ny, nx):
                            nonzero_queue[ny, nx] = ((d + 4) % 8 - 8, mines)
                        else:
                            zero_stack.put((ny, nx, (d + 4) % 8 - 8))
                    else:
                        # (ny, nx) is inbounds and flagged. It would be
                        # uncovered, but cannot be, we must add it to new and
                        # add its zero neighbours to the inner boundary.
                        inner_boundary.append((y, x))
                        if (ny, nx) not in self.normal_directions:
                            self._remove_from_untouched(ny, nx)
                            self.normal_directions[ny, nx] = (d + 4) % 8 - 8
                            new.append((ny, nx))

        # uncover the inner boundary and construct new
        for (y, x), (direction, mines) in nonzero_queue.items():
            if not is_covered(self.minefield[y][x]):
                # cell is already uncovered
                continue
            if self._uncover_cell(y, x, mines):
                old.append((y, x))

            for d in range(direction, direction + 8):
                ny, nx = y + DIRECTIONS[d][0], x + DIRECTIONS[d][1]
                if (self.dimensions[0] > ny >= 0 <= nx < self.dimensions[1]
                        and is_covered(self.minefield[ny][nx]) and
                        (ny, nx) not in self.normal_directions and
                        (ny, nx) not in nonzero_queue):
                    # (ny nx) is inbounds, covered, not on the boundary yet
                    # and not going to be uncovered, therefore it is new
                    self._remove_from_untouched(ny, nx)
                    self.normal_directions[ny, nx] = (d + 4) % 8 - 8
                    new.append((ny, nx))

        return new, old, inner_boundary + list(nonzero_queue.keys())

    def _update_state(self, possible_boundaries: list[_Boundary],
                      new: list[Cell], old: Iterable[Cell],
                      inner_boundary: Iterable[Cell]) -> None:
        """Extend each possible boundary and save them, sort all_boundaries."""
        # clear the saved boundaries
        self.all_boundaries = []
        self.ue_boundaries = []
        self.boundaries = dict()
        for cell in self.normal_directions:
            self.boundaries[cell] = []
        self.boundaries[UNTOUCHED] = []

        # further filter the boundaries and extend the possible ones to new
        # cells
        for b in possible_boundaries:
            # Possible boundaries cannot have mine on any uncovered cell,
            # it is sufficient to check the ones that were on the boundary
            for o in old:
                if b.get(o):
                    # the break will cause the 'else' branch to be skipped
                    break
                b.delete(o)
            else:
                # The boundary must not cause the newly uncovered nonzero cells
                # to have too many or too little mines. We do not have to check
                # zero cells, because their neighbours were also uncovered
                # and the boundary would have failed the previous check.
                for iy, ix in inner_boundary:
                    if not (
                        self._count_hypothetical_mines(iy, ix, b, False)
                        <= self.minefield[iy][ix]
                        <= self._count_hypothetical_mines(iy, ix, b, True)
                    ):
                        break
                else:
                    self.all_boundaries.extend(self._extend(b, new))

        # sort all boundaries
        for b in self.all_boundaries:
            for cell, mine in b:
                cell: tuple[int, int]
                if not mine:
                    self.boundaries[cell].append(b)
            if m := self.total_mines - b.get_number_of_mines() > 0:
                self.ue_boundaries.append(b)
            if m < self.covered - len(self.normal_directions):
                self.boundaries[UNTOUCHED].append(b)

        # update possible
        if (len(self.normal_directions) < self.covered and
                not self.ue_boundaries):
            self.possible.add(UNTOUCHED)
        elif UNTOUCHED in self.possible:
            self.possible.remove(UNTOUCHED)
        for cell in self.normal_directions:
            if self.boundaries[cell] == self.all_boundaries:
                self.possible.add(cell)

    def _count_mines(self, y: int, x: int) -> int:
        """Count the number of mines among the neighbours of (y, x)."""
        count = 0
        for dy, dx in DIRECTIONS:
            if (self.dimensions[0] > y + dy >= 0 <= x + dx < self.dimensions[1]
                    and is_mine(self.minefield[y + dy][x + dx])):
                count += 1
        return count

    def _uncover_cell(self, y: int, x: int, mines: int | None = None) -> bool:
        """
        Update minefield, redraw screen, remove cell from datastructures.
        Return True if the cell was on the boundary, False otherwise.
        """
        if mines is None:
            mines = self._count_mines(y, x)

        # print the uncovered cell to the screen
        self.renderer.draw_uncovered(y, x, mines)

        # remove it from datastructures containing covered cells
        self.covered -= 1
        self._remove_from_untouched(y, x)
        if (y, x) in self.possible:
            self.possible.remove((y, x))
        self.minefield[y][x] = mines
        if (y, x) in self.normal_directions:
            # The cell is on the boundary
            del self.normal_directions[(y, x)]
            return True
        return False

    def _extend(self, incomplete_boundary: _Boundary,
                cells_to_add: list[Cell]) -> Generator[_Boundary]:
        """Extend incomplete_boundary to given cells in every possible way."""
        if not cells_to_add:
            yield incomplete_boundary
            return
        if self._can_be_mine(incomplete_boundary, *cells_to_add[0]):
            branch = incomplete_boundary.copy()
            branch.set_mine(*cells_to_add[0])
            yield from self._extend(branch, cells_to_add[1:])
        if self._can_be_empty(incomplete_boundary, *cells_to_add[0]):
            incomplete_boundary.set_empty(*cells_to_add[0])
            yield from self._extend(incomplete_boundary, cells_to_add[1:])

    def _can_be_mine(self, given_boundary: _Boundary, y: int, x: int) -> bool:
        """
        Given an incomplete boundary, can cell (y, x) be a mine according to
        neighbouring uncovered cells?
        """
        if given_boundary.get_number_of_mines() == self.total_mines:
            # all available mines were placed
            return False
        for dy, dx in DIRECTIONS:
            if (self.dimensions[0] > y + dy >= 0 <= x + dx < self.dimensions[1]
                and 8 >= self.minefield[y + dy][x + dx] ==
                    self._count_hypothetical_mines(
                        y + dy, x + dx, given_boundary, False
                    )):
                # adding a mine would result in an uncovered cell to have
                # more mines than is its value
                return False
        return True

    def _can_be_empty(self, given_boundary: _Boundary, y: int, x: int) -> bool:
        """
        Given an incomplete boundary, can cell (y, x) be empty according to
        neighbouring uncovered cells?
        """
        if (self.total_mines - given_boundary.get_number_of_mines() ==
                self.covered - len(given_boundary)):
            # there would be no place to put all mines in
            return False
        for dy, dx in DIRECTIONS:
            if (self.dimensions[0] > y + dy >= 0 <= x + dx < self.dimensions[1]
                and 8 >= self.minefield[y + dy][x + dx] ==
                    self._count_hypothetical_mines(
                        y + dy, x + dx, given_boundary, True
                    )):
                # making (y, x) empty would make an uncovered cell unable to
                # have enough mines around
                return False
        return True

    def _count_hypothetical_mines(self, y: int, x: int, boundary: _Boundary,
                                  count_unset: bool) -> int:
        """
        Count mines around (y, x) if boundary was a description of reality.
        """
        count = 0
        for dy, dx in DIRECTIONS:
            if (self.dimensions[0] > y + dy >= 0 <= x + dx < self.dimensions[1]
                    and is_covered(self.minefield[y + dy][x + dx])
                    and boundary.get((y + dy, x + dx), count_unset)):
                count += 1
        return count

    def _explode(self, y: int, x: int) -> None:
        """Uncover a cell (y, x) containing mine, render, update game state."""
        for fy, fx in self.flags:
            if not is_mine(self.minefield[fy][fx]):
                self.renderer.draw_mistake(fy, fx)
        for my, mx in self.mine_cells:
            if is_pressable(self.minefield[my][mx]):
                self.renderer.draw_mine(my, mx)
        for my, mx in self.normal_directions:
            if is_unflagged_mine(self.minefield[my][mx]):
                self.renderer.draw_mine(my, mx)
        self.renderer.draw_explosion(y, x)
        if self.possible:
            self.renderer.draw_hint(*self.possible.pop())
        self.game_state = 2

    def _overwrite_minefield(
            self, boundary: _Boundary, fixcell: Cell | None = None,
            fixmine: bool = False
    ) -> None:
        """
        Write boundary into minefield, placing untouched mines randomly.
        When untouched fixcell given, fix it either to be or not to be mine.
        """
        change: int = 0
        change_list: list = list(boundary)
        if fixcell:
            change_list.append((fixcell, fixmine))
        for (y, x), mine in change_list:
            if mine and not is_mine(self.minefield[y][x]):
                self.minefield[y][x] += 1
                change -= 1
            elif not mine and is_mine(self.minefield[y][x]):
                self.minefield[y][x] -= 1
                change += 1

        if change > 0:
            for y, x in sample(tuple(self.empty_cells - {fixcell}), k=change):
                self.minefield[y][x] += 1
                self.mine_cells.add((y, x))
        elif change < 0:
            for y, x in sample(tuple(self.mine_cells - {fixcell}), k=-change):
                self.minefield[y][x] -= 1
                self.empty_cells.add((y, x))

    def _uncover_several(self, cells: list[Cell]) -> None:
        """Handle right-click on an uncovered cell with enough flags."""
        if len(cells) == 1:
            self._uncover(*cells[0])
        elif self.possible.issuperset(cells):
            self._uncover_several_safe(cells)
        elif self.possible.issubset(cells):
            for y, x in cells:
                if is_mine(self.minefield[y][x]):
                    self._explode(y, x)
                    return
            self._uncover_several_safe(cells)
        else:
            for cell in cells:
                if cell not in self.possible:
                    explosive_cell = cell
            # noinspection PyUnboundLocalVariable
            self._overwrite_minefield(choice(tuple(
                set(self.all_boundaries) - set(self.boundaries[explosive_cell])
            )))
            self._explode(*explosive_cell)

    def _uncover_several_safe(self, cells: list[Cell]) -> None:
        """
        Uncover each given cell on the boundary when known that it is empty.
        """
        new, old, uncovered = self._uncover_search(*cells)

        # cache possible boundaries, update state
        possible_boundaries: list[_Boundary] = self.all_boundaries
        self._update_state(possible_boundaries, new, old, uncovered)


class Renderer:
    MINE_CHAR: str = '💣'
    COVERED_CHAR: str = '□'
    HINT_CHAR: str = '🖢'
    FLAG_CHAR: str = '⚑'

    def __init__(self, window: curses.window, dimensions: tuple[int, int],
                 minefield: list[list[int]], pressed: list[Cell]) -> None:
        self.window = window
        self.dimensions = dimensions
        self.minefield = minefield
        self.pressed = pressed

    def draw_minefield(self) -> None:
        """Draw the whole minefield before the game starts."""
        for y in range(self.dimensions[0]):
            addstr(self.window, y, 0, '▌', curses.color_pair(conf.PAIR_SPACE))
            addstr(self.window, y, 1,
                   ' '.join(self.COVERED_CHAR * self.dimensions[1]),
                   curses.color_pair(conf.PAIR_SQUARE))
            addstr(self.window, y, 2*self.dimensions[1], '▐',
                   curses.color_pair(conf.PAIR_SPACE))
        self.window.noutrefresh()

    def draw_pressed(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, '·',
               curses.color_pair(conf.PAIR_PRESS))
        self._draw_spaces(y, x, True)
        self.window.noutrefresh()

    def draw_covered(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, '□',
               curses.color_pair(conf.PAIR_SQUARE))
        self._draw_spaces(y, x, False)
        self.window.noutrefresh()

    def draw_uncovered(self, y: int, x: int, mines: int) -> None:
        if mines:
            addstr(self.window, y, 2*x + 1, str(mines), curses.color_pair(
                getattr(conf, f'PAIR_{mines}')
            ))
        else:
            addstr(self.window, y, 2*x + 1, ' ',
                   curses.color_pair(conf.PAIR_1))
        self._draw_spaces(y, x, True)
        self.window.noutrefresh()

    def draw_mine(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, self.MINE_CHAR,
               curses.color_pair(conf.PAIR_MINE))
        self.window.noutrefresh()

    def draw_explosion(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, self.MINE_CHAR,
               curses.color_pair(conf.PAIR_EXPLOSION))
        if x == 0 or not is_mine(self.minefield[y][x - 1]):
            self._draw_space(y, 2*x, x == 0 or
                             not is_covered(self.minefield[y][x - 1]), False)
        # TODO: draw red space in red (or in the same color the cell on the
        #       left is)
        self.window.noutrefresh()

    def draw_hint(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, self.HINT_CHAR,
               curses.color_pair(conf.PAIR_HINT))
        if x == 0 or not is_mine(self.minefield[y][x - 1]):
            self._draw_space(y, 2*x, x == 0 or
                             not is_covered(self.minefield[y][x - 1]), True)
        self._draw_space(y, 2*x + 2, True, x == self.dimensions[1] - 1 or
                         not is_covered(self.minefield[y][x + 1]))
        self.window.noutrefresh()

    def _draw_spaces(self, y: int, x: int, uncovered: bool) -> None:
        self._draw_space(
            y, 2*x, x == 0 or not is_covered(self.minefield[y][x - 1]) or
            (y, x - 1) in self.pressed, uncovered
        )
        self._draw_space(
            y, 2*x + 2, uncovered, x == self.dimensions[1] - 1 or not
            is_covered(self.minefield[y][x + 1]) or (y, x + 1) in self.pressed
        )

    def _draw_space(self, chy: int, chx: int, left: bool, right: bool)\
            -> None:
        char = ' ' if left == right else '▌'
        attr = curses.A_REVERSE if right else 0
        addstr(self.window, chy, chx, char,
               curses.color_pair(conf.PAIR_SPACE) | attr)

    def draw_flag(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, self.FLAG_CHAR,
               curses.color_pair(conf.PAIR_FLAG))
        self._draw_spaces(y, x, False)
        self.window.noutrefresh()

    def draw_mistake(self, y: int, x: int) -> None:
        addstr(self.window, y, 2*x + 1, self.FLAG_CHAR,
               curses.color_pair(conf.PAIR_MISTAKE))
        self._draw_spaces(y, x, False)
        self.window.noutrefresh()
