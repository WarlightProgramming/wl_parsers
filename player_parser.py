# Imports
# core parser class and functions
from parser_core import *

# main player parser class
class PlayerParser(WLParser):

    ## constructor
    ### takes a player ID
    def __init__(self, playerID):
        self.baseURL = "https://www.warlight.net/Profile?"
        self.ID = playerID
        self.URL = self.makeURL(p=playerID)

    ## playerExists
    ### returns a boolean determining whether a player exists
    @getPageData
    def playerExists(self):
        page = self.pageData
        marker = "Sorry, the requested player was not found."
        return (marker not in page)

    ## getClanID
    ### returns ID number for player's clan
    @getPageData
    def getClanID(self):
        page = self.pageData
        marker = '<a href="/Clans/?ID='
        if marker not in page: return None
        return self.getIntegerValue(page, marker)

    ## getClanIcon
    ### returns URL string for clan icon
    @getPageData
    def getClanIcon(self):
        page = self.pageData
        marker = '"vertical-align: middle" src="'
        end = '" border="'
        if marker not in page: return None
        return self.getValueFromBetween(page, marker, end)

    ## getLocation
    ### returns location string for a player
    ### either a country name or "United States: [state name]"
    @getPageData
    def getLocation(self):
        page = self.pageData
        marker = 'title="Plays from '
        end = '"'
        if marker not in page: return ""
        return self.getValueFromBetween(page, marker, end)

    ## getClanname
    ### returns name (string) of player's clan
    @getPageData
    def getClanName(self):
        page = self.pageData
        outerMarker = '<a href="/Clans/?ID='
        if outerMarker not in page: return ""
        outerEnd = '/a>'
        clanNameArea = self.getValueFromBetween(page, outerMarker, outerEnd)
        innerMarker = 'border="0" />'
        innerEnd = '<'
        if innerMarker in clanNameArea:
            return self.trimString(self.getValueFromBetween(clanNameArea,
                                                            innerMarker,
                                                            innerEnd))
        else:
            otherMarker = '">'
            otherEnd = '<'
            return self.trimString(self.getValueFromBetween(clanNameArea,
                                                            otherMarker,
                                                            otherEnd))

    ## getPlayerName
    ### gets player's name
    @getPageData
    def getPlayerName(self):
        page = self.pageData
        return self.getValueFromBetween(page, '<title>', ' -')

    ## getMemberStatus
    ### returns boolean (True if user is a Member)
    @getPageData
    def getMemberStatus(self):
        page = self.pageData
        memberString = 'id="MemberIcon" title="WarLight Member"'
        return (memberString in page)

    ## getLevel
    ### returns player's level
    @getPageData
    def getLevel(self):
        page = self.pageData
        return self.getIntegerValue(page, '<big><b>Level ')

    ## getPoints
    ### returns points earned in last 30 days (int)
    @getPageData
    def getPoints(self):
        page = self.pageData
        points = self.getTypedValue(page, 'days:</font> ',
                                    (string.digits + ","))
        return int(points.replace(",",""))

    ## getEmail
    ### returns player (partial) e-mail as a string
    @getPageData
    def getEmail(self):
        page = self.pageData
        marker = "E-mail:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    ## getLink
    ### returns player-supplied link as a string
    @getPageData
    def getLink(self):
        page = self.pageData
        marker = "Player-supplied link:"
        end = "</a>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getValueFromBetween(dataRange, '">', None)

    ## getTagline
    ### returns player tagline as a string
    @getPageData
    def getTagline(self):
        page = self.pageData
        marker = "Tagline:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    ## getBio
    ### returns player bio as a string
    @getPageData
    def getBio(self):
        page = self.pageData
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    ## getJoinString
    ### returns player join date as a string
    ### formatted mm/dd/yyyy
    @getPageData
    def getJoinString(self):
        page = self.pageData
        marker = "Joined WarLight:</font> "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)
        
    ## getJoinDate
    ### returns player join date as a datetime object
    def getJoinDate(self):
        return self.getDate(self.getJoinString())

    ## getMemberString
    ### returns player membership date as a string
    ### formatted mm/dd/yyyy
    @getPageData
    def getMemberString(self):
        page = self.pageData
        marker = "Member since</font> "
        end = "</font>"
        if marker not in page: return ""
        return self.getValueFromBetween(page, marker, end)

    ## getMemberDate
    ### returns player membership date as a datetime object
    ### if player is not a member, returns None
    def getMemberDate(self):
        memberString = self.getMemberString()
        if memberString == "": return None
        return self.getDate(memberString)

    ## getCurrentGames
    ### returns integer amount of ongoing multi-day games
    @getPageData
    def getCurrentGames(self):
        page = self.pageData
        dataRange = self.getValueFromBetween(page, 
                    "Currently in</font> ", "games")
        if "multi-day" not in dataRange: return 0
        return self.getIntegerValue(dataRange, "")

    ## getPlayedGames
    ### returns integer amount of played games
    @getPageData
    def getPlayedGames(self):
        page = self.pageData
        return self.getIntegerValue(page, "Played in</font> ")

    ## getPercentRT
    ### returns float percentage of real-time games (relative to played)
    @getPageData
    def getPercentRT(self):
        page = self.pageData
        dataRange = self.getValueFromBetween(page, "Played in",
                                             "<br />")
        return self.getNumericValue(dataRange, " (")

    ## getLastSeenString
    ### returns string indicating time since user last performed
    ### an action; minimum value is "less than 15 minutes ago"
    @getPageData
    def getLastSeenString(self):
        page = self.pageData
        marker = "Last seen </font>"
        end = "<font"
        return self.getValueFromBetween(page,
                                        marker, end)

    ## getLastSeen
    ### returns floating-point value representing
    ### time since user was last online, in hours
    @getPageData
    def getLastSeen(self):
        lastSeenString = self.getLastSeenString()
        if "less than" in lastSeenString:
            return 0
        return self.timeConvert(lastSeenString)

    ## getBootCount
    ### returns number of times a player has been booted
    @getPageData
    def getBootCount(self):
        page = self.pageData
        if "never been booted" in page: return 0
        marker = "This player has been booted "
        return self.getIntegerValue(page, marker)

    ## getBootRate
    ### returns percentage of time that a player has been booted
    ### as a floating-point value
    @getPageData
    def getBootRate(self):
        page = self.pageData
        if "never been booted" in page: return 0.0
        marker = "This player has been booted "
        end = "</font>"
        dataRange = self.getValueFromBetween(page, marker, end)
        return self.getNumericValue(dataRange, " (")

    ## getSingleStats
    ### returns a player's single-player stats as a dictionary
    ### formatted {'level name': # of turns (integer)}
    @getPageData
    def getSingleStats(self):
        page = self.pageData
        marker = "<h3>Single-player stats</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split('color="#858585')[1:]
        for dataPoint in dataSet:
            levelName = self.getValueFromBetween(dataPoint, '">',
                        ':</font>')
            levelTurns = self.getIntegerValue(dataPoint, "Won in ")
            data[levelName] = levelTurns
        return data

    ## getFavoriteGames
    ### returns a player's favorite games in a list of tuples:
    ### (gameID (integer), game name (string))
    @getPageData
    def getFavoriteGames(self):
        page = self.pageData
        data = list()
        marker = "<h3>Favorite Games</h3>"
        if marker not in page: return data
        end = "<h3>"
        dataRange = self.getValueFromBetween(page, marker, end)
        dataSet = dataRange.split("GameID=")[1:]
        for dataPoint in dataSet:
            gameID = self.getIntegerValue(dataPoint, "")
            gameName = self.getValueFromBetween(dataPoint,
                       '">', "</a>")
            gameData = (gameID, gameName)
            data.append(gameData)
        return data

    ## getTournaments
    ### returns a player's favorite tournaments in a list of tuples
    ### (tournament ID (integer), tournament name (string), rank (integer))
    ### if a player isn't ranked, rank is set to None
    @getPageData
    def getTournaments(self):
        page = self.pageData
        marker = "<h3>Tournaments</h3>"
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split("- ")[1:]
        for dataPoint in dataSet:
            if dataPoint[0] in string.digits:
                rank = self.getIntegerValue(dataPoint, "")
            else: rank = None
            tourneyID = self.getIntegerValue(dataPoint,
                        "TournamentID=")
            tourneyName = self.getValueFromBetween(dataPoint, '">',
                          "</a>")
            data.append((tourneyID, tourneyName, rank))
        return data

    ## getLadderData
    ### fetches a player's ladder data in a dictionary
    ### output[ladder name] is a tuple
    ### (team ID (integer), rank (integer), rating (integer),
    ###  peakRank (integer), peakRating (integer))
    @getPageData
    def getLadderData(self):
        page = self.pageData
        marker = "<h3>Ladder Statistics</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split("a href=")[1:]
        for dataPoint in dataSet:
            teamID = self.getIntegerValue(dataPoint, "TeamID=")
            ladderName = self.getValueFromBetween(dataPoint, '">',
                         "</a>")
            if ("Not Ranked" in dataPoint):
                rank = 0
            else: rank = self.getIntegerValue(dataPoint, "Ranked ")
            rating = self.getIntegerValue(dataPoint, "rating of ")
            if ("Best rating ever:" not in dataPoint):
                peakRating = 0
            else: peakRating = self.getIntegerValue(dataPoint,
                               "Best rating ever: ")
            if ("best rank ever: " not in dataPoint):
                peakRank = 0
            else: peakRank = self.getIntegerValue(dataPoint,
                             "best rank ever: ")
            data[ladderName] = (teamID, rank, rating, 
                                peakRank, peakRating)
        return data

    ## getRankedData
    ### returns a player's ranked data as a dictionary
    ### and three other outputs
    ### dictionary[gameType] is a tuple
    ### (games won (int), games played (int), win percent (float))
    ### rankedWins (integer): total ranked wins
    ### rankedCount (integer): total ranked games
    ### rankedPercent (float): win percent for all ranked games
    @getPageData
    def getRankedData(self):
        page = self.pageData
        marker = "<h3>Ranked Games</h3>"
        data = dict()
        if marker not in page: return data, 0, 0, 0.0
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        if "No completed ranked games" in dataRange:
            return data, 0, 0, 0.0
        rankedCount = self.getIntegerValue(dataRange,
                      "Completed</font> ")
        if "ranked games (" in dataRange:
            rankedWins = self.getIntegerValue(dataRange,
                         "ranked games (")
        else:
            rankedWins = self.getIntegerValue(dataRange,
                         "ranked game (")
        rankedPercent = Decimal(rankedWins) / Decimal(rankedCount)
        rankedPercent = float(rankedPercent * Decimal(100))
        dataSet = dataRange.split('color="#858585"')[2:]
        for dataPoint in dataSet:
            gameType = self.getValueFromBetween(dataPoint,
                       '>', ':</font')
            gamesWon = self.getIntegerValue(dataPoint,
                       "</font> ")
            gamesPlayed = self.getIntegerValue(dataPoint,
                          " / ")
            winPercent = Decimal(gamesWon) / Decimal(gamesPlayed)
            winPercent = float(winPercent * Decimal(100))
            data[gameType] = (gamesWon, gamesPlayed, winPercent)
        return data, rankedWins, rankedCount, rankedPercent

    ## getPreviousNames
    ### returns a list of previous names as tuples
    ### (previous name (string), date of change (datetime object))
    @getPageData
    def getPreviousNames(self):
        page = self.pageData
        marker = "<h3>Previously known as..."
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        dataSet = dataRange.split('&nbsp;&nbsp;&nbsp;')[1:]
        for dataPoint in dataSet:
            name = self.getValueFromBetween(dataPoint, None, " <font")
            untilString = self.getValueFromBetween(dataPoint,
                          '"gray">(', ")")
            until = self.getDate(untilString)
            data.append((name, until))
        return data

    ## getPlaySpeed
    ### returns play speed as a dictionary
    ### output [type]: average time (datetime object)
    ### type is either "Multi-Day Games" or "Real-Time Games"
    @getPageData
    def getPlaySpeed(self):
        page = self.pageData
        marker = "<h3>Play Speed</h3>"
        data = dict()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "<h3")
        typeMarkers = ["Multi-Day Games:", "Real-Time Games:"]
        for typeMarker in typeMarkers:
            markedRange = self.getValueFromBetween(dataRange,
                          typeMarker, "<h5")
            avgString = self.getValueFromBetween(markedRange,
                        "Average:</font> ", "<br />")
            avgTime = self.timeConvert(avgString)
            data[typeMarker[:-1]] = avgTime
        return data
 
    ## getFavoriteMaps
    ### returns a player's favorite maps as a list of tuples
    ### (name (string), author (string), link (string))
    @getPageData
    def getFavoriteMaps(self):
        page = self.pageData
        baseURL = "https://warlight.net"
        marker = "Favorite Maps</h3"
        data = list()
        if marker not in page: return data
        dataRange = self.getValueFromBetween(page, marker, "</td")
        dataSet = dataRange.split('a href="')[1:]
        for dataPoint in dataSet:
            link = self.getValueFromBetween(dataPoint, '', '">')
            name = self.getValueFromBetween(dataPoint, 
                   "</a> <br>", "<br>")
            author = self.getValueFromBetween(dataPoint, "by ",
                     "</font>")
            data.append((name, author, link))
        return data

    ## getAchievementRate
    ### returns integer % value representing achievements completed
    @getPageData
    def getAchievementRate(self):
        page = self.pageData
        marker = "<h3>Achievements"
        if marker not in page: return 0
        dataRange = self.getValueFromBetween(page, marker, 
                    "</font>")
        return self.getIntegerValue(dataRange, "(")