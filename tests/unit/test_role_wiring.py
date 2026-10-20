"""Regression tests for the wiring between the role tasks and the modules.

These cover bugs that made the role a no-op or a crash, none of which were
visible from the per-class unit tests:

- modules were called with connection arguments only, so the objects from the
  ``opnsense_haproxy_*`` dicts never reached the API;
- ``_create_ansible_module`` used the base class's empty argument spec, so no
  module parameter was declared;
- ``postRequest`` assumed a dict response, but configtest/reconfigure return a
  plain string;
- a module existed with no task file, so it could never be used.
"""

import json
import pathlib
import re
import sys

import pytest
import yaml
from unittest.mock import MagicMock, patch

from module_utils.opnsense_utils.OpnsenseApi import Haproxy, OpnsenseApiError
from module_utils.opnsense_utils.OpnsenseModule import OpnsenseHaproxyModule

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TASKS_DIR = REPO_ROOT / "tasks"
LIBRARY_DIR = REPO_ROOT / "library"


# --- module argument spec ---------------------------------------------------

class _SpecModule(OpnsenseHaproxyModule):
    """Subclass whose parameters only exist in its own ARGUMENT_SPEC."""

    OBJECT_TYPE = "test"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "width": dict(type="int", default=7),
        "special": dict(type="str", no_log=False),
    }

    def _build_desired_state(self):
        return {"name": self.module.params["name"]}


def _build_module(args):
    """Run _create_ansible_module the way main() does, with args on argv."""
    module = _SpecModule.__new__(_SpecModule)
    argv = ["opnsense_haproxy_test", json.dumps({"ANSIBLE_MODULE_ARGS": args})]
    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr(sys, "argv", argv)
        return module._create_ansible_module()


def test_subclass_argument_spec_reaches_ansible_module():
    """The subclass spec must be merged in, not the empty base class one."""
    base_params = {
        "api_url": "https://fw.local",
        "api_key": "k",
        "api_secret": "s",
        "api_ssl_verify": False,
        "haproxy_reload": False,
        "state": "present",
    }
    module = _build_module({**base_params, "name": "obj", "width": 42})

    assert module.params["name"] == "obj"
    # A parameter that only the subclass declares must survive.
    assert module.params["width"] == 42
    # Defaults from the subclass spec are applied.
    assert module.params["special"] is None or isinstance(module.params["special"], str)


def test_base_spec_is_still_merged():
    """Connection arguments from the base class keep working."""
    module = _build_module({
        "name": "obj",
        "api_url": "https://fw.local",
        "api_key": "k",
        "api_secret": "s",
        "api_ssl_verify": False,
    })
    assert module.params["api_url"] == "https://fw.local"
    assert module.params["state"] == "present"
    assert module.check_mode is False


# --- API client responses ---------------------------------------------------

def test_post_request_accepts_string_result():
    """configtest/reconfigure answer with a string, not a dict.

    Reading 'failed' out of that string used to raise AttributeError, which
    broke every run with haproxy_reload: true.
    """
    api = Haproxy("https://firewall.local", ("key", "secret"), False)
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "Configuration imported OK."}
        mock_post.return_value = mock_response
        result = api.postRequest("https://fw.local/api/settings/reconfigure", {})
        assert result == {"result": "Configuration imported OK."}


def test_post_request_raises_on_failed_string_result():
    api = Haproxy("https://fw.local", ("key", "secret"), False)
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "configuration failed"}
        mock_post.return_value = mock_response
        with pytest.raises(OpnsenseApiError):
            api.postRequest("https://fw.local/api/settings/configtest", {})


# --- role task files --------------------------------------------------------

def _task_files():
    return sorted(TASKS_DIR.glob("manage_*.yml"))


def _library_modules():
    return {path.stem for path in LIBRARY_DIR.glob("*.py")}


def test_every_module_is_reachable_from_the_role():
    """A module with no task file can never be used (mapfiles regression)."""
    used = set()
    for path in _task_files():
        for task in yaml.safe_load(path.read_text()):
            used.update(key for key in task if key in _library_modules())
    assert used == _library_modules(), f"unreachable modules: {_library_modules() - used}"


@pytest.mark.parametrize("path", _task_files(), ids=lambda p: p.name)
def test_task_passes_object_data_to_the_module(path):
    """Each task must hand the object's own parameters to the module.

    The bug: tasks passed only the connection arguments, so the role reported
    success without configuring anything.
    """
    tasks = yaml.safe_load(path.read_text())
    assert tasks, path

    for task in tasks:
        module_args = {k: v for k, v in task.items() if k in _library_modules()}
        assert len(module_args) == 1, f"{path.name}: no module call found"
        (module_name, args), = module_args.items()

        # Arguments are merged from the item's dict, its name and the shared
        # connection arguments.
        assert isinstance(args, str), f"{path.name}: arguments must be one merged template"
        assert "item.value" in args, f"{path.name}: object parameters are not passed"
        assert "item.key" in args, f"{path.name}: object name is not passed"
        assert "opnsense_haproxy_connection_args" in args

        # The loop must iterate the role variable for this object type.
        match = re.search(r"opnsense_haproxy_\w+", task["loop"])
        assert match, f"{path.name}: unexpected loop {task['loop']}"
        defaults = yaml.safe_load((REPO_ROOT / "defaults" / "main.yml").read_text())
        assert match.group() in defaults, f"{path.name}: {match.group()} is not a role variable"


def test_task_include_order_matches_dependencies():
    """Referenced objects must exist first: servers before backends, etc."""
    includes = [
        task["ansible.builtin.include_tasks"].split("/")[-1]
        for task in yaml.safe_load((TASKS_DIR / "main.yml").read_text())
        if "ansible.builtin.include_tasks" in task
    ]
    order = {name: index for index, name in enumerate(includes)}

    for earlier, later in [
        ("manage_acls.yml", "manage_frontends.yml"),
        ("manage_servers.yml", "manage_backends.yml"),
        ("manage_backends.yml", "manage_frontends.yml"),
        ("manage_users.yml", "manage_groups.yml"),
        ("manage_healthchecks.yml", "manage_servers.yml"),
    ]:
        assert order[earlier] < order[later], f"{earlier} must be included before {later}"
