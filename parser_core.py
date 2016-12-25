# Imports

## requests - to make HTTP requests
import requests

## string - primarily for string constants
import string

## decimal - more precise mathematical operations
from decimal import Decimal

## datetime - for handling date/time information
import datetime

# Classless functions

## getPageData
### function decorator to ensure that
### object retrieves page data before
### performing an operation
###
### @PARAMS
### 'func': class method to be called
def getPageData(func):
    def func_wrapper(self, *args):
        if (not(hasattr(self, 'pageData'))):
            self.getData()
        return func(self, *args)
    return func_wrapper

# Error classes

## ContentError
### error raised when provided content doesn't conform to markers
### specified by calling program or function
class ContentError(Exception):
    pass

# Main parser class

class WLParser(object):

    ## constructor
    ### takes in a baseURL (defaults to warlight.net)
    ### and creates URL querystring with specific
    ### provided parameters and values
    def __init__(self, baseURL=None, **kwargs):
        self.baseURL = "https://www.warlight.net/?"
        if baseURL is not None:
            self.baseURL = baseURL
        self.URL = self.makeURL(**kwargs)

    ## makeURL
    ### helper function for constructor
    ### generates URL querystring based on
    ### provided parameters and values
    def makeURL(self, **kwargs):
        URL = self.baseURL
        appendString = ""
        for kwarg in kwargs:
            appendString += "&"
            appendString += str(kwarg)
            appendString += "="
            appendString += str(kwargs[kwarg])
        URL += appendString[1:]
        return URL

    ## getData
    ### retrieves page data through an HTTP GET request
    ### optionally loops until the request completes
    ###
    ### @PARAMS
    ### 'loop' (string): whether to loop until request succeeds
    ### (default: True)
    def getData(self, loop=True):
        stop = False
        while (not stop):
            try:
                r = requests.get(self.URL)
                stop = True
            except:
                if (not loop): stop = True
        self.pageData = r.text

    ## getValueFromBetween
    ### gets a value in a text field situated between
    ### two known markers
    ###
    ### @PARAMS
    ### 'text' (string): text to extract from
    ### 'before' (string): known marker occurring before desired text
    ### 'after' (string): known marker occurring after desired text
    @staticmethod
    def getValueFromBetween(text, before, after):
        if before is None: before = ""
        if after is None: after = ""
        if (before not in text):
            raise ContentError("Missing 'before' marker: " + before +
                               " in " + text)
        if (after not in text):
            raise ContentError("Missing 'after' marker! " + after +
                               " in " + text)
        beforeLoc = text.find(before) + len(before)
        value = text[beforeLoc:]
        if (after == ""): return value
        afterLoc = value.find(after)
        value = value[:afterLoc]
        return value

    ## getTypedValue
    ### given a known marker and a string containing all values
    ### defining some acceptable type, returns values within a given
    ### text field directly after the known marker that all fall within the
    ### constraints of that acceptable type, terminating when a value
    ### outside the acceptable type is encountered
    ###
    ### @PARAMS
    ### 'text' (string): text field to extract data from
    ### 'marker' (string): known marker occurring before data to be extracted
    ### 'typeRange' (string): all members of a known type describing content to
    ###     be extracted
    ### 'check' (bool): default True; if True, will raise a ContentError
    ###     if there is no content in the desired range of the specified type
    @staticmethod
    def getTypedValue(text, marker, typeRange, check=True):
        if marker not in text:
            raise ContentError("Missing marker: " + marker + " in " +
                               text)
        loc = text.find(marker) + len(marker)
        text = text[loc:]
        data = ""
        while (len(text) > 0 and text[0] in typeRange):
            data += text[0]
            text = text[1:]
        if (check and (len(data) == 0)):
            raise ContentError("No content in specified range!")
        return data

    ## getNumericValue
    ### wrapper function for getTypedValue for numeric data
    ###
    ### @PARAMS:
    ### 'text' (string): text field to extract data from
    ### 'marker' (string): known marker occurring before data to be extracted
    @classmethod
    def getNumericValue(cls, text, marker):
        return float(cls.getTypedValue(text, marker, 
                                       (string.digits + ".+-")))

    ## getIntegerValue
    ### wrapper function for getTypedValue for integer data
    ###
    ### @PARAMS:
    ### 'text' (string): text field to extract data from
    ### 'marker' (string): known marker occuring before data to be extracted
    @classmethod
    def getIntegerValue(cls, text, marker):
        return int(cls.getTypedValue(text, marker,
                                     (string.digits + "-+")))

    ## getLetterValue
    ### wrapper function for getTypedValue for alphabetical data
    ###
    ### @PARAMS:
    ### 'text' (string): text field to extract data from
    ### 'marker' (string): known marker occurring before data to be extracted
    @classmethod
    def getLetterValue(cls, text, marker):
        return cls.getTypedValue(text, marker, (string.ascii_lowercase
                                 + string.ascii_uppercase))

    ## timeConvert
    ### converts time in string format to # of hours
    ###
    ### @PARAMS:
    ### 'timeString' (string): time in string format
    @staticmethod
    def timeConvert(timeString):
        timeString = timeString.replace(",", "")
        timeData = timeString.split(" ")
        count = Decimal(0)
        fieldTimes = dict()
        fieldTimes["year"] = Decimal(24) * Decimal(365.2425)
        fieldTimes["years"] = Decimal(24) * Decimal(365.2425)
        fieldTimes["month"] = Decimal(2) * Decimal(365.2425)
        fieldTimes["months"] = Decimal(2) * Decimal(365.2425)
        fieldTimes["day"] = Decimal(24)
        fieldTimes["days"] = Decimal(24)
        fieldTimes["hour"] = Decimal(1)
        fieldTimes["hours"] = Decimal(1)
        fieldTimes["minute"] = Decimal(1) / Decimal(60)
        fieldTimes["minutes"] = Decimal(1) / Decimal(60)
        fieldTimes["second"] = Decimal(1) / Decimal(3600)
        fieldTimes["seconds"] = Decimal(1) / Decimal(3600)
        fieldData = dict()
        for field in fieldTimes:
            if field not in timeData: continue
            loc = timeData.index(field)
            if (loc == 0): continue
            data = int(timeData[loc-1])
            count += (Decimal(data) * Decimal(fieldTimes[field]))
        return float(count)

    ## getDate
    ### creates datetime object from string-formatted date
    ### assumes American format (mm/dd/yyyy)
    ###
    ### @PARAMS
    ### 'dateString' (string): string formatted as mm/dd/yy date
    @staticmethod
    def getDate(dateString):
        dateData = dateString.split('/')
        month, day, year = (int(dateData[0]), int(dateData[1]),
                            int(dateData[2]))
        return datetime.date(year=year, month=month, day=day)

    ## getDateTime
    ### creates datetimeobject from string-formatted date and time
    ### assumes American date (mm/dd/yyyy) followed by hh:mm:ss time
    ###
    ### @PARAMS
    ### 'dateTimeString' (string): string formatted as mm/dd/yy hh:mm:ss
    @staticmethod
    def getDateTime(dateTimeString):
        dateString, timeString = dateTimeString.split(" ")
        dateData = dateString.split('/')
        month, day, year = (int(dateData[0]), int(dateData[1]),
                            int(dateData[2]))
        timeData = timeString.split(':')
        hour, minute, second = (int(timeData[0]), int(timeData[1]),
                                int(timeData[2]))
        return datetime.datetime(year=year, month=month, day=day,
                                 hour=hour, minute=minute,
                                 second=second)

    ## trimString
    ### removes leading and ending spaces in a string
    @staticmethod
    def trimString(string):
        while (string[0] == " " or string[0] == "\n"):
            string = string[1:]
        while (string[-1] == " " or string[-1] == "\n"):
            string = string[:-1]
        return string