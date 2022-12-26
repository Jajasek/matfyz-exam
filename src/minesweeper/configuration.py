# This is a temporary config file
import curses

UNCOVER_PRESSED = curses.BUTTON1_PRESSED
UNCOVER_RELEASED = curses.BUTTON1_RELEASED
MARK_PRESSED = curses.BUTTON3_PRESSED
MARK_RELEASED = curses.BUTTON3_RELEASED
LEFT_PRESSED = curses.BUTTON1_PRESSED
LEFT_RELEASED = curses.BUTTON1_RELEASED

MINE_RATIO = 45/160
# 33 / 160  # the exact ratio in the original on expert difficulty

# components are in range [0, 1000]
RGB_BGC = (500, 500, 500)
RGB_BGU = (800, 800, 800)
RGB_SQUARE = (1000, 1000, 1000)
RGB_1 = (0, 0, 1000)
RGB_2 = (0, 500, 0)
RGB_3 = (1000, 0, 0)
RGB_4 = (0, 0, 500)
RGB_5 = (500, 0, 0)
RGB_6 = (0, 500, 500)
RGB_7 = (0, 0, 0)
RGB_8 = (500, 500, 500)
RGB_FLAG = (1000, 304, 304)
RGB_MINE = (0, 0, 0)
RGB_EXPLOSION = (1000, 0, 0)
RGB_HINT = (0, 750, 0)
RGB_EMOJI = (1000, 1000, 0)
RGB_COUNTER = (1000, 0, 0)
RGB_COUNTERBG = (0, 0, 0)
RGB_BORDER = (500, 500, 500)
RGB_MISTAKE = (0, 1000, 0)

COLOR_BGC = 8
COLOR_BGU = 9
COLOR_SQUARE = 10
COLOR_1 = 11
COLOR_2 = 12
COLOR_3 = 13
COLOR_4 = 14
COLOR_5 = 15
COLOR_6 = 16
COLOR_7 = 17
COLOR_8 = 18
COLOR_FLAG = 19
COLOR_MINE = 20
COLOR_EXPLOSION = 21
COLOR_HINT = 22
COLOR_EMOJI = 23
COLOR_COUNTER = 24
COLOR_COUNTERBG = 25
COLOR_BORDER = 26
COLOR_MISTAKE = 27

PAIR_1 = 1
PAIR_2 = 2
PAIR_3 = 3
PAIR_4 = 4
PAIR_5 = 5
PAIR_6 = 6
PAIR_7 = 7
PAIR_8 = 8
PAIR_FLAG = 9
PAIR_SQUARE = 10
PAIR_PRESS = 11
PAIR_MINE = 12
PAIR_EXPLOSION = 13
PAIR_HINT = 14
PAIR_EMOJI = 15
PAIR_COUNTER = 16
PAIR_BORDER = 17
PAIR_SPACE = 18
PAIR_MISTAKE = 19


# noinspection DuplicatedCode
def init_colors() -> None:
    """Define all required colors and color pairs."""
    curses.init_color(COLOR_BGC, *RGB_BGC)
    curses.init_color(COLOR_BGU, *RGB_BGU)
    curses.init_color(COLOR_SQUARE, *RGB_SQUARE)
    curses.init_color(COLOR_1, *RGB_1)
    curses.init_color(COLOR_2, *RGB_2)
    curses.init_color(COLOR_3, *RGB_3)
    curses.init_color(COLOR_4, *RGB_4)
    curses.init_color(COLOR_5, *RGB_5)
    curses.init_color(COLOR_6, *RGB_6)
    curses.init_color(COLOR_7, *RGB_7)
    curses.init_color(COLOR_8, *RGB_8)
    curses.init_color(COLOR_FLAG, *RGB_FLAG)
    curses.init_color(COLOR_MINE, *RGB_MINE)
    curses.init_color(COLOR_EXPLOSION, *RGB_EXPLOSION)
    curses.init_color(COLOR_HINT, *RGB_HINT)
    curses.init_color(COLOR_EMOJI, *RGB_EMOJI)
    curses.init_color(COLOR_COUNTER, *RGB_COUNTER)
    curses.init_color(COLOR_COUNTERBG, *RGB_COUNTERBG)
    curses.init_color(COLOR_BORDER, *RGB_BORDER)
    curses.init_color(COLOR_MISTAKE, *RGB_MISTAKE)

    curses.init_pair(PAIR_1, COLOR_1, COLOR_BGU)
    curses.init_pair(PAIR_2, COLOR_2, COLOR_BGU)
    curses.init_pair(PAIR_3, COLOR_3, COLOR_BGU)
    curses.init_pair(PAIR_4, COLOR_4, COLOR_BGU)
    curses.init_pair(PAIR_5, COLOR_5, COLOR_BGU)
    curses.init_pair(PAIR_6, COLOR_6, COLOR_BGU)
    curses.init_pair(PAIR_7, COLOR_7, COLOR_BGU)
    curses.init_pair(PAIR_8, COLOR_8, COLOR_BGU)
    curses.init_pair(PAIR_FLAG, COLOR_FLAG, COLOR_BGC)
    curses.init_pair(PAIR_SQUARE, COLOR_SQUARE, COLOR_BGC)
    curses.init_pair(PAIR_PRESS, COLOR_SQUARE, COLOR_BGU)
    curses.init_pair(PAIR_MINE, COLOR_MINE, COLOR_BGC)
    curses.init_pair(PAIR_EXPLOSION, COLOR_MINE, COLOR_EXPLOSION)
    curses.init_pair(PAIR_HINT, COLOR_HINT, COLOR_BGU)
    curses.init_pair(PAIR_EMOJI, COLOR_EMOJI, COLOR_BGU)
    curses.init_pair(PAIR_COUNTER, COLOR_COUNTER, COLOR_COUNTERBG)
    curses.init_pair(PAIR_BORDER, COLOR_BORDER, COLOR_BGU)
    curses.init_pair(PAIR_SPACE, COLOR_BGU, COLOR_BGC)
    curses.init_pair(PAIR_MISTAKE, COLOR_MISTAKE, COLOR_BGC)
