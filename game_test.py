import sys
import unittest

import game
import monop
import player
import util

class AIMonopolyPlayer(player.MonopolyPlayer):
    def have_turn(self, inout):
        self.print_location(inout)

        for holding in self.holdings:
            if holding.part_of_monopoly:
                # Houses might not always be $100
                if self.money > 100:
                    if holding.houses < 4:
                        inout.tell('{} placing house on {}\n'
                            .format(self, holding))
                    elif holding.houses == 5:
                        holding.place_hotel(inout, self)

        self.game.roll_dice(inout)

    def offer_property(self, inout, prop):
        if prop.cost <= self.money:
            prop.purchase(inout, self)
            inout.tell('{} bought {}\n'.format(self, prop))

    def out_of_money(self, inout):
        inout.tell('{} is out of money\n'.format(self))
        # first sell any houses
        # then mortgage

class IllegalAskError(Exception):
    pass

class AIInputOutput(util.InputOutput):
    def ask(self, msg):
        raise IllegalAskError(msg)

    def tell(self, msg):
        sys.stdout.write(msg)

class MonopolyFullGameTest(unittest.TestCase):
    def setUp(self):
        self.game = game.MonopolyGame(monop.load_board())
        self.players = []
        for i in range(2):
            self.players.append(AIMonopolyPlayer('player%s' % i, self.game))
        self.inout = AIInputOutput()

    def test_game(self):
        self.game.run_game_with_players(self.players, self.inout)

if __name__ == "__main__":
    sys.exit(unittest.main())
