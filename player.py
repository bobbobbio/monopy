import board
import game

class MonopolyPlayer(object):
    def __init__(self, name, _game):
        self.name = name
        self.money = 1500
        self.num = 0
        self.current_tile = None
        self.last_roll = None
        self.jail_cards = 0
        self.holdings = []

        self.game = _game

        self.turns_in_jail = 0

        self.num_doubles = 0

    def __str__(self):
        return "{} ({})".format(self.name, self.num)

    def print_location(self, inout):
        inout.tell("\n{} (cash ${}) on {}\n"
            .format(self, self.money, self.current_tile))

        if self.in_jail:
            inout.tell("(This is your {} turn in JAIL)\n".format(
                "1st" if self.turns_in_jail == 1 else
                "2nd" if self.turns_in_jail == 2 else
                "3rd (and final)"
            ))

    def add_to_holdings(self, prop):
        self.holdings.append(prop)

    def jail(self):
        if self.in_jail:
            raise game.MonopolyUsageError("Player is already in jail")

        self.turns_in_jail = 1

    def jailbreak_failure(self, inout):
        if not self.in_jail:
            raise game.MonopolyUsageError("Player isn't in jail")

        self.turns_in_jail += 1

        if self.turns_in_jail > 3:
            inout.tell("It's your third turn and you didn't roll doubles.  "
                "You have to pay $50\n")
            # We are now out of tries to get out of jail, so we have to pay $50
            self.pay(inout, 50)
            self.turns_in_jail = 0

    def jailbreak_success(self):
        if not self.in_jail:
            raise game.MonopolyUsageError("Player isn't in jail")

        self.turns_in_jail = 0

    @property
    def in_jail(self):
        return self.turns_in_jail > 0

    @property
    def monopolies(self):
        monopolies = set()
        for holding in self.holdings:
            if holding.part_of_monopoly:
                monopolies.add(holding.monopoly)

        return monopolies

    @property
    def total_worth(self):
        n = self.money
        for h in self.holdings:
            n += h.total_worth

        return n

    def print_holdings(self, inout):
        inout.tell("{}'s holdings (Total worth: {})\n"
            .format(self, self.total_worth))
        inout.tell('${}'.format(self.money))
        if self.jail_cards:
            inout.tell(', {} get-out-of-jail-free card{}'
                .format(self.jail_cards, 's' if self.jail_cards > 1 else ''))
        inout.tell('\n')
        board.print_tiles(self.holdings, inout)

    def place_on_tile(self, inout, tile):
        self.current_tile = tile
        inout.tell("That puts you on {}\n".format(self.current_tile))
        self.current_tile.activate(inout, self, self.game)

    def pay(self, inout, amount):
        self.money -= amount
        if self.money < 0:
            self.out_of_money(inout)
        assert self.money >= 0

    def award(self, amount):
        self.money += amount

    def use_jail_card(self):
        if not self.jail_cards:
            raise game.MonopolyUsageError("Player doesn't have jail card")
        if not self.in_jail:
            raise game.MonopolyUsageError("Player isn't in jail")

        self.jail_cards -= 1
        self.jailbreak_success()

    def pay_for_jail(self, inout):
        if not self.in_jail:
            raise game.MonopolyUsageError("Player isn't in jail")

        # Price for jail is $50
        self.pay(inout, 50)
        self.jailbreak_success()

    def resign_to(self, other_player):
        if self == other_player:
            raise game.MonopolyUsageError("Player can't resign to himself")

        # XXX: what to do when resigning when in debt?
        assert self.money >= 0

        other_player.award(self.money)
        self.money = 0
        for holding in self.holdings:
            holding.owner = other_player
            other_player.add_to_holdings(holding)
        self.holdings = []

        other_player.jail_cards += self.jail_cards
        self.jail_cards = 0

        self.game.player_resign(self)

    def give_jail_card(self):
        self.jail_cards += 1

    # ======= These are suppose to be implemented by subclass =======

    def offer_property(self, inout, prop):
        pass

    def have_turn(self, inout):
        pass

    def out_of_money(self, inout):
        pass

class HumanMonopolyPlayer(MonopolyPlayer):
    # XXX: These two functions are very similar, it would be nice if they could
    # code share somehow.
    def run_mortgage(self, inout):
        mortgagable_holdings = [h for h in self.holdings if h.mortgagable]

        if not mortgagable_holdings:
            if [h for h in self.holdings if h.houses]:
                inout.tell("You can't mortgage property with houses on it.\n")
            else:
                inout.tell("You don't have any un-mortgaged property.\n")
            return

        # Fast path it when you have only one holding you can mortgage
        if len(mortgagable_holdings) == 1:
            holding = mortgagable_holdings[0]
            inout.tell('Your only mortageable property is {}\n'.format(holding))
            if inout.ask_yn_question('Do you want to mortgage it? '):
                holding.mortgage(inout, self)
            return

        cmds = {}

        def add_holding(holding):
            cmds[str(holding)] = lambda: holding.mortgage(inout, self)

        for holding in mortgagable_holdings:
            add_holding(holding)

        inout.ask_cmd_until_done(
            'Which property do you want to mortgage? ', cmds)


    def run_unmortgage(self, inout):
        unmortgagable_holdings = [h for h in self.holdings if h.unmortgagable]

        if not unmortgagable_holdings:
            inout.tell("You don't have any mortgaged property.\n")
            return

        # Fast path it when you have only one holding you can unmortgage
        if len(unmortgagable_holdings) == 1:
            holding = unmortgagable_holdings[0]
            inout.tell('Your only unmortageable property is {}\n'
                .format(holding))
            if inout.ask_yn_question('Do you want to unmortgage it? '):
                holding.unmortgage(inout, self)
            return

        cmds = {}

        def add_holding(holding):
            cmds[str(holding)] = lambda: holding.unmortgage(inout, self)

        for holding in unmortgagable_holdings:
            add_holding(holding)

        inout.ask_cmd_until_done(
            'Which property do you want to unmortgage? ', cmds)

    def buy_houses_for_monopoly(self, monopoly, inout):
        monopoly_holdings = [h for h in self.holdings if h.monopoy == monopoly]
        for holding in monopoly_holdings:
            inout.tell(str(holding))
        inout.tell('How many houses do you wish to buy for\n')
        for holding in monopoly_holdings:
            inout.ask_int(holding.name)

    def buy_houses(self, inout):
        if not self.monopolies:
            inout.tell("But you don't have any monopolies!!\n")
            return

        cmds = {}

        def add_monopoly(monopoly):
            cmds[monopoly] = \
                lambda: self.buy_houses_for_monopoly(monopoly, inout)

        for monopoly in self.monopolies:
            add_monopoly(monopoly)

        inout.ask_cmd_until_done(
            'Which property do you wish to buy houses for? ', cmds)

    def sell_houses(self, inout):
        # XXX: implement
        pass

    def trade_with(self, other_player, inout):
        # XXX: implement
        pass

    def resign(self, inout):
        # XXX: implement
        pass

    def out_of_money(self, inout):
        while self.money <= 0:
            inout.tell('That leaves you ${} in debt\n'.format(-self.money))
            inout.ask_cmd('How are you going to fix it up? ',
                commands=self.default_commands(inout))

    def offer_property(self, inout, prop):
        if inout.ask_yn_question("Do you want to buy? "):
            prop.purchase(inout, self)

    def default_commands(self, inout):
        return {
            'mortgage':
                lambda: self.run_mortgage(inout),
            'unmortgage':
                lambda: self.run_unmortgage(inout),
            'buy houses':
                lambda: self.buy_houses(inout),
            'sell houses':
                lambda: self.sell_houses(inout),
            'card': self.use_jail_card,
            'pay': lambda: self.pay_for_jail(inout),
            'trade':
                lambda: self.game.trade(self, inout),
            'resign': lambda: self.resign(inout)
        }

    def have_turn(self, inout):
        self.print_location(inout)
        commands = self.default_commands(inout)
        commands['roll'] = lambda: self.game.roll_dice(inout)
        inout.ask_cmd("-- Command: ", commands=commands, default='roll')

