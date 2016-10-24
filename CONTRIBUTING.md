# Contributor's Guide
Feature requests, bug reports, and pull requests are all welcomed!
Head on over to https://github.com/ajyoon/blur and get in touch.

#### Development Dependencies

Development dependencies can be installed with pip from a dedicated
dev requirements file:

    $ pip install -r dev_requirements.txt

The documentation build dependencies can be similarly installed
from a dedicated requirements file:

    $ cd doc
    $ pip install -r doc_requirements.txt

#### Testing
The test suite is located in the `tests` directory. Travis CI has been
configured to automatically run these tests on any proposed changes to the
upstream git repository, but you can run these tests yourself as well.
Travis tests run on `pytest`, but any testing framework compatible
with the built-in Python `Unittest` and `doctest` module should work.

To run the tests, run `pytest` from the project root directory:

    ~/blur$ pytest

#### Building the documentation
The documentation for *blur* is built with
[sphinx](http://www.sphinx-doc.org/en/stable/)
and [napoleon](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/).

To build, simply navigate to the ``doc`` folder and call ``make html``

    $ cd blur/doc
    $ make html

The built docs will be placed in `blur/doc/build/html/`.

#### Code conventions
This codebase:
* Follows [PEP8](https://www.python.org/dev/peps/pep-0008/) strictly
* Follows [PEP257](https://www.python.org/dev/peps/pep-0257/) whenever sensible
* Uses [Google-style docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
