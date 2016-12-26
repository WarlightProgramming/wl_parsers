import sys
sys.path.append("..")
import os

# automated tests for clan_parser.py

from nose.tools import *
from clan_parser import *

# main class tests

## tests constructor
def test_clanParser():
    cp = ClanParser(129)
    assert_equals(cp.URL, "https://www.warlight.net/Clans/?ID=129")

## tests actual parser functions
@nottest
def test_parserTools():
    testLoc = "data/corpdata.html"
    with open(testLoc, "rt") as fin:
        testData = fin.read()
