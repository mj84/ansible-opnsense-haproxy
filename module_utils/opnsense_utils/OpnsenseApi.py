#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""OPNsense HAProxy plugin API client.

Provides a wrapper around the OPNsense HAProxy plugin REST API for
managing load balancer objects (ACLs, backends, frontends, servers, etc.).
"""

from __future__ import absolute_import, division, print_function

import json
import typing
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

import requests

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class OpnsenseApiError(Exception):
    """Base exception for API errors."""


class ObjectNotFoundError(OpnsenseApiError):
    """Raised when a requested object cannot be found."""


class ObjectTypeError(OpnsenseApiError):
    """Raised when an unsupported object type is requested."""


class ConfigTestError(OpnsenseApiError):
    """Raised when the HAProxy configuration test fails."""


class Haproxy:
    """Client for the OPNsense HAProxy plugin API.

    Example
    -------
    >>> api = Haproxy("https://firewall.local", ("key", "secret"), ssl_verify=False)
    >>> backends = api.listObjects("backend")
    >>> api.createObject("backend", "my_backend", {"enabled": "1"})
    >>> api.applyConfig()
    """

    OBJECT_TYPES: typing.Final[List[str]] = [
        "acl",
        "action",
        "cpu",
        "backend",
        "errorfile",
        "frontend",
        "group",
        "healthcheck",
        "lua",
        "mapfile",
        "server",
        "user",
    ]

    def __init__(self, url: str, auth: Tuple[str, str], ssl_verify: bool = False) -> None:
        """Initialize the API client.

        Args:
            url: Base URL of the OPNsense firewall (e.g. ``https://firewall.local``).
            auth: Tuple of (api_key, api_secret) for HTTP basic auth.
            ssl_verify: Whether to verify SSL certificates. Defaults to ``False``.
        """
        self.url = url
        self.auth = auth
        self.ssl_verify = ssl_verify
        if not self.ssl_verify:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def getRequest(self, url: str) -> Dict[str, Any]:
        """Send a GET request and return parsed JSON as an OrderedDict.

        Args:
            url: Full request URL.

        Returns:
            Parsed JSON response.
        """
        r = requests.get(url, auth=self.auth, verify=self.ssl_verify, timeout=30)
        return json.loads(r.content, object_pairs_hook=OrderedDict)

    def postRequest(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a POST request and return parsed JSON.

        Args:
            url: Full request URL.
            data: JSON payload to send.

        Returns:
            Parsed JSON response.

        Raises:
            OpnsenseApiError: If the API reports a failure.
        """
        r = requests.post(url, auth=self.auth, verify=self.ssl_verify, json=data, timeout=30)
        r_json = r.json()
        # The API reports failures either as 'errorMessage' or inside 'result'.
        # 'result' is a dict for the settings endpoints but a plain string for
        # the service endpoints (configtest/reconfigure), so handle both.
        result = r_json.get("result")
        failed = result.get("failed") is True if isinstance(result, dict) else "failed" in str(result)
        if r_json.get("errorMessage") or failed:
            raise OpnsenseApiError("API threw an error: %s" % r_json)
        return r_json

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def listObjects(self, objecttype: str) -> List[Dict[str, Any]]:
        """List all objects of a given type.

        Args:
            objecttype: One of the supported object types.

        Returns:
            List of object dictionaries.

        Raises:
            ObjectTypeError: If *objecttype* is not supported.
        """
        self._validate_objecttype(objecttype)
        url = self.url + "/api/haproxy/settings/search" + str(objecttype) + "s"
        objs = dict(self.getRequest(url))
        return objs["rows"]

    def getObjectByName(self, objecttype: str, name: str) -> Dict[str, Any]:
        """Retrieve a single object by its name.

        Args:
            objecttype: The object type.
            name: The object's unique name.

        Returns:
            Object dictionary.

        Raises:
            ObjectNotFoundError: If no object with the given name exists.
        """
        uuid = self.getUuidByName(objecttype, name)
        url = self.url + "/api/haproxy/settings/get" + objecttype + "/" + uuid
        return dict(self.getRequest(url)[objecttype])

    def getObjectByUuid(self, objecttype: str, uuid: str) -> Dict[str, Any]:
        """Retrieve a single object by its UUID.

        Args:
            objecttype: The object type.
            uuid: The object's UUID (use ``''`` to get an empty template).

        Returns:
            Object dictionary.
        """
        url = self.url + "/api/haproxy/settings/get" + objecttype + "/" + uuid
        return dict(self.getRequest(url)[objecttype])

    def createObject(self, objecttype: str, objectname: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new object.

        Args:
            objecttype: The object type.
            objectname: The object's name.
            properties: Dictionary of property key-value pairs.

        Returns:
            API response dict.
        """
        properties["name"] = objectname
        self._validate_objecttype(objecttype)
        url = self.url + "/api/haproxy/settings/add" + objecttype
        obj = {objecttype: properties}
        return self.postRequest(url, obj)

    def updateObject(
        self, objecttype: str, objectname: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing object.

        Args:
            objecttype: The object type.
            objectname: The object's name.
            properties: Dictionary of property key-value pairs to update.

        Returns:
            API response dict.
        """
        self._validate_objecttype(objecttype)
        uuid = self.getUuidByName(objecttype, objectname)
        url = self.url + "/api/haproxy/settings/set" + objecttype + "/" + uuid
        objdict = {objecttype: properties}
        return self.postRequest(url, objdict)

    def deleteObject(self, objecttype: str, objectname: str) -> Dict[str, Any]:
        """Delete an existing object.

        Args:
            objecttype: The object type.
            objectname: The object's name.

        Returns:
            API response dict.
        """
        self._validate_objecttype(objecttype)
        uuid = self.getUuidByName(objecttype, objectname)
        url = self.url + "/api/haproxy/settings/del" + objecttype + "/" + uuid
        return self.postRequest(url, {})

    def applyConfig(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Run a configuration test and, if valid, reconfigure HAProxy.

        Returns:
            Tuple of (configtest_response, reconfigure_response).

        Raises:
            ConfigTestError: If the configuration test fails.
        """
        configtest_url = self.url + "/api/haproxy/service/configtest"
        reconfigure_url = self.url + "/api/haproxy/service/reconfigure"
        configtest = self.postRequest(configtest_url, {})
        if "is valid" in configtest["result"]:
            reconfigure = self.postRequest(reconfigure_url, {})
            return configtest, reconfigure
        raise ConfigTestError("Configtest did not succeed!")

    # ------------------------------------------------------------------
    # UUID / name resolution helpers
    # ------------------------------------------------------------------

    def getUuidByName(self, objecttype: str, name: str) -> str:
        """Resolve an object name to its UUID.

        Args:
            objecttype: The object type.
            name: The object's name.

        Returns:
            The object's UUID, or ``''`` if *name* is empty.

        Raises:
            ObjectNotFoundError: If no object with the given name exists.
        """
        if objecttype not in self.OBJECT_TYPES:
            raise ObjectTypeError("Objecttype %s not supported!" % objecttype)
        if name == "":
            return ""
        objects = self.listObjects(objecttype)
        for obj in objects:
            if obj["name"] == name:
                return obj["uuid"]
        raise ObjectNotFoundError(
            "Found no object of type %s with name %s!" % (objecttype, name)
        )

    def getUuidsFromNames(self, objecttype: str, names: List[str]) -> List[str]:
        """Resolve a list of object names to their UUIDs.

        Args:
            objecttype: The object type.
            names: List of object names.

        Returns:
            List of corresponding UUIDs.
        """
        return [self.getUuidByName(objecttype, name) for name in names]

    # ------------------------------------------------------------------
    # Selection helpers (for OPNsense's dict-with-``selected``-flag format)
    # ------------------------------------------------------------------

    @staticmethod
    def isSelectionDict(values: Any) -> bool:
        """True for the API's selection shape, e.g. ``{"<uuid>": {"selected": "1"}}``."""
        first = next(iter(values.values()), None) if isinstance(values, dict) else None
        return isinstance(first, dict) and "selected" in first

    def getSelected(self, valuesdict: Dict[str, Any], retval: str = "key") -> str:
        """Return the currently selected key or value from a selection dict.

        Args:
            valuesdict: Dict where each value has a ``'selected'`` key (1 = selected).
            retval: Return ``'key'`` (default) or a specific value key.

        Returns:
            The selected key or value, or ``''`` if nothing is selected. A value
            that is not a selection dict is returned unchanged.
        """
        if not valuesdict:
            return ""
        if not self.isSelectionDict(valuesdict):
            # Already a plain value — some endpoints answer without the
            # selection wrapper.
            return valuesdict
        for key, value in valuesdict.items():
            # The API sends 'selected' as a string ("1"), tests and callers may
            # pass an int.
            if str(value.get("selected")) == "1":
                if retval == "key":
                    return key
                if retval not in value:
                    raise KeyError("%s is no key in dict %s" % (retval, value))
                return value[retval]
        return ""

    def getSelectedList(
        self, valuesdict: Dict[str, Any], retval: str = "value"
    ) -> List[str]:
        """Return a list of selected keys or values from a selection dict.

        Args:
            valuesdict: Dict where each value has a ``'selected'`` key (1 = selected).
            retval: Return ``'key'`` or a specific value key.

        Returns:
            List of selected keys or values. A value that is not a selection
            dict is treated as the list of selected items itself.
        """
        selected_items: List[str] = []
        if isinstance(valuesdict, list) and valuesdict == []:
            return []
        if valuesdict == {} or valuesdict == "":
            return []
        if not self.isSelectionDict(valuesdict):
            if isinstance(valuesdict, str):
                return [valuesdict]
            return valuesdict
        for key, value in valuesdict.items():
            if str(value.get("selected")) == "1":
                if retval == "key":
                    selected_items.append(key)
                else:
                    if retval not in value:
                        raise KeyError("%s is no key in dict %s" % (retval, value))
                    selected_items.append(value[retval])
        return selected_items

    def findValueInDict(
        self,
        valuesdict: Dict[str, Any],
        searchvalue: str,
        prop: str = "value",
        retval: str = "key",
        warn_on_duplicate: bool = False,
    ) -> str:
        """Find the key (or value) whose *prop* matches *searchvalue*.

        Args:
            valuesdict: Dict to search.
            searchvalue: Value to match against *prop*.
            prop: Property name to compare (default ``'value'``).
            retval: Return ``'key'`` or *prop* itself.
            warn_on_duplicate: If ``True``, warn when multiple entries match
                and return the last one (YAML-style dedup).

        Returns:
            The matching key or property value, or ``''`` if not found.
        """
        import warnings

        matches: List[Tuple[str, Dict[str, Any]]] = []
        for key, value in valuesdict.items():
            if prop in value and value[prop] == searchvalue:
                matches.append((key, value))

        if not matches:
            return ""

        if warn_on_duplicate and len(matches) > 1:
            warnings.warn(
                "Multiple SSL objects found with description '%s': "
                "%d matches. Using the last one." % (searchvalue, len(matches))
            )

        last_key, last_value = matches[-1]
        if retval == "key":
            return last_key
        if retval not in last_value:
            raise KeyError("%s is no key in dict %s" % (retval, last_value))
        return last_value[retval]

    def getSslObjectKeys(
        self, ssl_objects: Dict[str, Any], names: List[str]
    ) -> List[str]:
        """Resolve SSL object names to their keys.

        Args:
            ssl_objects: Dict of SSL objects (from an empty template).
            names: List of SSL object names.

        Returns:
            List of corresponding keys (UUIDs).

        Raises:
            ObjectNotFoundError: If an SSL object name is not found.
        """
        ssl_object_keys: List[str] = []
        for name in names:
            ssl_object_key = self.findValueInDict(ssl_objects, name)
            if ssl_object_key == "":
                raise ObjectNotFoundError("No SSL object with name %s" % name)
            ssl_object_keys.append(ssl_object_key)
        return ssl_object_keys

    def getSelectedKeysFromDict(self, objs: Dict[str, Any]) -> List[str]:
        """Return keys where ``selected == '1'``.

        Args:
            objs: Dict of objects with a ``'selected'`` field.

        Returns:
            List of selected keys, or the input treated as the list of selected
            keys when it is not a selection dict.
        """
        if objs == {} or objs == "":
            return []
        if not self.isSelectionDict(objs):
            if isinstance(objs, str):
                return [objs]
            return objs
        return [key for key, value in objs.items() if str(value.get("selected")) == "1"]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def compareLists(
        list_one: List[str], list_two: List[str], order_sensitive: bool = False
    ) -> bool:
        """Compare two lists for equality, optionally checking order.

        Args:
            list_one: First list.
            list_two: Second list.
            order_sensitive: If ``True``, list order must also match.

        Returns:
            ``True`` if the lists contain the same elements.
        """
        if set(list_one) != set(list_two):
            return False
        if order_sensitive and list_one != list_two:
            return False
        return True

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_objecttype(self, objecttype: str) -> None:
        """Raise ``ObjectTypeError`` if *objecttype* is not supported."""
        if objecttype not in self.OBJECT_TYPES:
            raise ObjectTypeError("%s is no valid object type!" % objecttype)
