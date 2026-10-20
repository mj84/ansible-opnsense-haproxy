#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy user groups on OPNsense."""

DOCUMENTATION = r"""
---
module: opnsense_haproxy_group
short_description: Manage HAProxy user groups on OPNsense
description:
  - Creates, updates, or deletes HAProxy user groups via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the group (must be unique).
    type: str
    required: true
  enabled:
    description:
      - Whether the group is enabled.
    type: bool
    default: true
  description:
    description:
      - A description for the group.
    type: str
    default: ""
  members:
    description:
      - List of user names that are members of this group.
    type: list
    elements: str
    default: []
  state:
    description:
      - Whether the group should exist or not.
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
  - module: opnsense_haproxy_user
  - module: opnsense_haproxy_acl
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create a group
  opnsense_haproxy_group:
    name: admins
    enabled: true
    description: "Administrator group"
    members: [admin, operator]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a group
  opnsense_haproxy_group:
    name: admins
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

from __future__ import absolute_import, division, print_function

from ansible.module_utils.opnsense_utils import Haproxy, OpnsenseHaproxyModule


class GroupModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy user groups."""

    OBJECT_TYPE = "group"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "enabled": dict(type="bool", default=True),
        "description": dict(type="str", default=""),
        "members": dict(type="list", elements="str", default=[]),
    }

    def _build_desired_state(self):
        params = self.module.params
        # Resolve member UUIDs from template
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")
        members_uuids = self._resolve_names_to_uuids(template, params["members"], "members")
        return {
            "enabled": str(int(params["enabled"])),
            "description": params["description"],
            "members": ",".join(members_uuids),
        }

    def _diff_state(self, current, desired):
        """Custom diff for group — members need list comparison."""
        changes = {}
        messages = []
        needs_change = False
        params = self.module.params

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            if prop == "members":
                current_list = self.api.getSelectedList(current_value)
                if not self.api.compareLists(current_list, params["members"]):
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append(
                        "Changing %s: %s => %s" % (prop, current_list, params["members"])
                    )
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = GroupModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
