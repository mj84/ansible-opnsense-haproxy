"""Shared setup for the end-to-end tests: the mock API and a roles path.

These tests run the real role, through the real ansible-playbook command,
against ``tests/mock_api/server.py``. Nothing is mocked below the HTTP layer.
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MOCK_DIR = REPO_ROOT / 'tests' / 'mock_api'
ROLE_NAME = 'local.maj.opnsense.haproxy'


def _load_mock_server():
    """Load tests/mock_api/server.py by path, without touching sys.path."""
    try:
        spec = importlib.util.spec_from_file_location('mock_haproxy_server', str(MOCK_DIR / 'server.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.MockHaproxyApi
    except Exception:  # pragma: no cover - covered by the skip below
        return None


MockHaproxyApi = _load_mock_server()

# The role's modules execute on the controller here, and they import requests.
CAN_RUN = (
    importlib.util.find_spec('ansible') is not None
    and importlib.util.find_spec('requests') is not None
    and MockHaproxyApi is not None
)


def _skip_unless_runnable():
    if not CAN_RUN:
        pytest.skip('needs ansible-core and requests in the test interpreter')


def _ansible_playbook():
    """The ansible-playbook executable belonging to this interpreter."""
    candidate = Path(sys.executable).parent / 'ansible-playbook'
    if candidate.exists():
        return str(candidate)
    found = shutil.which('ansible-playbook')
    if found:
        return found
    pytest.skip('ansible-playbook not found')


class PlaybookRun(object):
    """One ansible-playbook invocation, with the numbers from its recap."""

    def __init__(self, result):
        self.result = result
        self.stdout = result.stdout
        self.stderr = result.stderr
        match = re.search(r'^localhost\s*:.*$', result.stdout, re.M)
        recap = match.group(0) if match else ''
        self.ok = self._number(recap, 'ok')
        self.changed = self._number(recap, 'changed')
        self.failed = self._number(recap, 'failed')
        self.unreachable = self._number(recap, 'unreachable')

    @property
    def output(self):
        return self.stdout + self.stderr

    @staticmethod
    def _number(recap, key):
        match = re.search(r'%s=(\d+)' % key, recap)
        return int(match.group(1)) if match else -1

    def assert_ran(self):
        """The play must succeed; a failed task is a real bug, not a skip."""
        assert self.result.returncode == 0, self.output
        assert self.unreachable == 0, self.output
        assert self.failed == 0, self.output


@pytest.fixture()
def mock_api():
    """A fresh mock API on an ephemeral port, empty apart from the SSL objects."""
    _skip_unless_runnable()
    api = MockHaproxyApi()
    api.start()
    try:
        yield api
    finally:
        api.stop()


@pytest.fixture()
def run_playbook(tmp_path):
    """Runs one of the mock_api playbooks against a given mock API."""
    roles = tmp_path / 'roles'
    roles.mkdir()
    try:
        (roles / ROLE_NAME).symlink_to(REPO_ROOT)
    except OSError:  # pragma: no cover - filesystems without symlink support
        pytest.skip('symlinks are not supported on this filesystem')

    def run(playbook, mock_api, extra_vars=None, check=False):
        command = [
            _ansible_playbook(),
            '-i', str(MOCK_DIR / 'inventory'),
            str(MOCK_DIR / playbook),
            '-e', 'mock_api_url=http://127.0.0.1:%d' % mock_api.port,
        ]
        if check:
            command.append('--check')
        for key, value in sorted((extra_vars or {}).items()):
            command += ['-e', '%s=%s' % (key, value)]

        # Start from the ambient environment but drop ANSIBLE_* so a developer's
        # own settings cannot change what the role does.
        env = {k: v for k, v in os.environ.items() if not k.startswith('ANSIBLE_')}
        env['ANSIBLE_CONFIG'] = str(MOCK_DIR / 'ansible.cfg')
        env['ANSIBLE_ROLES_PATH'] = str(roles)

        result = subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=300,
        )
        return PlaybookRun(result)

    return run
