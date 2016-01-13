#!/usr/bin/env python
"""Unit testing for pyasgard.

`config.py` can be used for storing custom parameters::

    ENC_PASSWD = 'dGVzdHBhc3N3ZA=='
    URL = 'http://asgard.demo.com'
    USERNAME = 'happydog'
"""
import logging
import re
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

    for word in ['api_version', 'asg', 'data', 'elb', 'headers', 'instance',
                 'mapping_table', 'username', 'url']:
        assert word in dir(asgard)


def test_url_formatter():
    """Check the URL formatter when combining the base URL with endpoint."""
    test_asgard = Asgard('http://test.com', ec2_region='test_region')

    test_url = test_asgard.format_url(  # pylint: disable=W0212
        '/region/list.json', {'test': 'this'})
    logging.debug(test_url)

    assert test_url == 'http://test.com/test_region/region/list.json'

    test_url = test_asgard.format_url(  # pylint: disable=W0212
        MAPPING_TABLE['application']['list']['instances']['path'], {'app_id':
                                                                    'THIS'})

    assert test_url == 'http://test.com/test_region/instance/list/THIS.json'

    with pytest.raises(KeyError):
        test_url = test_asgard.format_url(  # pylint: disable=W0212
            MAPPING_TABLE['application']['list']['instances']['path'],
            {'something': 'ELSE'})


def test_authentication_errors():
    """Check if full call with authentication works."""
    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL)
        asgard.instance.show(instance_id='i21bcfec8')

    with pytest.raises(AsgardAuthenticationError):
        asgard = Asgard(URL, username='not_user')
        asgard.instance.show(instance_id='i21bcfec8')


def test_asgard_error():
    """Make sure AsgardError triggers appropriately."""
    with pytest.raises(AsgardError):
        asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
        asgard.instance.show(instance_id='sjdlkjf')


def test_builtin_errors():
    """Check that builtin errors trigger with bad formats."""
    with pytest.raises(TypeError):
        asgard = Asgard(URL,
                        username=USERNAME,
                        password=ENC_PASSWD,
                        data={'bad': 'param'})
        asgard.instance.show(instance_id='i21bcfec8')

    with pytest.raises(AttributeError):
        asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
        asgard.list()


def test_success():
    """Make sure that basic good call works."""
    asgard = Asgard(URL, username=USERNAME, password=ENC_PASSWD)
    response = asgard.regions.list()
    assert 'us-east-1' in [region['code'] for region in response]


def test_applications():
    """Check Applications are working."""
    log = logging.getLogger(__name__)

    test_name = 'pyasgard_test'
    test_description = 'Testing this out.'

    pre_response = ASGARD.application.list()

    ASGARD.application.create(name=test_name, description=test_description)

    post_response = ASGARD.application.list()

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

    check_app_exists = ASGARD.application.show(app_name=test_name)
    logging.debug('check_app:\n%s', pformat(check_app_exists))
    assert check_app_exists['app']['description'] == test_description

    ASGARD.application.delete(name=test_name)

    with pytest.raises(AsgardError):
        check_app_deleted = ASGARD.application.show(app_name=test_name)
        logging.debug('check_app:\n%s', pformat(check_app_deleted))


def test_mappings():
    """Check mapping table has at minimum _method_, _path_, and _status_"""
    for resource in MAPPING_TABLE.keys():
        logging.debug('Resource = %s', resource)
        for methods in MAPPING_TABLE[resource].values():
            assert 'method' in methods
            assert 'path' in methods
            assert 'status' in methods


def test_json_return():
    """With a good list call, we should get a list of dicts.

    When doing list operations, Asgard returns a JSON response with a list of
    dict objects for iterating over.
    """
    returned = ASGARD.regions.list()
    logging.debug(returned)

    assert isinstance(returned, list)
    for item in returned:
        assert isinstance(item, dict)

    # Check another list, just in case
    returned = ASGARD.cluster.list()
    logging.debug(returned)

    assert isinstance(returned, list)

    for item in returned:
        assert isinstance(item, dict)


def test_html_return():
    """Send bad data, make sure that returned HTML comes back as a dict."""
    returned = ASGARD.application.create(name='ntangsurat', email='')
    logging.debug(returned)
    assert isinstance(returned, dict)


def test_bad_argument():
    """We should raise TypeError when a bad argument is seen."""
    with pytest.raises(TypeError):
        ASGARD.cluster.list(something='bad')

    with pytest.raises(TypeError):
        ASGARD.application.create(something='bad')


def test_errors():
    """Make sure custom errors have the right attributes."""
    asgarderror = AsgardError('message', 404)
    assert str(asgarderror) == repr('404: message')
    assert asgarderror.error_code == 404

    asgarderror = AsgardAuthenticationError('message')
    assert str(asgarderror) == repr('401: message')
    assert asgarderror.error_code == 401


def test_server():
    """Make sure basic Server calls work."""
    assert isinstance(ASGARD.server.build(), int)

    match = re.search(r'^\d{1,3}' + 3 * r'\.\d{1,3}', ASGARD.server.ip())
    assert match.group()

    match = re.search(r'\d+d \d+h \d+m \d+s', ASGARD.server.uptime())
    assert match.group()


if __name__ == '__main__':
    """This is not the best way to run.

    Coverage report shows missing lines when in fact they are actually covered.
    This seems to be a known issue with py.test and something about import
    order. For now, run full command `py.test -v --cov pyasgard --cov-report
    term-missing --cov-report html test_pyasgard.py` or `tox`.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)s]%(module)s:%(funcName)s - %(message)s')
    TEST_ARGS = ['-v', '--cov', 'pyasgard', '--cov-report', 'term-missing',
                 '--cov-report', 'html', __file__]
    pytest.main(TEST_ARGS)
