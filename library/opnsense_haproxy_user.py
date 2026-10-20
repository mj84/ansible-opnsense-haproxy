#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy users on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_user
short_description: Manage HAProxy users on OPNsense
description:
  - Creates, updates, or deletes HAProxy users via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The username (must be unique).
    type: str
    required: true
  password:
    description:
      - The user password.
    type: str
    required: false
    no_log: true
  enabled:
    description:
      - Whether the user is enabled.
    type: bool
    default: true
  description:
    description:
      - A description for the user.
    type: str
    default: ""
  state:
    description:
      - Whether the user should exist or not.
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
  - module: opnsense_haproxy_group
  - module: opnsense_haproxy_acl
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create a user
  opnsense_haproxy_user:
    name: admin
    password: "secret"
    enabled: true
    description: "Administrator"
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a user
  opnsense_haproxy_user:
    name: admin
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


class UserModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy users."""

    OBJECT_TYPE = "user"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "password": dict(type="str", required=False, no_log=True),
        "enabled": dict(type="bool", default=True),
        "description": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        return {
            "password": self.module.params["password"],
            "enabled": str(int(self.module.params["enabled"])),
            "description": self.module.params["description"],
        }


def main():
    module = UserModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
