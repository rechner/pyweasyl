#!/usr/bin/env python
# vim: set softtabstop=4:ts=4

import sys
import urllib
import urllib2
import json
from bs4 import BeautifulSoup

class Weasyl(object):
    ENDPOINT_URL = "https://www.weasyl.com/api/"
    USER_AGENT = 'Mozilla/4.0 (compatible; {0}) ' \
                 'PyWeasyl client 0.1a, '.format(sys.platform)
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'X-Weasyl-API-Key' : api_key
        }

    # json decoding raises a ValueError if there's a problem
    def _request(self, endpoint, params={}):
        data = urllib.urlencode(params)
        url = self.ENDPOINT_URL + endpoint
        print url, data
        req = urllib2.Request(url, data, self.headers)
        resp = urllib2.urlopen(req)
        return json.loads(resp.read())
            

    # GET requests:
    # ============
    def version(self):
        response = self._request('version')
        return response['short_sha']

    def whoami(self):
        return self._request('whoami')

    def useravatar(self, username=None):
        if username is None:
            response = self._request('useravatar')
        else:
            response = self._request('useravatar', { 'username': username })
        return response['avatar']



if __name__ == '__main__':
    api = Weasyl("APiKeyHere")
    print api.version()
