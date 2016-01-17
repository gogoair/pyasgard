# -*- coding: UTF-8 -*-
"""Convert HTML to dict with some help from Beautiful Soup 4.

Original code found: http://www.xavierdupre.fr/blog/2013-10-27_nojs.html
Original author: Xavier Dupré

We use Beautiful Soup 4 to sanitize the incoming HTML before parsing. Once
done, we construct a dictionary object from the HTML tags that can be converted
to JSON if desired.

Usage:
    import json

    from pyasgard.htmltodict import HTMLToDict

    dictionary = HTMLToDict().dict(html_string)
    json_string = json.dumps(dictionary)
"""
from bs4 import BeautifulSoup

try:
    # python2
    from HTMLParser import HTMLParser
    STRING_TYPES = (str, unicode)  # pylint: disable=E0602
except ImportError:
    # python3
    from html.parser import HTMLParser  # pylint: disable=C0411
    STRING_TYPES = (str)  # pylint: disable=C0103,R0204


class HTMLToDict(HTMLParser):
    """Parse HTML and transcode to dict."""

    def __init__(self, content, raise_exception=True):
        HTMLParser.__init__(self)

        self.doc = {}
        self.path = []
        self.cur = self.doc
        self.line = 0
        self.raise_exception = raise_exception
        self.soup = BeautifulSoup(content, 'html.parser')

        self.feed(self.soup.prettify())

    @property
    def json(self):
        """Return the JSON object."""
        return self.doc

    def dict(self):
        """Convert HTML to dict.

        Calling the _json_ attribute will use HTMLParser to convert the
        contents of self.feed from HTML into a Dict object.
        """
        return self.json

    def handle_starttag(self, tag, attrs):
        """Handle starting tag."""
        self.path.append(tag)
        attrs = {key: value for key, value in attrs}

        if tag in self.cur:
            if isinstance(self.cur[tag], list):
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
            else:
                self.cur[tag] = [self.cur[tag]]
                self.cur[tag].append({"__parent__": self.cur})
                self.cur = self.cur[tag][-1]
        else:
            self.cur[tag] = {"__parent__": self.cur}
            self.cur = self.cur[tag]

        for attribute, value in attrs.items():
            self.cur["#" + attribute] = value

        self.cur[""] = ""

    def handle_endtag(self, tag):
        """Handle ending tag."""
        if tag != self.path[-1] and self.raise_exception:
            raise Exception(("HTML malformed around line: {0} "
                             "(check for unclosed tags, "
                             "e.g. <br>, <hr>, <img .. >)").format(self.line))

        del self.path[-1]

        memo = self.cur
        self.cur = self.cur["__parent__"]
        self.clean(memo)

    def handle_data(self, data):
        """Handle data."""
        self.line += data.count("\n")
        if "" in self.cur:
            self.cur[""] += data

    def clean(self, values):
        """Strip whitespace from data."""
        for key in list(values.keys()):
            value = values[key]

            if isinstance(value, STRING_TYPES):
                stripped = value.strip(" \n\r\t")

                if stripped == '':
                    del values[key]
                else:
                    values[key] = stripped

        del values["__parent__"]
