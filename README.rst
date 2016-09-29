.. attention:: DEPRECATED
   This is no longer being maintained and no future changes, updates or enhancements will be added.

Asgard Python Library
---------------------

This is a wrapper for the asgard api.

The api mapping is in ``pyasgard/endpoints.py``

Example usage:

.. code:: python

    from pyasgard import Asgard

    # With authentication
    # from base64 import b64encode
    # asgard = Asgard('http://asgard.example.com',
    #                 username='user',
    #                 password=b64encode('secret'))
    asgard = Asgard('http://asgard.example.com')

    asgard.ami.list()
    asgard.ami.show(ami_id='ami-i1234x')

    asgard.cluster.list()
    asgard.cluster.resize(name='appname', minAndMaxSize=4)

Warning
=======

The ``Asgard.asg.create()`` command requires some hacking to support a
dynamic keyword argument. This is documented in the command docstring as
well.

.. code:: python

    client = Asgard('http://test.com')

    vpc_id = 'vpc-something'
    lb_list = ['lb-something']
    lb_param = 'selectedLoadBalancersForVpcId{0}'.format(vpc_id)

    api = client.mapping_table['asg']['create']['default_params']
    api[lb_param] = lb_list

    client.asg.create(**{lotsofparams})

Testing
=======

To run the unit tests, create a ``config.py`` file and run ``tox``:

.. code:: python

    # Unit test contants
    ENC_PASSWD = 'dGVzdHBhc3N3ZA=='
    URL = 'http://asgard.demo.com'
    USERNAME = 'happydog'
