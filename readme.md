Project Title: Deep Learning with Blokus
Author : Savanna Endicott
Date: September 13th 2017

Packages Used:
Tensorflow 1.3.0
numpy 1.13.1

Game Classes:
- Board
- GameEngine
- Move
- Piece
- Display : NoDisplay, CLIDisplay
- Players : AlphaBetaAI, RandomPlayer, NNPlayer

Neural Network Classes:
- NNPlayer
- features.py contains methods to create input features and useful/reusable deep learning methods
- LinearModel
- Evaluator

Testing:
- run Game.py
    - options in the main function are in comments
    - Can be used to play out games with or without a display
    - Can be used to play games with all random players (MUCH faster), or including various players

- run features.py
    - first, run Game.py if you haven't yet this day
        (has to be done at least once the day you run features.py, looks inside that testing folder)
       - will create a game under today's directory
    - then run features
    - will run each state of the game before a move through the feature creating methods
    - keeps track of results
    - outputs the input matrices of state/result to supervised learning in the form of numpy vectors
    - works with any board size (specify in game.py when you play a game, then give features.py that game id
    - if you want to see the board as the game is replayed, comment out the board drawing (see the file for instructions)



