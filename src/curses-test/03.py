import curses


def main(stdscr: curses.window):
    stdscr.addstr(0, 0, f'Pairs: {curses.COLOR_PAIRS}, Colors: {curses.COLORS}')
    stdscr.addstr(1, 0, f'can_change_color: {curses.can_change_color()}')
    while True:
        c = stdscr.getch()
        stdscr.addstr(2, 0, str(c))
        stdscr.clrtoeol()
        stdscr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
