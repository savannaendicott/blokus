"""Classes and utilities to describe all of the game pieces.
"""

piece_names = ["line5","-L","L5tall","z5","chunky5","T5","C5","L5","M5","X5","tree5","Z5","l4","cube","L4","z4","t4","line3","3corner","twoPiece","singleSquare","X5"]
def negateList(lst):
    """Helper function: negate every item in a list
    """
    return [-x for x in lst]

class Piece(object):
    """A piece is a collection of tiles with various (x,y) offsets.

    Variables:
    - x: Lists of x coordinates of the piece
    - y: Lists of y coordinates of the piece
    - img : picture! png format
    - id : used for visual representation in logs

    x and y each have 8 elements, which are:
    x/y[0]: Initial orientation
    x/y[1]: Rotated CW once
    x/y[2]: Rotated CW twice
    x/y[3]: Rotated CW three times
    x/y[k+4]: x/y[k] flipped horizontally
    """

    def __init__(self, x_list, y_list, pid):
        if len(x_list) != len(y_list):
            raise ValueError(
                "Length of x and y lists are unequal (%d and %d)" % \
                (len(x_list), len(y_list)))
        if len(x_list) == 0:
            raise ValueError("No tiles provided!")
        if len(x_list) > 5:
            raise ValueError("%d tiles provided; maximum 5" % len(x_list))

        # Calculate flipped lists
        x_list_flipped = negateList(x_list)
        y_list_flipped = negateList(y_list)

        # Set up data structure
        self.x = []
        self.y = []
        self.pieceId = pid

        # Position 0: default
        self.x.append(x_list)
        self.y.append(y_list)

        # Position 1: rotated x1
        self.x.append(y_list)
        self.y.append(x_list_flipped)

        # Position 2: rotated x2
        self.x.append(x_list_flipped)
        self.y.append(y_list_flipped)

        # Position 3: rotated x3
        self.x.append(y_list_flipped)
        self.y.append(x_list)

        # Positions 4-7: flipped copies
        for i in range(4):
            self.x.append(negateList(self.x[i]))
            self.y.append(self.y[i])

        #print self.x

    def get_indeces(self):
        return self.x[0], self.y[0]

    def get_num_tiles(self):
        """Return the number of tiles in this block. Helpful for iterating 
        through each tile.
        """
        return len(self.x[0])

    def get_id(self):
        """Return string representing id
        """
        return self.pieceId

    def get_unique_indices(self):
        unique_states = []
        for r in range(4):

            tiles = []
            state = self.get_states(r, False)
            for i in range(len(state[0])):
                tiles.append([state[0][i], state[1][i]])
            if not self.pair_in_pairs(tiles, unique_states):
                unique_states.append(tiles)

            tiles = []
            state = self.get_states(r, True)
            for i in range(len(state[0])):
                tiles.append([state[0][i], state[1][i]])
            if not self.pair_in_pairs(tiles, unique_states):
                unique_states.append(tiles)
        return unique_states

    def pair_in_pairs(self, tiles, sets_of_tiles):
        if sets_of_tiles == []: return False
        for set in sets_of_tiles:
            num_found = 0
            for tile in set:
                if tile in tiles:
                    num_found += 1
            if num_found == len(set): return True
        return False
    def get_tile(self, tile, x_offset=0, y_offset=0, rot=0, flip=False):
        """Return the (x,y) position of the <tile>th tile in this piece.

        x_offset, y_offset, rot, and flip are provided to help easily calculate 
        positions on the game board.
        """

        # Find the correct rotation/flip in the list
        idx = rot
        if flip:
            idx += 4

        x = self.x[idx]
        y = self.y[idx]

        # Add offsets
        return (x[tile] + x_offset, y[tile] + y_offset)

    def get_states(self, rotation, flip):
        index = rotation
        if flip: index +=4

        return self.x[index], self.y[index]

def get_piece_list(fname):
        """Read the game pieces from the file <fname>
        File format must be:
        - Line 1: N (number of pieces)
        - For k in [0, N):
          - Line 1: piece id
          - Line 2: L (number of lines in piece)
          - Lines 3 - L+1: layout of piece (# means tile, O means center)
        """

        pieces = []
        with open(fname) as f:
            lines = f.read().splitlines()

        N = int(lines[0])
        L = 1
        for i in range(N):
            x_origin = 0
            y_origin = 0

            x_list = []
            y_list = []

            pieceId = lines[L]
            num_lines = int(lines[L+1])
            for j in range(num_lines):
                line = lines[L + 2 + j]
                for k in range(len(line)):
                    if line[k] in ('O', 'o', '0'):
                        x_origin = k
                        y_origin = j
                    if line[k] is not ' ':
                        x_list.append(k)
                        y_list.append(j)

            x_list = [x - x_origin for x in x_list]
            y_list = [y - y_origin for y in y_list]
            pieces.append(Piece(x_list, y_list, pieceId))

            L += 2 + num_lines

        return pieces


def get_piece_index(name):
    for i in range(len(piece_names)):
        if piece_names[i] == name:
            return i

def get_piece_by_index(index):
    p_list = get_piece_list("valid_pieces.txt")
    return p_list[index]

def get_piece_by_id(self,id):
    p_list = get_piece_list("valid_pieces.txt")
    for piece in p_list:
        if piece.get_id() == id:
            return piece
    return None

def test_num_unique_positions():
    piecelist = get_piece_list("valid_pieces_less.txt")
    print "total pieces : %d" % len(piecelist)
    total_unique = 0
    for piece in piecelist:
        unique = []
        for rotation in range(4):
            pos = piece.get_states(rotation, True)
            if piece not in unique:
                unique.append(pos)
            pos = piece.get_states(rotation, False)
            if piece not in unique:
                unique.append(pos)
        total_unique += len(unique)
    print "total unique shapes: %d" % total_unique


if __name__ == "__main__":
    test_num_unique_positions()