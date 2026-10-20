#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy Lua scripts on OPNsense."""

DOCUMENTATION = r"""
---
module: opnsense_haproxy_lua
short_description: Manage HAProxy Lua scripts on OPNsense
description:
  - Creates, updates, or deletes HAProxy Lua scripts via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the Lua script (must be unique).
    type: str
    required: true
  enabled:
    description:
      - Whether the Lua script is enabled.
    type: bool
    default: true
  description:
    description:
      - A description for the Lua script.
    type: str
    default: ""
  content:
    description:
      - The Lua script content.
    type: str
    default: ""
  state:
    description:
      - Whether the Lua script should exist or not.
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
- name: Create a Lua script
  opnsense_haproxy_lua:
    name: my_script
    enabled: true
    description: "My custom Lua script"
    content: |
      -- Lua code here
      core.register_action("my_action")
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a Lua script
  opnsense_haproxy_lua:
    name: my_script
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

from ansible.module_utils.opnsense_utils import OpnsenseHaproxyModule


class LuaModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy Lua scripts."""

    OBJECT_TYPE = "lua"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "enabled": dict(type="bool", default=True),
        "description": dict(type="str", default=""),
        "content": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        return {
            "enabled": str(int(self.module.params["enabled"])),
            "description": self.module.params["description"],
            "content": self.module.params["content"],
        }


def main():
    module = LuaModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
