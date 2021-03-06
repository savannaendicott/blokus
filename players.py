import copy
import sys
import random
from board import Move

colors = ["RED", "YELLOW", "GREEN", "BLUE"]


class State(object):
    def __init__(self, board, player, move):
        self.board = board
        self.move = move
        self.player = player

class Player(object):

    def __init__(self, ps, index):
        self._pieces = ps
        self.id = index
        self._colour = colors[index]
        self._score = 89
        self._passed = False

    def get_move(self, board, players):
        raise NotImplementedError("Error: using base input class")

    def get_type(self):
        raise NotImplementedError("Error: using base input class")

    def pass_turn(self):
        self._passed = True

    def get_color(self):
        return self._colour

    def passed(self):
        return self._passed

    def get_score(self):
        return self._score

    def get_id(self):
        return self.id

    def get_num_pieces(self):
        return self._pieces.__len__()

    def get_biggest_piece_size(self):
        return self._pieces[0].get_num_tiles()

    def get_liberties(self, board):
        num_liberties = 0
        for x in range(0, 20):
            for y in range(0, 20):
                if not board.check_tile_legal(self.id, x, y):
                    continue
                if board.check_tile_attached(self.id, x, y):
                    num_liberties += 1
        return num_liberties

    def get_legal_moves(self, board, biggestFirst = False):

        # Get a list of unique (x, y) points that might be legal
        # Check for all legal diagonal points and consider all points in a
        # radius-2 box around them

        max_size = 5
        xy_list = []
        for x in range(0, board.N):
            for y in range(0, board.N):
                if not board.check_tile_legal(self.id, x, y):
                    continue
                if board.check_tile_attached(self.id, x, y):
                    min_x = max(0, x- 2)
                    max_x = min(board.N, x + 3)
                    min_y = max(0, y - 2)
                    max_y = min(board.N, y + 3)
                    for xi in range(min_x, max_x):
                        for yi in range(min_y, max_y):
                            xy_list.append((xi, yi))
        xy_list = sorted(set(xy_list))

        #analyzed_coords = []
        # Generate all legal moves
        move_list = []
        for piece in self._pieces:
            if biggestFirst and piece.get_num_tiles() < max_size :
                if move_list.__len__ == 0: max_size -= 1
                else: break
            for (x, y) in xy_list:
                for rot in range(0, 4):
                    for flip in [False, True]:
                        new_move = Move(piece, x, y, rot, flip)
                        if board.check_move_valid(self, new_move):
                            if new_move not in move_list:
                                move_list.append(new_move)

        return move_list

    def get_pieces_str(self):
        piecesLeftStr = ""
        for piece in self._pieces:
            piecesLeftStr += piece.get_id() + " "
        return self._colour + "'s pieces: " + piecesLeftStr

    def play_piece(self, piece):
        self.remove_piece_by_id(piece.get_id())
        #self._pieces.remove(piece)
        self._score -= piece.get_num_tiles()

    def remove_piece_by_id(self, id):
        for piece in self._pieces:
            if id == piece.get_id():
                self._pieces.remove(piece)
                return

    def play_move(self, piece_id, x, y, rot, flip):
        move = None
        for piece in self._pieces:
            if piece.get_id == piece_id:
                move = Move(piece,x,y,rot,flip)
        return move

class RandomPlayer(Player):
    """RandomInput players choose random moves (equally distributed over piece
    number, x/y, and rotation/flip)
    """
    def get_move(self, board, players, biggest_first=False):
        move_list = self.get_legal_moves(board, biggest_first)

        if move_list.__len__() == 0:
            return None

        else:
            n = random.randint(0, len(move_list) - 1)
            return move_list[n]

    def get_type(self):
        return "random player"

class AlphaBetaAI(Player):
    """ strategy is which function will be called as the heuristic, represented as an int
    """

    def __init__(self, ps, index, strategy=0, maxDepth = 3):
        super(AlphaBetaAI, self).__init__(ps, index)

        if(strategy < 0 or strategy > 3):
            print "Error: invalid strategy %d" % strategy
            sys.exit(1)

        self.strategy = strategy
        self.turn = 0
        self.maxDepth = maxDepth
        self.visited = []
        self.players = None

    def set_players(self, players):
        self.players = players

    def get_move(self, board, players):
        self.turn +=1
        if self.turn < 3 :
            return self.play_random_big_piece(board)
        if self.players == None : self.set_players(players)
        value, move = self.alpha_beta(State(board, self, None),0, -100000, 100000, self)
        return move

    def expand(self, state, player):
        children = []
        possible_moves = self.get_legal_moves(state.board, False)
        for move in possible_moves:
            if state.board.check_move_valid(player, move):
                board = copy.deepcopy(state.board)
                board.add_move(player, move)
                child = State(board, player, move)
                if not self.already_visited(child):
                    children.append(child)
        return children


    # AlphaBetaSearch performs the alpha beta pruning
    # on min max algorithm and return the best position
    def alpha_beta(self, state, depth, alpha, beta, player):
        best = None
        children = self.expand(state, player)

        if children.__len__==0 or state.board.game_over or depth == self.maxDepth:
            if not state.move == None:
                return self.assign_value(state.board, state.move), state.move

        if player.get_id() == self.get_id():
            bestValue = alpha
            for child in children :
                value = self.alpha_beta(child, depth + 1, bestValue, beta, self.next_player(player))
                bestValue = max(bestValue, value)
                best = child.move
                if(beta <= bestValue): break

        else:
            bestValue = beta
            for child in children:
                value = self.alpha_beta(child, depth + 1, alpha, bestValue, self.next_player(player))
                bestValue = min(bestValue, value)
                best = child.move
                if bestValue <= alpha : break

        return beta, best

    def assign_value(self, board, move):
        if(self.strategy == 0):
            return self.diff_remaining_piece_size()
        elif(self.strategy ==1):
            return self.diff_remaining_tiles()
        elif(self.strategy == 2):
            return self.diff_remaining_piece_size() + self.diff_remaining_tiles() + self.bigger_first(move)
        elif(self.strategy == 4):
            return self.bigger_first(move)*2 + self.diff_remaining_tiles()
        else: return 0

    def diff_remaining_piece_size(self):
        total = 0

        # difference between average size of your remaining pieces and average size of their remaining pieces
        average_remaining = []
        for player in self.players:
            average_remaining.append(player.get_score() / self.get_num_pieces())

        for i in range(self.players.__len__()):
            if i != self.get_id():
                total += average_remaining[self.get_id()] - average_remaining[i]

        return total

    def play_random_big_piece(self,board):
        moves = self.get_legal_moves(board, True)
        if moves.__len__() == 0:
            return None

        else:
            n = random.randint(0, len(moves) - 1)
            return moves[n]

    def bigger_first(self, move):
        return move.piece.get_num_tiles()

    def diff_remaining_tiles(self):
        total = 0
        for p in self.players:
            if not p.get_id() == self.get_id():
                total += p.get_score() - self.get_score()

        return total

    def next_player(self, player):
        if player.get_id() == self.players.__len__() - 1:
            return self.players[0]
        else: return self.players[player.get_id() + 1]

    def already_visited(self, node):
        for seenNode in self.visited:
            if node.board == seenNode.board:
                return True
        return False

    def get_type(self):
        return "AI-"+ str(self.strategy)
