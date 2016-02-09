"""Python interface to Netflix Asgard REST API."""
import base64
import inspect
import logging
from pprint import pformat
from string import Template

import requests

from .asgardcommand import AsgardCommand
from .endpoints import MAPPING_TABLE
from .exceptions import (AsgardAuthenticationError, AsgardError,
                         AsgardReturnedError)
from .htmltodict import HTMLToDict

__author__ = "Sijis Aviles <saviles@gogoair.com>"
__version__ = "1.2"


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

        self.htmldict = None

    def __dir__(self):
        self_keys = list(self.__dict__.keys())
        map_keys = list(self.mapping_table.keys())
        return self_keys + map_keys

    def __getattr__(self, api_call):
        """Execute dynamic method and pass keyword args as data to API call."""
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

    def find_path_keys(self, path):
        """Extract keys from the path.

        Args:
            path: String of endpoint path with possible _${parameter}_
            templated parameters.

        Returns:
            List of parameters found in endpoint path.
        """
        keys = [param[2] for param in Template.pattern.findall(path)]

        self.log.debug('Template find=%s', Template.pattern.findall(path))
        self.log.debug('path_keys=%s', keys)

        return keys

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

        path_keys = self.find_path_keys(path)

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
        self.log.debug('Request response:\n%s',
                       pformat(inspect.getmembers(response)))

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
        self.log.debug('Received response status: %s', response.status_code)

        # Just in case
        if response is None:
            message = 'Response Not Found'
            self.log.error(message)

            with open('unexpected.html', 'wt') as unexpected_html:
                unexpected_html.write(response.text)

            raise AsgardError(message)

        if response.status_code == 401:
            raise AsgardAuthenticationError(response.reason)

        if response.status_code != status:
            error = AsgardError(
                self.format_dict(response), response.status_code)
            self.log.fatal(error)

            with open('error.html', 'wt') as error_html:
                error_html.write(response.text)

            raise error

        return self.format_dict(response)

    def format_dict(self, response):
        """Format the response into a dict from HTML or JSON.

        Deserialize json content if content exist. In some cases Asgard returns
        ' ' strings. Also return false non strings (0, [], (), {})

        Args:
            response: requests.models.Response object.

        Returns:
            Dict representation of HTML or JSON.
            Str when Asgard returns simple text.
            Int when Asgard returns simple integer.
        """
        try:
            response_json = response.json()
            self.log.debug('Response JSON:\n%s', pformat(response_json))

            with open('output.json', 'wt') as output_json:
                output_json.write(response.text)

            return response_json
        except ValueError:
            self.log.debug('Response HTML:\n%s', response.text)

            with open('output.html', 'wt') as output_html:
                output_html.write(response.text)

            self.htmldict = HTMLToDict(response.text)
            if 'html' in self.htmldict.dict():
                return self.parse_errors()
            else:
                return response.text

    def parse_errors(self):
        """Parse out the Asgard errors from the htmldict output.

        To avoid false positives, if _error_ or _message_ HTML classes are
        found, the contents will be checked to make sure safe words are
        included indicating a true positive.

        Returns:
            Dict representation of HTML page.

        Raises:
            AsgardReturnedError: Asgard returned a page with embedded errors or
                messages.
        """
        safe_words = ['created', 'deleted', 'updated']

        possible_issues = self.htmldict.soup.find_all(
            class_=('errors', 'message'))
        self.log.debug('Possible issues: %s', possible_issues)

        # No issues found, return safely
        if possible_issues == []:
            return self.htmldict.dict()

        # Return safely if any safe word is found
        for issue in possible_issues:
            self.log.debug('Issue: %s', issue)

            if any(word in issue.text.lower() for word in safe_words):
                return self.htmldict.dict()

        self.log.fatal('Asgard returned possible issues: %s', possible_issues)
        raise AsgardReturnedError(self.htmldict)
