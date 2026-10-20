"""Unit tests for the OpnsenseHaproxyModule base class."""

from contextlib import contextmanager

from unittest.mock import MagicMock, patch

from module_utils.opnsense_utils.OpnsenseApi import ObjectNotFoundError
from module_utils.opnsense_utils.OpnsenseModule import OpnsenseHaproxyModule


# Minimal concrete subclass for testing
class _TestModule(OpnsenseHaproxyModule):
    OBJECT_TYPE = "test"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "value": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        return {
            "name": self.module.params["name"],
            "value": self.module.params["value"],
        }


@contextmanager
def _make_mock_module(params=None):
    """Create a _TestModule with mocked AnsibleModule and API client."""
    defaults = {
        "name": "test_obj",
        "value": "test_value",
        "api_url": "https://firewall.local",
        "api_key": "key",
        "api_secret": "secret",
        "api_ssl_verify": False,
        "haproxy_reload": False,
        "state": "present",
    }
    if params is not None:
        defaults.update(params)
    params = defaults
    mock_ansible = MagicMock()
    mock_ansible.params = params
    mock_ansible.check_mode = params.get("check_mode", False)
    mock_ansible.exit_json = MagicMock()
    mock_ansible.fail_json = MagicMock()

    with patch.object(OpnsenseHaproxyModule, "_create_ansible_module", return_value=mock_ansible):
        with patch.object(OpnsenseHaproxyModule, "_create_api_client") as mock_api:
            mock_api.return_value = MagicMock()
            module = _TestModule()
            module._mock_ansible = mock_ansible
            module._mock_api = mock_api.return_value
            yield module


class TestLoadCurrentState:
    """Test _load_current_state()."""

    def test_object_exists(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "old"}
            result = module._load_current_state()
            assert result is not None
            assert result["name"] == "test_obj"
            module._mock_api.getObjectByName.assert_called_once_with("test", "test_obj")

    def test_object_not_found(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            result = module._load_current_state()
            assert result is None


class TestRunPresent:
    """Test run() for state=present."""

    def test_create_new_object(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            result = module.run()
            assert result["changed"] is True
            assert "must be created" in result["msg"][0]
            module._mock_api.createObject.assert_called_once()

    def test_update_existing_object(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "old"}
            result = module.run()
            assert result["changed"] is True
            assert "must be changed" in result["msg"][0]
            module._mock_api.updateObject.assert_called_once()

    def test_no_change_needed(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "test_value"}
            result = module.run()
            assert result["changed"] is False
            assert "already present" in result["msg"][0]
            module._mock_api.updateObject.assert_not_called()

    def test_create_in_check_mode(self):
        with _make_mock_module({"check_mode": True}) as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            result = module.run()
            assert result["changed"] is True
            module._mock_api.createObject.assert_not_called()

    def test_update_in_check_mode(self):
        with _make_mock_module({"check_mode": True}) as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "old"}
            result = module.run()
            assert result["changed"] is True
            module._mock_api.updateObject.assert_not_called()

    def test_create_triggers_reload(self):
        with _make_mock_module({"haproxy_reload": True}) as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            module.run()
            module._mock_api.applyConfig.assert_called_once()

    def test_create_no_reload(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            module.run()
            module._mock_api.applyConfig.assert_not_called()


class TestRunAbsent:
    """Test run_absent() for state=absent."""

    def test_delete_existing_object(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "test_value"}
            result = module.run_absent()
            assert result["changed"] is True
            assert "must be deleted" in result["msg"][0]
            module._mock_api.deleteObject.assert_called_once()

    def test_object_already_absent(self):
        with _make_mock_module() as module:
            module._mock_api.getObjectByName.side_effect = ObjectNotFoundError("not found")
            result = module.run_absent()
            assert result["changed"] is False
            assert "is not present" in result["msg"][0]
            module._mock_api.deleteObject.assert_not_called()

    def test_delete_in_check_mode(self):
        with _make_mock_module({"check_mode": True}) as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "test_value"}
            result = module.run_absent()
            assert result["changed"] is True
            module._mock_api.deleteObject.assert_not_called()

    def test_delete_triggers_reload(self):
        with _make_mock_module({"haproxy_reload": True}) as module:
            module._mock_api.getObjectByName.return_value = {"name": "test_obj", "value": "test_value"}
            module.run_absent()
            module._mock_api.applyConfig.assert_called_once()


class TestDiffState:
    """Test the default _diff_state() implementation."""

    def test_simple_value_change(self):
        with _make_mock_module() as module:
            current = {"name": "test_obj", "value": "old"}
            desired = {"name": "test_obj", "value": "new"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is True
            assert changes["value"] == "new"
            assert len(messages) == 1

    def test_no_simple_change(self):
        with _make_mock_module() as module:
            current = {"name": "test_obj", "value": "same"}
            desired = {"name": "test_obj", "value": "same"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False
            assert changes == {}

    def test_selection_field_change(self):
        with _make_mock_module() as module:
            current = {"name": "test_obj", "field": {"uuid1": {"selected": 1, "value": "old_selected"}}}
            desired = {"name": "test_obj", "field": "uuid2"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is True
            assert changes == {"field": "uuid2"}

    def test_selection_field_unchanged(self):
        """The selected key is what counts, not the whole dict."""
        with _make_mock_module() as module:
            current = {"name": "test_obj", "field": {"uuid1": {"selected": 1, "value": "old"}}}
            desired = {"name": "test_obj", "field": "uuid1"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False
            assert changes == {}

    def test_name_field_ignored(self):
        with _make_mock_module() as module:
            current = {"name": "old_name", "value": "same"}
            desired = {"name": "new_name", "value": "same"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False

    def test_flat_values_are_not_treated_as_selection_dicts(self):
        """Empty, string and numeric values must not reach the selection branch."""
        with _make_mock_module() as module:
            current = {"name": "test_obj", "a": "", "b": 0, "c": {}, "d": [], "e": "plain"}
            desired = {"name": "test_obj", "a": "", "b": 0, "c": {}, "d": [], "e": "plain"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False
            module._mock_api.getSelected.assert_not_called()

    def test_is_selection_dict(self):
        """The API shape is {"<uuid>": {"selected": "1", ...}}."""
        is_selection = OpnsenseHaproxyModule._is_selection_dict
        assert is_selection({"uuid1": {"selected": "1", "name": "web1"}}) is True
        assert is_selection({}) is False
        assert is_selection({"uuid1": "web1"}) is False
        assert is_selection("web1") is False
        assert is_selection(None) is False

    def test_reference_behind_a_selection_dict_is_not_a_change(self):
        """A healthCheck the user already has must not look like a change.

        The API reports single-choice fields as a dict of every option with the
        chosen one flagged, so the current value has to be reduced to its key
        before it is compared with what the user asked for.
        """
        with _make_mock_module() as module:
            current = {"name": "test_obj", "field": {"hc-1": {"selected": "1", "name": "web"}}}
            desired = {"name": "test_obj", "field": "hc-1"}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False
            assert changes == {}

    def test_reference_list_behind_a_selection_dict_is_not_a_change(self):
        with _make_mock_module() as module:
            current = {
                "name": "test_obj",
                "field": {"acl-1": {"selected": "1", "name": "a"}, "acl-2": {"selected": "0"}},
            }
            desired = {"name": "test_obj", "field": ["acl-1"]}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False
            assert changes == {}

    def test_reference_list_in_the_desired_order_is_not_a_change(self):
        """The API may report the options in any order."""
        with _make_mock_module() as module:
            current = {
                "name": "test_obj",
                "field": {"acl-2": {"selected": "1"}, "acl-1": {"selected": "1"}},
            }
            desired = {"name": "test_obj", "field": ["acl-1", "acl-2"]}
            needs_change, changes, messages = module._diff_state(current, desired)
            assert needs_change is False


class TestReferenceKeys:
    """Test the _reference_keys helper that makes the shapes comparable."""

    def test_selection_dict_yields_the_selected_keys(self):
        keys = OpnsenseHaproxyModule._reference_keys
        assert keys({"a": {"selected": "1"}, "b": {"selected": "0"}, "c": {"selected": 1}}) == ["a", "c"]

    def test_comma_string_yields_the_parts(self):
        keys = OpnsenseHaproxyModule._reference_keys
        assert keys("a,b") == ["a", "b"]
        assert keys("a") == ["a"]
        assert keys("") == []

    def test_list_passes_through(self):
        assert OpnsenseHaproxyModule._reference_keys(["a", "b"]) == ["a", "b"]

    def test_scalars_yield_a_single_entry(self):
        keys = OpnsenseHaproxyModule._reference_keys
        assert keys("http") == ["http"]
        assert keys(None) == []
        assert keys(0) == []
