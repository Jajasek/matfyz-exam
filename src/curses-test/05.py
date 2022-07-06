import curses


def main(stdscr: curses.window) -> None:
    stdscr.refresh()
    stdscr.addstr(0, 0, 'Pair 0', curses.color_pair(0))
    while True:
        stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)
