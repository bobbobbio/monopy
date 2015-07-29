import json
import random

import cards

class MonopolyUsageError(Exception):
    pass

# Abstract class that represents a tile on the Monopoly board
class MonopolyBoardTile(object):
    def __init__(self, board, name):
        self.name = name
        self.board = board

    def __str__(self):
        return self.name

    def activate(self, _inout, _player, _game):
        pass

# Represents a monopoly property
class MonopolyBoardPropertyTile(MonopolyBoardTile):
    def __init__(self, board, name, cost, monopoly, rents):
        super(MonopolyBoardPropertyTile, self).__init__(board, name)
        self.cost = cost
        self.owner = None
        # houses == 5 is used to represent having a hotel
        self.houses = 0
        self.mortgaged = False
        self.monopoly = monopoly
        assert len(rents) == 6 or len(rents) == 0
        self.rents = rents

    # This is the number of other properties in the monopoly that are managed by
    # the same owner. Zero if no owner.
    @property
    def management_num(self):
        if self.owner is None:
            return 0

        n = 0
        for tile in self.monopoly_members:
            if self.owner == tile.owner:
                n += 1
        assert n >= 1

        return n

    @property
    def monopoly_members(self):
        for tile in self.board.get_tiles(monopoly=self.monopoly):
            yield tile

    @property
    def part_of_monopoly(self):
        if self.owner is None:
            return False

        for tile in self.monopoly_members:
            if self.owner != tile.owner:
                return False
        return True

    @property
    def total_worth(self):
        n = self.cost
        n += self.houses * 25
        return n

    @property
    def mortgagable(self):
        return not self.mortgaged and not self.houses

    @property
    def unmortgagable(self):
        return self.mortgaged

    def mortgage(self, inout, player):
        assert self.mortgagable
        assert player == self.owner

        self.mortgaged = True

        # The mortgage value is half the cost of the property
        money = int(self.cost / 2)
        player.award(money)
        inout.tell('That got you ${}\n'.format(money))

    def unmortgage(self, inout, player):
        assert self.unmortgagable
        assert player == self.owner

        self.mortgaged = False

        # To unmortgage you have to pay the mortgage plus 10% interest
        cost = int((self.cost / 2) * 1.10)
        player.pay(inout, cost)
        inout.tell('That cost you ${}\n'.format(cost))

    @property
    def rent(self):
        if self.part_of_monopoly and self.houses == 0:
            return self.rents[0] * 2
        else:
            return self.rents[self.houses]

    def print_rent(self, inout):
        if self.houses == 5:
            inout.tell("with a hotel, rent is {}\n".format(self.rent))
        elif self.houses > 0:
            inout.tell("with {} house{}, rent is {}\n".format(
                self.houses, 's' if self.houses > 1 else '', self.rent))
        else:
            inout.tell("rent is {}\n".format(self.rent))

    def purchase(self, inout, player):
        assert self.owner is None
        player.pay(inout, self.cost)
        self.owner = player
        player.add_to_holdings(self)

    def activate(self, inout, player, _game):
        if self.owner is None:
            assert not self.mortgaged
            inout.tell("That would cost ${}\n".format(self.cost))
            player.offer_property(inout, self)
        elif self.owner != player:
            inout.tell("Owned by {}\n".format(self.owner.name))

            if self.mortgaged:
                inout.tell('The thing is mortgaged.  You got lucky this time\n')
                return

            self.print_rent(inout)

            player.pay(inout, self.rent)
            self.owner.award(self.rent)
        else:
            inout.tell("You own it.\n")

    def place_house(self, inout, player):
        assert self.owner is not None
        assert self.owner == player

        assert self.part_of_monopoly
        assert self.houses < 4

        # XXX: I'm not sure that houses should always be $100
        player.pay(inout, 100)

        self.houses += 1

    def place_hotel(self, inout, player):
        assert self.owner is not None
        assert self.owner == player

        assert self.part_of_monopoly
        assert self.houses == 4

        player.pay(inout, 100)

        # houses == 5 is used to represent having a hotel
        self.houses += 1

class MonopolyBoardRRTile(MonopolyBoardPropertyTile):
    def __init__(self, board, name, cost):
        super(MonopolyBoardRRTile, self).__init__(board, name, cost,
                monopoly="Railroad", rents=[])

    @property
    def rent(self):
        if self.owner is None:
            return 25

        num_owned = 0
        for rr in self.monopoly_members:
            if rr.owner == self.owner:
                num_owned += 1

        assert num_owned
        return 25 << (num_owned - 1)

class MonopolyBoardUtiltyTile(MonopolyBoardPropertyTile):
    def __init__(self, board, name, cost):
        super(MonopolyBoardUtiltyTile, self).__init__(board, name, cost,
            monopoly="Utility", rents=[])

    @property
    def rent(self):
        if self.owner is None:
            return 0

        if self.part_of_monopoly:
            return 10 * self.board.last_roll
        else:
            return 4 * self.board.last_roll

    @property
    def part_of_monopoly(self):
        return False

    @property
    def all_utilities(self):
        return super(MonopolyBoardUtiltyTile, self).part_of_monopoly

    def print_rent(self, inout):
        if self.part_of_monopoly:
            inout.tell("rent is 10 * roll ({}) = {}\n"
                .format(self.board.last_roll, self.rent))
        else:
            inout.tell("rent is 4 * roll ({}) = {}\n"
                .format(self.board.last_roll, self.rent))

    def place_house(self, inout, player):
        raise MonopolyUsageError("Can't place a house on a utility")

class MonopolyBoardSafeTile(MonopolyBoardTile):
    def activate(self, inout, _player, _game):
        inout.tell("This is a safe place\n")

class MonopolyBoardGoTile(MonopolyBoardSafeTile):
    pass

class MonopolyBoardCardTile(MonopolyBoardTile):
    def __init__(self, board, name):
        super(MonopolyBoardCardTile, self).__init__(board, name)
        self.deck = None

    def activate(self, inout, player, game):
        # XXX: Remove the card from the deck when drawn?
        card = random.choice(self.deck)
        card.activate(inout, player, game)

class MonopolyBoardCCTile(MonopolyBoardCardTile):
    def __init__(self, board, name):
        super(MonopolyBoardCCTile, self).__init__(board, name)
        self.deck = board.cc_deck

class MonopolyBoardChanceTile(MonopolyBoardCardTile):
    def __init__(self, board, name):
        super(MonopolyBoardChanceTile, self).__init__(board, name)
        self.deck = board.chance_deck

class MonopolyBoardIncTaxTile(MonopolyBoardTile):
    pass
class MonopolyBoardLuxTaxTile(MonopolyBoardTile):
    pass

class MonopolyBoardGotoJailTile(MonopolyBoardTile):
    def activate(self, inout, player, game):
        game.board.advance_player_to(inout, player, game.board.jail_tile)

class MonopolyBoardJailTile(MonopolyBoardTile):
    def __init__(self, board, name):
        super(MonopolyBoardJailTile, self).__init__(board, name)
        self.board_index = None

TILE_TABLE = {
    "PRPRT":   MonopolyBoardPropertyTile,
    "SAFE":    MonopolyBoardSafeTile,
    "GO":      MonopolyBoardGoTile,
    "CC":      MonopolyBoardCCTile,
    "INC_TAX": MonopolyBoardIncTaxTile,
    "LUX_TAX": MonopolyBoardLuxTaxTile,
    "RR":      MonopolyBoardRRTile,
    "CHANCE":  MonopolyBoardChanceTile,
    "UTIL":    MonopolyBoardUtiltyTile,
    "GOTO_J":  MonopolyBoardGotoJailTile,
    "JAIL":    MonopolyBoardJailTile
}

def trun(o, n):
    return str(o)[:n] if len(str(o)) > n else str(o)

def _print_tile(tile, inout):
    # Name
    inout.tell('%-25s' % trun(tile, 25))
    if isinstance(tile, MonopolyBoardPropertyTile):
        # Owner
        if tile.owner:
            inout.tell('%-14s ' % trun(tile.owner, 14))
        else:
            inout.tell(' ' * 15)

        # Type
        inout.tell('%-10s' % trun(tile.monopoly, 10))

        # Price
        inout.tell('%5d ' % tile.cost)

        # Mg #
        if tile.management_num != 0:
            inout.tell('%4d ' % tile.management_num)
        else:
            inout.tell(' ' * 5)

        # Rent
        inout.tell('%4d ' % tile.rent)
    else:
        inout.tell(' ' * 41)

def _print_header(inout):
    inout.tell('%-25s' % 'Name')
    inout.tell('%-15s' % 'Owner')
    inout.tell('%-10s' % 'Type')
    inout.tell('%-6s' % 'Price')
    inout.tell('%-5s' % 'Mg #')
    inout.tell('%-5s' % 'Rent')

def print_tiles(tiles, inout):
    _print_header(inout)
    inout.tell('\n')
    for tile in tiles:
        _print_tile(tile, inout)
        inout.tell('\n')

def players_print(players, inout):
    _print_header(inout)
    inout.tell('Player')
    inout.tell('\n')
    for player in players:
        _print_tile(player.current_tile, inout)
        inout.tell(trun(player, 14))
        inout.tell('\n')

class MonopolyBoard(object):
    def __init__(self):
        self.tiles = []
        self.monopolies = set()
        self.last_roll = None

        self.jail_tile = None
        self.go_tile = None

        self.cc_deck = []
        self.chance_deck = []

    def load_board(self, board_file):
        assert len(self.tiles) == 0
        with open(board_file) as f:
            for td in json.loads(f.read()):
                assert td['type'] in TILE_TABLE
                tile_class = TILE_TABLE[td['type']]
                del td['type']
                td['board'] = self
                tile = tile_class(**td)

                if isinstance(tile, MonopolyBoardJailTile):
                    self.jail_tile = tile
                    self.jail_tile.board_index = len(self.tiles) - 1
                    # This tile isn't part of a normal board rotation
                    continue

                if isinstance(tile, MonopolyBoardGoTile):
                    self.go_tile = tile

                self.tiles.append(tile)

                if isinstance(tile, MonopolyBoardPropertyTile):
                    self.monopolies.add(tile.monopoly)

        # The board had better have these
        assert self.jail_tile
        assert self.go_tile

    def load_com_chest_cards(self, com_chest_cards_file):
        assert len(self.cc_deck) == 0
        with open(com_chest_cards_file) as f:
            for card in json.loads(f.read()):
                self.cc_deck.append(cards.create_card(**card))

    def load_chance_cards(self, chance_cards_file):
        assert len(self.chance_deck) == 0
        with open(chance_cards_file) as f:
            for card in json.loads(f.read()):
                self.chance_deck.append(cards.create_card(**card))

    def advance_player_by_roll(self, inout, player, roll):
        self.last_roll = roll
        if player.current_tile != self.jail_tile:
            i = self.tiles.index(player.current_tile)
        else:
            i = self.jail_tile.board_index
        i = (i + roll) % len(self.tiles)
        self.advance_player_to(inout, player, self.tiles[i])

    def advance_player_to(self, inout, player, tile, dont_pass_go=False):
        if tile == self.jail_tile:
            # Don't collect $200 when going to jail.
            dont_pass_go = True
            player.jail()

        # When rolling from jail, we have to take the player out of jail first.
        if player.current_tile == self.jail_tile:
            player.current_tile = self.tiles[self.jail_tile.board_index]

        # If the destination index is less than the players index, we had to
        # have passed go (index zero) in the move.  Also if we advance to go
        # from go we treat it as passing go again.
        if dont_pass_go is False:
            player_tile = self.tiles.index(player.current_tile)
            destination_tile = self.tiles.index(tile)
            if destination_tile < player_tile or destination_tile == 0:
                player.award(200)
                inout.tell('You pass === GO === and get $200\n')

        player.place_on_tile(inout, tile)

    def get_tiles(self, monopoly=None):
        if monopoly is None:
            for tile in self.tiles:
                yield tile
            return

        for tile in self.tiles:
            if not isinstance(tile, MonopolyBoardPropertyTile):
                continue
            if tile.monopoly == monopoly:
                yield tile

    def full_print(self, inout):
        for _ in range(2):
            _print_header(inout)
            inout.tell(' ' * 5)
        inout.tell('\n')

        col1 = 0
        col2 = (len(self.tiles) + 1) / 2
        while col2 < len(self.tiles):
            _print_tile(self.tiles[col1], inout)
            inout.tell(' ' * 5)
            _print_tile(self.tiles[col2], inout)
            inout.tell('\n')
            col1 += 1
            col2 += 1

