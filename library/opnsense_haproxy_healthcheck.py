#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy healthchecks on OPNsense."""

DOCUMENTATION = r"""
---
module: opnsense_haproxy_healthcheck
short_description: Manage HAProxy healthchecks on OPNsense
description:
  - Creates, updates, or deletes HAProxy healthchecks via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the healthcheck (must be unique).
    type: str
    required: true
  type:
    description:
      - The healthcheck protocol type.
    type: str
    choices:
      - tcp
      - http
      - agent
      - ldap
      - mysql
      - pgsql
      - redis
      - smtp
      - esmtp
      - ssl
    default: http
  description:
    description:
      - A description for the healthcheck.
    type: str
    default: ""
  interval:
    description:
      - The check interval (e.g. ``2s``, ``30s``, ``5000ms``).
    type: str
    default: "2s"
  force_ssl:
    description:
      - Force SSL for the healthcheck.
    type: bool
    default: false
  checkport:
    description:
      - The port to use for healthchecks (defaults to the server port if empty).
    type: str
    default: ""
  http_method:
    description:
      - The HTTP method for HTTP healthchecks.
    type: str
    default: options
  http_uri:
    description:
      - The URI to check for HTTP healthchecks.
    type: str
    default: "/"
  http_version:
    description:
      - The HTTP version for healthchecks.
    type: str
    choices: [http10, http11]
    default: http10
  http_host:
    description:
      - The Host header value for HTTP healthchecks.
    type: str
    default: localhost
  http_expression_enabled:
    description:
      - Enable expression-based HTTP healthcheck matching.
    type: bool
    default: false
  http_expression:
    description:
      - The expression type for HTTP healthcheck matching.
    type: str
    choices:
      - ""
      - status
      - rstatus
      - string
      - rstring
    default: ""
  http_negate:
    description:
      - Negate the HTTP healthcheck expression.
    type: bool
    default: false
  http_value:
    description:
      - The expected value for HTTP healthcheck matching.
    type: str
    default: ""
  tcp_enabled:
    description:
      - Enable TCP healthcheck payload sending.
    type: bool
    default: false
  tcp_send_value:
    description:
      - The payload to send for TCP healthchecks.
    type: str
    default: ""
  tcp_match_type:
    description:
      - The type of TCP match.
    type: str
    choices:
      - ""
      - string
      - rstring
      - binary
    default: ""
  tcp_negate:
    description:
      - Negate the TCP healthcheck match.
    type: bool
    default: false
  tcp_match_value:
    description:
      - The expected value for TCP healthcheck matching.
    type: str
    default: ""
  agent_port:
    description:
      - The port for agent healthchecks.
    type: str
    default: ""
  mysql_user:
    description:
      - The MySQL user for MySQL healthchecks.
    type: str
    default: ""
  mysql_post41:
    description:
      - Use MySQL protocol version 4.1+.
    type: bool
    default: false
  pgsql_user:
    description:
      - The PostgreSQL user for PostgreSQL healthchecks.
    type: str
    default: ""
  smtp_domain:
    description:
      - The domain for SMTP healthchecks.
    type: str
    default: ""
  esmtp_domain:
    description:
      - The domain for ESMTP healthchecks.
    type: str
    default: ""
  db_user:
    description:
      - The user for generic database healthchecks.
    type: str
    default: ""
  state:
    description:
      - Whether the healthcheck should exist or not.
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
- name: Create an HTTP healthcheck
  opnsense_haproxy_healthcheck:
    name: http_check
    type: http
    description: "HTTP health check"
    interval: "5s"
    http_method: GET
    http_uri: /health
    http_version: http11
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a healthcheck
  opnsense_haproxy_healthcheck:
    name: http_check
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


class HealthcheckModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy healthchecks."""

    OBJECT_TYPE = "healthcheck"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "type": dict(
            type="str",
            choices=["tcp", "http", "agent", "ldap", "mysql", "pgsql", "redis", "smtp", "esmtp", "ssl"],
            default="http",
        ),
        "description": dict(type="str", default=""),
        "interval": dict(type="str", default="2s"),
        "force_ssl": dict(type="bool", default=False),
        "checkport": dict(type="str", default=""),
        "http_method": dict(type="str", default="options"),
        "http_uri": dict(type="str", default="/"),
        "http_version": dict(type="str", choices=["http10", "http11"], default="http10"),
        "http_host": dict(type="str", default="localhost"),
        "http_expression_enabled": dict(type="bool", default=False),
        "http_expression": dict(
            type="str", choices=["", "status", "rstatus", "string", "rstring"], default=""
        ),
        "http_negate": dict(type="bool", default=False),
        "http_value": dict(type="str", default=""),
        "tcp_enabled": dict(type="bool", default=False),
        "tcp_send_value": dict(type="str", default=""),
        "tcp_match_type": dict(
            type="str", choices=["", "string", "rstring", "binary"], default=""
        ),
        "tcp_negate": dict(type="bool", default=False),
        "tcp_match_value": dict(type="str", default=""),
        "agent_port": dict(type="str", default=""),
        "mysql_user": dict(type="str", default=""),
        "mysql_post41": dict(type="bool", default=False),
        "pgsql_user": dict(type="str", default=""),
        "smtp_domain": dict(type="str", default=""),
        "esmtp_domain": dict(type="str", default=""),
        "db_user": dict(type="str", default=""),
    }

    def _build_desired_state(self):
        params = self.module.params
        return {
            "description": params["description"],
            "type": params["type"],
            "interval": params["interval"],
            "force_ssl": str(int(params["force_ssl"])),
            "checkport": params["checkport"],
            "http_method": params["http_method"],
            "http_uri": params["http_uri"],
            "http_version": params["http_version"],
            "http_host": params["http_host"],
            "http_expressionEnabled": str(int(params["http_expression_enabled"])),
            "http_expression": params["http_expression"],
            "http_negate": str(int(params["http_negate"])),
            "http_value": params["http_value"],
            "tcp_enabled": str(int(params["tcp_enabled"])),
            "tcp_sendValue": params["tcp_send_value"],
            "tcp_matchType": params["tcp_match_type"],
            "tcp_negate": str(int(params["tcp_negate"])),
            "tcp_matchValue": params["tcp_match_value"],
            "agent_port": params["agent_port"],
            "mysql_user": params["mysql_user"],
            "mysql_post41": str(int(params["mysql_post41"])),
            "pgsql_user": params["pgsql_user"],
            "smtp_domain": params["smtp_domain"],
            "esmtp_domain": params["esmtp_domain"],
            "agentPort": params["agent_port"],
            "smtpDomain": params["smtp_domain"],
        }

    def _diff_state(self, current, desired):
        """Custom diff for healthcheck — selection fields need getSelected()."""
        changes = {}
        messages = []
        needs_change = False

        selection_fields = ["type", "http_method", "http_version", "http_expression", "tcp_matchType"]

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            if prop in selection_fields:
                selected = self.api.getSelected(current_value)
                if selected != desired_value:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, desired_value))
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = HealthcheckModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
