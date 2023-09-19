import pytest

from ..commands.run.util import create_ins
from ..fixtures import *
from tests import util
from sinol_make.helpers import package_util


@pytest.mark.parametrize("create_package", [util.get_long_name_package_path()], indirect=True)
def test_get_task_id(create_package):
    package_path = create_package
    assert package_util.get_task_id() == "lpn"
    with open(os.path.join(package_path, "config.yml"), "w") as config_file:
        config_file.write("title: Long package name\n")
    with pytest.raises(SystemExit):
        package_util.get_task_id()


def test_extract_test_id():
    assert package_util.extract_test_id("in/abc1a.in", "abc") == "1a"
    assert package_util.extract_test_id("in/abc10a.in", "abc") == "10a"
    assert package_util.extract_test_id("in/abc12ca.in", "abc") == "12ca"
    assert package_util.extract_test_id("in/abc0ocen.in", "abc") == "0ocen"
    assert package_util.extract_test_id("in/long_task_id2bc.in", "long_task_id") == "2bc"


def test_get_group():
    assert package_util.get_group("in/abc1a.in", "abc") == 1
    assert package_util.get_group("in/long_name2ocen.in", "long_name") == 0


def test_get_tests(create_package):
    os.chdir(create_package)
    task_id = package_util.get_task_id()
    create_ins(create_package, task_id)
    tests = package_util.get_tests("abc", None)
    assert tests == ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]


def test_extract_file_name():
    assert package_util.get_file_name("in/abc1a.in") == "abc1a.in"


def test_get_executable():
    assert package_util.get_executable("abc.cpp") == "abc.cpp.e"


def test_get_time_limit():
    config = {
        "time_limit": 1000,
        "time_limits": {
            "0": 5000,
            "2": 2000,
        },
        "override_limits": {
            "py": {
                "time_limit": 2000,
                "time_limits": {
                    "0": 6000,
                    "2": 3000,
                },
            }
        }
    }

    assert package_util.get_time_limit("in/abc1a.in", config, "cpp", "abc") == 1000
    assert package_util.get_time_limit("in/abc2a.in", config, "cpp", "abc") == 2000
    assert package_util.get_time_limit("in/abc2b.in", config, "cpp", "abc") == 2000
    assert package_util.get_time_limit("in/abc3a.in", config, "cpp", "abc") == 1000
    assert package_util.get_time_limit("in/abc3ocen.in", config, "cpp", "abc") == 5000

    assert package_util.get_time_limit("in/abc1a.in", config, "py", "abc") == 2000
    assert package_util.get_time_limit("in/abc2a.in", config, "py", "abc") == 3000
    assert package_util.get_time_limit("in/abc2b.in", config, "py", "abc") == 3000
    assert package_util.get_time_limit("in/abc3a.in", config, "py", "abc") == 2000
    assert package_util.get_time_limit("in/abc3ocen.in", config, "py", "abc") == 6000

    # Test getting default time limit.
    config = {
        "time_limits": {
            "1": 1000,
        },
        "override_limits": {
            "py": {
                "time_limits": {
                    "1": 2000,
                }
            }
        }
    }
    assert package_util.get_time_limit("in/abc1a.in", config, "cpp", "abc") == 1000
    assert package_util.get_time_limit("in/abc1a.in", config, "py", "abc") == 2000
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "cpp", "abc")
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "py", "abc")

    config = {
        "time_limits": {
            "1": 1000,
        },
        "override_limits": {
            "py": {
                "time_limit": 500,
                "time_limits": {
                    "1": 1000,
                }
            }
        }
    }
    assert package_util.get_time_limit("in/abc1a.in", config, "cpp", "abc") == 1000
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "cpp", "abc")
    assert package_util.get_time_limit("in/abc1a.in", config, "py", "abc") == 1000
    assert package_util.get_time_limit("in/abc2a.in", config, "py", "abc") == 500


def test_get_memory_limit():
    config = {
        "memory_limit": 256,
        "memory_limits": {
            "0": 128,
            "2": 512,
        },
        "override_limits": {
            "py": {
                "memory_limit": 512,
                "memory_limits": {
                    "0": 256,
                    "2": 1024,
                },
            }
        }
    }

    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp", "abc") == 256
    assert package_util.get_memory_limit("in/abc2a.in", config, "cpp", "abc") == 512
    assert package_util.get_memory_limit("in/abc2b.in", config, "cpp", "abc") == 512
    assert package_util.get_memory_limit("in/abc3ocen.in", config, "cpp", "abc") == 128

    assert package_util.get_memory_limit("in/abc1a.in", config, "py", "abc") == 512
    assert package_util.get_memory_limit("in/abc2a.in", config, "py", "abc") == 1024
    assert package_util.get_memory_limit("in/abc2b.in", config, "py", "abc") == 1024
    assert package_util.get_memory_limit("in/abc3ocen.in", config, "py", "abc") == 256

    # Test getting default memory limit.
    config = {
        "memory_limits": {
            "1": 1024,
        },
        "override_limits": {
            "py": {
                "memory_limits": {
                    "1": 2048,
                }
            }
        }
    }
    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp", "abc") == 1024
    assert package_util.get_memory_limit("in/abc1a.in", config, "py", "abc") == 2048
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "cpp", "abc")
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "py", "abc")

    config = {
        "memory_limits": {
            "1": 1024,
        },
        "override_limits": {
            "py": {
                "memory_limit": 512,
                "memory_limits": {
                    "1": 1024,
                }
            }
        }
    }
    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp", "abc") == 1024
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "cpp", "abc")
    assert package_util.get_memory_limit("in/abc1a.in", config, "py", "abc") == 1024
    assert package_util.get_memory_limit("in/abc2a.in", config, "py", "abc") == 512


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_validate_files(create_package, capsys):
    package_path = create_package
    util.create_ins_outs(package_path)
    task_id = package_util.get_task_id()
    assert task_id == "abc"
    package_util.validate_test_names(task_id)

    os.rename(os.path.join(package_path, "in", "abc1a.in"), os.path.join(package_path, "in", "def1a.in"))
    with pytest.raises(SystemExit):
        package_util.validate_test_names(task_id)
    out = capsys.readouterr().out
    assert "def1a.in" in out

    os.rename(os.path.join(package_path, "in", "def1a.in"), os.path.join(package_path, "in", "abc1a.in"))
    os.rename(os.path.join(package_path, "out", "abc1a.out"), os.path.join(package_path, "out", "def1a.out"))
    with pytest.raises(SystemExit):
        package_util.validate_test_names(task_id)
    out = capsys.readouterr().out
    assert "def1a.out" in out
