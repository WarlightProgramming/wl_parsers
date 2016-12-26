import os
os.chdir("..")

# automated tests for clan_parser.py

from nose.tools import *
from clan_parser import *

# main class tests

## tests constructor
def test_clanParser():
    cp = ClanParser(129)
    assert_equals(cp.URL, "https://www.warlight.net/Clans?ID=129")