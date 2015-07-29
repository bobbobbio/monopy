import random
import sys

# This Roll class is subclassing the int class, that way it can be treated like
# an int in almost all cases, but we retain what the roll is so we can print it
# properly
class Roll(int):
    def __new__(cls, *args):
        values = list(args)
        value = reduce(lambda x, y: x + y, values)
        obj = super(Roll, cls).__new__(cls, value)
        obj.values = values
        return obj

    def is_doubles(self):
        return len(self.values) == 2 and len(set(self.values)) == 1

    def __str__(self):
        return ', '.join([str(v) for v in self.values])

def roll_dice(n_dice, n_sides=6):
    values = []
    for _ in xrange(n_dice):
        values.append(int(random.random() * n_sides) + 1)
    return Roll(*values)

def roll_one_die():
    return roll_dice(n_dice=1)

def roll_two_dice():
    return roll_dice(n_dice=2)

# This is an abstract class that represents some way of communicating with the
# player over text.  Subclasses should implement tell and ask.
class InputOutput(object):
    def ask(self, _msg):
        # Meant to be implemented by subclass
        pass

    def ask_int(self, msg):
        while True:
            res = self.ask(msg)
            try:
                n = int(res)
            except ValueError:
                self.tell("I can't understand that\n")
                continue
            return n

    def ask_yn_question(self, msg, commands=None):
        if commands is None:
            commands = {}
        response = [False]
        yes = [False]
        def answer_yes():
            yes[0] = True
            response[0] = True
        def answer_no():
            yes[0] = False
            response[0] = True

        commands['yes'] = answer_yes
        commands['no'] = answer_no

        while not response[0]:
            self.ask_cmd(msg, commands)

        return yes[0]

    def ask_cmd_until_done(self, msg, commands):
        done = [False]
        def finish():
            done[0] = finish

        assert 'done' not in commands
        commands['done'] = finish

        while not done[0]:
            self.ask_cmd(msg, commands)

    def ask_cmd(self, msg, commands, default=None):
        assert '' not in commands, 'Empty string is not a valid command'

        if default:
            assert default in commands, '%s not a valid option' % default
            commands[''] = commands[default]

        # Sort and replace empty string with <RETURN>
        options = list(commands.keys())
        if default:
            options.remove(default)
            options.remove('')
            options.append(default + ' (default)')
        options = sorted(options)

        while True:
            res = self.ask(msg)

            if res == '?':
                self.tell("Valid inputs are: " + ', '.join(options) + '\n')
                continue

            found = []
            for cmd, cb in commands.iteritems():
                # fuzzy match.
                if cmd.lower().startswith(res.lower()):
                    found.append(cb)
                # exact match, remove others and go with this.
                if cmd.lower() == res.lower():
                    found = [cb]
                    break

            if not found or len(found) > 1:
                self.tell('Illegal response: "{}".'.format(res) +
                "  Use '?' to get a list of valid answers\n")
            else:
                found[0]()
                break

    def tell(self, _msg):
        # Meant to be implemented by subclasses
        pass

class CliInputOutput(InputOutput):
    def ask(self, msg):
        return raw_input(msg)

    def tell(self, msg):
        sys.stdout.write(msg)
