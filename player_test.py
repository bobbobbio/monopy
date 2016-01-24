#!/usr/bin/python

import sys
import unittest
import textwrap

import game
import board
import monop_testing

class MonopolyPlayerTest(monop_testing.MonopolyTestCase):
    def test_initial_money(self):
        # All players should start with 1500 in money
        self.assertEqual(self.player.money, 1500)

    def test_print_location(self):
        self.player.print_location(self.inout)
        self.assertEqual(self.inout.output, textwrap.dedent('''
            tester0 (1) (cash $1500) on Go
        '''))

    def test_award(self):
        initial_money = self.player.money

        self.player.award(100)

        self.assertEqual(self.player.money, initial_money + 100)

    def test_pay(self):
        initial_money = self.player.money

        self.player.pay(self.inout, 50)

        self.assertEqual(self.player.money, initial_money - 50)

    def test_award_pay(self):
        initial_money = self.player.money

        self.player.award(100)
        self.player.pay(self.inout, 50)

        self.assertEqual(self.player.money, initial_money + 100 - 50)

    def test_in_jail(self):
        self.player.jail()
        self.assertTrue(self.player.in_jail)

    def test_jailbreak_failure(self):
        initial_money = self.player.money
        self.player.jail()

        self.player.jailbreak_failure(self.inout)
        self.player.jailbreak_failure(self.inout)
        self.player.jailbreak_failure(self.inout)

        self.assertEqual(self.player.money, initial_money - 50)
        self.assertFalse(self.player.in_jail)

    def test_jailbreak_success(self):
        initial_money = self.player.money
        self.player.jail()

        self.player.jailbreak_success()

        self.assertEqual(self.player.money, initial_money)
        self.assertFalse(self.player.in_jail)

    def test_jailbreak_failure_then_success(self):
        initial_money = self.player.money
        self.player.jail()

        self.player.jailbreak_failure(self.inout)
        self.player.jailbreak_failure(self.inout)
        self.player.jailbreak_success()

        self.assertEqual(self.player.money, initial_money)
        self.assertFalse(self.player.in_jail)

    def test_pay_for_jail(self):
        initial_money = self.player.money
        self.player.jail()

        self.player.pay_for_jail(self.inout)

        self.assertEqual(self.player.money, initial_money - 50)
        self.assertFalse(self.player.in_jail)

    def test_jail_card_usage(self):
        initial_money = self.player.money

        self.player.give_jail_card()
        self.player.jail()

        self.player.use_jail_card()

        self.assertEqual(self.player.money, initial_money)
        self.assertFalse(self.player.in_jail)

    def test_use_jail_card_no_jail_card(self):
        self.player.jail()
        with self.assertRaises(game.MonopolyUsageError):
            self.player.use_jail_card()

    def test_use_jail_card_not_in_jail(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.player.use_jail_card()

    def test_pay_for_jail_not_in_jail(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.player.pay_for_jail(self)

    def test_already_in_jail(self):
        self.player.jail()
        with self.assertRaises(game.MonopolyUsageError):
            self.player.jail()

    def test_jailbreak_success_not_in_jail(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.player.jailbreak_success()

    def test_jailbreak_failure_not_in_jail(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.player.jailbreak_failure(self.inout)

    def test_out_of_money(self):
        self.player.pay(self.inout, self.player.money + 1)

        self.assertTrue(self.player.ran_out_of_money)
        self.assertEqual(self.player.couldnt_pay, 1)

    def test_total_worth(self):
        test_holding = board.MonopolyBoardPropertyTile(
            self.board, "Test Tile", 100, "Red", [])
        self.player.add_to_holdings(test_holding)

        self.assertEqual(self.player.total_worth,
            self.player.money + test_holding.total_worth)

    def test_resign_to(self):
        test_holding = board.MonopolyBoardPropertyTile(
            self.board, "Test Tile", 100, "Red", [])
        self.player.add_to_holdings(test_holding)
        self.player.give_jail_card()

        other_player = self.game.players[1]

        initial_money = other_player.money
        player_money = self.player.money

        self.player.resign_to(other_player)

        self.assertEqual(other_player.money, player_money + initial_money)
        self.assertEqual(other_player.holdings, [test_holding])
        self.assertEqual(other_player.jail_cards, 1)

    # TODO: test rest of player

if __name__ == "__main__":
    sys.exit(unittest.main())
