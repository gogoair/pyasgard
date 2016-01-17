"""Pyasgard exceptions."""


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


class AsgardReturnedError(AsgardError):
    """Embedded error or message in HTML returned from Asgard."""

    def __init__(self, htmldict):
        """Save HTMLToDict object for inspection.

        Args:
            htmldict: HTMLToDict object.
        """
        super(AsgardReturnedError, self).__init__('Asgard returned error.')

        self.htmldict = htmldict
        self.issues = [
            issue.text
            for issue in htmldict.soup.find_all(class_=('message', 'errors'))
        ]

    def __str__(self):
        return '\n'.join(self.issues)
