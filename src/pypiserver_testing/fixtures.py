"""Factories for pytest fixtures.

We generally define factories here to make it easier for code using
this library to compose fixtures as desired. Otherwise, upon importing
this module, pytest would register all fixtures, and any ``autouse``
fixtures would get triggered, which isn't necessarily intuitive!

To use the fixtures, you need to run the factory functions in the top
level of calling code. You should assign the return value to a variable,
which will become the name of the fixture for the defined scope. For
example:

.. code:: python

    import pytest
    from pypiserver_testing_common.fixtures import create_venv_fixture

    # Define the "venv" fixture
    venv = create_venv_fixture()

    @pytest.fixture()
    def new_fixture(venv):
        # This fixture relies on venv
        pass

    def test_something(venv):
        # This test relies on the venv fixture


Try to keep these alphabetical, to make them easy to find.
"""

import sys
from os import path
from shutil import rmtree
from subprocess import Popen
from tempfile import mkdtemp

import pytest

from .const import PY2
from .system import (
    activate_venv,
    create_venv_cmd,
    run,
)


def create_venv_fixture(scope='module', autouse=False, python=None):
    """Create a fixture that creates a venv and returns its path.

    Note this is a relatively expensive (read: time-consuming) feature,
    so it's best to keep its scope as large as possible.

    The fixture will yield the path to the virtual environment, and at
    the end of its scope, remove the virtual environment from the
    filesystem.

    :param str scope: the scope for the generated fixture
    :param bool autouse: whether the fixture should be used automatically
    :param Union[str, pathlib.Path] python: the python executable to use,
        either as a basename (like "pyton2.7") or a full path. If not
        provided, the python of the current execution environment will
        be used.

    :returns: the pytest fixture
    """

    @pytest.fixture(scope=scope, autouse=autouse)
    def venv_fixture():
        """Return the path to a new python virtual environment.

        Cleans up the venv at the end of the scope.
        """
        venv_root = mkdtemp()
        venv_dir = path.join(venv_root, 'venv')
        run(create_venv_cmd(venv_dir, python=python))
        yield venv_dir
        rmtree(venv_dir)

    return venv_fixture


def create_active_venv_fixture(venv_fixture, scope='module', autouse=False):
    """Create a fixture to activate a specified virtual environment.

    :param venv_fixture:
    :param str scope: the scope for the generated fixture
    :param bool autouse: whether the fixture should be used automatically
    """
