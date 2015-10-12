Asgard Python Library
---------------------

This is a wrapper for the asgard api.

The api mapping is in `pyasgard/endpoints.py`

Example usage:
```python
from pyasgard import Asgard

# With authentication
# from base64 import b64encode
# asgard = Asgard('http://asgard.example.com',
#                 username='user',
#                 password=b64encode('secret'))
asgard = Asgard('http://asgard.example.com')

asgard.show_ami(ami_id='ami-i1234x')
asgard.cluster_resize(name='appname', minAndMaxSize=4)
```

## Testing
To run the unit tests, create a `config.py` file and run:

```python
# Unit test contants
ENC_PASSWD = 'dGVzdHBhc3N3ZA=='
URL = 'http://asgard.demo.com'
USERNAME = 'happydog'
```

```bash
./test_pyasgard.py
```
