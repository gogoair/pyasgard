"""Python interface to Netflix Asgard REST API."""
__author__ = "Sijis Aviles <saviles@gogoair.com>"
__version__ = "1.0"

import base64
import inspect
import json
import logging
from pprint import pformat
from string import Template

import requests

from .endpoints import MAPPING_TABLE
from .htmltodict import HTMLToDict


class AsgardError(Exception):
    """Error from request to Asgard API."""

    def __init__(self, msg, error_code=None):
        super(AsgardError, self).__init__(msg)
        self.error_code = error_code

    def __str__(self):
        message = super(AsgardError, self).__str__()
        return repr('%s: %s' % (self.error_code, message))


class AsgardAuthenticationError(AsgardError):
    """Failed authentication with Asgard API."""

    def __init__(self, msg):
        super(AsgardAuthenticationError, self).__init__(msg, error_code=401)

    def __str__(self):
        return super(AsgardAuthenticationError, self).__str__()


class AsgardCommand(object):  # pylint: disable=R0903
    """Dynamic construction of attributes based on endpoint mapping table.

    Instead of writing out each API endpoint as a method here or binding
    the API endpoints at instance runttime, we can simply use an elegant
    Python technique to construct method execution on- demand. We simply
    provide a mapping table between Asgard API calls and function names
    (with necessary parameters to replace embedded keywords on GET or json
    data on POST/PUT requests).

    __getattr__() is used as callback method implemented so that when an
    object tries to call a method which is not defined here, it looks to
    find a relationship in the the mapping table.  The table provides the
    structure of the API call and parameters passed in the method will
    populate missing data.

    Raises:
        AttributeError: Attribute is not part of the mapping table.

    Returns:
        Dict representation of HTML or JSON returned from Asgard API.

    TODO:
        Should probably url-encode GET query parameters on replacement
    """

    def __init__(self, client, api_call, menu):
        super(AsgardCommand, self).__init__()

        self.log = logging.getLogger(__name__)
        self.log.debug('getattr locals():\n%s', pformat(locals()))

        self.client = client
        self.api_call = api_call

        # Missing method is also not defined in our mapping table
        try:
            self.api_map = menu[self.api_call]
            self.log.debug('api_map:\n%s', pformat(self.api_map))
        except KeyError:
            raise AttributeError(('Method "{0}" does not exist.\n'
                                  'Options available are: {1}').format(
                                      self.api_call, menu.keys()))

    def __dir__(self):
        """Dynamically generate attributes and methods based on endpoints."""
        self_keys = list(self.__dict__.keys())
        menu_keys = list(self.api_map.keys())
        return self_keys + menu_keys

    def __getattr__(self, command):
        """Recursively generate objects for endpoints."""
        return AsgardCommand(self.client, command, self.api_map)

    def __call__(self, **kwargs):
        """Request call to Asgard API.

        This constructs the outgoing request to your Asgard Server.

        Args:
            **kwargs: Only excepts keywords used in the endpoint mapping
                _path_, _valid_params_, and _default_params_.

        Returns:
            A dict of the HTML or JSON from Asgard.

        Raises:
            TypeError: If an unexpected keyword was passed in.
        """
        self.log.debug('call locals():\n%s', pformat(locals()))

        method = self.api_map['method']
        status = self.api_map['status']

        url = self.client.format_url(self.api_map['path'], kwargs)

        self.validate_params(kwargs)

        body = self.construct_body(kwargs)

        if method == 'GET':
            action = 'params'
        else:
            action = 'data'

        url_params = {
            'url': url,
            action: body,
            'headers': self.client.headers,
            'timeout': 15,
        }

        auth = self.client.get_auth()
        url_params.update(auth)

        response = self.client.asgard_request(method, url_params)

        return self.client.response_handler(response, status)

    def construct_body(self, kwargs):
        """Form body of request.

        Body can be passed from data or in args.

        Returns:
            Dict for body of request, e.g.::

                requests.get(url, params=body)
                requests.post(url, data=body)
        """
        # Provide a JSON object override
        if 'json' in kwargs:
            return json.dumps(kwargs['json'])

        body = {}
        body.update(self.api_map.get('default_params', {}))
        body.update(kwargs.pop('data', None) or self.client.data)
        body.update(kwargs)
        self.log.log(15, 'body=%s', body)

        return body

    def validate_params(self, kwargs):
        """Validate remaining kwargs against valid_params."""
        valid_params = self.api_map.get('valid_params', ())
        self.log.log(15, 'valid_params=%s', valid_params)

        for keyword in kwargs:
            if keyword not in valid_params:
                if 'default_params' not in self.api_map:
                    raise TypeError('Was not expecting any arguments.')
                elif keyword not in self.api_map['default_params']:
                    raise TypeError(('{0}() got an unexpected keyword '
                                     'argument "{1}"').format(self.api_call,
                                                              keyword))


class Asgard(object):
    """Python API Wrapper for Asgard."""

    def __init__(self,  # pylint: disable=R0913
                 url,
                 username=None,
                 password=None,
                 headers=None,
                 # client_args={},
                 api_version=1,
                 ec2_region='us-east-1'):
        """New Asgard object for interacting with the API.

        Instantiates an instance of Asgard. Takes optional parameters for
        HTTP Basic Authentication

        Parameters:
            url: https://company.asgard.com (use http if not SSL enabled).
            username: Specific to your asgard account.
            password: (b64encode(bytes)) Specific to your asgard account or
                your account's API token if use_api_token is True.
            headers: Pass headers in dict form, overrides default headers.
            api_version: Version number of Asgard API to use.
            ec2_region: AWS region to use.

        Not Implemented:
            use_api_token: Use api token for authentication instead of user's
                actual password.
            client_args: Pass arguments to http client in dict form.
                {'cache': False, 'timeout': 2}
                or a common one is to disable SSL certficate validation
                {"disable_ssl_certificate_validation": True}
        """
        self.log = logging.getLogger(__name__)
        self.log.debug('init locals():\n%s', pformat(locals()))

        self.data = {}
        self.url = '{0}/{1}'.format(url.rstrip('/'), ec2_region)
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

    def __dir__(self):
        self_keys = list(self.__dict__.keys())
        map_keys = list(self.mapping_table.keys())
        return self_keys + map_keys

    def __getattr__(self, api_call):
        # Execute dynamic method and pass in keyword args as data to API call
        return AsgardCommand(self, api_call, self.mapping_table)

    def decrypt_password(self, password):
        """Decrypt the encrypted password string.

        Args:
            password: String that has been encoded using b64encode(bytes).

        Returns:
            Decrypted password string.
        """
        password = base64.b64decode(password.encode('ascii'))
        self.log.debug('Password decrypted.')
        return password.decode()

    def get_auth(self):
        """Gets username and password for request authentication.

        Returns:
            Empty dict if no authentication specified, otherwise return::

                {'auth': (username, password)}
        """
        if self.username and self.password:
            return {'auth':
                    (self.username, self.decrypt_password(self.password))}

        return {}

    def format_url(self, path, kwargs):
        """Format request URL with endpoint mapping.

        Substitute `${}` placeholders with data from keywords. This removes the
        key from the dict to prevent reuse in parameters.

        Args:
            path: URL path string to use, e.g. /application
            kwargs: Dict containing any keys that need to be substituted in
                _path_.

        Returns:
            Fully constructed URL string with substitutions in place.
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

        url = '{0}{1}'.format(self.url, substitute_path)
        self.log.log(15, 'url=%s', url)

        return url

    def asgard_request(self, method, url_params):
        """Make an http request (data replacements are finalized)."""
        self.log.log(15, 'getattr(%s, %s)(%s)\n[auth] redacted', requests,
                     method.lower(), pformat(dict((
                         key, value
                     ) for key, value in url_params.items() if key != 'auth')))
        response = getattr(requests, method.lower())(**url_params)
        self.log.debug(pformat(inspect.getmembers(response)))

        return response

    def response_handler(self, response, status):
        """
        Handle response as callback

        If the response status is different from status defined in the
        mapping table, then we assume an error and raise proper exception

        Args:
            response: A requests.Response object from making request to Asgard
                API.
            status: Expected status integer.

        Returns:
            A dict mapping representation of the HTML or JSON returned from
            Asgard API call.

        Raises:
            AsgardError: Response is missing or status code is not expected.
            AsgardAuthenticationError: Asgard reported bad authentication.
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
            error = AsgardError(
                self.format_dict(response), response.status_code)
            self.log.fatal(error)
            raise error

        return self.format_dict(response)

    def format_dict(self, response):
        """Format the response into a dict from HTML or JSON."""
        # Deserialize json content if content exist. In some cases Asgard
        # returns ' ' strings. Also return false non strings (0, [], (), {})
        try:
            response_json = response.json()
            self.log.debug('Response JSON:\n%s', pformat(response_json))
            return response_json
        except ValueError:
            self.log.debug('Response HTML:\n%s', response.text)
            return HTMLToDict().dict(response.text)
