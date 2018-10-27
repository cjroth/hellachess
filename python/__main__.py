import curses
from curses import wrapper

from game import (
    Board,
    Player,
    Pawn,
    Rook,
    Knight,
    King,
    Bishop,
    Queen,
    Renderer,
    TraditionalStrategy,
)

board = Board(8)

p1 = Player('Chris')
p1.color = curses.COLOR_RED
board.add_player(p1)
p1.setup(TraditionalStrategy)

p2 = Player('Jess')
p2.color = curses.COLOR_BLUE
board.add_player(p2)
p2.setup(TraditionalStrategy)


def main(stdscr):
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    renderer = Renderer(stdscr)
    renderer.render_board(board)

    stdscr.refresh()
    stdscr.getkey()

wrapper(main)
