
from board import Move, Board
import copy
import sys
from pieces import PieceList

colors = ["RED", "YELLOW", "GREEN", "BLUE"]

class Player(object):

    def __init__(self, ps, index):
        self._pieces = ps
        self.id = index
        self._colour = colors[index]
        self._score = 89
        self._passed = False

    def playPiece(self, piece):
        self.removePieceByID(piece.getId())
        #self._pieces.remove(piece)
        self._score -= piece.getNumTiles()

    def removePieceByID(self, id):
        for piece in self._pieces:
            if id == piece.getId():
                self._pieces.remove(piece)
                return

    def getMove(self, board, players):
        raise NotImplementedError("Error: using base input class")


    def getType(self):
        raise NotImplementedError("Error: using base input class")

    def getLegalMoves(self, board, biggestFirst = False):

        # Get a list of unique (x, y) points that might be legal
        # Check for all legal diagonal points and consider all points in a
        # radius-2 box around them

        max_size = 5
        xy_list = []
        for x in range(0, 20):
            for y in range(0, 20):
                if not board.checkTileLegal(self.id, x, y):
                    continue
                if board.checkTileAttached(self.id, x, y):
                    min_x = max(0, x - 2)
                    max_x = min(20, x + 3)
                    min_y = max(0, y - 2)
                    max_y = min(20, y + 3)
                    for xi in range(min_x, max_x):
                        for yi in range(min_y, max_y):
                            xy_list.append((xi, yi))
        xy_list = sorted(set(xy_list))

        print
        # Generate all legal moves
        move_list = []
        for piece in self._pieces:
            if biggestFirst and piece.getNumTiles() < max_size :
                if move_list.__len__ == 0 : max_size -= 1
                else: break
            for (x, y) in xy_list:
                for rot in range(0, 4):
                    for flip in [False, True]:
                        new_move = Move(piece, x, y, rot, flip)
                        if board.checkMoveValid(self, new_move):
                            move_list.append(new_move)
                            # new_move.describe(board.piece_list.getPiece(piece).getId())
        return move_list

    def printPieces(self):
        piecesLeftStr = ""
        for piece in self._pieces:
            piecesLeftStr += piece.getId() + " "
        print self._colour + "'s pieces: " + piecesLeftStr

    def passTurn(self):
        self._passed = True

    def getColor(self):
        return self._colour

    def passed(self):
        return self._passed

    def getScore(self):
        return self._score

    def getId(self):
        return self.id

    def getNumPieces(self):
        return self._pieces.__len__()

class RandomPlayer(Player):
    """RandomInput players choose random moves (equally distributed over piece
    number, x/y, and rotation/flip)
    """
    def getMove(self, board, players, biggest_first=False):
        import random
        move_list = self.getLegalMoves(board, biggest_first)

        self.printPieces()

        # Pass if there are none
        if move_list.__len__() == 0:
            print "No move chosen"
            return None

        # Otherwise, pick a random move
        else:
            n = random.randint(0, len(move_list) - 1)
            move = move_list[n]
            return move_list[n]

    def getType(self):
        return "random player"

class State(object):
        def __init__(self, board, player, move):
            self.board = board
            self.move = move
            self.player = player

class AlphaBetaAI(Player):
    """ strategy is which function will be called as the heuristic, represented as an int
    """

    def __init__(self, ps, index, strategy=0, maxDepth = 5):
        super(AlphaBetaAI, self).__init__(ps, index)

        if(strategy < 0 or strategy > 2):
            print "Error: invalid strategy %d" % strategy
            sys.exit(1)

        self.strategy = strategy
        self.maxDepth = maxDepth
        self.visited = []
        self.players = None

    def setPlayers(self, players):
        self.players = players

    def getMove(self, board, players):
        if self.players == None : self.setPlayers(players)
        self.printPieces()
        value, move = self.alpha_beta(State(board, self, 0),0, -100000, 100000, self)
        if not move == None : self.playPiece(move.getPiece())
        return move

    # takes less than a second
    def expand(self, state, player):
        children = []
        possibleMoves = self.getLegalMoves(state.board, True)
       # print possibleMoves.__len__()
        for move in possibleMoves:
            if state.board.checkMoveValid(player, move):
                board = copy.deepcopy(state.board)
                board.addMove(player, move)
                print move.describe()# print played piece
                self.printPieces()# print players pieces
                child = State(board, player, move)
                if not self.already_visited(child):
                    children.append(child)
        return children

    # AlphaBetaSearch performs the alpha beta pruning
    # on min max algorithm and return the best position
    def alpha_beta(self, state, depth, alpha, beta, player):
        best = None
        children = self.expand(state, player)
        print "depth: %d, %d children nodes" % (depth, children.__len__())

        if children.__len__==0 or state.board.game_over or depth == self.maxDepth:
            return state.move, self.assign_value(state.board)

        if player.getId() == self.getId():
            bestValue = alpha
            for child in children :
                #print child.board.piece_list.getPiece(child.move.getPiece())
                value = self.alpha_beta(child, depth + 1, bestValue, beta, self.nextPlayer(player))
                bestValue = max(bestValue, value)
                best = child.move
                if(beta <= bestValue): break

        else:
            bestValue = beta
            for child in children:
                value = self.alpha_beta(child, depth + 1, alpha, bestValue, self.nextPlayer(player))
                bestValue = min(bestValue, value)
                best = child.move
                if bestValue <= alpha : break

        return beta, best

    def assign_value(self, board):
        if(self.strategy == 0):
            return self.diffRemainingPieceSize()
        elif(self.strategy ==1):
            return self.diffRemainingTiles()
        elif(self.strategy == 2):
            return self.diffRemainingPieceSize() + self.diffRemainingTiles()

    def diffRemainingPieceSize(self):
        total = 0

        # difference between average size of your remaining pieces and average size of their remaining pieces
        average_remaining = []
        for player in self.players:
            average_remaining.append(player.getScore() / self.getNumPieces())

        for i in range(self.players.__len__()):
            if i != self.getId():
                total += average_remaining[self.getId()] - average_remaining[i]

        return total

    def diffRemainingTiles(self):
        total = 0
        for p in self.players:
            if not p == self.player:
                total += p.getScore() - self.getScore()

        return total

    def nextPlayer(self, player):
        if player.getId() == self.players.__len__() - 1:
            return self.players[0]
        else: return self.players[player.getId() + 1]

    def already_visited(self, node):
        for seenNode in self.visited:
            if node.board == seenNode.board:
                return True
        return False

    def getType(self):
        return "AI"
