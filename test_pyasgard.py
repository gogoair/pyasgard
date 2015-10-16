#!/usr/bin/env python
"""Unit testing for pyasgard.

`config.py` can be used for storing custom parameters::

    ENC_PASSWD = 'dGVzdHBhc3N3ZA=='
    URL = 'http://asgard.demo.com'
    USERNAME = 'happydog'
"""
import logging
from pprint import pformat

import pytest

from pyasgard.endpoints import MAPPING_TABLE
from pyasgard.pyasgard import Asgard, AsgardAuthenticationError, AsgardError

try:
    from config import URL, ENC_PASSWD, USERNAME
except ImportError:
    ENC_PASSWD = 'dGVzdHBhc3N3ZA=='
    URL = 'http://asgard.demo.com'
    USERNAME = 'happydog'

ASGARD = Asgard(URL, username=USERNAME, password=ENC_PASSWD)


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
        MAPPING_TABLE['list_application_instances']['path'],
        {'app_id': 'THIS'})

    assert test_url == 'http://test.com/test_region/instance/list/THIS.json'

    with pytest.raises(KeyError):
        test_url = test_asgard._format_url(  # pylint: disable=W0212
            MAPPING_TABLE['list_application_instances']['path'],
            {'something': 'ELSE'})


def test_authentication_errors():
    """Check if full call with authentication works."""
    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL)
        asgard.show_instance(instance_id='i21bcfec8')

    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL, username='not_user')
        asgard.show_instance(instance_id='i21bcfec8')


def test_asgard_error():
    """Make sure AsgardError triggers appropriately."""
    with pytest.raises(AsgardError):
        asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
        asgard.show_instance(instance_id='sjdlkjf')


def test_builtin_errors():
    """Check that builtin errors trigger with bad formats."""
    with pytest.raises(TypeError):
        asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD, data={'bad': 'param'})
        asgard.show_instance(instance_id='i21bcfec8')

    with pytest.raises(AttributeError):
        asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
        asgard.list()


def test_success():
    """Make sure that basic good call works."""
    asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
    response = asgard.list_regions()
    assert 'us-east-1' in [region['code'] for region in response]


def test_applications():
    """Check Applications are working."""
    log = logging.getLogger(__name__)

    test_name = 'pyasgard_test'
    test_description = 'Testing this out.'

    pre_response = ASGARD.list_applications()

    ASGARD.create_application(name=test_name, description=test_description)

    post_response = ASGARD.list_applications()

    new_application = []
    for app in post_response:
        pre_apps = [pre_app['name'] for pre_app in pre_response]
        log.debug('pre_apps=%s', pre_apps)

        log.debug('app name=%s', app['name'])
        if app['name'] not in pre_apps:
            new_application.append(app)

    log.debug('new_application=%s', new_application)

    assert len(new_application) == 1

    new_application = new_application[0]

    assert new_application['name'] == test_name
    assert new_application['description'] == test_description

    check_app_exists = ASGARD.show_application(app_name=test_name)
    logging.debug('check_app:\n%s', pformat(check_app_exists))
    assert check_app_exists['app']['description'] == test_description

    ASGARD.delete_application(name=test_name)

    with pytest.raises(AsgardError):
        check_app_deleted = ASGARD.show_application(app_name=test_name)
        logging.debug('check_app:\n%s', pformat(check_app_deleted))


def test_mappings():
    """Check mapping table has at minimum _method_, _path_, and _status_"""
    for values in MAPPING_TABLE.values():
        assert 'method' in values
        assert 'path' in values
        assert 'status' in values


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    TEST_ARGS = ['-v', '--cov=pyasgard', '--cov-report', 'term-missing',
                 '--cov-report', 'html', __file__]
    pytest.main(TEST_ARGS)
