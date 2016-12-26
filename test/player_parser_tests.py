import sys
sys.path.append("..")

import requests
requests.packages.urllib3.disable_warnings()

# automated tests for player_parser.py

from nose.tools import *
from player_parser import *

# main class tests
## constructor test

def test_playerParser():
    pp = PlayerParser(3022124041)
    assert_equals(pp.ID, 3022124041)
    assert_equals(pp.URL, "https://www.warlight.net/Profile?p=3022124041")
