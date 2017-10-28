from pieces import PieceList
import numpy

class Move(object):
    """A Move describes how one of the players is going to spend their move.

    It contains:
    - Piece: the ID of the piece being used
    - x/y: the center coordinates of the piece [0-19)
    - Rotation: how many times the piece should be rotated CW [0-3]
    - Flip: whether the piece should be flipped (True/False)
    """
    def __init__(self, piece, x=0, y=0, rot=0, flip=False):
        self.piece = piece
        self.x = x
        self.y = y
        self.rot = rot
        self.flip = flip

    def get_piece(self):
        return self.piece

    def describe(self):
        flipStr = "flipped" if self.flip else ""
        return "Piece "+ self.piece.getId() + " " + flipStr+" with center coordinate (%d, %d), " \
             "rotation %d\n" % (self.x, self.y, self.rot)

class Board(object):
    """A Board describes the current state of the game board. It's separate from
    the game engine to allow the Input objects to check if their moves are valid,
    etc... without the help of the game engine.

    The Board stores:
    - board_w/board_h: the width and height of the playing area
    - _state: a 2D array of the board state. -1 = free; 0-3 = player x's tile
    - _legal: a 4 x 2D array. _legal[player][y][x] is True iff (x,y) is not
      on another player's piece or adjacent to a player's own piece
    - _connected: a 4 x 2D array. _connected[player][y][x] is True iff (x,y) is 
      diagonally connected to another one of the player's tiles
    - piece_list: A PieceList object (probably shared with the game engine) to
      help understand the moves
    """

    def __init__(self, board_w, board_h, num_p):
        self.board_w = board_w
        self.board_h = board_h
        self.game_over = False

        self._state = [[-1 for c in range(board_w)] for r in range(board_h)]

        self._connected = [
            [
                [False for c in range(board_w)
            ] for r in range(board_h)]
        for p in range(4)]

        # Set up initial corners for each player now
        self._connected[0][0             ][self.board_w-1] = True
        self._connected[1][0             ][             0] = True
        self._connected[2][self.board_h-1][             0] = True
        self._connected[3][self.board_h-1][self.board_h-1] = True

    def add_move(self, p, move):
        if not self.check_move_valid(p, move):
            raise ValueError("Move is not allowed")

        player = p.getId()
        piece = move.get_piece()

        # Update internal state for each tile
        for t in range(move.get_piece().getNumTiles()):
            (x,y) = piece.getTile(t, move.x, move.y, move.rot, move.flip)
            self._state[y][x] = player

            # The diagonals are now attached
            if x > 0 and y > 0:
                self._connected[player][y-1][x-1] = True
            if x > 0 and y < self.board_h-1:
                self._connected[player][y+1][x-1] = True
            if x < self.board_w-1 and y < self.board_h-1:
                self._connected[player][y+1][x+1] = True
            if x < self.board_w-1 and y > 0:
                self._connected[player][y-1][x+1] = True

        return piece.getNumTiles()

    def check_move_valid(self, player, move):
        attached_corner = False

        for t in range(move.get_piece().getNumTiles()):
            (x,y) = move.get_piece().getTile(t, move.x, move.y, move.rot, move.flip)

            # If any tile is illegal, this move isn't valid
            if not self.check_tile_legal(player.getId(), x, y):
                return False

            if self._connected[player.getId()][y][x]:
                attached_corner = True

            # If at least one tile is attached, this move is valid
        return attached_corner

    def check_tile_attached(self, player, x, y):
        """Check if (<x>, <y>) is diagonally attached to <player>'s moves.

        Note that this does not check if this move is legal.

        Returns True if attached or False if not.
        """

        # Make sure tile in bounds
        if x < 0 or x >= self.board_w or y < 0 or y >= self.board_h:
            return False

        # Otherwise, it's in the lookup table
        return self._connected[player][y][x]


    def check_tile_legal(self, player, x, y):
        """Check if it's legal for <player> to place one tile at (<x>, <y>).
        """

        # Make sure tile in bounds
        if x < 0 or x >= self.board_w or y < 0 or y >= self.board_h:
            return False

        if not self._state[y][x] == -1 :
            return False

        if y > 0 and self._state[y-1][x] == player: return False
        if y < self.board_h -1 and self._state[y+1][x] == player: return False
        if x > 0 and self._state[y][x-1] == player: return False
        if x < self.board_w -1 and self._state[y][x+1] == player: return False
        return True

    def get_state(self, x, y):
        return self._state[y][x]

    def __eq__(self, other):
        """Override the default Equals behavior"""
        for w in range(self.board_w):
            for h in range(self.board_h):
                if not other.get_state(w,h) == self.getState(w,h):
                    return False
        return True

    def print_state(self):
        for i in range(self.board_h):
            str = ""
            for j in range(self.board_w):
                str+= "[%d]" % self._state[j][i]
            print str

# class GameState(Object):
#     def __init__(self, board, players):
#         self.players = players
#         self.board = board

