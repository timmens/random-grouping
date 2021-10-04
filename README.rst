.. image:: .image.png
    :width: 500

.. image:: https://anaconda.org/timmens/randomgroups/badges/version.svg
   :target: https://anaconda.org/timmens/randomgroups

.. image:: https://anaconda.org/timmens/randomgroups/badges/platforms.svg
   :target: https://anaconda.org/timmens/randomgroups

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT
    :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://github.com/timmens/random-grouping/actions/workflows/python-package-conda.yml/badge.svg
    :target: https://github.com/timmens/random-grouping/actions/workflows/python-package-conda.yml


Use Case
--------

This package exports a single function called ``create_matching`` which can be used to
to create matchings for different meetings from a varying but overlapping set of
members. In particular the internal algorithm makes sure that group matchings in
different meetings are mixed.


Installation
------------


The package can be installed via conda. To do so, type the following commands in your
favorite terminal emulator:

.. code-block:: bash

    $ conda config --add channels conda-forge
    $ conda install -c timmens randomgroups


If you prefer to use pip you can install the latest version directly from GitHub.

.. code-block:: bash

    $ pip install --upgrade git+git://github.com/timmens/random-grouping.git


How to Use
----------

The code expects a csv file containing *id*, *name*, and *joins* columns, where *id*
is used internally to keep track of matchings, *name* is a str column which is used
when creating the human-readable output and *joins* is a {0, 1} column which denotes
if the given individual wants to join the current meeting. An example file is given
here `names.csv <https://github.com/timmens/random-grouping/blob/main/example_data/names.csv>`_.
Note that the rows in *id* column have to be unique. If new individuals wish to be added
these individuals simply need to be appended to the data file, the code will update all
further files automatically.

**First Time Use:**

If no prior matchings have been recorded you can create a new set of groups by running
the following lines in a Python shell

.. code-block:: Python3

    from randomgroups import create_matching

    names_path = "/path/to/names.csv"
    output_path = "/path/to/folder/where/to/store/output/data"

    create_matching(
        names_path=names_path,
        output_path=output_path,
        min_size=3,
    )


Here the argument ``min_size`` denotes the minimum number of members in a group. In the
folder ``output_path`` two files will be created. One, ``matchings.txt`` which contain
the named matchings for the current meeting, and second, ``matchings_history.csv`` which
contains information on matchings. The latter file needs to be saved since it will be
used in subsequent function calls. Example files are given here: `matching.txt <https://github.com/timmens/random-grouping/blob/main/example_data/matching.txt>`_,
`matchings_history.csv <https://github.com/timmens/random-grouping/blob/main/example_data/matchings_history.csv>`_.


*Remark:* If the files ``names.csv`` is a Google sheet which is updated on a regular
basis it can be sensible not to donwload the file but to provide a link to the sheet
directly. In the case with Google sheets this is easily done by opening the Google
sheet and then publishing the document in the file options. This creates a link to a
downloadable csv file which updates when the Google sheet is updated. This URL can then
be passed to ``names_path``.


**Subsequent Usage:**

Once the file ``matchings_history.csv`` has been created one can further pass the path
of this file to the function call via ``matchings_history_path=...``. The previous
matchings will then influence new group formations.


**Assortative Matching:**

The 'status' column in the names csv-file allows one to distuingish between 'student'
and 'faculty'. One can then use the 'wans_mixing' column to specify whether an
individual wants to be mixed with people from another group. This is not absolute.
A float parameter ("faculty_multiplier") can be specified in a dictionary an passed
to the main function via the argument "matching_params". If this parameter is very
high it will be less likely that faculty that does not want to mix is mixed.


Contributing
------------

If you want to contribute to this repository feel free to open a pull request or submit
an issue. You can also simply contact me, see `here <https://github.com/timmens>`_.
