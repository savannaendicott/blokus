import sys
import numpy as np


from displays import CLIDisplay, NoDisplay
from inputs import RandomInput
from pieces import PieceList
from board import Move, Board

class GameEngine(object):
    """Game engine class stores the current game state and controls when to 
    get input/draw output
    """

    board_w = 20
    board_h = 20

    def __init__(self, display, inputs):
        self.display = display
        if not 1 < len(inputs) < 5:
            print "Error: invalid number of players, must be between 1 and 4"
            sys.exit(1)
        self.inputs = inputs
        self.num_players = len(inputs)

        self.piece_list = PieceList("valid_pieces.txt")
        num_pcs = self.piece_list.getNumPieces()

        self.turn_num = 0
        self.passed = [False]* self.num_players
        self.score = [89]*self.num_players
        self.board = Board(self.board_w, self.board_h, self.piece_list)
        self.pieces = [[True for piece in range(num_pcs)] for p in range(self.num_players)]

    def _playTurn(self):
        """Play a single round of turns.

        Check for empty moves from the inputs (signalling passes) and ask for 
        new moves if illegal moves are provided.
        """
        self.turn_num += 1
        #print "Starting turn %d" % self.turn_num

        for p in range(self.num_players):
            if self.passed[p]:
                continue

            #print "Board state:"
            self.display.drawBoard(self.board)

            while True:
                move = self.inputs[p].getMove(p, self.board, self.pieces)
                if move is None:
                    self.passed[p] = True
                    break
                if not self.pieces[p][move.piece]:
                    print "Error: piece has already been used. Try again:"
                    continue
                try:
                    # change this to subtract that amount instead
                    self.score[p] -= self.board.addMove(p, move)
                    self.pieces[p][move.piece] = False
                    break
                except ValueError as e:
                    print "Error: move is illegal. Try again:"

        #print "Ending turn %d" % self.turn_num

    def _allPlayersPassed(self):
        """Return True if all players have passed.
        """
        for p in range(self.num_players):
            if not self.passed[p]:
                return False
        return True

    def _print_scores(self):
        for p in range(self.num_players):
            print "Player %d: %d pts" % (p+1, self.score[p])

    def _print_remaining_pieces(self):
        remainingStr = "\nRemaining Pieces:\n"
        for player in range(self.num_players):
            remainingStr += "\nPlayer %d: "%(player);
            for index in range(len(self.pieces[player])):
                if self.pieces[player][index]:
                    remainingStr += self.piece_list.getPiece(index).getId() + " ";
        print remainingStr

    def playGame(self):
        while not self._allPlayersPassed():
            self._playTurn()
        
        self._print_scores()
        self._print_remaining_pieces()
        # print pieces left for each player?
        return self.score


def test_bots():
    num_games = 20
    num_bots = 4

    disp = NoDisplay()
    inputs = [RandomInput() for p in range(num_bots)]

    results = []
    for i in range(num_games):
        engine = GameEngine(disp, inputs)
        result = engine.playGame()
        results.append(result)

    win_count = [0] * num_bots
    for i in range(num_games):
        winner = np.argmax(results[i])
        print "Game %d:" % i+1
        for j in range(num_bots):
            print "%2d" % results[i][j]
        win_count[winner] += 1
    print "Overall:"
    for i in range(num_bots):
        print "%2d" % win_count[i]

def main():
    num_players = 4;
    disp = CLIDisplay()
    inputs = [RandomInput() for p in range(num_players)]
    engine = GameEngine(disp, inputs)
    engine.playGame()

if __name__ == "__main__":
    main()
    #test_bots()
    
