import httplib, urllib, urllib2
from urllib2 import HTTPError, URLError

SERVER_ADDRESS = "192.168.1.108:5000/post_info/1"

"""Attempts to open a url and returns the contents if url is correct
   returns False or none if error (404, etc)"""
 #set x to true if you want this function to print details
def getPage(url,data,verbose=False,):
    if url[:7] != "http://": url = "http://"+url

    data = urllib.urlencode(data)
    try:
        if verbose: print 'Trying to fetch',url

        headers = {"Content-type": "application/x-www-form-urlencoded",
           "Accept": "text/plain", "User-Agent":"PowerWatch v1.0"}
        req = urllib2.Request(url,data,headers)
        response = urllib2.urlopen(req)
        page = response.read()
        if verbose:
            print 'Fetch completed; Size:',len(page)
        return page
    except HTTPError, e:
        print 'The server couldn\'t fulfill the request. On URL',url
        print 'Error code:', e.code, responses[int(e.code)]
    except URLError, e:
        print 'Failed to reach',url
        print 'Reason:', e.reason

def sendData(data_):
    import json
    if not checkData(data_): return
    page = getPage(SERVER_ADDRESS, json.dumps(data_))
    return page == "OK"

#check the dictionary if it has the valid 
def checkData(data_):
    import collections

    print "checking if data has valid values"
    keys_tocheck = ["watts","va","vr","pf","volt","amp"]
    valid = collections.Counter(keys_tocheck) == collections.Counter(data_.keys())
    print "VALID?",valid

    return valid

responses = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}   
