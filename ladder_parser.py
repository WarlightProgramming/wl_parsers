# Imports

## parser core - mainly the core parser class
from parser_core import *

# LadderParser class
class LadderParser(WLParser):

    ## constructor
    ### @PARAMS:
    ### 'ladderID': integer ID for ladder to parse
    def __init__(self, ladderID):
        self.baseURL = "https://www.warlight.net/LadderSeason?"
        self.ID = ladderID
        self.URL = self.makeURL(ID=ladderID)

    ## getSize
    ### returns integer amount of teams on ladder
    @getPageData
    def getSize(self):
        page = self.pageData
        marker = "<td>There are currently "
        return self.getIntegerValue(page, marker)

    ## trimUnranked
    ### given a list of teams, removes unranked teams
    @staticmethod
    def trimUnranked(teams):
        trimmedTeams = [team for team in teams if team[1] != 0]
        return trimmedTeams

    ## getTeams
    ### returns teams from the ladder as a list of tuples:
    ### (teamID, teamRank, rankShift, teamRating, players)
    ### where players is a list of tuples:
    ### (playerName, clan)
    ### where clan is a tuple:
    ### (clanID, clanName) - (None, "") if no clan
    def getTeams(self, rankedOnly=False):
        offset = 0
        stop = False
        allTeams = list()
        while(not stop):
            rankParser = LadderRankingParser(self.ID, offset)
            allTeams += rankParser.getLadderTeams()
            if ((rankParser.isEmpty) or 
                (rankedOnly and rankParser.hasUnranked)):
                stop = True
            offset += 50
        if rankedOnly: 
            allTeams = self.trimUnranked(allTeams)
        self.allTeams = allTeams
        return allTeams

# ladder ranking parser class
## retrieves a list of teams with rankings, one page at a time
## retrieves up to 50 teams at once
class LadderRankingParser(WLParser):

    ## constructor
    ### needs a ladder ID and an offset
    def __init__(self, ladderID, offset):
        self.baseURL = "https://www.warlight.net/LadderTeams?"
        self.URL = self.makeURL(ID=ladderID, Offset=offset)
        self.hasUnranked = False
        self.isEmpty = False

    ## getLadderTeams
    ### returns teams given a page of the ladder
    ### list of tuples:
    ### (teamID, teamRank, rankShift, teamRating, players)
    ### where player is a list of tuples:
    ### (playerName, (clanID, clanName))
    ###
    ### @TODO: break up into multiple functions
    @getPageData
    def getLadderTeams(self):
        page = self.pageData
        marker = '</thead>'
        end = '<table class="LadderTeamsPager">'
        dataRange = self.getValueFromBetween(page, marker, end)
        teams = list()
        if ("<tr >" not in dataRange): 
            self.isEmpty = True
            return teams
        dataSet = dataRange.split("<tr >")[1:]
        upArrow = 'img src="/Images/UpArrow.png"'
        downArrow = 'img src="/Images/DownArrow.png"'
        for dataPoint in dataSet:
            if ("<td>Not Ranked </td>" in dataPoint):
                teamRank = 0
                self.hasUnranked = True
            else:
                teamRank = self.getIntegerValue(dataPoint, "<td>")
            rankShift = (dataPoint.count(upArrow) - 
                         dataPoint.count(downArrow))
            teamMarker = 'LadderTeam?LadderTeamID='
            teamID = self.getIntegerValue(dataPoint, teamMarker)
            teamIDString = teamMarker + str(teamID)
            players = list()
            dataList = dataPoint.split("<a ")
            currentClanID, currentClanName = None, ""
            clanIDMarker = '"/Clans/?ID='
            clanNameMarker = '" title="'
            clanNameEnd = '">'
            nameMarker = teamIDString + '">'
            nameEnd = '</a'
            for dataUnit in dataList:
                if clanIDMarker in dataUnit and clanNameMarker in dataUnit:
                    currentClanID = self.getIntegerValue(dataUnit, clanIDMarker)
                    currentClanName = self.getValueFromBetween(dataUnit,
                                      clanNameMarker, clanNameEnd)
                elif nameMarker in dataUnit and nameEnd in dataUnit:
                    playerName = self.getValueFromBetween(dataUnit,
                                 nameMarker, nameEnd)
                    players.append((playerName,
                                    (currentClanID, currentClanName)))
                    currentClanID = None
                    currentClanName = ""
                else: continue
            ratingRange = dataPoint.split("<td>")[-1]
            if len(ratingRange) < 1 or (ratingRange[0] not in string.digits):
                teamRating = 0
            else:
                teamRating = self.getIntegerValue(ratingRange, "")
            teams.append((teamID, teamRank, rankShift, teamRating,
                          players))
        return teams

# parser class to fetch history of a ladder, 50 games at a time
class LadderHistoryParser(WLParser):

    ## constructor
    ### takes a ladder ID and an offset (ideally a multiple of 50)
    def __init__(self, ladderID, offset):
        self.baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(ID=ladderID, Offset=offset)
        self.isEmpty = False
        self.earliestTime = None
        self.gameMarker = '<tr style="background-color: inherit">'

    ## getGameHistory
    ### returns game history of a ladder as list of tuples:
    ### (gameID, gameTime, alphaTeam, betaTeam, finished, endDate, expired)
    ### gameTime is a datetime object
    ### alphaTeam is the winning team if a game is finished
    ### betaTeam is the losing team if a game is finished
    ### finished is a boolean
    ### endDate is None if finished is False
    ###
    ### @TODO: break up into multiple functions
    @getPageData
    def getGameHistory(self, returnExpired=True):
        page = self.pageData
        games = list()
        marker = "</thead>"
        end = '<div class="LadderGamesPager'
        dataRange = self.getValueFromBetween(page, marker, end)
        gameMarker = self.gameMarker
        if gameMarker not in dataRange: 
            self.isEmpty = True
            return games
        dataSet = dataRange.split(gameMarker)[1:]
        for dataPoint in dataSet:
            expired = False
            if "</a> (expired)" in dataPoint:
                expired = True
                if (returnExpired == False):
                    continue
            multiMarker = 'MultiPlayer?GameID='
            gameID = self.getIntegerValue(dataPoint,
                                          multiMarker)
            gameTime = self.getValueFromBetween(dataPoint,
                       'style="white-space: nowrap">',
                       '</td>')
            if gameTime == "": endDate = None
            else: endDate = self.getDateTime(gameTime)
            if "defeated" in dataPoint:
                alphaData, betaData = dataPoint.split("defeated")
                finished = True

            else:
                alphaData, betaData = dataPoint.split(" vs ")
                finished = False
            alphaTeam = self.getIntegerValue(alphaData,
                        '?LadderTeamID=')
            betaTeam = self.getIntegerValue(betaData,
                       '?LadderTeamID=')
            games.append((gameID, gameTime, alphaTeam, betaTeam, finished,
                          endDate, expired))
            self.earliestTime = gameTime
        return games

# parser a page of history for a ladder team
class LadderTeamHistoryParser(LadderHistoryParser):

    ## constructor
    ### needs ladderID, teamID, and offset
    def __init__(self, ladderID, teamID, offset):
        self.baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(ID=ladderID, LadderTeamID=teamID, Offset=offset)
        self.isEmpty = False
        self.earliestTime = None
        self.gameMarker = '<tr style="background-color: '