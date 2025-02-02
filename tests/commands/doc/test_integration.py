import os
import glob
import pytest

from sinol_make import configure_parsers
from sinol_make.commands.doc import Command
from sinol_make.helpers import paths
from tests.fixtures import create_package
from tests import util


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_simple(capsys, create_package):
    """
    Test `doc` command with no parameters.
    """
    parser = configure_parsers()
    args = parser.parse_args(["doc"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Compilation was successful for all files." in out

    for pattern in command.LOG_PATTERNS:
        assert glob.glob(os.path.join(os.getcwd(), 'doc', pattern)) == []


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_argument(capsys, create_package):
    """
    Test `doc` command with specified file.
    """
    parser = configure_parsers()
    args = parser.parse_args(["doc", "doc/doczad.tex"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Compilation was successful for all files." in out

    logs_exist = False
    logs_dir = paths.get_cache_path('doc_logs')
    for pattern in command.LOG_PATTERNS:
        assert glob.glob(os.path.join(os.getcwd(), 'doc', pattern)) == []
        logs_exist = logs_exist | (glob.glob(os.path.join(logs_dir, pattern)) != [])
    assert logs_exist
