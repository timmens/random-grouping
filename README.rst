.. image:: .image.png
    :width: 500

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black


Use Case
--------

The code in this repo can be used to create random groups given some set of members,
even if

1. the set of members varies between meetings
2. old group matchings should inform new group matchings

Or in plain English: You need to create group matchings on a, say, weekly, basis and
you want new group matchings to be sufficiently different from old matchings.


How to Use It
-------------

First Time Use
^^^^^^^^^^^^^^

1. Create Python Environment
""""""""""""""""""""""""""""
If you are using the code for the very first time you will need to create a Python
environment which allows you to execute the code. All necessary packages are listed in
the file `environment.yml <https://github.com/timmens/random-grouping/blob/main/environment.yml>`_.
A particularly easy approach is to use the package manager conda. Clone the repository
and change to the root directory; then run in your favorite terminal emulator

.. code-block:: zsh

    conda env create -f environment.yml
    conda activate random-group
    conda develop .


2. Configure Project
""""""""""""""""""""

Now you need to specify the arguments in `config.yaml <https://github.com/timmens/random-grouping/blob/main/config.yaml>`_.
In particular you need to specify how the project accesses the names and ids of the
participants. You can choose to provide a url to the corresponding csv file or you save
it locally in ``src/data``. To see how the file needs to be structured see `names.csv <https://github.com/timmens/random-grouping/blob/main/src/data/names.csv>`_.


3. Build Project
""""""""""""""""

To build the project and produce results we use `pytask <https://pytask-dev.readthedocs.io/en/latest/index.html>`_.
Again open your favorite terminal emulator and run

.. code-block:: zsh

    pytask -m preliminaries
    pytask -m build
    pytask -m update_source


And you're done. The group matchings can be found in the file ``BLD/matchings.txt``.


Using the Project Again
^^^^^^^^^^^^^^^^^^^^^^^

Thanks to the command ``pytask -m update_source`` the information in the previous
matchings is saved and will influence new group matchings. To create a new matching
change the configurations to your liking, update ``names.csv`` if necessary, and then
simply run

.. code-block:: zsh

    pytask -m build
    pytask -m update_source



How We Solve the Problem
------------------------

To be written.


Contributing
------------

If you want to contribute to this repository feel free to open a pull request or submit
an issue. You can also simply contact me, see `here <https://github.com/timmens>`_.
