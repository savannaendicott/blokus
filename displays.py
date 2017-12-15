"""Classes to control the game's display (screen, GUI, etc)
"""

from board import Board
import colorama
colorama.init(autoreset=True)

DISPLAY_ERR_STRING = "Error: using base display class"

class Display(object):
    """the Display class defines an interface for the game engine to draw the
    game state onto the screen.

    Child classes can use game engine data to draw the game onto the
    command line, on a GUI, etc...
    """

    def draw_board(self, board):
        """Draw the board onto the screen, command line, etc
        """
        raise NotImplementedError(DISPLAY_ERR_STRING)

class NoDisplay(Display):
    """The NoDisplay doesn't bother drawing the game. Useful for running many
    iterations of the game.
    """

    def draw_board(self, board):
        pass

class CLIDisplay(Display):
    """The CLIDisplay class prints the game board to the command line
    """
    def draw_board(self, board):
        str_horiz = "+" + "-"*board.N + "+"

        color_fore = [
            colorama.Fore.RED,
            colorama.Fore.YELLOW,
            colorama.Fore.GREEN,
            colorama.Fore.BLUE
        ]

        color_back = [
            colorama.Back.RED,
            colorama.Back.YELLOW,
            colorama.Back.GREEN,
            colorama.Back.BLUE
        ]

        color_reset = colorama.Style.RESET_ALL

        print str_horiz
        for r in range(board.N):
            str_line = "|"
            for c in range(board.N):
                state_xy = board.get_state_at_point(c, r)
                if state_xy == -1:
                    str_line += color_reset + "."
                else:
                    p = state_xy
                    str_color = color_fore[p] + color_back[p] + "%d" % p
                    str_line += str_color
            str_line += color_reset + "|"
            print str_line
        print str_horiz
        print ""
