import logging
import os
from datetime import date


def fill_game_log(move, p, game_id):
    dir_name = "logs/"+date.today().__str__()[5:]
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(dir_name +"/"+str(game_id)+".txt", 'a') as f:
        f.write(str(p.get_id())+": " +  move.get().__str__() + "\n")

def log_board_size(game_id, N):
    assert isinstance(N, int)
    dir_name = "logs/" + date.today().__str__()[5:]
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(dir_name + "/" + str(game_id) + ".txt", 'a') as f:
        f.write(str(N) + "\n")

class TrainingLog(object):

    def __init__(self):
        self.seen = []
        self.game_str = ""
        self.training = logging.getLogger('training')
        self.training.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/input-features-and-moves.txt')
        fh.setLevel(logging.DEBUG)
        frmt = logging.Formatter('%(message)s')
        fh.setFormatter(frmt)
        if self.training.handlers:
            self.training.handlers = []
        self.training.addHandler(fh)

        self.game_buffer = []

    def end_game_log(self, won):
        game_id = get_next_game_id()
        game_str = ""
        for move in self.game_buffer:
            game_str += move.__str__()

        self.training.debug(str(game_id) + ";"+str(won) + ";"+ game_str)
        self.game_buffer = []

    def training_input(self, board, move):
        board_str = board.get_state()
        move_str = move.get()
        properties = [move_str, board_str]
        self.game_buffer.append(properties)

    def log_move(self, move):
        with open("moves-random.txt", 'a') as f:
            f.write(move.get().__str__() + "\n")


    def log_game(self, string):
        with open("gamelogger.txt", 'a') as f:
            f.write(string + "\n")

    def send_game_log(self):
        with open("gamelogger.txt", 'a') as f:
            f.write("\n\n\n\n\n ------------------------\n")

def get_next_game_id():
        with open('logs/game_index.txt', 'r+') as f:
            value = int(f.read()) + 1
            f.seek(0)
            f.write(str(value))
        return value

def get_next_move_id():
        with open('logs/move_index.txt', 'r+') as f:
            value = int(f.read()) + 1
            f.seek(0)
            f.write(str(value))
        return value

def remove_duplicate_lines(infilename, outfilename):
        lines_seen = set()  # holds lines already seen
        outfile = open(outfilename, "w")
        for line in open(infilename, "r"):
            if line not in lines_seen:  # not a duplicate
                outfile.write(line)
                lines_seen.add(line)
        outfile.close()

def get_num_lines_in_file(filename):
    counter = 0
    with open(filename, 'r') as f:
        for line in f:
            counter +=1
    return counter



