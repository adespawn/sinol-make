import sys

import yaml
import glob

from sinol_make import configure_parsers
from sinol_make import util as sm_util
from sinol_make.commands.gen import Command
from sinol_make.commands.ingen import Command as IngenCommand
from sinol_make.commands.ingen.ingen_util import get_ingen
from sinol_make.commands.outgen import Command as OutgenCommand
from sinol_make.helpers import package_util, paths, cache
from tests.fixtures import *
from tests import util


def simple_run(arguments=None, command="gen"):
    if arguments is None:
        arguments = []
    parser = configure_parsers()
    args = parser.parse_args([command] + arguments)
    if command == "gen":
        command = Command()
    elif command == "ingen":
        command = IngenCommand()
    elif command == "outgen":
        command = OutgenCommand()
    else:
        raise ValueError("Invalid command")
    command.run(args)


def get_md5_sums(package_path):
    try:
        with open(os.path.join(package_path, "in", ".md5sums"), "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError | yaml.YAMLError:
        return {}


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_simple(capsys, create_package):
    """
    Test `ingen` command with no parameters on package with no tests.
    """
    simple_run()

    out = capsys.readouterr().out
    assert "Successfully generated input files." in out
    assert "Successfully generated all output files." in out


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_correct_inputs(capsys, create_package):
    """
    Test `ingen` command with all unchanged inputs.
    """
    task_id = package_util.get_task_id()
    correct_solution = package_util.get_correct_solution(task_id)
    cache.save_compiled(correct_solution, "exe")
    simple_run()
    md5_sums = get_md5_sums(create_package)

    # Run again to check if all inputs are unchanged.
    simple_run()
    out = capsys.readouterr().out
    assert "All output files are up to date." in out
    assert md5_sums == get_md5_sums(create_package)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_changed_inputs(capsys, create_package):
    """
    Test `ingen` command with changed inputs.
    """
    task_id = package_util.get_task_id()
    correct_solution = package_util.get_correct_solution(task_id)
    cache.save_compiled(correct_solution, "exe")
    simple_run()
    md5_sums = get_md5_sums(create_package)
    correct_md5 = md5_sums.copy()

    # Simulate change in input files.
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    for file in ins[:2]:
        md5_sums[os.path.basename(file)] = "0"

    with open(os.path.join(create_package, "in", ".md5sums"), "w") as f:
        yaml.dump(md5_sums, f)
    sys.stdout.write(str(md5_sums))

    simple_run()
    out = capsys.readouterr().out
    assert "Generating output files for 2 tests" in out
    for file in ins[:2]:
        assert "Successfully generated output file " + os.path.basename(file.replace("in", "out")) in out
    assert "Successfully generated all output files." in out
    assert correct_md5 == get_md5_sums(create_package)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_shell_ingen_unchanged(create_package):
    """
    Test if ingen.sh is unchanged after running `ingen` command.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    shell_ingen_path = get_ingen(task_id)
    assert os.path.splitext(shell_ingen_path)[1] == ".sh"
    edited_time = os.path.getmtime(shell_ingen_path)
    simple_run()
    assert edited_time == os.path.getmtime(shell_ingen_path)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_only_inputs_flag(create_package):
    """
    Test if `--only-inputs` flag works.
    """
    simple_run(["--only-inputs"])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) > 0
    assert len(outs) == 0
    assert not os.path.exists(os.path.join(create_package, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_ingen(create_package):
    """
    Test if `ingen` command works.
    """
    simple_run(None, "ingen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) > 0
    assert len(outs) == 0
    assert not os.path.exists(os.path.join(create_package, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                            indirect=True)
def test_only_outputs_flag(create_package):
    """
    Test if `--only-outputs` flag works.
    """
    simple_run(['--only-inputs'])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    in1 = ins[0]
    for file in ins[1:]:
        os.unlink(file)
    assert len(outs) == 0
    def in_to_out(file):
        return os.path.join(create_package, "out", os.path.basename(file).replace(".in", ".out"))

    simple_run(["--only-outputs"])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) == 1
    assert os.path.exists(in_to_out(in1))
    assert len(outs) == 1


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_outgen(create_package):
    """
    Test if `outgen` command works.
    """
    simple_run(None, "ingen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    in1 = ins[0]
    for file in ins[1:]:
        os.unlink(file)
    assert len(outs) == 0
    def in_to_out(file):
        return os.path.join(create_package, "out", os.path.basename(file).replace(".in", ".out"))

    simple_run(None, "outgen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) == 1
    assert os.path.exists(in_to_out(in1))
    assert len(outs) == 1


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_missing_output_files(create_package):
    """
    Test if `ingen` command generates missing output files.
    """
    package_path = create_package
    for args in [[], ["--only-outputs"]]:
        simple_run()
        outs = glob.glob(os.path.join(package_path, "out", "*.out"))
        os.unlink(outs[0])
        assert not os.path.exists(outs[0])
        simple_run(args)
        assert os.path.exists(outs[0])
        shutil.rmtree(paths.get_cache_path())
        os.unlink(os.path.join(package_path, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_correct_solution_changed(create_package):
    """
    Test if `.md5sums` is deleted when correct solution is changed.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    md5sums = os.path.join(package_path, "in", ".md5sums")
    simple_run()
    assert os.path.exists(md5sums)
    outputs = {}
    for output in glob.glob(os.path.join(package_path, "out", "*.out")):
        outputs[os.path.basename(output)] = sm_util.get_file_md5(output)

    solution = package_util.get_correct_solution(task_id)
    with open(os.path.join(solution), "w") as f:
        f.write("int main() {}")
    cache.check_correct_solution(task_id)
    assert not os.path.exists(md5sums)
    simple_run()
    assert os.path.exists(md5sums)
    for output in glob.glob(os.path.join(package_path, "out", "*.out")):
        assert outputs[os.path.basename(output)] != sm_util.get_file_md5(output)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_fsanitize(create_package):
    """
    Test if ingen is compiled with -fsanitize=address,undefined flags.
    """
    if sm_util.is_macos_arm():
        pytest.skip("-fsanitize=address,undefined is not supported on Apple Silicon")
    for ingen in ["prog/geningen3.cpp", "prog/geningen4.cpp"]:
        with pytest.raises(SystemExit) as e:
            simple_run([ingen])
        assert e.type == SystemExit
        assert e.value.code == 1
