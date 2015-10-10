"""Python interface to Netflix Asgard REST API."""
__author__ = "Sijis Aviles <saviles@gogoair.com>"
__version__ = "1.0"

import base64
import logging
import re
from pprint import pformat

import requests

from endpoints import mapping_table as mapping_table

# try:
#     import simplejson as json
# except ImportError:
#     import json


def clean_kwargs(kwargs):
    """Format the kwargs to conform to API"""

    for key, value in kwargs.iteritems():
        if hasattr(value, '__iter__'):
            kwargs[key] = ','.join(map(str, value))


def decrypt_hash(string):
    """Decrypt the encrypted password string."""
    string = base64.b64decode(string)
    return string


class AsgardError(Exception):
    """Error from request to Asgard API."""

    def __init__(self, msg, error_code=None):
        super(AsgardError, self).__init__()
        self.msg = msg
        self.error_code = error_code

    def __str__(self):
        return repr('%s: %s' % (self.error_code, self.msg))


class AuthenticationError(AsgardError):
    """Failed authentication with Asgard API."""

    def __init__(self, msg):
        super(AuthenticationError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Asgard(object):  # pylint: disable=R0903
    """ Python API Wrapper for Asgard"""

    def __init__(self,
                 url,
                 username=None,
                 password=None,
                 headers=None,
                 # client_args={},
                 api_version=1,
                 ec2_region='us-east-1'):
        """
        Instantiates an instance of Asgard. Takes optional parameters for
        HTTP Basic Authentication

        Parameters:
        url - https://company.asgard.com (use http if not SSL enabled)
        username - Specific to your asgard account (typically email)
        password - (b64encode(str)) Specific to your asgard account or your
            account's API token if use_api_token is True
        use_api_token - use api token for authentication instead of user's
            actual password
        headers - Pass headers in dict form. This will override default.
        client_args - Pass arguments to http client in dict form.
            {'cache': False, 'timeout': 2}
            or a common one is to disable SSL certficate validation
            {"disable_ssl_certificate_validation": True}
        """
        logging.debug(pformat(locals()))
        self.data = None
        self.url = '{}/{}'.format(url.rstrip('/'), ec2_region)
        self.username = username
        self.password = password

        # Set headers
        self.headers = headers
        if self.headers is None:
            self.headers = {
                'User-agent': 'Asgard Python Library v%s' % __version__,
                'Content-Type': 'application/json'
            }

        self.api_version = api_version
        self.mapping_table = mapping_table

    def __getattr__(self, api_call):
        """
        Instead of writing out each API endpoint as a method here or
        binding the API endpoints at instance runttime, we can simply
        use an elegant Python technique to construct method execution on-
        demand. We simply provide a mapping table between Asgard API calls
        and function names (with necessary parameters to replace
        embedded keywords on GET or json data on POST/PUT requests).

        __getattr__() is used as callback method implemented so that
        when an object tries to call a method which is not defined here,
        it looks to find a relationship in the the mapping table.  The
        table provides the structure of the API call and parameters passed
        in the method will populate missing data.

        TODO:
            Should probably url-encode GET query parameters on replacement
        """

        def call(self, **kwargs):
            """Request to API based on method and endpoint mapping."""
            logging.debug(pformat(locals()))

            api_map = self.mapping_table[api_call]
            logging.debug(pformat(api_map))

            path = api_map['path']
            method = api_map['method']
            status = api_map['status']
            valid_params = api_map.get('valid_params', ())
            logging.debug('valid_params=%s', valid_params)
            # Body can be passed from data or in args
            body = kwargs.pop('data', None) or self.data

            # Substitute mustache '{{}}' placeholders with data from keywords
            # Optional pagination parameters will default to blank
            # regex_pattern = '\{\{(?P<m>[a-zA-Z_]+)\}\}'
            regex_pattern = '{{(?P<m>[a-zA-Z_]+)}}'
            url = re.sub(regex_pattern,
                         lambda m: '{}'.format(kwargs.pop(m.group(1), '')),
                         '{}{}'.format(self.url, path))
            logging.debug(url)

            # Validate remaining kwargs against valid_params and add
            # params url encoded to url variable.
            logging.debug(kwargs)
            for keyword in kwargs:
                if keyword not in valid_params:
                    raise TypeError("%s() got an unexpected keyword argument "
                                    "'%s'" % (api_call, keyword))

            # Make an http request (data replacements are finalized)
            url_params = {
                'url': url,
                'data': body,
                'headers': self.headers,
                'timeout': 15,
            }

            if self.username and self.password:
                auth = {'auth': (self.username, decrypt_hash(self.password))}
                url_params.update(auth)

            logging.debug(
                'getattr(%s, %s)(%s)', requests, method.lower(), pformat({
                    key: value
                    for key, value in url_params.items() if key != 'auth'
                }))

            response = getattr(requests, method.lower())(**url_params)
            logging.debug(response)

            return self._response_handler(response, status)

        logging.debug('Looking up %s', api_call)
        # Missing method is also not defined in our mapping table
        if api_call not in self.mapping_table:
            raise AttributeError('Method "%s" Does Not Exist' % api_call)

        # Execute dynamic method and pass in keyword args as data to API call
        return call.__get__(self)  # pylint: disable=E1101

    @staticmethod
    def _response_handler(response, status):
        """
        Handle response as callback

        If the response status is different from status defined in the
        mapping table, then we assume an error and raise proper exception
        """
        logging.debug(pformat(locals()))

        # Just in case
        if response is None:
            message = 'Response Not Found'
            logging.error(message)
            raise AsgardError(message)

        if response.status_code == 401:
            raise AuthenticationError(response.reason)

        if response.status_code != status:
            error = AsgardError(response.reason, response.status_code)
            logging.fatal(error)
            raise error

        # Deserialize json content if content exist. In some cases Asgard
        # returns ' ' strings. Also return false non strings (0, [], (), {})
        response_json = response.json()
        logging.debug(pformat(response_json))
        return response_json
