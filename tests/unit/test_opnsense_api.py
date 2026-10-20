"""Unit tests for the OPNsense HAProxy API client."""

import pytest
from unittest.mock import MagicMock, patch

from module_utils.opnsense_utils.OpnsenseApi import (
    ConfigTestError,
    Haproxy,
    ObjectNotFoundError,
    ObjectTypeError,
    OpnsenseApiError,
)


class TestHaproxyInit:
    """Test Haproxy client initialization."""

    def test_init_defaults(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), ssl_verify=False)
        assert api.url == "https://firewall.local"
        assert api.auth == ("key", "secret")
        assert api.ssl_verify is False

    def test_init_ssl_verify(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), ssl_verify=True)
        assert api.ssl_verify is True


class TestValidateObjecttype:
    """Test object type validation."""

    def test_valid_type(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        # Should not raise
        api._validate_objecttype("backend")

    def test_invalid_type(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with pytest.raises(ObjectTypeError):
            api._validate_objecttype("invalid_type")


class TestCompareLists:
    """Test list comparison utility."""

    def test_identical_lists(self):
        assert Haproxy.compareLists(["a", "b", "c"], ["a", "b", "c"]) is True

    def test_same_elements_different_order(self):
        assert Haproxy.compareLists(["a", "b", "c"], ["c", "a", "b"]) is True

    def test_same_elements_different_order_order_sensitive(self):
        assert Haproxy.compareLists(["a", "b", "c"], ["c", "a", "b"], order_sensitive=True) is False

    def test_different_elements(self):
        assert Haproxy.compareLists(["a", "b"], ["a", "c"]) is False

    def test_empty_lists(self):
        assert Haproxy.compareLists([], []) is True

    def test_one_empty(self):
        assert Haproxy.compareLists(["a"], []) is False


class TestGetSelected:
    """Test getSelected helper."""

    def test_get_selected_key(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "http", "selected": 1},
            "uuid2": {"value": "tcp", "selected": 0},
        }
        assert api.getSelected(data) == "uuid1"

    def test_get_selected_value(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "http", "selected": 1},
            "uuid2": {"value": "tcp", "selected": 0},
        }
        assert api.getSelected(data, retval="value") == "http"

    def test_get_selected_no_match(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "http", "selected": 0},
            "uuid2": {"value": "tcp", "selected": 0},
        }
        assert api.getSelected(data) == ""


class TestGetSelectedList:
    """Test getSelectedList helper."""

    def test_get_selected_list_keys(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "web1", "selected": 1},
            "uuid2": {"value": "web2", "selected": 1},
            "uuid3": {"value": "web3", "selected": 0},
        }
        result = api.getSelectedList(data, retval="key")
        assert result == ["uuid1", "uuid2"]

    def test_get_selected_list_values(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "web1", "selected": 1},
            "uuid2": {"value": "web2", "selected": 1},
        }
        result = api.getSelectedList(data, retval="value")
        assert result == ["web1", "web2"]

    def test_get_selected_list_empty(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        assert api.getSelectedList([]) == []


class TestFindValueInDict:
    """Test findValueInDict helper."""

    def test_find_by_value(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "web1"},
            "uuid2": {"value": "web2"},
        }
        assert api.findValueInDict(data, "web1") == "uuid1"

    def test_find_not_found(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"value": "web1"},
        }
        assert api.findValueInDict(data, "nonexistent") == ""


class TestGetUuidByName:
    """Test UUID resolution by name."""

    def test_get_uuid_by_name(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch.object(api, "listObjects") as mock_list:
            mock_list.return_value = [
                {"name": "web1", "uuid": "uuid-123"},
                {"name": "web2", "uuid": "uuid-456"},
            ]
            assert api.getUuidByName("server", "web1") == "uuid-123"

    def test_get_uuid_by_name_empty(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        assert api.getUuidByName("server", "") == ""

    def test_get_uuid_by_name_not_found(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch.object(api, "listObjects") as mock_list:
            mock_list.return_value = [{"name": "web1", "uuid": "uuid-123"}]
            with pytest.raises(ObjectNotFoundError):
                api.getUuidByName("server", "web2")

    def test_get_uuid_invalid_type(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with pytest.raises(ObjectTypeError):
            api.getUuidByName("invalid", "name")


class TestGetSslObjectKeys:
    """Test SSL object key resolution."""

    def test_get_ssl_object_keys(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        ssl_objects = {
            "uuid1": {"value": "cert1"},
            "uuid2": {"value": "cert2"},
        }
        result = api.getSslObjectKeys(ssl_objects, ["cert1", "cert2"])
        assert result == ["uuid1", "uuid2"]

    def test_get_ssl_object_key_not_found(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        ssl_objects = {"uuid1": {"value": "cert1"}}
        with pytest.raises(ObjectNotFoundError):
            api.getSslObjectKeys(ssl_objects, ["cert_missing"])


class TestPostRequest:
    """Test POST request error handling."""

    def test_post_request_success(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"result": {"failed": False}}
            mock_post.return_value = mock_response
            result = api.postRequest("https://firewall.local/api/test", {})
            assert result == {"result": {"failed": False}}

    def test_post_request_failed(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"result": {"failed": True}}
            mock_post.return_value = mock_response
            with pytest.raises(OpnsenseApiError):
                api.postRequest("https://firewall.local/api/test", {})

    def test_post_request_error_message(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"errorMessage": "Something went wrong"}
            mock_post.return_value = mock_response
            with pytest.raises(OpnsenseApiError):
                api.postRequest("https://firewall.local/api/test", {})


class TestApplyConfig:
    """Test applyConfig method."""

    def test_apply_config_success(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch.object(api, "postRequest") as mock_post:
            mock_post.side_effect = [
                {"result": "config is valid"},
                {"result": "reconfigured"},
            ]
            result = api.applyConfig()
            assert len(result) == 2
            assert result[0] == {"result": "config is valid"}
            assert result[1] == {"result": "reconfigured"}

    def test_apply_config_failure(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        with patch.object(api, "postRequest") as mock_post:
            mock_post.return_value = {"result": "config is INVALID"}
            with pytest.raises(ConfigTestError):
                api.applyConfig()


class TestGetSelectedKeysFromDict:
    """Test getSelectedKeysFromDict helper."""

    def test_selected_keys(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"selected": "1"},
            "uuid2": {"selected": "0"},
            "uuid3": {"selected": "1"},
        }
        result = api.getSelectedKeysFromDict(data)
        assert result == ["uuid1", "uuid3"]

    def test_selected_keys_empty(self):
        api = Haproxy("https://firewall.local", ("key", "secret"), False)
        data = {
            "uuid1": {"selected": "0"},
        }
        result = api.getSelectedKeysFromDict(data)
        assert result == []
