# Imports
# core parser class and functions
from parser_core import *

# main forum parser class
class ForumPageParser(WLParser):

    ## constructor
    ### takes a forum thread ID and offset
    def __init__(self, threadID, offset):
        self.baseURL = ("https://www.warlight.net/Forum/" + 
                        str(threadID) + "?")
        self.ID = threadID
        self.offset = offset
        self.URL = self.makeURL(Offset=offset)

    ## getLength
    ### returns integer amount of total comments in thread
    @getPageData
    def getLength(self):
        page = self.pageData
        marker = "Posts "
        end = "&nbsp;"
        contentArea = self.getValueFromBetween(page, marker, end)
        return self.getIntegerValue(contentArea, "of ")

    ## threadExists
    ### returns a boolean determining whether a thread exists
    @getPageData
    def threadExists(self):
        page = self.pageData
        marker = "Oops!  That thread doesn't exist. It may have been deleted."
        return (marker not in page)

    ## isErrorPage
    ### returns True if a page is the Warlight error page
    @getPageData
    def isErrorPage(self):
        page = self.pageData
        errorMarker = '<h1>Whoops, an error has occurred</h1>'
        return (errorMarker in page)

    ## pageExists
    ### returns a boolean determining whether a page is empty
    @getPageData
    def pageExists(self):
        page = self.pageData
        return (not self.isErrorPage() and self.getPostCount() > 0)

    ## getPostCount
    ### returns the number of posts on page (integer)
    @getPageData
    def getPostCount(self):
        pageLength = max(self.offset, self.getLength())
        return min(20, pageLength-self.offset)

    ## getTitle
    ### returns thread title as a string
    @getPageData
    def getTitle(self):
        before = "<title>"
        after = " - Play Risk"
        return self.getValueFromBetween(self.pageData,
                                        before, after)

    ## getPosts
    ### returns posts on page as a list of tuples
    ### (ID, author, title, message, time)
    ### where author is a tuple
    ### (profile ID, username, memberStatus, clan)
    ### where clan is a tuple or None (if no clan)
    ### (clan ID, clan name)
    ###
    ###@TODO: split into helper functions
    @getPageData
    def getPosts(self):
        pageData = self.pageData
        splitter = '" cellspacing="0" class="region" style="padding-bottom:15px; width: 100%; max-width: 900px;'
        postData = pageData.split(splitter)[1:]
        posts = list()
        for post in postData:
            idMarker = "PostForDisplay_"
            ID = self.getIntegerValue(post, idMarker)
            titleMarker = '<font color="#CCCCCC">'
            titleEnd = '</font>'
            title = self.getValueFromBetween(post, titleMarker, titleEnd)
            messageStart = '"PostForDisplay_' + str(ID) + '">'
            messageEnd = '</div>'
            message = self.trimString(self.getValueFromBetween(post, 
                                      messageStart, messageEnd))
            timeStringStart = '</font>:'
            timeStringEnd = '</th>'
            timeString = self.trimString(
                             self.getValueFromBetween(post, timeStringStart,
                                                      timeStringEnd))
            time = self.getDateTime(timeString)
            authorID = self.getIntegerValue(post, 'Profile?p=')
            authorStart = str(authorID) + '">'
            authorEnd = '</a>'
            authorName = self.getValueFromBetween(post, authorStart,
                                                  authorEnd)
            memberMarker = 'Images/SmallMemberIcon.png'
            memberStatus = (memberMarker in post)
            clanMarker = '/Clans/?ID='
            if clanMarker in post:
                clanID = self.getIntegerValue(post, clanMarker)
                clanNameMarker = clanMarker + str(clanID) + '" title="'
                clanNameEnd = '"><img'
                try:
                    clanName = self.getValueFromBetween(post, clanNameMarker,
                                                        clanNameEnd)
                    clan = (clanID, clanName)
                except:
                    clan = None
            else:
                clan = None
            author = (authorID, authorName, memberStatus, clan)
            dataPoint = (ID, author, title, message, time)
            posts.append(dataPoint)
        return posts

# forum thread parser
class ForumThreadParser(object):
    
    ## constructor
    ### takes a thread ID
    def __init__(self, threadID, minOffset=0):
        self.ID = threadID
        self.minOffset = minOffset
        self.pages = list()

    ## getPages
    ### retrieves page parsers
    def getPages(self):
        self.pages = list()
        threadEnded, offset = False, self.minOffset
        while (threadEnded is False):
            page = ForumPageParser(self.ID, offset)
            if page.pageExists():
                self.pages.append(page)
                offset += 20
            else:
                threadEnded = True

    ## getPostData
    ### retrieves post data, updates posts, post count,
    ### and title
    def getPostData(self):
        if (len(self.pages) == 0):
            self.getPages()
        firstPage = self.pages[0]
        self.title = firstPage.getTitle()
        self.postCount = firstPage.getPostCount()
        self.posts = list()
        for page in self.pages:
            postsInPage = page.getPosts()
            self.posts += postsInPage
        return self.posts

# subforum page parser
class SubforumPageParser(WLParser):
    
    ## constructor
    ### needs a forum name
    def __init__(self, forumName, offset):
        self.baseURL = ("https://www.warlight.net/Forum/" + forumName + "?")
        self.URL = self.makeURL(Offset=offset)

    ## fetchThreads
    ### returns threads on page as a list of tuples
    ### (thread name, thread author name,
    ###  post count, last post datetime, last post author)
    @getPageData
    def fetchThreads(self):
        threads = list()
        if (self.threadExists() == False):
            return threads
        contentBreaker = '<th>Last&nbsp;Post</th>'
        pageLoc = self.pageData.find(contentBreaker)
        pageData = self.pageData[pageLoc:]
        threadSplitter = '<tr>'
        threadData = pageData.split(threadSplitter)[1:]
        for dataPoint in threadData:
            titleBreaker = '<a href="'
            titleLoc = dataPoint.find(titleBreaker)
            dataPoint = dataPoint[titleLoc:]
            title = self.getValueFromBetween(dataPoint,
                    '">', '</a>')
            author = self.getValueFromBetween(dataPoint,
                     '"by ', ".</font>")
            postCount = self.getIntegerValue(dataPoint,
                        '<td nowrap="nowrap">')
            dateBreaker = 'padding-right:15px">'
            dateLoc = dataPoint.find(dateBreaker)
            dataPoint = self.trimString(dataPoint[dateLoc:])
            date = self.getDateTime(self.getValueFromBetween(
                                    dataPoint, "", "      "))
            latestAuthor = self.getValueFromBetween(dataPoint,
                           '#C6C6C6">by ', "</span>")
            threads.append((title, author, postCount,
                            postCount, date, latestAuthor))
        return threads

    ## threadsExist
    ### returns True if threads exist, False otherwise
    @getPageData
    def threadsExist(self):
        threadsMarker = "This forum has no posts."
        return (threadsMarker not in self.pageData)

# subforum parser
## scrapes a whole subforum
class SubforumParser(object):

    ## constructor
    ### takes forumName, cutoffTime (default None) - datetime object,
    ### minOffset (default 0)
    def __init__(self, forumName, cutoffTime=None, minOffset=0):
        self.forumName = forumName
        self.cutoff = cutoffTime
        self.minOffset = None
        self.pages = list()

    ## getPages
    ### generates subforum page parsers and stores them
    def getPages(self):
        self.pages = list()
        emptyPages, offset = False, minOffset
        while (emptyPages == False):
            pageParser = SubforumPageParser(self.forumName,
                                              offset)
            postsOnPage = pageParser.threadsExist()
            if postsOnPage:
                threadsOnPage = pageParser.fetchThreads()
                firstThreadTime = threadsOnPage[-1][1]
                if self.cutoff is None or firstThreadTime > self.cutoff:
                    self.pages.append(pageParser)
                else: # cutoff is not None and firstThreadTime is too old
                    emptyPages = True
            else:
                emptyPages = True

    ## getPosts
    ### returns posts as list of tuples
    ### in format returned by SubforumPageParser
    def fetchThreads(self):
        threads = list()
        if (len(self.pages) == 0):
            self.getPages()
        for i in xrange(len(self.pages)):
            page = self.pages[i]
            posts = page.fetchThreads()
            if (i == len(self.pages) - 1):
                skipRemaining = False
                for post in posts:
                    if skipRemaining: break
                    postTime = post[3]
                    if postTime > self.cutoff:
                        threads.append(post)
                    else:
                        skipRemaining = True
            else:
                threads += posts
        return posts