import curses
import curses.panel


def main(stdscr: curses.window):
    curses.mousemask(-1)
    win = curses.newwin(4, 10, 0, 0)
    # pan = curses.panel.new_panel(win)
    # pan.top()
    stdscr.getch()
    win.addstr(0, 0, 'a')
    win.refresh()
    n = 0
    while True:
        event = stdscr.getch()
        if event == curses.KEY_MOUSE:
            stdscr.addstr(6, 0, f'* stdscr: {curses.getmouse()}')
            stdscr.clrtoeol()
            stdscr.addstr(7, 0, ' ')
            stdscr.refresh()
        win.addstr(0, 0, str(n))
        n += 1
        win.refresh()
        stdscr.refresh()
        # event = win.getch()
        # if event == curses.KEY_MOUSE:
        #     stdscr.addstr(7, 0, f'*    win: {curses.getmouse()}')
        #     stdscr.clrtoeol()
        #     stdscr.addstr(6, 0, ' ')


if __name__ == '__main__':
    curses.wrapper(main)
