#!/usr/bin/env python
"""Unit testing for pyasgard."""
import logging
import pickle
from base64 import b64encode
from pprint import pformat

import pytest

from pyasgard.pyasgard import (Asgard, AsgardAuthenticationError, AsgardError,
                               clean_kwargs)

URL = 'http://asgard.example.com'


def test_clean_kwargs():
    """Testing functionality of pyasgard.pyasgard.clean_kwargs()."""
    kwargs = {
        'this': 'that',
        'something': 'other',
        'fun': 'time',
        'eggs': ('humpty', 'dumpty'),
        'fruits': ('apple', 'pear', 'orange'),
        'books': ('the king and i', 'someone', 'peter pan', 'someone else'),
        'mixed_set': ('one', 2, 'three', 4),
        'mixed_list': (1, 2, 3, 'four', 'five'),
        'mixed_dict': ('thing', 1, 2, 'thingy')
    }
    clean_kwargs(kwargs)

    formatted_kwargs = {
        'this': 'that',
        'something': 'other',
        'fun': 'time',
        'eggs': 'humpty,dumpty',
        'fruits': 'apple,pear,orange',
        'books': 'the king and i,someone,peter pan,someone else',
        'mixed_set': 'one,2,three,4',
        'mixed_list': '1,2,3,four,five',
        'mixed_dict': 'thing,1,2,thingy'
    }

    assert kwargs == formatted_kwargs


def test_dir():
    """Test Asgard.__dir__ contains all attributes and dynamic endpoints."""
    asgard = Asgard('sdkfj')
    logging.debug('dir:\n%s', pformat(dir(asgard)))

    assert all(word in dir(asgard)
               for word in ['api_version', 'data', 'headers', 'list_instances',
                            'mapping_table', 'username', 'url'])


def test_url_formatter():
    """Check the URL formatter when combining the base URL with endpoint."""
    test_asgard = Asgard('http://test.com', ec2_region='test_region')

    test_url = test_asgard._format_url(  # pylint: disable=W0212
        '/region/list.json', {'test': 'this'})
    logging.debug(test_url)

    assert test_url == 'http://test.com/test_region/region/list.json'

    test_url = test_asgard._format_url(  # pylint: disable=W0212
        '/region/{{test}}/list.json', {'test': 'THIS'})

    assert test_url == 'http://test.com/test_region/region/THIS/list.json'

    test_url = test_asgard._format_url(  # pylint: disable=W0212
        '/region/{{test}}/list.json', {'something': 'ELSE'})

    assert test_url == 'http://test.com/test_region/region//list.json'


def test_authentication_errors():
    """Check if full call with authentication works."""
    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL)
        asgard.show_instance(instance_id='i21bcfec8')

    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL, username='not_devops')
        asgard.show_instance(instance_id='i21bcfec8')


def test_asgard_error():
    """Make sure AsgardError triggers appropriately."""
    with pytest.raises(AsgardError):
        asgard = Asgard(URL, username='devops', password=b64encode('*PASSWORD*'))
        asgard.show_instance(instance_id='sjdlkjf')


def test_builtin_errors():
    """Check that builtin errors trigger with bad formats."""
    with pytest.raises(TypeError):
        asgard = Asgard(URL, username='devops', password='bad_password')
        asgard.show_instance(instance_id='i21bcfec8')

    with pytest.raises(AttributeError):
        asgard = Asgard(URL, username='devops', password=b64encode('*PASSWORD*'))
        asgard.list()


def test_success():
    """Make sure that basic good call works."""
    asgard = Asgard(URL, username='devops', password=b64encode('*PASSWORD*'))
    response = asgard.list_regions()
    with open('pickles/regions.pickle', 'r') as regions_pickle:
        assert response == pickle.load(regions_pickle)


if __name__ == '__main__':
    pytest.main()
