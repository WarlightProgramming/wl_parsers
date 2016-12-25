# Imports

## parser_core - core parser class
from parser_core import *

## requests - to handle HTTP requests
import requests

# Main clan parser class
class ClanParser(WLParser):

    ## constructor
    ### extends WLParser constructor with clan-specific URL
    ###
    ### @PARAMS
    ### 'clanID' (string or integer): ID of targeted clan
    def __init__(self, clanID):
        self.baseURL = "https://www.warlight.net/Clans/?"
        self.ID = clanID
        self.URL = self.makeURL(ID=clanID)

    ## getClanName
    ### returns the name of a clan
    @getPageData
    def getClanName(self):
        page = self.pageData
        return self.getValueFromBetween(page, "<title>", " -")

    ## getMemberCount
    ### returns a clan's member count
    @getPageData
    def getMemberCount(self):
        page = self.pageData
        marker = "Number of members:</font> "
        return self.getIntegerValue(page, marker)

    ## getLink
    ### gets URL string for clan's designated link
    @getPageData
    def getLink(self):
        page = self.pageData
        marker = 'Link:</font> <a rel="nofollow" href="'
        end = '">'
        link = self.getValueFromBetween(page, marker, end)
        if link == "http://": return ""
        return link

    ## getTagline
    ### returns clan tagline
    @getPageData
    def getTagline(self):
        page = self.pageData
        marker = 'Tagline:</font> '
        end = '<br />'
        return self.getValueFromBetween(page, marker, end)

    ## getCreatedDate
    ### returns datetime object representing the creation date of a clan
    @getPageData
    def getCreatedDate(self):
        page = self.pageData
        marker = "Created:</font> "
        end = "<br"
        dateString = self.getValueFromBetween(page, marker, end)
        return self.getDate(dateString)

    ## getBio
    ### returns clan bio from clan page
    @getPageData
    def getBio(self):
        page = self.pageData
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    ## getMembers
    ### returns members of a clan in a list of tuples in the format:
    ### (playerID (int), playerName (string), playerTitle (string),
    ###  isMember (bool))
    @getPageData
    def getMembers(self):
        page = self.pageData
        marker = '<table class="dataTable">'
        end = '</table>'
        data = list()
        dataRange = self.getValueFromBetween(page, marker, end)
        dataSet = dataRange.split('<tr>')[2:]
        for dataPoint in dataSet:
            isMember = ('title="Warlight Member"' in dataPoint)
            playerID = self.getIntegerValue(dataPoint, "/Profile?p=")
            playerName = self.getValueFromBetween(dataPoint,
                         '">', '</a>')
            titleRange = dataPoint.split("<td>")[-1]
            playerTitle = self.getValueFromBetween(titleRange, "",
                          "</td")
            data.append((playerID, playerName, playerTitle, isMember))
        return data

# getClans
## returns a set of all clan IDs on warlight
def getClans():
    URL = "https://www.warlight.net/Clans/List"
    r = requests.get(URL)
    clanSet = set()
    clanData = r.text.split("/Clans/?ID=")[1:]
    for clan in clanData:
        clanID = ""
        while clan[0] in string.digits:
            clanID += clan[0]
            clan = clan[1:]
        clanSet.add(int(clanID))
    return clanSet