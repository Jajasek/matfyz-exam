from curses import wrapper, mousemask, KEY_MOUSE, getmouse, ALL_MOUSE_EVENTS,\
    BUTTON2_PRESSED


def main(stdscr):
    mousemask(-1)

    try:
        while True:
            ch = stdscr.getch()
            if ch == KEY_MOUSE:
                print(getmouse())
    except Exception as e:
        print(e)
        while True:
            pass


if __name__ == '__main__':
    wrapper(main)
