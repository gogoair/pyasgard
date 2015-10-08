Asgard Python Library
---------------------

This is a wrapper for the asgard api.

The api mapping is in pyasgard/endpoints.py

Example usage:
```
from pyasgard import Asgard

asgard = Asgard(asgard_url='http://asgard.example.com')

asgard.show_ami(ami_id='ami-i1234x')
asgard.cluster_resize(name='appname', minAndMaxSize=4)

```
