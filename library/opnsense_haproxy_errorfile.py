#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy errorfiles on OPNsense."""

DOCUMENTATION = r"""
---
module: opnsense_haproxy_errorfile
short_description: Manage HAProxy errorfiles on OPNsense
description:
  - Creates, updates, or deletes HAProxy errorfiles via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the errorfile (must be unique).
    type: str
    required: true
  code:
    description:
      - The HTTP status code for this errorfile (e.g. ``403``, ``503``).
    type: str
    required: true
  description:
    description:
      - A description for the errorfile.
    type: str
    default: ""
  content:
    description:
      - The errorfile content (HTML or text).
    type: str
    default: ""
  state:
    description:
      - Whether the errorfile should exist or not.
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
- name: Create a custom 503 errorfile
  opnsense_haproxy_errorfile:
    name: custom_503
    code: "503"
    description: "Custom maintenance page"
    content: "<html><body><h1>Maintenance</h1></body></html>"
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete an errorfile
  opnsense_haproxy_errorfile:
    name: custom_503
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


class ErrorfileModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy errorfiles."""

    OBJECT_TYPE = "errorfile"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "code": dict(type="str", required=True),
        "description": dict(type="str", default=""),
        "content": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        return {
            "code": self.module.params["code"],
            "description": self.module.params["description"],
            "content": self.module.params["content"],
        }


def main():
    module = ErrorfileModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
