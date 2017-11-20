import logging


class TrainingLog(object):

    def __init__(self):
        self.seen = []
        self.training = logging.getLogger('training')
        self.training.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/training.txt')
        fh.setLevel(logging.DEBUG)
        frmt = logging.Formatter('%(asctime)s : %(message)s')
        fh.setFormatter(frmt)
        if self.training.handlers:
            self.training.handlers = []
        self.training.addHandler(fh)

        self.game_buffer = [[[] for c in range(20)] for r in range(20)]

    def end_game_log(self, won, game_id):
        for x in range(20):
            for y in range(20):
                if not self.game_buffer[x][y] == []:
                    self.game_buffer[x][y].append( 1 if self.game_buffer[x][y][0] == won else 0)
                else:
                    self.game_buffer[x][y].append(-1)
        self.training.debug(str(game_id) + ": "+self.game_buffer.__str__())
        self.game_buffer = [[None] * 20] * 20

    # current properties = tile_value, lib_before, score, lib_after, player_is_nn
    def training_input(self, coords,  move_id, properties):
        if move_id not in self.seen:
            self.seen.append(move_id)
            for p in properties:
                self.game_buffer[coords[0]][coords[1]].append(p)

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

    @staticmethod
    def remove_duplicate_lines(infilename, outfilename):
        lines_seen = set()  # holds lines already seen
        outfile = open(outfilename, "w")
        for line in open(infilename, "r"):
            if line not in lines_seen:  # not a duplicate
                outfile.write(line)
                lines_seen.add(line)
        outfile.close()