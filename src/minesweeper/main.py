import curses
import curses.ascii

from minefield import Minefield
from configuration import UNCOVER_PRESSED, UNCOVER_RELEASED, MARK_PRESSED, \
    MARK_RELEASED, init_colors, PAIR_BORDER
from MyLib.ocurses.curses_utilities import border, addstr


class FairMinesweeper:
    """The application object managing mainloop."""
    def __init__(self, stdscr: curses.window) -> None:
        # This is mandatory to initialize curses, but it is undocumented
        stdscr.refresh()
        # Define colors and color pairs
        init_colors()
        # the window representing the whole screen
        self.stdscr = stdscr
        # the window representing the space occupied by application window
        self.window = self.get_app_window()
        self.draw_frames()

        winy, winx = self.window.getmaxyx()
        offsety, offsetx = self.window.getbegyx()
        # noinspection PyTypeChecker
        self.minefield = Minefield(curses.newwin(
            winy - 4, winx - 2, offsety + 3, offsetx + 1
        ))

        # start receiving mouse events
        curses.mousemask(-1)
        curses.mouseinterval(0)
        curses.curs_set(0)

    def get_app_window(self) -> curses.window:
        """Create a window containing the minefield with frame and bar."""
        # The app has to have odd width
        maxy, maxx = self.stdscr.getmaxyx()
        if maxx % 2:
            return self.stdscr
        # noinspection PyTypeChecker
        return curses.newwin(maxy, maxx - 1, 0, 0)

    def draw_frames(self) -> None:
        """Draw frames aroud the application window and minefield."""
        border(self.window, u'\u2551', u'\u2551', u'\u2550', u'\u2550',
               u'\u2554', u'\u2557', u'\u255A', u'\u255D',
               curses.color_pair(PAIR_BORDER))
        winy, winx = self.window.getmaxyx()
        addstr(self.window, 2, 0, u'\u2560' + u'\u2550' * (winx - 2) +
               u'\u2563', curses.color_pair(PAIR_BORDER))
        self.window.refresh()

    def mainloop(self) -> None:
        while True:
            curses.doupdate()
            # event = self.stdscr.getch()
            event = self.getch()
            if event == curses.KEY_MOUSE:
                _, x, y, _, bstate = curses.getmouse()
                if self.is_inside_minefield(y, x):
                    if bstate == UNCOVER_PRESSED:
                        self.minefield.mouse_uncover_press(y, x)
                    elif bstate == UNCOVER_RELEASED:
                        self.minefield.mouse_uncover_release()
                    elif bstate == MARK_PRESSED:
                        self.minefield.mouse_mark_press(y, x)
                    elif bstate == MARK_RELEASED:
                        self.minefield.mouse_mark_release()
                else:
                    if bstate == UNCOVER_RELEASED:
                        self.minefield.mouse_uncover_cancel()
                    elif bstate == MARK_RELEASED:
                        self.minefield.mouse_mark_cancel()
            elif event == curses.ascii.ESC:
                # TODO: menu
                pass

    def getch(self) -> int:
        """Get a curses event."""
        # This method was created to enable ovrwriting it with a method
        # returning emulated events for testing purposes.
        return self.stdscr.getch()

    def is_inside_minefield(self, y: int, x: int) -> bool:
        """Determine if char (y, x) is inside the minefield  window."""
        offsety, offsetx = self.minefield.window.getbegyx()
        maxy, maxx = self.minefield.window.getmaxyx()
        return (offsety <= y < offsety + maxy and
                offsetx <= x < offsetx + maxx)

    @classmethod
    def run(cls) -> None:
        def main(stdscr: curses.window) -> None:
            cls(stdscr).mainloop()

        # set the delay in ms after pressing the ESC key (the start of function
        # key sequence) to the minimum
        curses.set_escdelay(1)
        curses.wrapper(main)

    @classmethod
    def emulated_run(cls) -> None:
        commands = [
            (0, 6, 6, 0, MARK_PRESSED),
            (0, 6, 6, 0, MARK_RELEASED),
            (0, 6, 7, 0, UNCOVER_PRESSED),
            (0, 6, 6, 0, UNCOVER_RELEASED),
            (0, 6, 6, 0, MARK_PRESSED),
            (0, 6, 6, 0, MARK_RELEASED),
            (0, 6, 6, 0, UNCOVER_PRESSED),
            (0, 6, 6, 0, UNCOVER_RELEASED),
        ]
        curses.getmouse = iter(commands).__next__

        def main(stdscr: curses.window) -> None:
            app = FairMinesweeper(stdscr)
            app.getch = lambda: curses.KEY_MOUSE
            app.mainloop()

        curses.wrapper(main)


if __name__ == '__main__':
    FairMinesweeper.run()
    # FairMinesweeper.emulated_run()
