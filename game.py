import sys
import numpy as np


from displays import CLIDisplay, NoDisplay
from players import RandomPlayer, AlphaBetaAI
from pieces import Piece
from board import Move, Board
import time
import copy

class GameEngine(object):
    """Game engine class stores the current game state and controls when to 
    get input/draw output
    """

    board_w = 20
    board_h = 20

    def __init__(self, display, players):
        self.display = display
        if not 1 < players.__len__() < 5:
            print "Error: invalid number of players %d, must be between 1 and 4" % players.__len__()
            sys.exit(1)

        player_config = players
        piece_list = self.getPieceList("valid_pieces.txt")

        self.turn_num = 0
        self.board = Board(self.board_w, self.board_h, player_config.__len__)

        self.players = []
        for i in range(0, player_config.__len__()):
            if (player_config[i] == "R"):
                self.players.append(RandomPlayer(copy.deepcopy(piece_list), i))
            elif (player_config[i] == "AB_0"):
                self.players.append(AlphaBetaAI(copy.deepcopy(piece_list), i))
           # elif (player_config[i] == "AB_1"):
                #self.inputs.append(AlphaBetaAI(i, self.pieces, 1))
           # elif (player_config[i] == "AB_2"):
             #   self.inputs.append(AlphaBetaAI(i, self.pieces, 2))
            else:
                print "Error: invalid input type "+ player_config
                sys.exit(1)

    def _playTurn(self):
        """Play a single round of turns.
        Check for empty moves from the inputs (signalling passes) and ask for 
        new moves if illegal moves are provided.
        """
        self.turn_num += 1
        passed = 0

        for p in self.players:
            if p.passed():
                passed += 1
                if passed == self.players.__len__() : self.board.game_over = True
                else : continue

            self.display.drawBoard(self.board)

            while True:
                startTime = int(round(time.time() * 1000))
                print p.getColor()+"'s turn "
                move = p.getMove(self.board, self.players)
                p.playPiece(move.getPiece())
                #print "Done in %d ms" % (int(round(time.time() * 1000)) - startTime)
                if move is None:
                    print p.getColor() + " passed"
                    p.passTurn()
                    break

                print "Move: "+ move.describe()
                try:
                    self.board.addMove(p, move)
                    break
                except ValueError as e:
                    print "Error: move is illegal. Try again:"

    def _print_results(self):
        min = 1000
        winner = None
        for p in self.players:
            if (p.getScore() < min):
                winner = p
                min = p.getScore()

        print winner.getColor() + "(" +winner.getType() +"): is the winner!"
        for p in self.players:
            print p.getColor() + "(" +p.getType() +"): %d pts" % p.getScore()
            p.printPieces()

    def playGame(self):
        while not self.board.game_over:
            self._playTurn()
        
        self._print_results()

        scores = []
        for p in self.players:
            scores.append(p.getScore())
        return scores

# def test_bots():
#     num_games = 20
#     num_bots = 4
#
#     disp = NoDisplay()
#     #inputs = [RandomInput(p) for p in range(num_bots)]
#
#     results = []
#     for i in range(num_games):
#         engine = GameEngine(disp, inputs)
#         result = engine.playGame()
#         results.append(result)
#
#     win_count = [0] * num_bots
#     for i in range(num_games):
#         winner = np.argmax(results[i])
#         print "Game %d:" % i+1
#         for j in range(num_bots):
#             print "%2d" % results[i][j]
#         win_count[winner] += 1
#     print "Overall:"
#     for i in range(num_bots):
#         print "%2d" % win_count[i]

    def getPieceList(self,fname):
        """Read the game pieces from the file <fname>

        << Edit by Savanna Endicott >>
        File format must be:
        - Line 1: N (number of pieces)
        - For k in [0, N):
          - Line 1: piece id
          - Line 2: L (number of lines in piece)
          - Lines 3 - L+1: layout of piece (# means tile, O means center)

        File format must be:
        - Line 1: N (number of pieces)
        - For k in [0, N):
          - Line 1: L (number of lines in piece)
          - Lines 2 - L+1: layout of piece (# means tile, O means center)

        Sample file:
        2
        2
        O#
        ##
        1
        ##O##
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

def main():
    disp = CLIDisplay()
    players = ["AB_0", "R", "R", "R"]
    engine = GameEngine(disp, players)
    engine.playGame()

if __name__ == "__main__":
    main()
    #test_bots()
    
