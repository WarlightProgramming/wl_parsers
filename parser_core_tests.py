# automated tests for parser_core.py

from nose.tools import *
from parser_core import *
from datetime import *

# decorator test

class PageDataTester(object):

    def getData(self):
        self.pageData = "abacus"

    @getPageData
    def testFunction(self):
        pass

def test_getPageData():
    pdTester = PageDataTester()
    assert (hasattr(pdTester, 'pageData') == False)
    pdTester.testFunction()
    assert (pdTester.pageData == "abacus")

# main parser class test

## no explicit test for makeURL
## currently implicitly tested with constructor

def test_WLParser():
    # test constructor
    ## with no base URL or parameters
    testParser = WLParser()
    assert_equals(testParser.baseURL, "https://www.warlight.net/?")
    assert_equals(testParser.URL, testParser.baseURL)
    ## with base URL
    testURL = "http://testURL.com/?"
    testParser = WLParser(testURL)
    assert_equals(testParser.baseURL, testURL)
    assert_equals(testParser.URL, testURL)
    ## with base URL and parameters
    testParser = WLParser(testURL, param="data", param2=4)
    assert_equals(testParser.baseURL, testURL)
    assert_equals(testParser.URL, (testURL + "param2=4&param=data"))

# static method tests

def test_getValueFromBetween():
    text = "abacus"
    before = "a"
    after = "a"
    assert_equals(WLParser.getValueFromBetween(text, before, after),
                  "b")
    after = "cus"
    assert_equals(WLParser.getValueFromBetween(text, before, after),
                  "ba")
    before = ""
    assert_equals(WLParser.getValueFromBetween(text, before, after),
                  "aba")
    after = ""
    assert_equals(WLParser.getValueFromBetween(text, before, after),
                  "abacus")

def test_getTypedValue():
    text = "abc123"
    marker = "c"
    typeRange = "bc12"
    assert_equals(WLParser.getTypedValue(text, marker, typeRange),
                  "12")
    marker = "a"
    assert_equals(WLParser.getTypedValue(text, marker, typeRange),
                  "bc12")
    typeRange = "123"
    marker = "c"
    assert_equals(WLParser.getTypedValue(text, marker, typeRange),
                  "123")
    typeRange = "c"
    assert_equals(WLParser.getTypedValue(text, marker, typeRange, False),
                  "")

def test_getNumericValue():
    text = "aksjdflakvlkajsdlfj2390vkj;sadfkj;vaglskdfj"
    marker = "sdlfj"
    assert_equals(WLParser.getNumericValue(text, marker), 2390)
    text = "aksjdflakvlkajsdlfj23.90vkj;sadfkj;vaglskdfj"
    assert_equals(WLParser.getNumericValue(text, marker), 23.90)

def test_getIntegerValue():
    text = "aksjdflakvlkajsdlfj2390vkj;sadfkj;vaglskdfj"
    marker = "sdlfj"
    assert_equals(WLParser.getIntegerValue(text, marker), 2390)
    text = "aksjdflakvlkajsdlfj23.90vkj;sadfkj;vaglskdfj"
    assert_equals(WLParser.getIntegerValue(text, marker), 23)

def test_getLetterValue():
    text = "lskajs aslfdlkjfdslsflkjdfl salka;ldfkflfkf"
    marker = "jdfl "
    assert_equals(WLParser.getLetterValue(text, marker), "salka")
    marker = "ldfk"
    assert_equals(WLParser.getLetterValue(text, marker), "flfkf")

def test_timeConvert():
    tc = WLParser.timeConvert
    basic = "1 hour"
    assert_equals(tc(basic), 1)
    multi = "1039 hours"
    assert_equals(tc(multi), 1039)
    comprehensive = ("1 year, 6 months, 2 days, 12 hours, "
                     "49 minutes, and 12 seconds")
    assert_almost_equal(tc(comprehensive), 13209.55, places=2)

def test_getDate():
    gd = WLParser.getDate
    testString = "09/01/2013"
    assert_equals(gd(testString), date(2013, 9, 1))

def test_getDateTime():
    gdt = WLParser.getDateTime
    testString = "09/01/2013 04:20:00"
    assert_equals(gdt(testString), datetime(2013, 9, 1,
                                            4, 20, 0))

def test_trimString():
    testString = """    
                    this is the only text that matters


                 """
    assert_equals(WLParser.trimString(testString), 
                  "this is the only text that matters")