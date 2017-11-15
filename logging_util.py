import logging


class TrainingLog(object):

    def __init__(self):
        self.training_verbose = logging.getLogger('training-verbose')
        self.training_verbose.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/training-verbose.txt')
        fh.setLevel(logging.DEBUG)
        frmt = logging.Formatter('%(asctime)s : %(message)s')
        fh.setFormatter(frmt)
        self.training_verbose.addHandler(fh)

        self.training_export = logging.getLogger('training-export')
        self.training_export.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/training-export.csv')
        fh.setLevel(logging.INFO)
        frmt = logging.Formatter('%(asctime)s,%(message)s')
        fh.setFormatter(frmt)
        self.training_export.addHandler(fh)



    def log_verbose(self, game_id, p_id, state, move, move_id):
        str = "Game:"+ game_id.__str__() + ", player:" + p_id.__str__() + ", move: "+ move.raw() + ", move id: "+move_id.__str__() + ", state: " + state.__str__()

        self.training_verbose.debug(str)

    def export(self, game_id, p_id, lib_before, score, lib_after, move, move_id):
        bool_player = 1 if p_id == 0 else 0
        #2017-11-13 23:44:05,904,184,2,5,24,4,0
        # id; player; ones; lib_b4; score; lib_after; zeroes;
        str = game_id.__str__() + "," + p_id.__str__() + "," + lib_before.__str__() + "," + score.__str__() \
              + "," + lib_after.__str__() + "," + bool_player.__str__() +","+move.raw()+","+move_id.__str__()

        self.training_export.info(str)


class GameWinnerLog:

    def __init__(self):
        self.logger = logging.getLogger('gameidvswin')
        self.logger.setLevel(logging.DEBUG)  # log all escalated at and above DEBUG

        fh = logging.FileHandler('logs/gameidvswin.txt')
        fh.setLevel(logging.INFO)
        frmt = logging.Formatter('%(message)s')
        fh.setFormatter(frmt)
        self.logger.addHandler(fh)

    def log(self, game_id, result):
        self.logger.info(game_id.__str__() + " : " + result.__str__())

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
    def csv_util():
        games = []
        winners = []

        with open('logs/gameidvswin.txt', 'r+') as f:
            with open('logs/old/gameidvswin.txt', 'a') as outfile:
                for line in f:
                    data = line.split(":")
                    games.append(data[0].strip())
                    winners.append(data[1])
                    outfile.write(line)
                    # f.truncate()
        seen = []

        with open('logs/gameidvswin.txt', 'w') as f:
            f.write("")

        with open('logs/training-export.csv', 'r+') as input_file:
            with open('logs/training-complete.csv', 'a') as outfile:
                for line in input_file:
                    data = line.split(",")

                    game_id = data[1]
                    player = data[2]
                    lib_b4 = data[3]
                    score = data[4]
                    lib_after = data[5]
                    player_is_nn = data[6]
                    piece_id = data[7]
                    piece_x = data[8]
                    piece_y = data[9]
                    rotation = data[10]
                    flip = data[11]
                    move_id = data[12]

                    # piece_id, x,y, self.rot, self.flip)
                    new_line = game_id.__str__() + "," + player.__str__() + "," + lib_b4.__str__() + "," + score.__str__() + "," + lib_after.__str__() \
                               + "," + player_is_nn.__str__() + "," + piece_id.__str__() + "," + piece_x.__str__() + \
                               "," + piece_y.__str__() + "," + rotation.__str__() + "," + flip.__str__() + "," + move_id.__str__()

                    index = Logger.get_index(games, game_id)
                    if game_id in games:
                        win = 1 if int(winners[index]) == int(player.strip()) else 0
                        outfile.write(str(win) + "," + new_line)