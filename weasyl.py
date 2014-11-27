#!/usr/bin/env python
#*-* coding: utf-8 *-*
# vim: set softtabstop=4:ts=4

# Python bindings for the Weasyl REST API.
# Copyright (C) 2014 Rechner Fox

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Python binding to implement the Weasyl HTTP API, version 1.2.
https://projects.weasyl.com/weasylapi/

Where specified, ``login name`` and ``user name`` refer to a
username in all lowercase, of only alphanumeric ASCII characters.

All dates are referenced in ISO 8601 UTC time: ``YYYY-MM-DDTHH:MM:SSZ``
"""

import sys
import urllib
import urllib2
import json
#from bs4 import BeautifulSoup

class Weasyl(object):
    """
    Initialize with an API key for authenticated operation.
    """
    ENDPOINT_URL = "https://www.weasyl.com/api/"
    USER_AGENT = 'Mozilla/4.0 (compatible; {0}) ' \
                 'PyWeasyl client 0.1a, '.format(sys.platform)

    def __init__(self, api_key=''):
        self._api_key = api_key
        self.headers = {}
        if api_key != '':
            self.headers = {
                'X-Weasyl-API-Key' : api_key
            }

    def __repr__(self):
        return "<{0}('{1}')".format(self.__class__.__name__, self.api_key)

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        self._api_key = api_key
        self.headers = {} # URLLib2 or Weasyl gets weird when headers are blank
        if api_key != '':
            self.headers = {
                'X-Weasyl-API-Key' : api_key
            }

    # json decoding raises a ValueError if there's a problem
    def _GET_request(self, endpoint, params={}):
        params = self._cullParameters(params)
        data = urllib.urlencode(params)
        # urllib doesn't like us skipping parameters
        url = "{0}{1}?{2}".format(self.ENDPOINT_URL, endpoint, data)
        req = urllib2.Request(url, None, self.headers)
        try:
            resp = urllib2.urlopen(req)
            resp_decoded = json.loads(resp.read())
        except urllib2.HTTPError as e:
            err = 'Unspecified'
            code = -1
            resp = e.read()
            try:  # Server might return plain text if API key is wrong
                resp_decoded = json.loads(resp)
            except ValueError:
                err = resp
                resp_decoded = {}
            if 'error' in resp_decoded:
                # First case according to spec, second observed
                if 'name' in resp_decoded['error']:
                    err = resp_decoded['error']['name']
                else:
                    err = resp_decoded['error']['text']
                if 'code' in resp_decoded['error']:
                    code = resp_decoded['error']['code']

            if e.code == 401:
                raise self.Unauthorized(err, code, e.reason)
            elif e.code == 403:
                raise self.Forbidden(err, code, e.reason)
            elif e.code == 404:
                raise self.NotFound(err, code, e.reason)
            elif e.code == 422:
                raise self.Unprocessable(err, code, e.reason)
            elif e.code == 500:
                raise self.ServerError(err, code, e.reason)
        return resp_decoded

    def _POST_request(self, endpoint, params={}):
        params = self._cullParameters(params)
        data = urllib.urlencode(params)
        # urllib doesn't like us skipping parameters
        if data == '':
            data = None
        url = "{0}{1}".format(self.ENDPOINT_URL, endpoint)
        req = urllib2.Request(url, data, self.headers)
        resp = urllib2.urlopen(req)
        return resp.read()

    # remove keys from a dictionary with None-type values
    def _cullParameters(self, params):
        for key in params.keys():
            if params[key] is None:
                del params[key]
        return params

    # GET requests:
    # ============
    def version(self):
        """
        The current version of Weasyl, as a shortened SHA string.
        """
        response = self._GET_request('version')
        return response['short_sha']

    def whoami(self):
        """
        The currently logged-in user, as JSON.  For example:
            {"login": "weykent", "userid": 5756}

        If there is no current user, this will raise
        a 401 Error.
        """
        return self._GET_request('whoami')

    def useravatar(self, username):
        """
        Returns the URL for a given user's avatar.

        Arguments:
            * username -- The user's login name.

        Users without an avatar will get the default avatar icon back.
        If the user does not exist, this may return a 401 Error.
        """
        # Got even easier
        return 'https://www.weasyl.com/~{0}/avatar'.format(username)

        #response = self._GET_request('useravatar',
        #                             { 'username': username })
        #return response['avatar']

    def frontpage(self, since=None, count=None):
        """
        A list of submissions from the front page, respecting the
        current user's browsing settings.

        Keyword arguments (optional):
            * since - An ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
                (in UTC)
            * count - If specified, no more than this many
                submissions will be returned.

        This will return at most 100 submissions, and a 'count'
        value exceeding 100 will be coerced to 100.  Submissions
        are filtered by user's tag filters or other options.

        The datastructure returned is of the type submission objects.
        (https://projects.weasyl.com/weasylapi/#submissions)
        """
        params = { 'since' : since, 'count' : count }
        return self._GET_request('submissions/frontpage', params)


    def view_submission(self, submitid, anyway=False,
                        increment_views=False):
        """
        Returns a submission object to view a particular submission
        (image).

        Arguments:
            * submitid -- The reference ID of the submission.

        Keyword arguments (optional):
            * anyway -- If False, the current user's tag filters may
                cause an error to be returned instead of a submission
                object.  When True (or non-empty), tag filters will
                be ignored.
            * increment_views -- If False, the view count for the
                submission will not be incremented.  If True while
                authenticated, the view count may be increased.

        Raises Weasyl.Forbidden with reason 'submissionRecordMissing'
        if the submission does not exist.
        """
        if not anyway:  # 'anyway' parameter just needs to be non-empty
            anyway = None
        if not increment_views:
            increment_views = False
        params = {
            'anyway' : anyway,
            'increment_views' : increment_views
        }
        url = 'submissions/{0:d}/view'.format(submitid)
        return self._GET_request(url, params)

    def view_user(self, username):
        """
        Retrieves information about a user.

        Arguments:
            * username -- Login name of user.

        Returns an user object.
        https://projects.weasyl.com/weasylapi/#users
        """
        url = 'users/{0}/view'.format(username)
        return self._GET_request(url)

    def user_gallery(self, username, since=None, count=None,
                     folderid=None, backid=None, nextid=None):
        """
        Fetches the gallery for a user by login name.

        Arguments:
            * username -- Login name of user.

        Keyword arguments (optional):
            * since -- An ISO 8601 timestamp.  Only submissions made
                after this time will be returned.
            * count -- Limit submissions returned to this number.
            * folderid - Return only submissions matching the given
                `folderid`.
            * backid -- Return only submissions with a `submitid` greater
                than `backid`.
            * nextid -- Return only submissions with a `submitid` less
                than `nextid`.

        Returns a maximum of 100 submissions per request.  The result is
        a dictionary with three keys: submissions, backid, and nextid.
        `submissions` will be an array of submission objects.
        https://projects.weasyl.com/weasylapi/#submissions

        `backid` and `nextid` are used for pagination.
        https://projects.weasyl.com/weasylapi/#pagination
        """
        url = 'users/{0}/gallery'.format(username)
        return self._GET_request(url)

    def message_submissions(self, count=None, backtime=None,
                            nexttime=None):
        """
        List submissions in an authenticated user's inbox.

        Keyword arguments (optional):
            * count -- Limit number of submissions returned
            * backtime - Return only submissions with a unixtime
                greater than `backtime` for pagination.
            * nexttime - Return only submissions with a unixtime
                less than `nexttime` for pagination.

        Returns a maximum of 100 submissions per request.  The result is
        a dictionary with three keys: submissions, backid, and nextid.
        `submissions` will be an array of submission objects.
        https://projects.weasyl.com/weasylapi/#submissions

        `backid` and `nextid` are used for pagination.
        https://projects.weasyl.com/weasylapi/#pagination
        """
        params = {
            'count' : count,
            'backtime' : backtime,
            'nexttime' : nexttime
        }
        return self._GET_request('messages/submissions', params)

    def message_summary(self):
        """
        Lists summary of notifications for an authenticated user. The
        result contains the following keys:
            * comments
            * journals
            * notifications
            * submissions
            * unread_notes

        Note: The result of this endpoint is cached by the server.
        New information is only available every three minutes or when
        a new note arrives.
        """
        return self._GET_request('messages/summary')

    def oauth2_authorize(self, client_id, redirect_uri, state,
                         scope='whilesite', response_type='code'):
        """
        The standard OAuth2 authorization endpoint.  Currently only
        authorisation code grants with callback URIs are supported.

        Arguments:
            * client_id -- The client identifier issued to the
                consumer by Weasyl.
            * redirect_uri -- The callback URI the consumer provided
                to Weasyl before the client_id was issued.
            * state -- A random, unguessable string.

        Keyword arguments (optional):
            * scope -- Currently, only one scope is allowed: "wholesite".
            * response_type -- Currently, only one response type is
                allowed: "code".

        On successful authorisation, the user agent will be redirected
        to the `redirect_uri` with the query parameters of `code` and
        `state`.  `code` will be a random string used to retrieve the
        authorisation code grant, and `state` will be the same `state`
        as was passed originally.
        """
        params = {
            'client_id' : client_id,
            'redirect_uri' : redirect_uri,
            'scope' : scope,
            'state' : state,
            'response_type' : response_type
        }
        return self._GET_request('oauth2/authorize', params)

    def oauth2_token(self, client_secret, **kwargs):
        """
        The endpoint for fetching and refreshing OAuth2 tokens.

        Arguments:
            * client_secret -- The client secret issued to the consumer
                by Weasyl.

        This function accepts additional form parameters passed
        by keyword argument, as described in
        http://tools.ietf.org/html/rfc6749#section-6

        Note: Access tokens expire after an hour, be sure to use the
        provided refresh token before then.
        """
        params = kwargs
        params['client_secret'] = client_secret
        self._POST_request('oauth2/token', kwargs)

    class Error(Exception):
        """Base exception class"""
        def __init__(self, err, code=-1, http_reason=''):
            self.error = err
            self.code = code
            self.http_reason = http_reason
        def __str__(self):
            return repr(self.error)

    class Unauthorized(Error):
        pass

    class Forbidden(Error):
        pass

    class NotFound(Error):
        pass

    class Unprocessable(Error):
        pass

    class ServerError(Error):
        pass

if __name__ == '__main__':
    #TODO: Turn these into test cases
    api = Weasyl()
    #print api.version()
    #print api.whoami()
    #print api.useravatar('rechner')
    #print api.view_submission(602979) #General
    #print api.view_submission(789591) #18+ submission
    #print api.view_submission(999999) #DNE
    #print api.frontpage(count=10)
    #print api.view_user('rechner')
    #print api.user_gallery('rechner')
    #print api.message_submissions()
    #print api.message_summary()

