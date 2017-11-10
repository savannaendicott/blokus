import sys
import numpy as np


from displays import CLIDisplay, NoDisplay
from players import RandomPlayer, AlphaBetaAI
from pieces import Piece
from board import Move, Board
from random import randint
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
        self._moves = [[]for p in range(players.__len__())]
        if not 1 < players.__len__() < 5:
            print "Error: invalid number of players %d, must be between 1 and 4" % players.__len__()
            sys.exit(1)

        player_config = players
        piece_list = self.get_piece_list("valid_pieces.txt")

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
                #print p.get_color()+"'s turn "
                move = p.get_move(self.board, self.players)
                if not move is None : p.play_piece(move.get_piece())
                #print "Done in %d ms" % (int(round(time.time() * 1000)) - startTime)
                if move is None:
                   # print p.get_color() + " passed"
                    p.pass_turn()
                    break

                #print "Move: "+ move.describe()
                try:
                    self.board.add_move(p, move)
                    #print move.raw()
                    self._moves[p.get_id()].append(move.raw())
                    break
                except ValueError as e:
                    print "Error: move is illegal. Try again:"
    def _print_results(self):
        print self._get_winner().get_color() +" is the winner!"
        print self._get_results()

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
        for p in self.players:
            str+= "\n"+p.get_color() + "(" + p.get_type() + "): %d pts" % p.get_score()+" with remaining pieces:\n"
            str += "   " +p.get_pieces_str()+"\n"
        return str

    def print_moves(self):
        str = ""
        for player in self.players:
            str += "\n" + player.get_color()+"'s moves:\n----------------\n"
            for move in self._moves[player.get_id()]:
                str += move + "\n"
        return str

    def play_game(self):
        while not self.board.game_over:
            self._play_turn()

        str = self._get_results() + self.print_moves()

        return self._get_winner() , str

    def get_piece_list(self,fname):
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

def test_bots():
    file_name = "logs/log-"+time.strftime("%d%m%Y")+".txt"
    file_object = open(file_name, "a")
    num_games = 50
    player_types = ["AB_0", "AB_1", "AB_2", "AB_3", "R"]
    win_count = [0] * 5
    played_games = [0] * 5

    disp = NoDisplay()

    file_object.write(time.strftime("%c")+"\n")

    results = []
    for i in range(num_games):
        print
        players = []
        player_str = ""
        for j in range(4):
            players.append(player_types[randint(0, 4)])
            player_str += players[j]+" "

        print "Game %d with players: " + players % i
        for str in players:
            played_games[getIndex(str, player_types)] += 1
        file_object.write("New Game with players "+ player_str)
        engine = GameEngine(disp, players)
        startTime = int(round(time.time() * 1000))
        result, str = engine.play_game()
        win_count[getIndex(players[result], player_types)] +=1

        file_object.write("\nDone in %d ms" % (int(round(time.time() * 1000)) - startTime))
        results.append(result)
        file_object.write(str+"\n\n")

    file_object.write("\n\n-----------------\nOVERALL:")
    for i in range(player_types.__len__()):
        if played_games[i] == 0: percent = 0
        else: percent = win_count[i] / played_games[i]
        file_object.write(player_types[i] + ": %2d wins / %2d games played = %.2f \n" % (win_count[i], played_games[i], percent))

    file_object.close()

def getIndex(str, array):
    for i in range(array.__len__()):
        if array[i] == str:
            return i

def main():
    disp = CLIDisplay()
    players = ["AB_0", "AB_1", "AB_2", "AB_3"]
    engine = GameEngine(disp, players)
    engine.play_game()

if __name__ == "__main__":
    test_bots()
    #main()

    
