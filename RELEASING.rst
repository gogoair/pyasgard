Publishing a release
------------------------

Dependencies
============

There are few package dependencies needed to get this going.

.. code:: bash

    $ pip install wheel twine


Create pypi account
===================

Create your own account on pypi.python.org. This should only needed to be done once.

.. code:: bash

    $ python setup.py register


Update packing details
======================

Last minutes changes that need to occur to prepare for a release.

* Modify ``pyasgard/version.py`` and increase version number.

* Modify ``setup.py``, if necessary.

* Tag the repo accordingly

.. code:: bash

    $ git tag vX.Y.Z
    $ git push --tags


Create the binaries
===================

Now its time to create the binaries and upload it to pypi.

.. code:: bash

    # create binaries and wheel
    $ python setup.py sdist
    $ python setup.py bdist_wheel --universal

    # uploads releases to pypi
    $ twine upload dist/pyasgard-X.Y.Z.tar.gz 
    $ twine upload dist/pyasgard-X.Y.Z-*.whl

