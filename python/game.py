import curses

ALIVE = 'Alive'
DEAD = 'Dead'


def add_coordinate(a, b):
    return tuple(map(sum, zip(a, b)))


class InvalidMove(Exception):
    def __init__(self, x, y):
        super(InvalidMove, self).__init__('Invalid Move: {x}, {y}'.format(x=x, y=y))


class GameOver(Exception):
    def __init__(self, winner):
        super(GameOver, self).__init__('Winner: {winner}'.format(winner.name))


class Player:
    name = None
    board = None
    color = curses.COLOR_BLUE
    pieces = set()

    def __init__(self, name):
        self.name = name

    def add_piece(self, piece):
        self.pieces |= {piece}

    def move_piece(self, piece, x, y):
        if piece not in self.pieces:
            raise InvalidMove(x, y)

        if (x, y) in piece.valid_moves():
            for p in self.board.pieces:
                if (x, y) == p.position:
                    if isinstance(p, King):
                        raise GameOver(self)
                    p.state = DEAD
                    p.position = None

            piece.has_moved = True
            piece.position = (x, y)
        else:
            raise InvalidMove(x, y)
        self.board.visualize()

    def valid_moves(self):
        moves = self.board.valid_moves()
        for piece in self.pieces:
            moves -= {piece.position}
        return moves

    def setup(self, strategy):
        strategy.setup(self)


class Board:
    size = None
    _valid_moves = None
    players = set()
    pieces = set()

    def __init__(self, size):
        self.size = size

    def valid_moves(self):
        if not self._valid_moves:
            positions = list(range(0, self.size))
            moves = set()
            for x in positions:
                for y in positions:
                    moves |= {(x, y)}
            self._valid_moves = moves

        return self._valid_moves

    def add_piece(self, piece):
        self.pieces |= {piece}

    def add_player(self, player):
        self.players |= {player}
        player.board = self

    def visualize(self, moves=None):
        positions = list(range(0, self.size))
        for y in positions[::-1]:
            row = ' {} |'.format(y)
            for x in positions:
                piece = [p for p in self.pieces if p.position == (x, y)]
                symbol = piece[0].symbol if piece else ' '
                row += '[{}]'.format(symbol) if moves and (x, y) in moves else ' {} '.format(symbol)
            print(row)

        row = '    '
        for x in positions:
            row += '---'
        print(row)

        row = '    '
        for x in positions:
            row += ' {} '.format(x)
        print(row)

    def has_line_of_sight(self, a, b):
        ax, ay = a
        bx, by = b

        if ax == bx and ay == by:
            return True

        positions = set()

        if ay == by:
            for x in list(range(ax, bx, -1 if ax > bx else 1)):
                positions |= {(x, ay)}

        if ax == bx:
            for y in list(range(ay, by, -1 if ay > by else 1)):
                positions |= {(ax, y)}

        if abs(ax - ay) == abs(bx - by) or abs(ax + ay) == abs(bx + by):
            for x in list(range(ax, bx, -1 if ax > bx else 1)):
                for y in list(range(ay, by, -1 if ay > by else 1)):
                    positions |= {(x, y)}

        if not positions:
            return False

        positions -= {a, b}

        for position in positions:
            if position in {piece.position for piece in self.pieces}:
                return False

        return True

    def tiles(self):
        z = list(range(0, self.size))

        colors = set()

        for x in z:
            for y in z:
                colors |= {(x, y, abs(y - x) % 2 == 0)}

        return colors

class Strategy:
    def setup(player):
        return NotImplemented


class TraditionalStrategy(Strategy):
    def setup(player):
        row1 = (Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn, Pawn)
        row2 = (Rook, Knight, Bishop, King, Queen, Bishop, Knight, Rook)

        y1 = 1
        y2 = 0

        if player.board.players - {player}:
            y1 = 6
            y2 = 7

        for x, piece_type in enumerate(row1):
            piece_type(player.board, player, x, y1)

        for x, piece_type in enumerate(row2):
            piece_type(player.board, player, x, y2)


class Piece:
    position = None
    player = None
    state = ALIVE
    has_moved = False

    def __init__(self, board, player, x, y):
        self.board = board
        self.position = (x, y)
        self.player = player

        self.player.add_piece(self)
        self.board.add_piece(self)

    def valid_moves(self):
        return NotImplemented


class Rook(Piece):
    symbol = '♖'

    sprite = """
  _   _
 | |_| |
 |     |
 '-----'
 |     |
/_.---._\\
'._____.'
"""

    def valid_moves(self):
        positions = set()

        for n in list(range(-self.board.size + 1, self.board.size)):
            positions |= {add_coordinate(self.position, (n, 0))}
            positions |= {add_coordinate(self.position, (0, n))}

        positions &= self.board.valid_moves() & self.player.valid_moves()

        for position in valid_positions.copy():
            if not self.board.has_line_of_sight(self.position, position):
                positions -= {position}

        return positions


class Knight(Piece):
    symbol = '♘'

    sprite = """
    \\
    |\.
   /   '.
  /_.'-  \\
     /   |
    /____|
   `.____.'

"""

    def valid_moves(self):
        positions = set()

        for move in [(1, 2), (2, 1)]:
            for j in [-1, 1]:
                for k in [1, -1]:
                    x, y = move
                    positions |= {add_coordinate(self.position, (x * j, y * k))}

        return positions - {self.position}


class King(Piece):
    symbol = '♔'

    sprite = """
      |
     ( )
  .-. ^ .-.
 :   `.'   :
 `.       .'
  )_.---._(
  `._____.'
"""

    def valid_moves(self):
        positions = set()

        moves = [0, -1, 1]
        for x in moves:
            for y in moves:
                positions |= {add_coordinate(self.position, (x, y))}

        return positions - {self.position}


class Bishop(Piece):
    symbol = '♗'

    sprite = """
      .-.
     .' '.
     (   )
     `. .'
      | |
    ._' '_.
    '--^--'
"""

    def valid_moves(self):
        positions = set()
        for x in [-1, 1]:
            for y in [-1, 1]:
                for d in list(range(-self.board.size + 1, self.board.size)):
                    positions |= {add_coordinate(self.position, (x * d, y * d))}

        positions &= self.board.valid_moves() & self.player.valid_moves()

        for position in positions.copy():
            if not self.board.has_line_of_sight(self.position, position):
                positions -= {position}

        return positions


class Pawn(Piece):
    symbol = '♙'

    sprite = """
   .-.
  .' '.
  (   )
   . .'
   | |
 ._' '_.
`._____.'
"""

    def valid_moves(self):
        positions = set()
        positions |= {add_coordinate(self.position, (0, 1))}

        if not self.has_moved:
            positions |= {add_coordinate(self.position, (0, 2))}

        for x in [-1, 1]:
            position = add_coordinate(self.position, (x, 1))
            if position in {piece.position for piece in (self.board.pieces - self.player.pieces)}:
                positions |= {position}

        positions &= self.board.valid_moves() & self.player.valid_moves()
        return positions


class Queen(Piece):
    symbol = '♛'

    sprite = """
    o   o
o   /\ /\  o
\`.'  `  `'/
 \        /
  \_.--._/
  '.____.'
    """

    def valid_moves(self):
        positions = set()

        for n in list(range(-self.board.size + 1, self.board.size)):
            positions |= {add_coordinate(self.position, (n, 0))}
            positions |= {add_coordinate(self.position, (0, n))}

        for x in [-1, 1]:
            for y in [-1, 1]:
                for d in list(range(-self.board.size + 1, self.board.size)):
                    positions |= {add_coordinate(self.position, (x * d, y * d))}

        positions &= self.board.valid_moves() & self.player.valid_moves()

        for position in positions.copy():
            if not self.board.has_line_of_sight(self.position, position):
                positions -= {position}

        return positions


class Renderer:
    stdscr = None
    grid = None

    def __init__(self, stdscr, grid=7):
        import curses

        self.stdscr = stdscr
        self.grid = grid

    def project(self, x, y):
        return self.grid * 8 - y * self.grid, x * self.grid * 2

    def render_piece(self, piece):
        import curses

        y, x = self.project(*piece.position)
        lines = piece.sprite.strip('\n').split('\n')

        for n in list(range(0, self.grid)):
            if n == len(lines):
                break
            line = lines[n].strip('\n').ljust(self.grid, ' ')
            self.stdscr.addstr(y + n, x, line)

    def render_tile(self, tile, piece):
        import curses
        x, y, color = tile

        y0, x0 = self.project(x, y)

        curses.init_pair(
            1,
            piece[0].player.color if piece else curses.COLOR_RED,
            curses.COLOR_BLACK if color == 0 else curses.COLOR_WHITE,
        )

        for yn in list(range(0, self.grid)):
            if piece:

                lines = piece[0].sprite.strip('\n').split('\n')
                if yn == len(lines):
                    break
                line = lines[yn].strip('\n').ljust(self.grid * 2, ' ')
                self.stdscr.addstr(y * self.grid + yn, self.grid * x * 2, line, curses.color_pair(1))

            else:
                y__ = y * self.grid + yn
                x__ = x * self.grid * 2
                self.stdscr.addstr(y__, x__, ' ' * self.grid * 2, curses.color_pair(1))

    def render_board(self, board):
        for tile in board.tiles():
            x, y, color = tile
            piece = [piece for piece in board.pieces if piece.position == (x, y)] or None
            self.render_tile(tile, piece)
