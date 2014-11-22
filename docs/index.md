PyWeasyl
========

Python bindings for the [Weasyl HTTP API](https://projects.weasyl.com/weasylapi/), version 1.2.

## Getting Started

Some features, such as listing galleries, and viewing public submissions
can be accomplished without authentication, however however the API is
most useful when dealing with accounts through use of an API key. Keys
can be generated for your own account under 
[Settings > Manage API Keys](https://www.weasyl.com/control/apikeys).

Then just pass the API key using the constructor:

```python
from weasyl import Weasyl
api = Weasyl("AA8grlkP7...")
```

The API key can later be changed by accessing the `api_key` attribute:

```python
api.api_key = ''  # Revert to unauthorized operation
```

## Basic Methods
### Weasyl.version()
`version(self)`

The current version of Weasyl, as a shortened SHA string.

```python
>>> api.version()
u'c759381'
```

### Weasyl.whoami()
`whoami(self)`

The currently logged-in user, as a dictionary.  For example:

`{"login": "weykent, "userid" : 5756}`

If there is no current user (running unauthorized), this will raise
[Weasyl.Unauthorized](#weasylunauthorized).

### Weasyl.useravatar()
`useravatar(self, username)`

Returns the URL for a given user's avatar.  For users without an avatar,
this will return the default avatar icon.  If the user does not exist,
an [Weasyl.Unauthorized](#weasylunauthorized) exception is raised.

#### Arguments:
- *username* - The user's login name, all lower-case alpha-numeric string.


### Weasyl.frontpage()
`frontpage(self, since=None, count=None)`

A list of submissions from the front page, respecting the current user's
browsing settings.

#### Optional arguments:
- `since` - An ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ) in UTC.  If
    privided, will only show frontpage submissions after the timestamp.
- `count` - If specified, no more than this many submissions will be returned.

Returns at most 100 submissions, and a 'count' value exceeding 100 will
be coerced to 100.  Submissions returned are filtered by user's tag filters
set through site preferences.

The structure returned is a [submission object](https://projects.weasyl.com/weasylapi/#submissions).

### Weasyl.view_submission()
`view_submission(self, submitid, anyway=False, increment_views=False)`

Returns a [submission object](https://projects.weasyl.com/weasylapi/#submissions)
containing all data pertaining to a particular submission (image). Raises
[Weasyl.Forbidden](#weasylforbidden) with reason 
`'submissionRecordMissing'` if the submission does not exist.

#### Arguments:
- `submitid` - The reference ID of the submission.

#### Optional arguments:
- `anyway` - If False, the current user's tag filters may cause an error
    to be returned instead of a submission object.  When True (or
    non-empty), tag filters will be ignored.
- `increment_views`- If False, the view count for the submission will
    not be incremented. If True while authenticated, the view count may
    be increased.

### Weasyl.view_user()
`view_user(self, username)`

Retrieves information about a user.  Returns an [user object](https://projects.weasyl.com/weasylapi/#users)
as a python dictionary.

### Weasyl.user_gallery()
`user_gallery(self, username[, since=None], [count=None], [folderid=None], [backid=None], [nextid=None])`

Fetches the gallery for a user by login name.  Returns a maximum of 100
submissions per request.  The result is a dictionary with three keys:
`submissions`, `backid`, and `nextid`.  `submissions` will be an array
of [submission objects](https://projects.weasyl.com/weasylapi/#submissions).
`backid` and `nextid` are used for [pagination](https://projects.weasyl.com/weasylapi/#pagination).

#### Arguments:
- `username` - Login name of user.

#### Optional arguments:
- `since` - An ISO 8601 timestamp.  Only submissions made after this time
    will be returned.
- `count` - Limit submissions returned to this number.
- `folderid` - Return only submissions matching the given `folderid`.
- `backid` - Return only submissions with a `submitid` greater than `backid`.
- `nextid` - Return only submissions with a `submitid` less than `nextid`.

### Weasyl.message_submissions()
`message_submissions(self, count=None, backtime=None, nexttime=None)`

List submissions in an authenticated user's inbox.  Returns a maximum of
100 submissions per request.  The result is a dictinoary with three keys:
`submissions`, `backid`, and `nextid`.  `submissions` will be an array
of [submission objects](https://projects.weasyl.com/weasylapi/#submissions).
`backid` and `nextid` are used for [pagination](https://projects.weasyl.com/weasylapi/#pagination).

#### Optional arguments:
- `count` - Limit number of submissions returned.
- `backtime` - Return only submissions with a unixtime greater than 
    `backtime` for pagination.
- `nexttime` - Return only submissison with a unixtime less than
    `nexttime` for pagination.

### Weasyl.message_summary():
`message_summary(self)`

Lists summary of notifications for an authenticated user.  The result
contains the following keys containing integers:

- `comments`
- `journals`
- `notifications`
- `submissions`
- `unread_notes`

Note that the result of this endpoint is cached by the server. New
information is only available every three minutes or when a new note
arrives.

### oauth2_authorize():
`oauth2_authorize(self, client_id, redirect_uri, state, scope='whilesite', response_type='code')`

The standard OAuth2 authorization endpoint.  Currently only authorisation
code grants with callback URIs are supported.

#### Arguments:
- `client_id` - The client identifier issued to the consumer by Weasyl.
- `redirect_uri` - The callback URI the consumer provided to Weasyl before
    the client_id was issued.
- `state` - A random, unguessable string.

#### Keyword arguments:
- `scope` - Currently, the only allowed scope is "wholesite".
- `response_type` - Currently, the only allowed response type is "code".

On successful authorisation, the user agent will be redirected to the
`redirect_uri` with the query parameters of `code` and `state`.  `code`
will be a random string used to retrieve the authorisation code grant,
and `state` will be the same `state` that was passed originally.

### oauth2_token():
`oauth2_token(self, client_secret, **kwargs)`

The endpoint for fetching and refreshing OAuth2 tokens.

#### Arguments:
- `client_secret` - The client secret issued to the consumer by Weasyl.

This function accepts additional form parameters passed by keyword
argument, as described in the [OAuth2 RFC](http://tools.ietf.org/html/rfc6749#section-6).

Note: Access tokens expire after one hour, be sure to use the provided
refresh token before then.

## Exceptions
If you get a Weasyl.Unauthorized exception with reason 'unauthorized',
it most likely means you got the API key wrong, or the API key is revoked
(opposed to being unset, which will result in a 'Session unsigned' message).

### Weasyl.Error
Base exception class.  All exceptions provide the following attributes:

- `error` - A string containing a human-readable error message.
- `code` - A Weasyl-provided error code number.
- `http_reason` - The HTTP error code which resulted in the error.

### Weasyl.Unauthorized
Equivalent to HTTP 401.  Generally returned if you attempt to access
data available only to registered identities.

### Weasyl.Forbidden
Equivalent to HTTP 403.

### Weasyl.NotFound
Equivalent to HTTP 404.

### Weasyl.Unprocessable
Equivalent to HTTP 422.

### Weasyl.ServerError
Equivalent to HTTP 500.
