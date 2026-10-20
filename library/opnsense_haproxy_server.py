#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy servers on OPNsense."""

DOCUMENTATION = r"""
---
module: opnsense_haproxy_server
short_description: Manage HAProxy servers on OPNsense
description:
  - Creates, updates, or deletes HAProxy backend servers via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the server (must be unique).
    type: str
    required: true
  address:
    description:
      - The server IP address or hostname.
    type: str
    required: true
  port:
    description:
      - The server port.
    type: str
    required: true
  description:
    description:
      - A description for the server.
    type: str
    default: ""
  checkport:
    description:
      - The port to use for healthchecks (defaults to I(port) if empty).
    type: str
    default: ""
  mode:
    description:
      - The server mode.
    type: str
    default: active
  ssl:
    description:
      - Enable SSL for the server.
    type: bool
    default: false
  ssl_verify:
    description:
      - Verify the server SSL certificate.
    type: bool
    default: true
  ssl_ca:
    description:
      - List of SSL CA certificate names to trust.
    type: list
    elements: str
    default: []
    notes:
      - Requires a two-step workflow due to OPNsense API limitations.
        See the role README for details.
  ssl_crl:
    description:
      - SSL CRL certificate name.
    type: str
    default: ""
    notes:
      - Requires a two-step workflow due to OPNsense API limitations.
        See the role README for details.
  ssl_client_certificate:
    description:
      - SSL client certificate name.
    type: str
    default: ""
    notes:
      - Requires a two-step workflow due to OPNsense API limitations.
        See the role README for details.
  weight:
    description:
      - The server weight.
    type: str
    default: ""
  check_interval:
    description:
      - Healthcheck interval.
    type: str
    default: ""
  check_down_interval:
    description:
      - Interval before marking server as down.
    type: str
    default: ""
  source:
    description:
      - Source address for the server.
    type: str
    default: ""
  advanced:
    description:
      - Advanced options string.
    type: str
    default: ""
  state:
    description:
      - Whether the server should exist or not.
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
  - module: opnsense_haproxy_backend
"""

EXAMPLES = r"""
- name: Create a backend server
  opnsense_haproxy_server:
    name: web1
    address: 10.0.0.1
    port: "8080"
    description: "Web server 1"
    mode: active
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create a server with SSL
  opnsense_haproxy_server:
    name: secure_backend
    address: 10.0.0.2
    port: "443"
    ssl: true
    ssl_verify: true
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a server
  opnsense_haproxy_server:
    name: web1
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


class ServerModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy backend servers."""

    OBJECT_TYPE = "server"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "address": dict(type="str", required=True),
        "port": dict(type="str", required=True),
        "description": dict(type="str", default=""),
        "checkport": dict(type="str", default=""),
        "mode": dict(type="str", default="active"),
        "ssl": dict(type="bool", default=False),
        "ssl_verify": dict(type="bool", default=True),
        "ssl_ca": dict(type="list", elements="str", default=[]),
        "ssl_crl": dict(type="str", default=""),
        "ssl_client_certificate": dict(type="str", default=""),
        "weight": dict(type="str", default=""),
        "check_interval": dict(type="str", default=""),
        "check_down_interval": dict(type="str", default=""),
        "source": dict(type="str", default=""),
        "advanced": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        params = self.module.params
        # Fetch the empty server template — contains all available SSL object
        # selection dicts so we can resolve names to UUIDs regardless of what
        # is currently linked to the server.
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")

        # For creation, SSL references must be empty (two-step workflow)
        # For updates, we resolve them from the template
        if self._load_current_state() is None:
            # New object — SSL refs cleared
            ssl_ca = ""
            ssl_crl = ""
            ssl_client_certificate = ""
        else:
            # Existing object — resolve from template
            ssl_ca = self._resolve_ssl_refs(params["ssl_ca"], template, "sslCA")
            ssl_crl = self._resolve_ssl_single_ref(params["ssl_crl"], template, "sslCRL")
            ssl_client_certificate = self._resolve_ssl_single_ref(
                params["ssl_client_certificate"], template, "sslClientCertificate"
            )

        return {
            "name": params["name"],
            "address": params["address"],
            "description": params["description"],
            "port": params["port"],
            "checkport": params["checkport"] or params["port"],
            "mode": params["mode"],
            "ssl": str(int(params["ssl"])),
            "sslVerify": str(int(params["ssl_verify"])),
            "sslCA": ssl_ca,
            "sslCRL": ssl_crl,
            "sslClientCertificate": ssl_client_certificate,
            "weight": params["weight"],
            "checkInterval": params["check_interval"],
            "checkDownInterval": params["check_down_interval"],
            "source": params["source"],
            "advanced": params["advanced"],
        }

    def _resolve_ssl_refs(self, names, template, key):
        """Resolve SSL CA names to UUIDs from the server template.

        Uses the empty-object template which contains all available SSL
        objects, not just the ones currently linked to the server.
        """
        if not names:
            return ""
        uuids = []
        for name in names:
            uuid = self.api.findValueInDict(
                template[key], searchvalue=name, warn_on_duplicate=True
            )
            if uuid != "":
                uuids.append(uuid)
        return ",".join(uuids)

    def _resolve_ssl_single_ref(self, name, template, key):
        """Resolve a single SSL reference (CRL or client cert) from the template.

        Uses the empty-object template which contains all available SSL
        objects, not just the ones currently linked to the server.
        """
        if not name:
            return ""
        return self.api.findValueInDict(
            template[key], searchvalue=name, warn_on_duplicate=True
        )

    def _diff_state(self, current, desired):
        """Custom diff for server — handles selection fields and SSL references."""
        changes = {}
        messages = []
        needs_change = False
        params = self.module.params

        # Fetch template for resolving SSL references from the full API catalog
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            if prop == "mode":
                selected = self.api.getSelected(current_value)
                if selected != params["mode"]:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, params["mode"]))
            elif prop in ("sslCA", "sslCRL", "sslClientCertificate"):
                # SSL references — compare resolved values
                if prop == "sslCA":
                    current_list = self.api.getSelectedList(current_value)
                    if not self.api.compareLists(current_list, params["ssl_ca"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params["ssl_ca"]))
                elif prop == "sslCRL":
                    current_selected = self.api.getSelected(current_value)
                    desired_uuid = self._resolve_ssl_single_ref(
                        params["ssl_crl"], template, "sslCRL"
                    )
                    if current_selected != desired_uuid:
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_selected, params["ssl_crl"]))
                elif prop == "sslClientCertificate":
                    current_selected = self.api.getSelected(current_value, retval="value")
                    if current_selected != params["ssl_client_certificate"]:
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append(
                            "Changing %s: %s => %s"
                            % (prop, current_selected, params["ssl_client_certificate"])
                        )
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = ServerModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
