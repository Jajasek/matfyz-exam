import curses


def main(stdscr):
    curses.mousemask(-1)
    while True:
        c = stdscr.getch()
        stdscr.addstr(0, 0, str(c))
        stdscr.clrtoeol()
        stdscr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
