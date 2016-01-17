"""AsgardCommand Class for pyasgard."""
import json
import logging
from pprint import pformat

from .exceptions import AsgardError


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

    def __init__(self, client, api_call, menu, parent='Asgard'):
        super(AsgardCommand, self).__init__()

        self.__name__ = '.'.join([parent, api_call])

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
        next_api = self.api_map.get(command, None)

        if isinstance(next_api, dict):
            self.log.debug('Next API level: %s', next_api)
            return AsgardCommand(self.client,
                                 command,
                                 self.api_map,
                                 parent=self.__name__)
        else:
            self.log.debug('Reached leaf "%s" of map: %s', command, next_api)
            return next_api

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

        try:
            return self.client.response_handler(response, status)
        except AsgardError:
            raise

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
