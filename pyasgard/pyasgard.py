"""Python interface to Netflix Asgard REST API."""
__author__ = "Sijis Aviles <saviles@gogoair.com>"
__version__ = "1.0"

import base64
import inspect
import logging
from pprint import pformat
from string import Template

import requests

from endpoints import MAPPING_TABLE


class AsgardError(Exception):
    """Error from request to Asgard API."""

    def __init__(self, msg, error_code=None):
        super(AsgardError, self).__init__()
        self.msg = msg
        self.error_code = error_code

    def __str__(self):
        return repr('%s: %s' % (self.error_code, self.msg))


class AsgardAuthenticationError(AsgardError):
    """Failed authentication with Asgard API."""

    def __init__(self, msg):
        super(AsgardAuthenticationError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class Asgard(object):  # pylint: disable=R0903
    """Python API Wrapper for Asgard."""

    def __init__(self,  # pylint: disable=R0913
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
        self.log = logging.getLogger(__name__)
        self.log.debug('init locals():\n%s', pformat(locals()))

        self.data = {}
        self.url = '{}/{}'.format(url.rstrip('/'), ec2_region)
        self.username = username
        self.password = password

        # Set headers
        self.headers = headers
        if self.headers is None:
            self.headers = {
                'User-agent': 'Asgard Python Library v%s' % __version__,
            }

        self.api_version = api_version
        self.mapping_table = MAPPING_TABLE

    def decrypt_hash(self, string):
        """Decrypt the encrypted password string."""
        string = base64.b64decode(string)
        self.log.debug('Password decrypted.')
        return string

    def __dir__(self):
        return self.__dict__.keys() + self.mapping_table.keys()

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
            """Request call to Asgard API."""
            self.log.debug('call locals():\n%s', pformat(locals()))

            api_map = self.mapping_table[api_call]
            self.log.debug('api_map:\n%s', pformat(api_map))

            method = api_map['method']
            status = api_map['status']
            valid_params = api_map.get('valid_params', ())
            self.log.log(15, 'valid_params=%s', valid_params)

            url = self._format_url(api_map['path'], kwargs)

            # Validate remaining kwargs against valid_params and add
            # params url encoded to url variable.
            for keyword in kwargs:
                if keyword not in valid_params:
                    raise TypeError("%s() got an unexpected keyword argument "
                                    "'%s'" % (api_call, keyword))

            # Body can be passed from data or in args
            body = {}
            body.update(api_map.get('default_params', {}))
            body.update(kwargs.pop('data', None) or self.data)
            body.update(kwargs)
            self.log.log(15, 'body=%s', body)

            if method == 'GET':
                action = 'params'
            else:
                action = 'data'

            url_params = {
                'url': url,
                action: body,
                'headers': self.headers,
                'timeout': 15,
            }

            if self.username and self.password:
                auth = {'auth': (self.username, self.decrypt_hash(self.password))}
                url_params.update(auth)

            # Make an http request (data replacements are finalized)
            self.log.log(
                15, 'getattr(%s, %s)(%s)\n[auth] redacted', requests,
                method.lower(), pformat({
                    key: value
                    for key, value in url_params.items() if key != 'auth'
                }))
            response = getattr(requests, method.lower())(**url_params)
            self.log.debug(pformat(inspect.getmembers(response)))

            return self._response_handler(response, status)

        ##################
        # Starting point #
        ##################
        self.log.debug('getattr locals():\n%s', pformat(locals()))

        # Missing method is also not defined in our mapping table
        if api_call not in self.mapping_table:
            raise AttributeError('Method "%s" Does Not Exist' % api_call)

        # Execute dynamic method and pass in keyword args as data to API call
        return call.__get__(self)  # pylint: disable=E1101

    def _format_url(self, path, kwargs):
        """Format request URL with endpoint mapping.

        Substitute mustache '{{}}' placeholders with data from keywords.
        """
        self.log.debug('URL formatter locals:\n%s', pformat(locals()))

        # get keys parsed
        path_keys = [param[2] for param in Template.pattern.findall(path)]
        self.log.debug('Template find=%s', Template.pattern.findall(path))
        self.log.debug('path_keys=%s', path_keys)

        # Substitute mustache '{}' placeholders with data from keywords
        substitute_path = Template(path).substitute(kwargs)
        self.log.debug('substitute_path=%s', substitute_path)

        self.log.debug('kwargs before pop=%s', pformat(kwargs))

        # remove ${} parameter from url, so its not added to querystring
        for param in path_keys:
            self.log.debug('Removing url param: %s', param)
            kwargs.pop(param)

        self.log.debug('kwargs after pop=%s', pformat(kwargs))

        url = '{}{}'.format(self.url, substitute_path)
        self.log.log(15, 'url=%s', url)

        return url

    def _response_handler(self, response, status):
        """
        Handle response as callback

        If the response status is different from status defined in the
        mapping table, then we assume an error and raise proper exception
        """

        self.log.debug('Expected response status: %s', status)
        self.log.debug('Request response:\n%s',
                  pformat(inspect.getmembers(response)))

        # Just in case
        if response is None:
            message = 'Response Not Found'
            self.log.error(message)
            raise AsgardError(message)

        if response.status_code == 401:
            raise AsgardAuthenticationError(response.reason)

        if response.status_code != status:
            error = AsgardError(response.reason, response.status_code)
            self.log.fatal(error)
            raise error

        # Deserialize json content if content exist. In some cases Asgard
        # returns ' ' strings. Also return false non strings (0, [], (), {})
        try:
            response_json = response.json()
            self.log.debug('Response JSON:\n%s', pformat(response_json))
            return response_json
        except ValueError:
            self.log.debug('Response HTML:\n%s', response.text)
            return response.text
