import sys
sys.path.append("..")
import os

# automated tests for clan_parser.py

from nose.tools import *
from clan_parser import *
import datetime

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
    cp = ClanParser(129)
    cp.pageData = testData
    assert_equals(cp.getClanName(), "CORP")
    assert_equals(cp.getMemberCount(), 87)
    assert_equals(cp.getLink(), "https://www.warlight.net/Map/23141-Empire-CORP")
    assert("from our ashes" in cp.getTagline())
    assert_equals(cp.getCreatedDate(), datetime.date(2016, 6, 30))
    assert ("Roleplayers of all kinds." in cp.getBio())
    assert ((8246332261, "Prabster Realm", "Account Guardian", False) in cp.getMembers())

## test clan retrieval
def test_getClans():
    assert (257 in getClans())
    assert (999 not in getClans())

if __name__ == "__main__":
    test_parserTools()
