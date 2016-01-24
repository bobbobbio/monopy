#!/usr/bin/python

import glob
import subprocess

def print_header(s, num_stars=10):
    print ("*" * num_stars), s, ("*" * num_stars)

res = {}
for test_file in glob.glob("*test.py"):
    print_header(test_file, num_stars=5)
    res[test_file] = subprocess.call("./" + test_file)

print_header("success")
for test_file in [f for f, r in res.iteritems() if r == 0]:
    print test_file

print_header("failure")
for test_file in [f for f, r in res.iteritems() if r != 0]:
    print test_file
