"""Base class for OPNsense HAProxy management modules.

All custom modules should inherit from ``OpnsenseHaproxyModule`` and only
implement ``_build_desired_state()`` (and optionally ``_diff_state()`` for
complex comparison logic).
"""

from __future__ import absolute_import, division, print_function

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule, _load_params

from .OpnsenseApi import (
    ConfigTestError,
    Haproxy,
    ObjectNotFoundError,
    OpnsenseApiError,
)


class OpnsenseHaproxyModule(ABC):
    """Base class for OPNsense HAProxy CRUD modules.

    Subclasses must define:

    * ``OBJECT_TYPE`` — the OPNsense API object type string (e.g. ``'backend'``).
    * ``ARGUMENT_SPEC`` — a dict of module-specific parameters.
    * ``_build_desired_state()`` — returns a dict of properties to send to the API.

    Optional overrides:

    * ``_diff_state(current, desired)`` — custom diff logic for complex types.
    * ``_resolve_references(template, names, key)`` — custom UUID resolution.
    """

    OBJECT_TYPE: str = None  # type: ignore
    ARGUMENT_SPEC: Dict[str, Any] = {}

    # Parameter prefixes for deprecated naming (e.g. acl_name -> name)
    DEPRECATED_PARAMS: Dict[str, str] = {}

    def __init__(self, supports_check_mode: bool = True):
        """Initialize the module.

        Args:
            supports_check_mode: Whether the module supports Ansible check mode.
        """
        self.module: AnsibleModule = self._create_ansible_module(supports_check_mode)
        self.api: Haproxy = self._create_api_client()
        self._check_mode: bool = self.module.check_mode

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """Execute the module: load state, diff, apply, return result.

        Returns:
            Dict suitable for ``module.exit_json(**result)``.
        """
        current = self._load_current_state()
        desired = self._build_desired_state()

        if current is None:
            # Object does not exist — ensure it shouldn't
            state = self.module.params.get("state", "present")
            if state == "absent":
                return {"changed": False, "msg": [f"{self.OBJECT_TYPE.title()} is not present."]}
            # Creating new object
            if not self._check_mode:
                try:
                    self.api.createObject(self.OBJECT_TYPE, self._get_name(desired), desired)
                    self._maybe_reload()
                except OpnsenseApiError as exc:
                    self.module.fail_json(msg=[f"Failed to create {self.OBJECT_TYPE}: {exc}"])
            return {"changed": True, "msg": [f"{self.OBJECT_TYPE.title()} must be created."]}

        # Object exists — check if update is needed
        needs_change, changes, messages = self._diff_state(current, desired)

        if not needs_change:
            return {"changed": False, "msg": [f"{self.OBJECT_TYPE.title()} already present."]}

        # Apply changes
        if not self._check_mode:
            try:
                self.api.updateObject(self.OBJECT_TYPE, self._get_name(current), changes)
                self._maybe_reload()
            except OpnsenseApiError as exc:
                self.module.fail_json(msg=[f"Failed to update {self.OBJECT_TYPE}: {exc}"])

        return {"changed": True, "msg": [f"{self.OBJECT_TYPE.title()} must be changed."] + messages}

    def run_absent(self) -> Dict[str, Any]:
        """Execute a delete operation (used when state == 'absent').

        Returns:
            Dict suitable for ``module.exit_json(**result)``.
        """
        current = self._load_current_state()
        if current is None:
            return {"changed": False, "msg": [f"{self.OBJECT_TYPE.title()} is not present."]}

        if not self._check_mode:
            try:
                self.api.deleteObject(self.OBJECT_TYPE, self._get_name(current))
                self._maybe_reload()
            except OpnsenseApiError as exc:
                self.module.fail_json(msg=[f"Failed to delete {self.OBJECT_TYPE}: {exc}"])

        return {"changed": True, "msg": [f"{self.OBJECT_TYPE.title()} must be deleted."]}

    # ------------------------------------------------------------------
    # State loading
    # ------------------------------------------------------------------

    def _load_current_state(self) -> Optional[Dict[str, Any]]:
        """Load the current state of the object from the API.

        Returns:
            Object dict if found, ``None`` otherwise.
        """
        name = self._get_name({})
        try:
            return self.api.getObjectByName(self.OBJECT_TYPE, name)
        except ObjectNotFoundError:
            return None

    def _get_name(self, desired: Dict[str, Any]) -> str:
        """Get the object name from module params or desired state."""
        name_param = self.module.params.get("name")
        if name_param:
            return name_param
        # Fallback: try common name keys
        for key in ["name", self.OBJECT_TYPE + "_name"]:
            val = desired.get(key)
            if val:
                return val
        return self.module.params.get(self.OBJECT_TYPE + "_name", "")

    # ------------------------------------------------------------------
    # API client
    # ------------------------------------------------------------------

    def _create_api_client(self) -> Haproxy:
        """Create the OPNsense API client from module parameters."""
        api_url = self.module.params["api_url"]
        api_key = self.module.params["api_key"]
        api_secret = self.module.params["api_secret"]
        api_ssl_verify = self.module.params.get("api_ssl_verify", False)
        return Haproxy(api_url, (api_key, api_secret), api_ssl_verify)

    def _maybe_reload(self) -> None:
        """Reload HAProxy configuration if ``haproxy_reload`` is set and not in check mode."""
        if self.module.params.get("haproxy_reload", False) and not self._check_mode:
            try:
                self.api.applyConfig()
            except ConfigTestError as exc:
                self.module.fail_json(msg=[f"HAProxy config test failed: {exc}"])
            except OpnsenseApiError as exc:
                self.module.fail_json(msg=[f"HAProxy reload failed: {exc}"])

    # ------------------------------------------------------------------
    # Diff logic
    # ------------------------------------------------------------------

    def _diff_state(
        self, current: Dict[str, Any], desired: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """Compare current and desired state.

        Returns:
            Tuple of (needs_change, changes_dict, messages_list).
        """
        # Default implementation — simple property comparison
        changes: Dict[str, Any] = {}
        messages: List[str] = []
        needs_change = False

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            # Skip the name field — it doesn't change
            if prop == "name":
                continue

            # OPNsense reports single- and multi-choice fields as
            # {"<uuid>": {"selected": "1", ...}} while the desired state holds
            # the resolved key (or a comma-joined string of keys). Reduce both
            # sides to key lists so they can be compared at all.
            if self._is_selection_dict(current_value) or isinstance(
                desired_value, (list, dict)
            ):
                current_keys = self._reference_keys(current_value)
                desired_keys = self._reference_keys(desired_value)
                if not Haproxy.compareLists(current_keys, desired_keys):
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append(
                        "Changing %s: %s => %s" % (prop, current_keys, desired_keys)
                    )
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages

    @staticmethod
    def _is_selection_dict(value: Any) -> bool:
        """True for an OPNsense selection dict, e.g. ``{"<uuid>": {"selected": "1"}}``."""
        return Haproxy.isSelectionDict(value)

    @staticmethod
    def _reference_keys(value: Any) -> List[str]:
        """Reduce a reference field to its list of UUID keys.

        The same reference arrives in three shapes: as the API's selection dict
        (``{"<uuid>": {"selected": "1", ...}}``), as the comma-joined string
        ``_build_desired_state()`` produces, or as a plain list. All three mean
        the same thing, so compare them as key lists.

        Args:
            value: Reference field in any of the shapes above.

        Returns:
            List of UUID keys, in the order they appear.
        """
        if isinstance(value, str):
            return [key for key in value.split(",") if key != ""]
        if isinstance(value, dict):
            return [
                key
                for key, entry in value.items()
                if isinstance(entry, dict) and str(entry.get("selected")) == "1"
            ]
        if isinstance(value, list):
            return list(value)
        return []

    # ------------------------------------------------------------------
    # Reference resolution helpers
    # ------------------------------------------------------------------

    def _resolve_name_to_uuid(
        self, template: Dict[str, Any], ref_name: str, ref_key: str
    ) -> str:
        """Resolve a single name to a UUID using an empty-object template.

        Args:
            template: Empty object dict from ``api.getObjectByUuid(type, '')``.
            ref_name: The name to resolve.
            ref_key: The key in the template dict (e.g. ``'linkedServers'``).

        Returns:
            The UUID, or ``''`` if not found.
        """
        if ref_name == "":
            return ""
        return self.api.findValueInDict(template[ref_key], ref_name)

    def _resolve_names_to_uuids(
        self, template: Dict[str, Any], names: List[str], ref_key: str
    ) -> List[str]:
        """Resolve a list of names to UUIDs using an empty-object template.

        Args:
            template: Empty object dict from ``api.getObjectByUuid(type, '')``.
            names: List of names to resolve.
            ref_key: The key in the template dict.

        Returns:
            List of UUIDs.
        """
        return [self._resolve_name_to_uuid(template, name, ref_key) for name in names]

    # ------------------------------------------------------------------
    # Internal: AnsibleModule creation
    # ------------------------------------------------------------------

    def _create_ansible_module(self, supports_check_mode: bool = True) -> AnsibleModule:
        """Create the AnsibleModule with shared + subclass-specific params."""
        base_spec = {
            "api_url": dict(type="str", required=True),
            "api_key": dict(type="str", required=True, no_log=True),
            "api_secret": dict(type="str", required=True, no_log=True),
            "api_ssl_verify": dict(type="bool", default=False),
            "haproxy_reload": dict(type="bool", default=False),
            "state": dict(type="str", choices=["present", "absent"], default="present"),
        }
        # Merge base spec with the subclass' own spec (self, not the base class,
        # so each module registers its own parameters)
        subclass_spec = self.ARGUMENT_SPEC

        # Deleting an object only needs its name — the type-specific parameters
        # are not known any more, so they must not be demanded.
        if self._raw_params().get("state") == "absent":
            subclass_spec = {
                key: ({**spec, "required": False} if spec.get("required") and key != "name" else spec)
                for key, spec in self.ARGUMENT_SPEC.items()
            }

        return AnsibleModule(
            argument_spec={**base_spec, **subclass_spec},
            supports_check_mode=supports_check_mode,
        )

    @staticmethod
    def _raw_params() -> Dict[str, Any]:
        """Parameters as Ansible handed them over, before validation."""
        try:
            return _load_params()
        except (Exception, SystemExit):
            return {}

    # ------------------------------------------------------------------
    # Abstract methods (must be implemented by subclasses)
    # ------------------------------------------------------------------

    @abstractmethod
    def _build_desired_state(self) -> Dict[str, Any]:
        """Build the desired state dictionary to send to the API.

        Returns:
            Dict of property key-value pairs.
        """
        pass
