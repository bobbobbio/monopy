import sys

import board
import player
import util

class MonopolyUsageError(Exception):
    pass

def maybe_quit(inout):
    if inout.ask_yn_question('Do you all really want to quit? '):
        sys.exit(0)

class MonopolyGame(object):
    def __init__(self, board_):
        self.players = []
        self.player_iter = None
        self.next_player_num = 1

        self.current_player = None

        self.board = board_

    # Here we are wrapping the given InputOutput object with our own version so
    # that when we pass the object to other functions, the player can still
    # issue commands that call back to the game class.
    class MonopolyGameInputOutput(util.InputOutput):
        def __init__(self, game, inout):
            self.game = game
            self.inout = inout

        def ask(self, *args, **kwargs):
            return self.inout.ask(*args, **kwargs)

        def tell(self, *args, **kwargs):
            return self.inout.tell(*args, **kwargs)

        def ask_cmd(self, msg, commands, default=None):
            extra_commands = {
                'quit': lambda: maybe_quit(self),
                'print': lambda: self.game.print_board(self),
                'where': lambda: self.game.print_player_locations(self),
                'own holdings':
                    lambda: self.game.current_player.print_holdings(self.inout),
                'holdings': lambda: self.game.print_holdings(self.inout),
            }
            commands.update(extra_commands)
            return self.inout.ask_cmd(msg, commands, default=default)

    def print_board(self, inout):
        self.board.full_print(inout)

    def print_player_locations(self, inout):
        board.players_print(self.players, inout)

    def print_holdings(self, inout):
        cmds = {}
        def add_player(p):
            cmds[p.name] = lambda: p.print_holdings(inout)
        for p in self.players:
            add_player(p)

        inout.ask_cmd_until_done('Whose holdings do you want to see? ', cmds)

    def player_resign(self, plr):
        self.players.remove(plr)

    def trade(self, trading_player, inout):
        if len(self.players) == 1:
            inout.tell("There ain't no-one around to trade WITH!!\n")
            return
        elif len(self.players == 2):
            pa, pb = self.players
            other_player = pa if pb == trading_player else pb
            trading_player.trade_with(other_player, inout)
            return

        cmds = {}
        def add_player(p):
            cmds[p.name] = lambda: trading_player.trade_with(p, inout)
        for p in self.players:
            add_player(p)

        cmds['done'] = lambda: None

        inout.ask_cmd('Which player do you wish to trade with? ', cmds)

    # Does a roll-off between all of the players to decide who goes first
    def initial_roll(self, inout):
        while True:
            max_roll = 0
            max_player = None
            same_roll = 1
            for player_ in self.players:
                roll = util.roll_two_dice()
                inout.tell("{} rolls {}\n".format(player_, roll))
                if roll > max_roll:
                    max_roll = roll
                    max_player = player_
                    same_roll = 1
                elif roll == max_roll:
                    same_roll += 1

            if same_roll > 1:
                inout.tell("%d people rolled the same thing" % same_roll
                    + ", so we'll try again\n")
                continue
            else:
                break

        inout.tell("{} goes first".format(max_player))
        self.current_player = max_player

        # Set the player iteration to the correct position
        while self.get_next_player() != self.current_player:
            pass

    # Ask for and create the players
    def get_players(self, inout):
        while True:
            num_players = inout.ask_int("How many players? ")
            if num_players <= 0:
                inout.tell("Sorry. Number must range from 1 to 9\n")
            else:
                break

        player_names = []
        while True:
            player_names = []
            for i in xrange(1, num_players + 1):
                player_name = ""
                while not player_name:
                    player_name = inout.ask("Player %d's name: " % i)
                player_names.append(player_name)

            unique_names = set([n.lower() for n in player_names])

            if "done" in unique_names:
                inout.tell(
                    '"done" is a reserved word.  '
                    'Please try again\n')
                continue

            if len(unique_names) != len(player_names):
                inout.tell(
                    "Hey!!! Some of those are "
                    "IDENTICAL!!  Let's try that "
                    "again....\n")
                continue

            # Success
            break

        for name in player_names:
            self.add_player(player.HumanMonopolyPlayer(name, self))

        inout.tell("\n")

        self.player_iter = iter(self.players)

    def add_player(self, plr):
        assert plr.name not in [p.name for p in self.players]

        start_tile = self.board.tiles[0]

        plr.num = self.next_player_num
        plr.current_tile = start_tile
        assert plr.game == self

        self.next_player_num += 1

        self.players.append(plr)

    def get_next_player(self):
        try:
            return self.player_iter.next()
        except StopIteration:
            self.player_iter = iter(self.players)
            return self.player_iter.next()

    def roll_dice(self, inout):
        roll = util.roll_two_dice()
        inout.tell("roll is {}\n".format(roll))

        # XXX: This num_doubles thing sucks....

        go_again = False

        if self.current_player.in_jail:
            # If we are in jail, our roll goes to trying to get us out.  Only
            # doubles lets this happen
            if not roll.is_doubles():
                inout.tell("Sorry, that doesn't get you out\n")
                self.current_player.jailbreak_failure(inout)
            else:
                inout.tell("Double roll gets you out.\n")
                self.current_player.jailbreak_success()
        else:
            # If we are not in jail and we roll doubles, this player gets to go
            # again.
            if roll.is_doubles():
                go_again = True
                self.current_player.num_doubles += 1
            else:
                self.current_player.num_double = 0

        # If you roll doubles 3 times, its off to jail for you
        if self.current_player.num_doubles >= 3:
            self.current_player.num_doubles = 0
            go_again = False
            inout.tell("That's 3 doubles.  You go to jail\n")
            self.board.advance_player_to(
                inout, self.current_player, self.board.jail_tile)

        # We check jail state again to catch the case where the player got out
        # of or into jail on this turn.
        if not self.current_player.in_jail:
            self.board.advance_player_by_roll(inout, self.current_player, roll)

        # advance to the next person's turn
        if not go_again:
            self.current_player = self.get_next_player()
        else:
            inout.tell("{} rolled doubles.  Goes again\n"
                .format(self.current_player.name))

    def run_game(self, inout):
        inout = MonopolyGame.MonopolyGameInputOutput(self, inout)

        self.get_players(inout)
        self.initial_roll(inout)
        self._run_game(inout)

    def run_game_with_players(self, players, inout):
        inout = MonopolyGame.MonopolyGameInputOutput(self, inout)

        for p in players:
            self.add_player(p)

        self.player_iter = iter(self.players)

        self.initial_roll(inout)
        self._run_game(inout)

    # The main game loop
    def _run_game(self, inout):
        while True:
            self.current_player.have_turn(inout)
