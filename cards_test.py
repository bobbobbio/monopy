#!/usr/bin/python

import sys
import unittest

import monop_testing
import cards

class MonpolyCardsTest(monop_testing.MonopolyTestCase):
    def test_monetary_card_add(self):
        msg = 'Test Monetary Card'
        card = cards.MonopolyMonetaryCard(100, msg)

        self.player.money = 200
        card.activate(self.inout, self.player, self.game)
        self.assertEqual(self.player.money, 300)
        self.assertEqual(self.inout.output, msg + '\n')

    def test_monetary_card_sub(self):
        msg = 'Test Monetary Card'
        card = cards.MonopolyMonetaryCard(-100, msg)

        self.player.money = 200
        card.activate(self.inout, self.player, self.game)
        self.assertEqual(self.player.money, 100)
        self.assertEqual(self.inout.output, msg + '\n')

    def test_monetary_players_cards(self):
        msg = 'Test Monetary Card'
        card = cards.MonopolyMonetaryPlayersCard(100, msg)

        for player in self.game.players:
            player.money = 100

        card.activate(self.inout, self.player, self.game)

        for player in self.game.players[1:]:
            self.assertEqual(player.money, 0)

        self.assertEqual(self.player.money, 100 * len(self.game.players))

        self.assertEqual(self.inout.output, msg + '\n')

# XXX: Test the rest of the card types.

if __name__ == "__main__":
    sys.exit(unittest.main())
