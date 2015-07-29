import unittest

import util

from game import MonopolyGame

import board
import player

class TestInputOutput(util.InputOutput):
    def __init__(self):
        self.output = ""
        self.ask_callback = None

    def set_ask_callback(self, cb):
        self.ask_callback = cb

    def ask(self, msg):
        return self.ask_callback(msg)

    def tell(self, msg):
        self.output += msg

def create_test_monopoly_board():
    b = board.MonopolyBoard()
    b.tiles = [board.MonopolyBoardGoTile(b, 'Go')]
    b.go_tile = b.tiles[0]
    b.jail_tile = board.MonopolyBoardJailTile(b, 'Jail')

    return b

class MonopolyTestPlayer(player.MonopolyPlayer):
    def __init__(self, name, game):
        super(MonopolyTestPlayer, self).__init__(name, game)
        self.ran_out_of_money = False
        self.couldnt_pay = 0

    def out_of_money(self, inout):
        self.ran_out_of_money = True
        assert self.money < 0
        self.couldnt_pay += -1 * self.money
        self.money = 0

class MonopolyTestCase(unittest.TestCase):
    def setUp(self):
        self.inout = TestInputOutput()
        self.board = create_test_monopoly_board()
        self.game = MonopolyGame(self.board)
        for i in range(5):
            self.game.add_player(
                MonopolyTestPlayer('tester%d' % i, self.game))
        self.player = self.game.players[0]
