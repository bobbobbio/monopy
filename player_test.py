import sys
import unittest

import monop_testing

class MonopolyPlayerTest(monop_testing.MonopolyTestCase):
    def test_initial_money(self):
        # All players should start with 1500 in money
        self.assertEqual(self.player.money, 1500)

    # TODO: test rest of player

if __name__ == "__main__":
    sys.exit(unittest.main())
