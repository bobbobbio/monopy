import board

class MonopolyCard(object):
    def __init__(self, message):
        self.message = message

    def activate(self, _inout, _player, _game):
        pass

class MonopolyMonetaryCard(MonopolyCard):
    def __init__(self, amount, message):
        super(MonopolyMonetaryCard, self).__init__(message)
        self.amount = amount

    def activate(self, inout, player, _game):
        inout.tell(self.message + "\n")
        if self.amount < 0:
            player.pay(inout, -self.amount)
        else:
            player.award(self.amount)

class MonopolyMonetaryPlayersCard(MonopolyCard):
    def __init__(self, amount, message):
        super(MonopolyMonetaryPlayersCard, self).__init__(message)
        self.amount = amount

    def activate(self, inout, player, game):
        inout.tell(self.message + "\n")

        total = 0
        for other_player in game.players:
            if self.amount >= 0:
                other_player.pay(inout, self.amount)
            else:
                other_player.award(-1 * self.amount)

            total += self.amount

        if total >= 0:
            player.award(total)
        else:
            player.pay(inout, -1 * total)

class MonopolyGetOutOfJailCard(MonopolyCard):
    def __init__(self, message):
        super(MonopolyGetOutOfJailCard, self).__init__(message)

    def activate(self, inout, player, _game):
        inout.tell(self.message)
        player.give_jail_card()

class MonopolyTaxCard(MonopolyCard):
    def __init__(self, message):
        super(MonopolyTaxCard, self).__init__(message)

    def activate(self, inout, player, _game):
        inout.tell(self.message)
        houses = 0
        hotels = 0
        for holding in player.holdings:
            if holding.houses < 5:
                houses += holding.houses
            else:
                hotels += 1

        player.pay(inout, houses * 25 + hotels * 100)

class MonopolyAdvanceCard(MonopolyCard):
    def __init__(self, tile_index, message):
        super(MonopolyAdvanceCard, self).__init__(message)
        self.tile_index = tile_index

    def activate(self, inout, _player, _game):
        inout.tell(self.message)
        # XXX ...

class MonopolyAdvanceToTileTypeCard(MonopolyCard):
    def __init__(self, tile_type, message):
        super(MonopolyAdvanceToTileTypeCard, self).__init__(message)
        self.tile_type = tile_type

    def activate(self, inout, _player, _game):
        inout.tell(self.message)
        # XXX ...

class MonopolyMoveBackCard(MonopolyCard):
    def __init__(self, num_spaces, message):
        super(MonopolyMoveBackCard, self).__init__(message)
        self.num_spaces = num_spaces

    def activate(self, inout, _player, _game):
        inout.tell(self.message)
        # XXX ...

class MonopolyGoToJailCard(MonopolyCard):
    def __init__(self, message):
        super(MonopolyGoToJailCard, self).__init__(message)

    def activate(self, inout, player, game):
        game.board.advance_player_to(inout, player, game.board.jail_tile)

def create_card(action, message):
    if action.startswith('++'):
        return MonopolyMonetaryCard(int(action[2:]), message)
    elif action.startswith('--'):
        return MonopolyMonetaryCard(-1 * int(action[2:]), message)
    elif action.startswith('+A'):
        return MonopolyMonetaryPlayersCard(int(action[2:]), message)
    elif action.startswith('-A'):
        return MonopolyMonetaryPlayersCard(-1 * int(action[2:]), message)
    elif action.startswith('MJ'):
        return MonopolyGoToJailCard(message)
    elif action.startswith('FF'):
        return MonopolyGetOutOfJailCard(message)
    elif action.startswith('MF'):
        return MonopolyAdvanceCard(int(action[2:]), message)
    elif action.startswith('MR'):
        return MonopolyAdvanceToTileTypeCard(
            board.MonopolyBoardRRTile, message)
    elif action.startswith('MU'):
        return MonopolyAdvanceToTileTypeCard(
            board.MonopolyBoardUtilityTile, message)
    elif action.startswith('MB'):
        return MonopolyMoveBackCard(int(action[2:]), message)
    elif action.startswith('TX'):
        return MonopolyTaxCard(message)
    else:
        raise Exception("Unknown card type '{}'".format(action))

