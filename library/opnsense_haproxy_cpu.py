#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy CPU affinity rules on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_cpu
short_description: Manage HAProxy CPU affinity rules on OPNsense
description:
  - Creates, updates, or deletes HAProxy CPU affinity rules via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the CPU affinity rule (must be unique).
    type: str
    required: true
  enabled:
    description:
      - Whether the CPU affinity rule is enabled.
    type: bool
    default: true
  process_id:
    description:
      - The process ID to bind to.
    type: str
    choices:
      - all
      - odd
      - even
      - x1
      - x2
      - x3
      - x4
      - x5
      - x6
      - x7
      - x8
      - x9
      - x10
      - x11
      - x12
      - x13
      - x14
      - x15
      - x16
      - x17
      - x18
      - x19
      - x20
      - x21
      - x22
      - x23
      - x24
      - x25
      - x26
      - x27
      - x28
      - x29
      - x30
      - x31
      - x32
      - x33
      - x34
      - x35
      - x36
      - x37
      - x38
      - x39
      - x40
      - x41
      - x42
      - x43
      - x44
      - x45
      - x46
      - x47
      - x48
      - x49
      - x50
      - x51
      - x52
      - x53
      - x54
      - x55
      - x56
      - x57
      - x58
      - x59
      - x60
      - x61
      - x62
      - x63
    default: all
  thread_id:
    description:
      - The thread ID to bind to.
    type: str
    choices:
      - all
      - odd
      - even
      - x1
      - x2
      - x3
      - x4
      - x5
      - x6
      - x7
      - x8
      - x9
      - x10
      - x11
      - x12
      - x13
      - x14
      - x15
      - x16
      - x17
      - x18
      - x19
      - x20
      - x21
      - x22
      - x23
      - x24
      - x25
      - x26
      - x27
      - x28
      - x29
      - x30
      - x31
      - x32
      - x33
      - x34
      - x35
      - x36
      - x37
      - x38
      - x39
      - x40
      - x41
      - x42
      - x43
      - x44
      - x45
      - x46
      - x47
      - x48
      - x49
      - x50
      - x51
      - x52
      - x53
      - x54
      - x55
      - x56
      - x57
      - x58
      - x59
      - x60
      - x61
      - x62
      - x63
    default: all
  cpu_id:
    description:
      - List of CPU IDs to bind to.
    type: list
    elements: str
    choices:
      - all
      - odd
      - even
      - x1
      - x2
      - x3
      - x4
      - x5
      - x6
      - x7
      - x8
      - x9
      - x10
      - x11
      - x12
      - x13
      - x14
      - x15
      - x16
      - x17
      - x18
      - x19
      - x20
      - x21
      - x22
      - x23
      - x24
      - x25
      - x26
      - x27
      - x28
      - x29
      - x30
      - x31
      - x32
      - x33
      - x34
      - x35
      - x36
      - x37
      - x38
      - x39
      - x40
      - x41
      - x42
      - x43
      - x44
      - x45
      - x46
      - x47
      - x48
      - x49
      - x50
      - x51
      - x52
      - x53
      - x54
      - x55
      - x56
      - x57
      - x58
      - x59
      - x60
      - x61
      - x62
      - x63
    default: ["all"]
  state:
    description:
      - Whether the CPU affinity rule should exist or not.
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
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create a CPU affinity rule
  opnsense_haproxy_cpu:
    name: haproxy_cpu0
    enabled: true
    process_id: x1
    thread_id: x1
    cpu_id: ["x0"]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a CPU affinity rule
  opnsense_haproxy_cpu:
    name: haproxy_cpu0
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

from ansible.module_utils.opnsense_utils import Haproxy, OpnsenseHaproxyModule


class CpuModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy CPU affinity rules."""

    OBJECT_TYPE = "cpu"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "enabled": dict(type="bool", default=True),
        "process_id": dict(
            type="str",
            choices=[
                "all", "odd", "even",
                "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10",
                "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
                "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
                "x31", "x32", "x33", "x34", "x35", "x36", "x37", "x38", "x39", "x40",
                "x41", "x42", "x43", "x44", "x45", "x46", "x47", "x48", "x49", "x50",
                "x51", "x52", "x53", "x54", "x55", "x56", "x57", "x58", "x59", "x60",
                "x61", "x62", "x63",
            ],
            default="all",
        ),
        "thread_id": dict(
            type="str",
            choices=[
                "all", "odd", "even",
                "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10",
                "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
                "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
                "x31", "x32", "x33", "x34", "x35", "x36", "x37", "x38", "x39", "x40",
                "x41", "x42", "x43", "x44", "x45", "x46", "x47", "x48", "x49", "x50",
                "x51", "x52", "x53", "x54", "x55", "x56", "x57", "x58", "x59", "x60",
                "x61", "x62", "x63",
            ],
            default="all",
        ),
        "cpu_id": dict(
            type="list",
            elements="str",
            choices=[
                "all", "odd", "even",
                "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10",
                "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19", "x20",
                "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29", "x30",
                "x31", "x32", "x33", "x34", "x35", "x36", "x37", "x38", "x39", "x40",
                "x41", "x42", "x43", "x44", "x45", "x46", "x47", "x48", "x49", "x50",
                "x51", "x52", "x53", "x54", "x55", "x56", "x57", "x58", "x59", "x60",
                "x61", "x62", "x63",
            ],
            default=["all"],
        ),
    }

    def _build_desired_state(self):
        return {
            "enabled": str(int(self.module.params["enabled"])),
            "process_id": self.module.params["process_id"],
            "thread_id": self.module.params["thread_id"],
            "cpu_id": ",".join(self.module.params["cpu_id"]),
        }

    def _diff_state(self, current, desired):
        """Custom diff for CPU module — process_id and thread_id use selection dicts."""
        changes = {}
        messages = []
        needs_change = False

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            if prop in ("process_id", "thread_id"):
                selected = self.api.getSelected(current_value)
                if selected != desired_value:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, desired_value))
            elif prop == "cpu_id":
                current_list = self.api.getSelectedList(current_value, retval="key")
                if not self.api.compareLists(current_list, self.module.params["cpu_id"]):
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, current_list, desired_value))
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = CpuModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
