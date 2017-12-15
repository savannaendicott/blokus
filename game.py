import sys
import copy
from random import randint
from logging_util import fill_game_log, get_next_game_id, log_board_size
from pieces import get_piece_list
from displays import CLIDisplay, NoDisplay
from players import RandomPlayer, AlphaBetaAI
from board import Board

PLAYER_TYPES = ["AB_0", "AB_1", "AB_2", "AB_3", "R"]
COLOURS = ["RED", "YELLOW", "GREEN", "BLUE"]

class GameEngine(object):
    """Game engine class stores the current game state, logs the game, and controls when to
    get input/draw output
    """

    def __init__(self, dimension, display, players, piece_src_file = "valid_pieces.txt"):
        assert 1 < len(players) <5, "Invalid number of players %d, must be between 1 and 4" % len(players)

        self.display = display
        self.turn_num = 0
        self.game_id = get_next_game_id()

        if dimension != 20:
            log_board_size(self.game_id, dimension)

        self.players = self.configure_players(players, piece_src_file)
        self.board = Board(dimension,len(self.players))

    def _play_turn(self):
        """Play a single round of turns"""
        self.turn_num += 1
        passed = 0

        for p in self.players:
            if p.passed():
                passed += 1
                if passed == len(self.players): self.board.game_over = True
                else: continue

            self.display.draw_board(self.board)

            while True:
                move = p.get_move(self.board, self.players)
                if not move is None :
                    p.play_piece(move.get_piece())

                if move is None:
                    p.pass_turn()
                    break

                try:
                    self.board.add_move(p, move)
                    fill_game_log(move, p, self.game_id)
                    break
                except ValueError as e:
                    print "Error: move is illegal. Try again:"

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
        str = ""
        for p in range(len(self.players)):
            str += "  "+ COLOURS[p]+":"+ self.players[p].get_score().__str__() + "\n"
        return str

    def play_game(self):
        while not self.board.game_over:
            self._play_turn()

        winner = self._get_winner()
        #self.logging_util.end_game_log(winner)
        str = self._get_results()

        return winner , str

    def configure_players(self, configs, src_file):
        plist = get_piece_list(src_file)
        players = []
        for i in range(len(configs)):
            if configs[i] == "R":
                players.append(RandomPlayer(copy.deepcopy(plist), i))
            elif configs[i] == "AB_0":
                players.append(AlphaBetaAI(copy.deepcopy(plist), i, 0))
            elif configs[i] == "AB_1":
                players.append(AlphaBetaAI(copy.deepcopy(plist), i, 1))
            elif configs[i] == "AB_2":
                players.append(AlphaBetaAI(copy.deepcopy(plist), i, 2))
            elif configs[i] == "AB_3":
                players.append(AlphaBetaAI(copy.deepcopy(plist), i, 3))
            else:
                print "Error: invalid input type "+ configs[i]
                sys.exit(1)
        return players

"""
    num_games:      number of games to play 
    player_types:   include all player types that could be used in this game (see options in PLAYER_TYPES above)
    N :             board dimensions (NxN)
   """
def test_bots(num_games = 1000, player_types=["R"], N = 20):
    disp = NoDisplay()
    results = []

    for i in range(num_games):
        players = []
        player_str = ""
        for j in range(4):
            players.append(player_types[randint(0, len(player_types)-1)])
            player_str += players[j] + " "

        print ("Game %d with players: " + player_str) % (i + 1)
        engine = GameEngine(N, disp, players, "valid_pieces.txt")
        result, str = engine.play_game()
        results.append(result)


"""
    player_types:   include all player types that could be used in this game (see options in PLAYER_TYPES above)
    N :             board dimensions (NxN)
"""
def main(player_types=["R"], N = 20):
    disp = CLIDisplay()
    players = []
    player_str = ""
    print len(player_types)
    for j in range(4):
        players.append(player_types[randint(0, len(player_types) - 1)])
        player_str += players[j] + " "
    print ("Players: " + player_str)
    engine = GameEngine(N, disp, players)
    winner, str = engine.play_game()
    print COLOURS[winner] + " won!"
    print "Scores: "
    print str

if __name__ == "__main__":



    # run the following to play game with all random players
    # and display the boards
    #main()

    # run the following to play game with a variety of AI and random players
    # and display the boards
    #main(PLAYER_TYPES)

    # run the following to play 1000 games with random players
    test_bots(1, ["R"], 9)

    # run the following to play 1 game with a variety of AI and random players
    #test_bots(1, PLAYER_TYPES)



