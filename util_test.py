#!/usr/bin/python

import sys
import unittest

from util import Roll
from monop_testing import TestInputOutput

class MonopolyUtilTest(unittest.TestCase):
    def setUp(self):
        self.inout = TestInputOutput()
        self.answers = []
        self.expected_prompt = "prompt"

        index = [0]
        def ans(prompt_actual):
            self.assertEqual(prompt_actual, self.expected_prompt)
            a = self.answers[index[0]]
            index[0] += 1
            return a

        self.inout.set_ask_callback(ans)

    def ask_int_test(self, int_expected):
        int_actual = self.inout.ask_int(self.expected_prompt)
        self.assertEqual(int_expected, int_actual)

    def test_ask_int(self):
        self.answers = ["42"]
        self.ask_int_test(42)
        self.assertEqual(self.inout.output, "")

    def test_ask_int_reask(self):
        self.answers = ["not an int", "42"]
        self.ask_int_test(42)
        self.assertEqual(self.inout.output, "I can't understand that\n")

    def test_ask_int_reask_multiple(self):
        self.answers = ["g80", "8df", "derp", "42"]
        self.ask_int_test(42)
        self.assertEqual(self.inout.output, "I can't understand that\n" * 3)

    def ask_cmd_test(self):
        test_command_called = [False]
        def test_command():
            test_command_called[0] = True

        commands = {
                'test_command': test_command
        }

        self.inout.ask_cmd(self.expected_prompt, commands)
        self.assertTrue(test_command_called[0])

    def test_ask_cmd(self):
        self.answers = ['test_command']
        self.ask_cmd_test()
        self.assertEqual(self.inout.output, '')

    def test_ask_cmd_reask(self):
        self.answers = ['derp', 'test_command']
        self.ask_cmd_test()
        self.assertEqual(self.inout.output, 'Illegal response: "derp". '
            " Use '?' to get a list of valid answers\n")

    def ask_yn_question_test(self, expected_answer):
        answer = self.inout.ask_yn_question(self.expected_prompt)
        self.assertEqual(answer, expected_answer)

    def test_ask_yn_question(self):
        self.answers = ['yes']
        self.ask_yn_question_test(True)
        self.assertEqual(self.inout.output, '')

    def test_ask_yn_question_reask(self):
        self.answers = ['derp', 'yes']
        self.ask_yn_question_test(True)
        self.assertEqual(self.inout.output, 'Illegal response: "derp". '
            " Use '?' to get a list of valid answers\n")

    def test_ask_yn_question_reask_multiple(self):
        self.answers = ['derp', 'True', 'False', 'No']
        self.ask_yn_question_test(False)

    def test_roll(self):
        r = Roll(1)
        self.assertEqual(r, 1)

    def test_roll_with_two_die(self):
        r = Roll(1, 45)
        self.assertEqual(r, 46)
        self.assertEqual(str(r), '1, 45')

    def test_roll_is_doubles(self):
        self.assertTrue(Roll(34, 34).is_doubles())
        self.assertFalse(Roll(34, 12).is_doubles())

if __name__ == "__main__":
    sys.exit(unittest.main())
