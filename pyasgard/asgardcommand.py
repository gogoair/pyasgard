"""AsgardCommand Class for pyasgard."""
import json
import logging
from collections import OrderedDict
from pprint import pformat

from .exceptions import AsgardError

# HACK: Python 2.7 is missing cool modules
try:
    from inspect import Parameter, Signature
except ImportError:
    pass


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
        self.log = logging.getLogger(__name__)

        self.__name__ = '.'.join([parent, api_call])
        self.log.debug('Command name: %s', self.__name__)

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

        try:
            docstring = self.api_map['doc']
        except (KeyError, TypeError):
            docstring = 'No docstring provided.'

        # The remainder of this __init__ is the result of fighting docstrings
        # while supporting Python 2.7, 3.4, and 3.5
        try:
            self.__class__.__doc__ = docstring
            self.__class__.__call__.__signature__ = self.construct_signature()
            self.log.debug('Python 3.5 works best.')
        except AttributeError:
            self.log.debug('Python 2.7 cannot modify the __class__ attribute.')

            # HACK: Python 2.7 IPython signature line
            self.__signature__ = self.pretty_format_params()
        except TypeError:
            self.log.debug('Python 3.4 inspect.Parameter does not work right.')
            self.__doc__ = None
            self.__class__.__doc__ = '{0}\nValid parameters: {1}'.format(
                docstring, self.pretty_format_params())

            # HACK: Python 3.4 IPython signature line
            self.__signature__ = self.pretty_format_params()

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

            # TODO: When Python 2.7 support is dropped, the rest of this block
            # should be changed to a simple:
            #
            # return AsgardCommand(self.client,
            #                      command,
            #                      self.api_map,
            #                      parent=self.__name__)
            docstring = next_api.get('doc', 'No docstring provided.')
            # call_docstring = self.__call__.__doc__

            next_command = type(
                'AsgardCommand',
                (AsgardCommand, ),
                {'__doc__': '{0}\nValid parameters: {1}'.format(
                    docstring,
                    self.pretty_format_params(api_map=next_api))})

            return next_command(self.client,
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

    def construct_signature(self):
        """Construct a pretty function signature for dynamic commands.

        The inspect modules Parameter and Signature are fully supported in
        Python 3.5, broken in 3.4, and missing in 2.7.

        Returns:
            Signature object for command.
        """
        param_dict = OrderedDict()

        for param, default in sorted(self.get_all_valid_params().items()):
            new_param = Parameter(param,
                                  Parameter.KEYWORD_ONLY,
                                  default=default)
            self.log.debug('New parameter: %s', new_param)

            param_dict[new_param] = param
            self.log.debug('Parameter dictionary growing: %s', param_dict)

        self.log.debug('Parameter dictionary: %s', param_dict)

        new_signature = Signature(parameters=param_dict)
        self.log.debug('New signature: %s', new_signature)

        return new_signature

    # TODO: When Python 2.7 support is removed, api_map kwarg should be removed
    def get_all_valid_params(self, api_map=None):
        """Make a list of valid parameters.

        This accumulates all known parameters from any keys embedded in _path_,
        _default_params_, and _valid_params_.

        Args:
            api_map: Dict containing keys: path, default_params, and
                valid_params.

        Returns:
            Dict of all valid parameters for command in _{key: default}_
            format.
        """
        params = {}

        if not api_map:
            api_map = self.api_map

        path_params = self.client.find_path_keys(api_map.get('path', ''))
        for param in path_params:
            params[param] = ''

        # Always make a list of valid parameters from endpoint mapping
        valid_params = api_map.get('valid_params', [])
        if isinstance(valid_params, str):
            valid_params = [valid_params]

        for param in valid_params:
            params[param] = ''

        params.update(api_map.get('default_params', {}))

        self.log.debug('Full list of params: %s', params)
        return params

    # TODO: Remove when Python 2.7 and 3.4 support have been dropped
    def pretty_format_params(self, api_map=None):
        """Pretty formatting wrapper around _get_all_valid_params()_.

        Args:
            api_map: Dict containing keys: path, default_params, and
                valid_params.

        Returns:
            Pretty string formatting of all parameters.
        """
        all_params_list = []
        for key, default in self.get_all_valid_params(api_map).items():
            all_params_list.append('{0!s}={1!r}'.format(key, default))

        all_params = ', '.join(sorted(all_params_list))
        return '({0})'.format(all_params)
