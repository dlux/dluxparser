==================
ABOUT THIS PROJECT
==================

.. image:: https://travis-ci.com/dlux/dluxparser.svg?branch=master
    :target: https://travis-ci.com/dlux/dluxparser

This repository contains a CLI parser to transform a given file into
a different type for instance excel to json.

.. code-block:: bash

    dluxparser --help 
    
For all supported file types or details of the input/output:

.. code-block:: bash

    dluxparser --help
    dluxparser log2json --help

INSTALLATION
------------

Clone & install the repository

.. code-block:: bash

  $ git clone https://github.com/dlux/dluxparser.git 

  $ pushd dluxparser
  $ pip install -e ./

  # OR Use provided Vagrant file
  $ cd etc
  $ vagrant up
  $ vagrant ssh
  
  # Verify installation:
  $ pip list | grep dluxparser

  # Usage
  $ dluxparser --help

Package Structure

.. code-block:: bash

   dluxparser
    ├── LICENSE
    ├── README.rst
    ├── requirements.txt               
    ├── setup.cfg
    ├── setup.py
    ├── cmd
    │   ├── __init__.py
    │   ├── csv2json.py
    │   ├── log2json.py
    │   └── main.py
    ├── doc
    │   └── source
    │       └── README.rst -> ../../README.rst
    ├── tests
    │   ├── __init__.py
    │   ├── test_csv2json.py
    │   └── test_log2json.py
    ├── Vagrantfile
    └── post_install.sh


Uninstall package

.. code-block:: bash

  $ pip uninstall dluxparser

References
----------

Further information about technologies in use: 

* http://www.luzcazares.com/openstack/empaqueta-tus-proyectos-python/
