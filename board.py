from pieces import get_piece_index, Piece, get_piece_by_index

class Move(object):
    """A Move describes how one of the players is going to spend their move.

    It contains:
    - Piece: the ID of the piece being used
    - x/y: the center coordinates of the piece [0-19)
    - Rotation: how many times the piece should be rotated CW [0-3]
    - Flip: whether the piece should be flipped (True/False)
    """
    def __init__(self, piece, x=0, y=0, rot=0, flip=False):
        if isinstance(piece,Piece):
            self.piece = piece
        else: self.piece = get_piece_by_index(piece)


        self.x = x
        self.y = y
        self.rot = rot
        self.flip = flip
        self.xlist, self.ylist = self._compute_indeces()

    def get_piece(self):
        return self.piece

    def describe(self):
        flipStr = "flipped" if self.flip else ""
        return "Piece "+ self.piece.get_id() + " " + flipStr+" with center coordinate (%d, %d), " \
             "rotation %d\n" % (self.x, self.y, self.rot)

    def get_indeces(self):
        return [self.xlist, self.ylist]

    def get(self):
        f = 1 if self.flip else 0
        return [get_piece_index(self.piece.get_id()), self.x, self.y, self.rot, f]

    def raw(self):
         return self.piece.get_id() +", %d, %d, %d, %d" %(self.x,self.y,self.rot, self.flip)

    def get_tiles(self):
        coords = []
        for t in range(self.piece.get_num_tiles()):
            temp = []
            (x, y) = self.piece.get_tile(t, self.x, self.y, self.rot, self.flip)
            temp.append(x)
            temp.append(y)
            coords.append(temp)
        return coords

    def get_configurations(self):
        flip = 1 if self.flip else 0
        return self.piece.get_id(), self.x, self.y, self.rot, flip

    def get_configurations_with_piece(self):
        flip = 1 if self.flip else 0
        return self.x, self.y, self.piece, self.rot, flip

    def _compute_indeces(self):
        idx = int(self.rot)
        if self.flip:
            idx += 4

        x_list = []
        y_list = []

        for index in range(len(self.piece.x[idx])):
            x =self.piece.x[idx][index]
            y = self.piece.y[idx][index]
            offset_x = x + int(self.x)
            offset_y = y + int(self.y)
            x_list.append(offset_x)
            y_list.append(offset_y)
        return x_list, y_list

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

    def __init__(self, dimension = 20, num_p=4):

        self.game_over = False
        self.N = dimension

        self._state = [[-1 for c in range(dimension)] for r in range(dimension)]

        self._connected = [
            [
                [False for c in range(dimension)
            ] for r in range(dimension)]
        for p in range(4)]

        # Set up initial corners for each player now
        self._connected[0][0             ][self.N-1] = True
        self._connected[1][0             ][             0] = True
        self._connected[2][self.N-1][             0] = True
        self._connected[3][self.N-1][self.N-1] = True

    def test_move(self, p , m):

        #assert len(m) == 5
        #assert len(move[0]) == len(move[1])
        move = m.get_indeces()
        print move
        tiles = []
        for i in range(len(move[0])):
            tiles.append([move[0][i], move[1][i]])

        for tile in tiles:
            self._state[tile[0]][tile[1]] = p

        #print "done"

    def clear_board(self):
        self._state = [[-1 for c in range(self.N)] for r in range(self.N)]


    def add_move(self, p, move):
        if isinstance(p, int):
            player = p
        else: player = p.get_id()

        if not self.check_move_valid(player, move):
            raise ValueError("Move is not allowed")

        piece = move.get_piece()

        # Update internal state for each tile
        for t in range(move.get_piece().get_num_tiles()):
            (x,y) = piece.get_tile(t, move.x, move.y, move.rot, move.flip)
            self._state[y][x] = player

            # The diagonals are now attached
            if x > 0 and y > 0:
                self._connected[player][y-1][x-1] = True
            if x > 0 and y < self.N-1:
                self._connected[player][y+1][x-1] = True
            if x < self.N-1 and y < self.N-1:
                self._connected[player][y+1][x+1] = True
            if x < self.N-1 and y > 0:
                self._connected[player][y-1][x+1] = True

        return piece.get_num_tiles()

    def check_move_valid(self, player, move):
        if isinstance(player, int):
            player = player
        else: player = player.get_id()
        attached_corner = False

        for t in range(move.get_piece().get_num_tiles()):
            (x,y) = move.get_piece().get_tile(t, move.x, move.y, move.rot, move.flip)

            # If any tile is illegal, this move isn't valid
            if not self.check_tile_legal(player, x, y):
                return False

            if self._connected[player][y][x]:
                attached_corner = True

            # If at least one tile is attached, this move is valid
        return attached_corner

    def check_tile_attached(self, player, x, y):
        if x < 0 or x >= self.N or y < 0 or y >= self.N:
            return False

        return self._connected[player][y][x]


    def check_tile_legal(self, player, x, y):
        """Check if it's legal for <player> to place one tile at (<x>, <y>).
        """

        # Make sure tile in bounds
        if x < 0 or x >= self.N or y < 0 or y >= self.N:
            return False

        if not self._state[y][x] == -1 :
            return False

        return self.adjacent_to_self(player, x, y)

    def adjacent_to_self(self, player, x, y):
        if y > 0 and self._state[y-1][x] == player: return False
        if y < self.N -1 and self._state[y+1][x] == player: return False
        if x > 0 and self._state[y][x-1] == player: return False
        if x < self.N -1 and self._state[y][x+1] == player: return False
        return True

    def get_state_at_point(self, x, y):
        return self._state[y][x]

    def get_state(self):
        return self._state

    def __eq__(self, other):
        """Override the default Equals behavior"""
        for w in range(self.N):
            for h in range(self.N):
                if not other.get_state_at_point(w,h) == self.N(w,h):
                    return False
        return True

    def legal(self,move):
        arr = move.get_indeces()
        xlist = arr[0]
        ylist = arr[1]
        assert (len(xlist) == len(ylist))

        for index in range(len(xlist)):
            x = xlist[index]
            y = ylist[index]
            if x < 0 or x >= self.board_w or y < 0 or y >= self.board.h:
                return False
        return True

    def is_legal(self, x, y, player):
        if not self.check_tile_legal(player, x, y):
            return False

        if self._connected[player.get_id()][y][x]:
            return True

        return False

    def is_corner_available(self, player, x, y):
        # for each state in the board
        corners = 0

        assert x < self.N and y < self.N

        if self._state[x][y] != 1:
            if not self._connected[player][x][y]:
                if not self.adjacent_to_self(player, x, y):
                    return True
        return False


def test_find_all_moves():
    import pieces
    plist = pieces.get_piece_list("valid_pieces.txt")

    total = 0
    for piece in plist:
        print piece.get_id()
        print len(piece.get_unique_indices())
        total += len(piece.get_unique_indices())
        #for indeces in piece.get_unique_indices():
            #print indeces
    print total