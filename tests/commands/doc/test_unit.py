import os
import pytest

from sinol_make.commands.doc import Command
from tests.fixtures import create_package
from tests import util


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_compile_file(create_package):
    command = Command()
    assert command.compile_file(os.path.abspath(os.path.join(os.getcwd(), "doc/doczad.tex"))) is True
