import curses
from contextlib import contextmanager


@contextmanager
def open_screen():
    scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    scr.keypad(1)
    try:
        yield scr
    except Exception as e:
        print(e)
        while True:
            pass
    finally:
        curses.nocbreak()
        scr.keypad(0)
        curses.echo()
        curses.endwin()


curses_mouse_states = {
    curses.BUTTON1_PRESSED: 'Button 1 Pressed',
    curses.BUTTON1_RELEASED: 'Button 1 Released',
    curses.BUTTON1_CLICKED: 'Button 1 Clicked',
    curses.BUTTON1_DOUBLE_CLICKED: 'Button 1 Double-Clicked',
    curses.BUTTON1_TRIPLE_CLICKED: 'Button 1 Triple-Clicked',

    curses.BUTTON2_PRESSED: 'Button 2 Pressed',
    curses.BUTTON2_RELEASED: 'Button 2 Released',
    curses.BUTTON2_CLICKED: 'Button 2 Clicked',
    curses.BUTTON2_DOUBLE_CLICKED: 'Button 2 Double-Clicked',
    curses.BUTTON2_TRIPLE_CLICKED: 'Button 2 Triple-Clicked',

    curses.BUTTON3_PRESSED: 'Button 3 Pressed',
    curses.BUTTON3_RELEASED: 'Button 3 Released',
    curses.BUTTON3_CLICKED: 'Button 3 Clicked',
    curses.BUTTON3_DOUBLE_CLICKED: 'Button 3 Double-Clicked',
    curses.BUTTON3_TRIPLE_CLICKED: 'Button 3 Triple-Clicked',

    curses.BUTTON4_PRESSED: 'Button 4 Pressed',
    curses.BUTTON4_RELEASED: 'Button 4 Released',
    curses.BUTTON4_CLICKED: 'Button 4 Clicked',
    curses.BUTTON4_DOUBLE_CLICKED: 'Button 4 Double-Clicked',
    curses.BUTTON4_TRIPLE_CLICKED: 'Button 4 Triple-Clicked',

    curses.BUTTON5_PRESSED: 'Button 5 Pressed',
    curses.BUTTON5_RELEASED: 'Button 5 Released',
    curses.BUTTON5_CLICKED: 'Button 5 Clicked',
    curses.BUTTON5_DOUBLE_CLICKED: 'Button 5 Double-Clicked',
    curses.BUTTON5_TRIPLE_CLICKED: 'Button 5 Triple-Clicked',

    curses.REPORT_MOUSE_POSITION: 'Middle Button Clicked',

    curses.BUTTON_SHIFT: 'Button Shift',
    curses.BUTTON_CTRL: 'Button Ctrl',
    curses.BUTTON_ALT: 'Button Alt'
}

with open_screen() as scr:
    n = 0
    curses.mousemask(-1)
    curses.mouseinterval(0)
    y, x = scr.getmaxyx()
    while True:
        c = scr.getch()
        if c == curses.KEY_MOUSE:
            mouse_state = curses.getmouse()[4]
            states = '; '.join(state_string for state, state_string
                               in curses_mouse_states.items()
                               if mouse_state & state)
            scr.addstr(0, 0, states)
            scr.clrtoeol()
            scr.addstr(1, 0, str(n))
            scr.refresh()
            n += 1
        elif c == ord('r'):
            x += 1
            scr.clear()
            curses.resizeterm(y, x)
            scr.addstr(0, 0, 'Resized?')
            scr.clrtoeol()
            scr.refresh()
        elif c == ord('q'):
            break
        elif c == curses.KEY_RESIZE:
            scr.addstr(0, 0, 'Key_Resize')
            scr.clrtoeol()
            scr.refresh()
