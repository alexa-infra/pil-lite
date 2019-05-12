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

And another way to build locally
--------------------------------

.. code:: bash

    apt-get install cmake
    mkdir -p src/build
    cd src/build
    CMAKE_PREFIX_PATH=~/.pyenv/versions/3.7.3/ cmake -G"Unix Makefiles" ..
    make
    cp libPilLite.so ../../PilLiteExt.so
    cd ../..
    PYTHONPATH=. pytest

Release
-------

.. code:: bash

    vim setup.py
    vim PilLite/__init__.py
    git commit -m "..."
    git tag -a 0.1.0 -m "version 0.1.0"
    git push origin master --tags
    pip install twine
    python setup.py sdist
    twine upload dist/Pil-Lite-0.1.0.tar.gz
