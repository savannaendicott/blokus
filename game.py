import sys
import time
import copy
from random import randint
from logging_util import TrainingLog, LoggingUtil, GameWinnerLog
from pieces import PieceList, Piece
from displays import CLIDisplay, NoDisplay
from players import RandomPlayer, AlphaBetaAI
from board import Move, Board


class GameEngine(object):
    """Game engine class stores the current game state and controls when to 
    get input/draw output
    """

    board_w = 20
    board_h = 20

    def __init__(self, id, display, players):
        self.game_id = id

        self.logging_util = TrainingLog()

        self.display = display
        self._moves = [[]for p in range(players.__len__())]
        self._states = []
        if not 1 < players.__len__() < 5:
            print "Error: invalid number of players %d, must be between 1 and 4" % players.__len__()
            sys.exit(1)

        player_config = players
        piece_list = PieceList.get_piece_list("valid_pieces.txt")

        self.turn_num = 0
        self.board = Board(self.board_w, self.board_h, player_config.__len__)

        self.players = []
        for i in range(0, player_config.__len__()):
            if (player_config[i] == "R"):
                self.players.append(RandomPlayer(copy.deepcopy(piece_list), i))
            elif (player_config[i] == "AB_0"):
                self.players.append(AlphaBetaAI(copy.deepcopy(piece_list), i, 0))
            elif (player_config[i] == "AB_1"):
                self.players.append(AlphaBetaAI(copy.deepcopy(piece_list), i, 1))
            elif (player_config[i] == "AB_2"):
                self.players.append(AlphaBetaAI(copy.deepcopy(piece_list), i, 2))
            elif (player_config[i] == "AB_3"):
                self.players.append(AlphaBetaAI(copy.deepcopy(piece_list), i, 3))
            else:
                print "Error: invalid input type "+ player_config
                sys.exit(1)

    def _play_turn(self):
        """Play a single round of turns.
        Check for empty moves from the inputs (signalling passes) and ask for 
        new moves if illegal moves are provided.
        """
        self.turn_num += 1
        passed = 0

        #print "turn %d" % self.turn_num
        for p in self.players:
            if p.passed():
                passed += 1
                if passed == self.players.__len__() : self.board.game_over = True
                else : continue

            self.display.draw_board(self.board)

            while True:
                startTime = int(round(time.time() * 1000))
                move = p.get_move(self.board, self.players)
                if not move is None : p.play_piece(move.get_piece())

                if move is None:
                    p.pass_turn()
                    break

                try:
                    liberties_before = p.get_liberties(self.board)
                    self.board.add_move(p, move)
                    move_id = LoggingUtil.get_next_move_id()
                    self.logging_util.log_verbose(self.game_id, p.get_id(), self.board.get_state(), move, move_id)
                    self.logging_util.export(self.game_id, p.get_id(), liberties_before, p.get_score(),
                                             p.get_liberties(self.board), move, move_id)
                    break
                except ValueError as e:
                    print "Error: move is illegal. Try again:"

        self._states.append(self.board.get_state())

    def _get_winner(self):
        min = 1000
        winner = -1
        index = 0
        for p in self.players:
            if (p.get_score() < min):
                winner = index
                min = p.get_score()
            index += 1

        return winner

    def _get_results(self):
        scores = []
        for p in self.players:
            scores.append(p.get_score())
        return scores.__str__() +"\n"

    # def print_moves(self):
    #     str = ""
    #     for player in self.players:
    #         str += "\n" + player.get_color()+"'s moves:\n----------------\n"
    #         for move in self._moves[player.get_id()]:
    #             str += move + "\n"
    #     return str



    # def print_game(self):
    #     str = ""
    #     for state in self._states:
    #         str += state.__str__() +"\n"
    #     return str

    def play_game(self):
        while not self.board.game_over:
            self._play_turn()

        str = self._get_results() # + self.print_game()

        return self._get_winner() , str

def get_index(arr, obj):
    for i in range(arr.__len__()):
        if str(arr[i]) == str(obj):
            return i
    return -1

def test_bots(num_games):
    player_types = ["AB_0", "AB_1", "AB_2", "AB_3", "R"]
    disp = NoDisplay()
    results = []
    logger = GameWinnerLog()

    for i in range(num_games):
        game_id = LoggingUtil.get_next_game_id()
        players = []
        player_str = ""
        for j in range(4):
            players.append(player_types[randint(0, 4)])
            player_str += players[j] + " "

        print ("Game %d with players: " + player_str) % (i + 1)
        engine = GameEngine(game_id, disp, players)
        result, str = engine.play_game()
        logger.log(game_id,result)
        results.append(result)

    LoggingUtil.csv_util()

def main():
    disp = CLIDisplay()
    players = ["AB_0", "AB_1", "AB_2", "AB_3"]
    engine = GameEngine(LoggingUtil.get_next_game_id(), disp, players)
    engine.play_game()


if __name__ == "__main__":
    test_bots(30)

    #main()

