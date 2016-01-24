#!/usr/bin/python

import sys
import unittest

import monop_testing
import board
import game

class MonopolyBoardPropertyTileTest(monop_testing.MonopolyTestCase):
    def setUp(self):
        super(MonopolyBoardPropertyTileTest, self).setUp()
        self.ptile1 = board.MonopolyBoardPropertyTile(
            self.board, "Test Tile", 100, "Red", [5, 15, 20, 25, 30, 35])
        self.ptile2 = board.MonopolyBoardPropertyTile(
            self.board, "Test Tile 2", 200, "Red", [10, 25, 35, 40, 45, 50])
        self.board.tiles.append(self.ptile1)
        self.board.tiles.append(self.ptile2)

    def test_purchase(self):
        self.player.money = 300
        # ptile1 has a cost of 100, (see setUp)
        self.ptile1.purchase(self.inout, self.player)
        self.assertEqual(self.player.money, 200)

    def test_monopoly_members(self):
        members = set()
        for t in self.ptile1.monopoly_members:
            members.add(t)
        self.assertEqual(members, set([self.ptile1, self.ptile2]))

        members = set()
        for t in self.ptile2.monopoly_members:
            members.add(t)
        self.assertEqual(members, set([self.ptile1, self.ptile2]))

    def test_part_of_monopoly(self):
        self.assertFalse(self.ptile1.part_of_monopoly)
        self.assertFalse(self.ptile2.part_of_monopoly)

        self.ptile1.purchase(self.inout, self.player)
        self.assertFalse(self.ptile1.part_of_monopoly)
        self.assertFalse(self.ptile2.part_of_monopoly)

        self.ptile2.purchase(self.inout, self.player)
        self.assertTrue(self.ptile1.part_of_monopoly)
        self.assertTrue(self.ptile2.part_of_monopoly)

    def test_rent_basic(self):
        # ptile1 has rents [5, 15, 20, 25, 30, 35] (see setUp)
        self.ptile1.purchase(self.inout, self.player)

        self.assertEqual(self.ptile1.rent, 5)

        self.ptile1.print_rent(self.inout)
        self.assertEqual(self.inout.output, 'rent is 5\n')

    def test_rent_monopoly(self):
        # ptile1 has rents [5, 15, 20, 25, 30, 35] (see setUp)
        self.ptile1.purchase(self.inout, self.player)
        self.ptile2.purchase(self.inout, self.player)

        # Rent doubles when it is part of a monopoly and there are no houses
        self.assertEqual(self.ptile1.rent, 10)

        self.ptile1.print_rent(self.inout)
        self.assertEqual(self.inout.output, 'rent is 10\n')

    def test_rent_with_house(self):
        # ptile1 has rents [5, 15, 20, 25, 30, 35] (see setUp)
        self.ptile1.purchase(self.inout, self.player)
        self.ptile2.purchase(self.inout, self.player)

        self.ptile1.place_house(self.inout, self.player)
        self.ptile1.place_house(self.inout, self.player)

        self.assertEqual(self.ptile1.rent, 20)

        self.ptile1.print_rent(self.inout)
        self.assertEqual(self.inout.output, 'with 2 houses, rent is 20\n')

    def test_rent_with_hotel(self):
        # ptile1 has rents [5, 15, 20, 25, 30, 35] (see setUp)
        self.ptile1.purchase(self.inout, self.player)
        self.ptile2.purchase(self.inout, self.player)

        for _ in xrange(4):
            self.ptile1.place_house(self.inout, self.player)

        self.assertEqual(self.ptile1.rent, 30)

        self.ptile1.place_hotel(self.inout, self.player)

        self.assertEqual(self.ptile1.rent, 35)

        self.ptile1.print_rent(self.inout)
        self.assertEqual(self.inout.output, 'with a hotel, rent is 35\n')

class MonopolyBoardRRTileTest(monop_testing.MonopolyTestCase):
    def setUp(self):
        super(MonopolyBoardRRTileTest, self).setUp()
        self.tile1 = board.MonopolyBoardRRTile(self.board, 'Test RR 1', 100)
        self.tile2 = board.MonopolyBoardRRTile(self.board, 'Test RR 2', 100)
        self.tile3 = board.MonopolyBoardRRTile(self.board, 'Test RR 3', 100)
        self.tile4 = board.MonopolyBoardRRTile(self.board, 'Test RR 4', 100)
        self.tiles = [self.tile1, self.tile2, self.tile3, self.tile4]

        for tile in self.tiles:
            self.board.tiles.append(tile)

    def test_rent_one(self):
        self.tile1.purchase(self.inout, self.player)

        # Rent is only 25 when you own one
        self.assertEqual(self.tile1.rent, 25)

    def test_rent_all(self):
        for tile in self.tiles:
            tile.purchase(self.inout, self.player)

        # Rent is 200 when you own all four
        for tile in self.tiles:
            self.assertEqual(tile.rent, 200)

    def test_place_house(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.tile1.place_house(self.inout, self.player)

class MonopolyBoardUtilityTileTest(monop_testing.MonopolyTestCase):
    def setUp(self):
        super(MonopolyBoardUtilityTileTest, self).setUp()
        self.tile1 = board.MonopolyBoardUtilityTile(
            self.board, 'Test Utility 1', 100)
        self.tile2 = board.MonopolyBoardUtilityTile(
            self.board, 'Test Utility 2', 100)
        self.tiles = [self.tile1, self.tile2]

        for tile in self.tiles:
            self.board.tiles.append(tile)

        self.board.last_roll = 10

    def test_rent_one(self):
        self.tile1.purchase(self.inout, self.player)

        # Before being a part of a monopoly the rent is  4 * last roll
        self.assertEqual(self.tile1.rent, 4 * self.board.last_roll)

    def test_rent_all(self):
        for tile in self.tiles:
            tile.purchase(self.inout, self.player)

        # When you own all of the utilities the rent is  10 * last roll
        for tile in self.tiles:
            self.assertEqual(tile.rent, 10 * self.board.last_roll)

    def test_place_house(self):
        with self.assertRaises(game.MonopolyUsageError):
            self.tile1.place_house(self.inout, self.player)

# XXX: Test the rest of the tiles

class MonopolyBoardTest(monop_testing.MonopolyTestCase):
    def setUp(self):
        super(MonopolyBoardTest, self).setUp()
        self.board.tiles.append(
            board.MonopolyBoardSafeTile(self.board, 'Safe Tile 1'))
        self.board.tiles.append(
            board.MonopolyBoardSafeTile(self.board, 'Safe Tile 2'))

    def test_passing_go(self):
        # Put the player on non-go tile
        self.board.advance_player_to(self.inout, self.player,
            self.board.tiles[1])

        pre_money = self.player.money

        # Advance the player to go...
        self.board.advance_player_to(self.inout, self.player,
            self.board.go_tile)

        # They should get 200 more money
        self.assertEqual(self.player.money, pre_money + 200)

    def test_not_passing_go(self):
        # Put the player on non-go tile
        self.board.advance_player_to(self.inout, self.player,
            self.board.tiles[1])

        pre_money = self.player.money

        # Advance the player to a safe tile that doesn't make them pass go
        self.board.advance_player_to(self.inout, self.player,
            self.board.tiles[2])

        # They shouldn't have gotten any money
        self.assertEqual(self.player.money, pre_money)

if __name__ == "__main__":
    sys.exit(unittest.main())
