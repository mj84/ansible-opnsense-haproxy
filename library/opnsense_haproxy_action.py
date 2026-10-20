#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy actions (Rules) on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_action
short_description: Manage HAProxy actions on OPNsense
description:
  - Creates, updates, or deletes HAProxy actions (rules) via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the action (must be unique).
    type: str
    required: true
  description:
    description:
      - A description for the action.
    type: str
    default: ""
  test_type:
    description:
      - The test type for the action.
    type: str
    choices: [if, unless]
    default: if
  operator:
    description:
      - The logical operator for combining ACLs.
    type: str
    choices: [and, or]
    default: and
  type:
    description:
      - The action type.
    type: str
    required: true
    choices:
      - use_backend
      - use_server
      - map_use_backend
      - http-request_allow
      - http-request_deny
      - http-request_tarpit
      - http-request_auth
      - http-request_redirect
      - http-request_lua
      - http-request_use-service
      - http-request_add-header
      - http-request_set-header
      - http-request_del-header
      - http-request_replace-header
      - http-request_replace-value
      - http-request_set-path
      - http-response_allow
      - http-response_deny
      - http-response_lua
      - http-response_add-header
      - http-response_set-header
      - http-response_del-header
      - http-response_replace-header
      - http-response_replace-value
      - http-response_set-status
      - tcp-request_connection_accept
      - tcp-request_connection_reject
      - tcp-request_content_accept
      - tcp-request_content_reject
      - tcp-request_content_lua
      - tcp-request_content_use-service
      - tcp-request_inspect-delay
      - tcp-response_content_accept
      - tcp-response_content_reject
      - tcp-response_content_lua
      - tcp-response_inspect-delay
      - custom
  value:
    description:
      - The action value. Format depends on I(type):
        - For header actions: I(name)::I(content) or I(name)::I(regex)
        - For set-status: I(code)::I(reason)
        - For use_backend: backend name
        - For others: the action-specific value
    type: str
    required: true
  linked_acls:
    description:
      - List of ACL names linked to this action.
    type: list
    elements: str
    default: []
  state:
    description:
      - Whether the action should exist or not.
    type: str
    choices: [present, absent]
    default: present
  api_url:
    description:
      - The URL of the OPNsense firewall API.
    type: str
    required: true
  api_key:
    description:
      - The API key for authentication.
    type: str
    required: true
    no_log: true
  api_secret:
    description:
      - The API secret for authentication.
    type: str
    required: true
    no_log: true
  api_ssl_verify:
    description:
      - Whether to verify the SSL certificate of the OPNsense API.
    type: bool
    default: false
  haproxy_reload:
    description:
      - Whether to reload HAProxy configuration after changes.
    type: bool
    default: false
seealso:
  - module: opnsense_haproxy_acl
  - module: opnsense_haproxy_backend
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create a use_backend action
  opnsense_haproxy_action:
    name: api_redirect
    type: use_backend
    value: api_pool
    linked_acls: [api_acl]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create an HTTP request deny action
  opnsense_haproxy_action:
    name: block_bad_robots
    type: http-request_deny
    value: ""
    linked_acls: [robot_acl]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create an HTTP header set action
  opnsense_haproxy_action:
    name: add_security_headers
    type: http-request_set-header
    value: X-Forwarded-Proto::https
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete an action
  opnsense_haproxy_action:
    name: api_redirect
    state: absent
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"
"""

RETURN = r"""
msg:
  description: Status message describing the action taken.
  type: str
  returned: always
changed:
  description: Whether the state was changed.
  type: bool
  returned: always
"""

from ansible.module_utils.opnsense_utils import OpnsenseHaproxyModule


class ActionModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy actions."""

    OBJECT_TYPE = "action"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "description": dict(type="str", default=""),
        "test_type": dict(type="str", choices=["if", "unless"], default="if"),
        "operator": dict(type="str", choices=["and", "or"], default="and"),
        "type": dict(
            type="str",
            required=True,
            choices=[
                "use_backend", "use_server", "map_use_backend",
                "http-request_allow", "http-request_deny", "http-request_tarpit",
                "http-request_auth", "http-request_redirect", "http-request_lua",
                "http-request_use-service", "http-request_add-header",
                "http-request_set-header", "http-request_del-header",
                "http-request_replace-header", "http-request_replace-value",
                "http-request_set-path",
                "http-response_allow", "http-response_deny", "http-response_lua",
                "http-response_add-header", "http-response_set-header",
                "http-response_del-header", "http-response_replace-header",
                "http-response_replace-value", "http-response_set-status",
                "tcp-request_connection_accept", "tcp-request_connection_reject",
                "tcp-request_content_accept", "tcp-request_content_reject",
                "tcp-request_content_lua", "tcp-request_content_use-service",
                "tcp-request_inspect-delay",
                "tcp-response_content_accept", "tcp-response_content_reject",
                "tcp-response_content_lua", "tcp-response_inspect-delay",
                "custom",
            ],
        ),
        "value": dict(type="str", required=True),
        "linked_acls": dict(type="list", elements="str", default=[]),
    }

    def _build_desired_state(self):
        params = self.module.params
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")

        # Resolve linked ACL UUIDs
        linked_acls_uuids = self._resolve_names_to_uuids(template, params["linked_acls"], "linkedAcls")

        # Build the type-specific value dict
        type_value = self._build_type_value(params["type"], params["value"], template)

        desired = {
            "description": params["description"],
            "testType": params["test_type"],
            "operator": params["operator"],
            "type": params["type"],
            "linkedAcls": ",".join(linked_acls_uuids),
        }
        desired.update(type_value)
        return desired

    def _build_type_value(self, action_type, value, template):
        """Build the type-specific properties for the action."""
        action_type_key = action_type.replace("-", "_")
        result = {}

        # HTTP header actions need name + content/regex
        if "http" in action_type and "header" in action_type:
            if "del" in action_type:
                result[action_type_key + "_name"] = value
            else:
                parts = value.split("::")
                result[action_type_key + "_name"] = parts[0]
                if "regex" in action_type and len(parts) > 1:
                    result[action_type_key + "_regex"] = parts[1]
                elif len(parts) > 1:
                    result[action_type_key + "_content"] = parts[1]
        # HTTP replace-value needs name + regex
        elif "http" in action_type and "value" in action_type:
            parts = value.split("::")
            result[action_type_key + "_name"] = parts[0]
            if len(parts) > 1:
                result[action_type_key + "_regex"] = parts[1]
        # HTTP set-status needs code + reason
        elif "http" in action_type and "status" in action_type:
            parts = value.split("::")
            result[action_type_key + "_code"] = parts[0]
            if len(parts) > 1:
                result[action_type_key + "_reason"] = parts[1]
        # use_backend needs a backend UUID
        elif action_type == "use_backend":
            backend_uuid = self._resolve_name_to_uuid(template, value, "use_backend")
            result[action_type_key] = backend_uuid
        else:
            result[action_type_key] = value

        return result

    def _diff_state(self, current, desired):
        """Custom diff for action — handles complex type-specific properties."""
        changes = {}
        messages = []
        needs_change = False
        params = self.module.params

        action_type_key = params["type"].replace("-", "_")
        complex_types = ["testType", "operator", "type"]
        # http_* actions carry sub-properties (header/value/status) instead of a
        # single value under action_type_key.
        has_http_subprops = (
            "http" in params["type"]
            and any(part in params["type"] for part in ("header", "value", "status"))
        )

        # Check simple properties
        for prop in ["description"]:
            if current.get(prop) != desired.get(prop):
                needs_change = True
                changes[prop] = desired[prop]
                messages.append("Changing %s: %s => %s" % (prop, current.get(prop), desired[prop]))

        # Check selection dict properties
        for ct in complex_types:
            if ct in current and ct in desired:
                selected = self.api.getSelected(current[ct])
                if selected != desired[ct]:
                    needs_change = True
                    changes[ct] = desired[ct]
                    messages.append("Changing %s: %s => %s" % (ct, selected, desired[ct]))

        # Check type-specific properties
        if action_type_key in desired:
            if action_type_key in current:
                # Simple type value
                if not has_http_subprops:
                    if current[action_type_key] != desired[action_type_key]:
                        needs_change = True
                        changes[action_type_key] = desired[action_type_key]
                        messages.append("Changing %s: %s => %s" % (
                            action_type_key, current[action_type_key], desired[action_type_key]
                        ))
            else:
                # Type key missing entirely — rebuild
                needs_change = True
                changes = {**changes, **{k: v for k, v in desired.items() if k not in changes}}
                messages.append("Action type key %s not in current object" % action_type_key)

        # Check HTTP header / value / status sub-properties
        if has_http_subprops:
            for special_prop in [action_type_key + "_name", action_type_key + "_regex",
                                 action_type_key + "_content", action_type_key + "_code",
                                 action_type_key + "_reason"]:
                if special_prop in desired:
                    if special_prop not in current:
                        needs_change = True
                        changes[special_prop] = desired[special_prop]
                        messages.append("Property %s missing" % special_prop)
                    elif current[special_prop] != desired[special_prop]:
                        needs_change = True
                        changes[special_prop] = desired[special_prop]
                        messages.append(
                            "Changing %s: %s => %s" % (special_prop, current[special_prop], desired[special_prop])
                        )

        # Check use_backend specifically
        if params["type"] == "use_backend" and not needs_change:
            current_use_backend = self.api.getSelected(current.get(action_type_key, {}))
            if current_use_backend != desired.get(action_type_key, ""):
                needs_change = True
                changes[action_type_key] = desired[action_type_key]
                messages.append(
                    "Changing %s: %s => %s" % (action_type_key, current_use_backend, desired[action_type_key])
                )

        # Check linked ACLs
        if "linkedAcls" in current and "linkedAcls" in desired:
            current_acls = self.api.getSelectedList(current["linkedAcls"])
            desired_acls = params["linked_acls"]
            if not self.api.compareLists(current_acls, desired_acls):
                needs_change = True
                changes["linkedAcls"] = desired["linkedAcls"]
                messages.append("Changing linkedAcls: %s => %s" % (current_acls, desired_acls))

        return needs_change, changes, messages


def main():
    module = ActionModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
