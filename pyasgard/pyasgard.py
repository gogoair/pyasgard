__author__ = "Sijis Aviles <saviles@gogoair.com>"
__version__ = "1.0"

import re
import httplib2
import urllib
try:
    import simplejson as json
except:
    import json
from httplib import responses
from endpoints import mapping_table as mapping_table

class AsgardError(Exception):
    def __init__(self, msg, error_code=None):
        self.msg = msg
        self.error_code = error_code

    def __str__(self):
        return repr('%s: %s' % (self.error_code, self.msg))


class AuthenticationError(AsgardError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def get_id_from_url(url):
    match = re_identifier.match(url)
    if match and match.group('identifier'):
        return match.group('identifier')


def clean_kwargs(kwargs):
    """Format the kwargs to conform to API"""

    for key, value in kwargs.iteritems():
        if hasattr(value, '__iter__'):
            kwargs[key] = ','.join(map(str, value))


class Asgard(object):
    """ Python API Wrapper for Asgard"""

    def __init__(self, asgard_url, asgard_username=None,
                 asgard_password=None, headers=None,
                 client_args={}, api_version=1, ec2_region='us-east-1'):
        """
        Instantiates an instance of Asgard. Takes optional parameters for
        HTTP Basic Authentication

        Parameters:
        asgard_url - https://company.asgard.com (use http if not SSL enabled)
        asgard_username - Specific to your asgard account (typically email)
        asgard_password - Specific to your asgard account or your account's
            API token if use_api_token is True
        use_api_token - use api token for authentication instead of user's
            actual password
        headers - Pass headers in dict form. This will override default.
        client_args - Pass arguments to http client in dict form.
            {'cache': False, 'timeout': 2}
            or a common one is to disable SSL certficate validation
            {"disable_ssl_certificate_validation": True}
        """
        self.data = None
        self.asgard_url = '{}/{}'.format(asgard_url.rstrip('/'), ec2_region)
        self.asgard_username = asgard_username
        self.asgard_password = asgard_password

        # Set headers
        self.headers = headers
        if self.headers is None:
            self.headers = {
                'User-agent': 'Asgard Python Library v%s' % __version__,
                'Content-Type': 'application/json'
            }

        # Set http client and authentication
        self.client = httplib2.Http(**client_args)
        if (self.asgard_username is not None and
                self.asgard_password is not None):
            self.client.add_credentials(
                self.asgard_username,
                self.asgard_password
            )

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
            """ """
            api_map = self.mapping_table[api_call]
            path = api_map['path']

            method = api_map['method']
            status = api_map['status']
            valid_params = api_map.get('valid_params', ())
            # Body can be passed from data or in args
            body = kwargs.pop('data', None) or self.data

            # Substitute mustache '{{}}' placeholders with data from keywords
            url = re.sub(
                '\{\{(?P<m>[a-zA-Z_]+)\}\}',
                # Optional pagination parameters will default to blank
                #lambda m: "%s" % kwargs.pop(m.group(1), ''),
                lambda m: '{}'.format(kwargs.pop(m.group(1), '')),
                '{}{}'.format(self.asgard_url, path)
            )

            # Validate remaining kwargs against valid_params and add
            # params url encoded to url variable.
            for kw in kwargs:
                if kw not in valid_params:
                    raise TypeError("%s() got an unexpected keyword argument "
                                    "'%s'" % (api_call, kw))
            else:
                clean_kwargs(kwargs)
                url += '?' + urllib.urlencode(kwargs)

            #clean_kwargs(kwargs)
            #url += '?' + urllib.urlencode(kwargs)

            return self._response_handler_test(url)
            # Make an http request (data replacements are finalized)
            '''
            response, content = \
                self.client.request(
                    url,
                    method,
                    body=json.dumps(body),
                    headers=self.headers
                )
            # Use a response handler to determine success/fail
            return self._response_handler(response, content, status)
            '''

        # Missing method is also not defined in our mapping table
        if api_call not in self.mapping_table:
            raise AttributeError('Method "%s" Does Not Exist' % api_call)

        # Execute dynamic method and pass in keyword args as data to API call
        return call.__get__(self)

    @staticmethod
    def _response_handler(response, status):
        """
        Handle response as callback

        If the response status is different from status defined in the
        mapping table, then we assume an error and raise proper exception

        Asgard's response is sometimes the url of a newly created user/
        ticket/group/etc and they pass this through 'location'.  Otherwise,
        the body of 'content' has our response.
        """
        # Just in case
        if not response:
            raise AsgardError('Response Not Found')

        if response.status_code != status:
            raise AsgardError(response.reason, response.status_code)

        # Deserialize json content if content exist. In some cases Asgard
        # returns ' ' strings. Also return false non strings (0, [], (), {})
        return response.json()
