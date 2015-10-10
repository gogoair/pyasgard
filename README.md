Asgard Python Library
---------------------

This is a wrapper for the asgard api.

The api mapping is in pyasgard/endpoints.py

Example usage:
```python
from pyasgard import Asgard

asgard = Asgard('http://asgard.example.com')

# With authentication
# from base64 import b64encode
# Asgard('http://asgard.example.com',
#     username='user',
#     password=b64encode('secret'))

asgard.show_ami(ami_id='ami-i1234x')
asgard.cluster_resize(name='appname', minAndMaxSize=4)

```
