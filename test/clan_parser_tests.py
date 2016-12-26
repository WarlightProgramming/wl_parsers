import sys
sys.path.append("..")

# global - preserved CORP data for testing
testLoc = "test/data/corpdata.html"
with open(testLoc, "rt") as fin:
    testData = fin.read()

# automated tests for clan_parser.py

from nose.tools import *
from clan_parser import *

# main class tests

## tests constructor
def test_clanParser():
    cp = ClanParser(129)
    assert_equals(cp.URL, "https://www.warlight.net/Clans/?ID=129")
