"""Test utilities for interacting with the test host.

Try to keep definitions alphabetical to make them easy to find.
"""

import sys
from contextlib import contextmanager
from os import chdir, environ, getcwd, path
from subprocess import PIPE, CalledProcessError, Popen

from .const import PY2


@contextmanager
def activate_venv(venv_dir):
    """Set up the environment to use the provided venv (POSIX only!).

    :param Union[str, pathlib.Path] venv_dir: the virtual environment's
        root directory
    """
    start_env = environ.copy()
    environ['VIRTUAL_ENV'] = str(venv_dir)
    environ['__PYVENV_LAUNCHER__'] = '{}/bin/python'.format(venv_dir)
    with add_to_path(path.join(venv_dir, 'bin')):
        yield
    environ.clear()
    environ.update(start_env)


@contextmanager
def add_to_path(target):
    """Adjust the PATH to add the target at the front (POSIX only!).

    :param Union[str, pathlib.Path] target: the path to add to the system
        PATH.
    """
    start = environ['PATH']
    environ['PATH'] = '{}:{}'.format(target, start)
    yield
    environ['PATH'] = start


def background(cmd, capture=False, **kwargs):
    """Background a subprocess.

    :param Iterable[str] cmd: the command to run in the background
    :param bool capture: whether to capture output
    :param kwargs: extra keyword arguments for ``Popen``

    :returns: the process object
    :rtype: subprocess.Popen
    """
    pipe = PIPE if capture else None
    proc = Popen(cmd, stdout=pipe, stderr=pipe, **kwargs)
    return proc


@contextmanager
def changedir(target):
    """Change to target and then change back.

    :param Union[str, pathlib.Path] target: the target directory to which
        to change
    """
    start = getcwd()
    chdir(target)
    yield
    chdir(start)


def pip_cmd(default_index='http://localhost:8080', *args):
    """Yield a command to run pip.

    :param str default_index: the index to use if no index argument is
        provided
    :param args: extra arguments for ``pip``

    :returns: arguments suitable for passing to ``Popen()``
    :rtype: Iterator[str]
    """
    yield 'pip'
    for arg in args:
        yield arg
    if (any(i in args for i in ('install', 'download', 'search'))
            and not any(
                i in args for i in ('-i', '--index', '--index-url')
            )):
        yield '-i'
        yield 'http://localhost:8080'


def pypiserver_cmd(root, cmd='run', *args):
    """Yield a command to run pypiserver.

    :param Union[str, pathlib.Path] root: the package root from which
        to serve packages.
    :param args: extra arguments for ``pypiserver <cmd>``

    :returns: arguments suitable for passing to ``Popen()``
    :rtype: Iterator[str]
    """
    # yield '{}/bin/pypiserver'.format(venv_dir)
    yield 'pypiserver'
    yield cmd
    yield str(root)
    for arg in args:
        yield arg


def run(cmd, raise_on_err=True, capture=False, **kwargs):
    """Run a subprocess.

    This is roughly the equivalent of some of the newer APIs introduced
    in Python 3.5+, but cross-platform.

    :param Iterable[str] cmd: the command to run
    :param bool raise_on_err: whether to raise a ``CalledProcessError``
        in the event of a non-zero returncode
    :param bool capture: whether to capture stdout and stderr
    :param kwargs: extra keyword arguments for ``Popen()``

    :returns: either the returncode or the stdout
    :rtype: Union[int, str]

    :raises CalledProcessError: if the process exits with a nonzero
        returncode
    """
    pipe = PIPE if capture else None
    proc = Popen(cmd, stdout=pipe, stderr=pipe, **kwargs)
    out, err = map(
        lambda x: x if x is None else x.decode('utf-8'),
        proc.communicate()
    )
    if raise_on_err and proc.returncode:
        raise CalledProcessError(
            proc.returncode, cmd, output=out, stderr=err
        )
    if capture:
        return out
    return proc.returncode


def twine_cmd(repo_url='http://localhost:8080', *args):
    """Yield a command to run twine.

    :param str repo_url: the URL of the repository to which twine
        should upload or register packages.
    :param args: arguments for `twine`

    :returns: arguments suitable for passing to ``Popen()``
    :rtype: Iterator[str]
    """
    yield 'twine'
    for arg in args:
        yield arg
    for part in ('--repository-url', repo_url):
        yield part
    if '-u' not in args:
        for part in ('-u', 'username'):
            yield part
    if '-p' not in args:
        for part in ('-p', 'password'):
            yield part


def create_venv_cmd(venv_dir, python=None, *args):
    """Yield a command to create a venv.

    :param Union[str, pathlib.Path] venv_dir: the path to the desired
        virtual environment base
    :param str python: the Python for which to create a venv. Can either
        be a basename (like "python2.7" or a full path to an executable).
        If not provided, the Python of the current execution environment
        will be used.
    :param args: extra arguments for the virtualenv command

    :raises CalledProcessError: if creating the venv fails
    """
    python = sys.executable if python is None else python
    if PY2:
        for part in ('virtualenv', '-p', python):
            yield part
    else:
        for part in (python, '-m', 'venv'):
            yield part
    yield str(venv_dir)
