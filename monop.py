import sys

import game
import board
import util

def load_board():
    b = board.MonopolyBoard()
    b.load_board('./brd.json')
    b.load_com_chest_cards('./com_chest_cards.json')
    b.load_chance_cards('./chance_cards.json')

    return b

def main():
    monop = game.MonopolyGame(load_board())
    monop.run_game(util.CliInputOutput())

if __name__ == "__main__":
    sys.exit(main())
