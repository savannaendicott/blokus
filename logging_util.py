import logging
import MoveGen

POSSIBLE_MOVES = len(MoveGen.get_all_possible_dimensions())

class TrainingLog(object):

    def __init__(self):
        self.seen = []
        self.game_str = ""
        self.training = logging.getLogger('training')
        self.training.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/ai-training-final.txt')
        fh.setLevel(logging.DEBUG)
        frmt = logging.Formatter('%(message)s')
        fh.setFormatter(frmt)
        if self.training.handlers:
            self.training.handlers = []
        self.training.addHandler(fh)

        self.game_buffer = [[] for c in range(POSSIBLE_MOVES)]

    def end_game_log(self, won, game_id):
        for index in range(POSSIBLE_MOVES):
            if not self.game_buffer[index] == []:
                self.game_buffer[index].append(1 if self.game_buffer[index][0] == won else 0)
            else:
                self.game_buffer[index].append(-1)
        self.training.debug(str(game_id) + ": " + self.game_buffer.__str__())
        self.game_buffer = [[] for c in range(POSSIBLE_MOVES)]

    def training_input(self, move, properties):
        # position = MoveGen.get_index(move.get_configurations_with_piece())
        position = MoveGen.find_move(move)
        if position is not None and position not in self.seen:
            self.seen.append(position)
            properties.append(move.get_piece().get_num_tiles())
            properties.append(move.get_indeces()[0][0])
            properties.append(move.get_indeces()[1][0])
            for p in properties:
                self.game_buffer[position].append(int(p))

    def log_game(self, string):
        with open("gamelogger.txt", 'a') as f:
            f.write(string + "\n")

    def send_game_log(self):
        with open("gamelogger.txt", 'a') as f:
            f.write("\n\n\n\n\n ------------------------\n")

class LoggingUtil:

    @staticmethod
    def get_index(arr, obj):
        for i in range(arr.__len__()):
            if arr[i] == obj:
                return i
        return -1

    @staticmethod
    def get_next_game_id():
        with open('logs/game_index.txt', 'r+') as f:
            value = int(f.read()) + 1
            f.seek(0)
            f.write(str(value))
        return value

    @staticmethod
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
