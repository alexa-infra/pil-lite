Build locally
-------------

.. code:: bash

    python src/py_ext_build.py
    PYTHONPATH=. pytest

Another way to build locally
----------------------------

.. code:: bash

    pip install -e .
    pytest

Release
-------

.. code:: bash

    vim PilLite/__about__.py
    git commit -m "..."
    git tag -a 0.1.0 -m "version 0.1.0"
    git push origin master --tags
    pip install twine
    python setup.py sdist
    twine upload dist/Pil-Lite-0.1.0.tar.gz
