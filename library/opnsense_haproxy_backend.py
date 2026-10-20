#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy backend pools on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_backend
short_description: Manage HAProxy backend pools on OPNsense
description:
  - Creates, updates, or deletes HAProxy backend pools via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the backend (must be unique).
    type: str
    required: true
  enabled:
    description:
      - Whether the backend is enabled.
    type: bool
    default: true
  description:
    description:
      - A description for the backend.
    type: str
    default: ""
  mode:
    description:
      - The backend mode.
    type: str
    choices: [http, tcp]
    default: http
  algorithm:
    description:
      - The load balancing algorithm.
    type: str
    choices: [source, roundrobin, static-rr, leastconn, uri]
    default: source
  proxy_protocol:
    description:
      - Proxy protocol version.
    type: str
    choices: ["", "v1", "v2"]
    default: ""
  linked_servers:
    description:
      - List of server names to include in this backend.
    type: list
    elements: str
    default: []
  source:
    description:
      - Source address for the backend.
    type: str
    default: ""
  health_check_enabled:
    description:
      - Enable health checking.
    type: bool
    default: true
  health_check:
    description:
      - Healthcheck name to use.
    type: str
    default: ""
  health_check_log_status:
    description:
      - Log health check status.
    type: bool
    default: false
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
  health_check_fall:
    description:
      - Number of consecutive failures before marking server as down.
    type: str
    default: ""
  health_check_rise:
    description:
      - Number of consecutive successes before marking server as up.
    type: str
    default: ""
  persistence:
    description:
      - Session persistence type.
    type: str
    choices: ["", "sticktable", "cookie"]
    default: sticktable
  persistence_cookie_mode:
    description:
      - Cookie persistence mode.
    type: str
    choices: [piggyback, new]
    default: piggyback
  persistence_cookie_name:
    description:
      - Cookie name for persistence.
    type: str
    default: SRVCOOKIE
  persistence_strip_quotes:
    description:
      - Strip quotes from cookie values.
    type: bool
    default: true
  stickiness_pattern:
    description:
      - Stickiness pattern.
    type: str
    choices: ["", "sourceipv4", "sourceipv6", "cookievalue", "rdpcookie"]
    default: sourceipv4
  stickiness_data_types:
    description:
      - List of stickiness data types.
    type: list
    elements: str
    default: []
    choices:
      - conn_cnt
      - conn_cur
      - conn_rate
      - sess_cnt
      - sess_rate
      - http_req_cnt
      - http_req_rate
      - http_err_cnt
      - http_err_rate
      - bytes_in_cnt
      - bytes_in_rate
      - bytes_out_cnt
      - bytes_out_rate
  stickiness_expire:
    description:
      - Stickiness expire time.
    type: str
    default: "30m"
  stickiness_size:
    description:
      - Stickiness size limit.
    type: str
    default: "50k"
  stickiness_cookie_name:
    description:
      - Cookie name for stickiness.
    type: str
    default: ""
  stickiness_cookie_length:
    description:
      - Cookie length for stickiness.
    type: str
    default: ""
  stickiness_conn_rate_period:
    description:
      - Connection rate period for stickiness.
    type: str
    default: "10s"
  stickiness_sess_rate_period:
    description:
      - Session rate period for stickiness.
    type: str
    default: "10s"
  stickiness_http_req_rate_period:
    description:
      - HTTP request rate period for stickiness.
    type: str
    default: "10s"
  stickiness_http_err_rate_period:
    description:
      - HTTP error rate period for stickiness.
    type: str
    default: "10s"
  stickiness_bytes_in_rate_period:
    description:
      - Bytes in rate period for stickiness.
    type: str
    default: "1m"
  stickiness_bytes_out_rate_period:
    description:
      - Bytes out rate period for stickiness.
    type: str
    default: "1m"
  basic_auth_enabled:
    description:
      - Enable basic authentication.
    type: bool
    default: false
  basic_auth_users:
    description:
      - List of users allowed by basic auth.
    type: list
    elements: str
    default: []
  basic_auth_groups:
    description:
      - List of groups allowed by basic auth.
    type: list
    elements: str
    default: []
  tuning_timeout_connect:
    description:
      - Connect timeout.
    type: str
    default: ""
  tuning_timeout_check:
    description:
      - Check timeout.
    type: str
    default: ""
  tuning_timeout_server:
    description:
      - Server timeout.
    type: str
    default: ""
  tuning_retries:
    description:
      - Number of retries.
    type: str
    default: ""
  custom_options:
    description:
      - Custom HAProxy options string.
    type: str
    default: ""
  tuning_default_server:
    description:
      - Default server for fallback.
    type: str
    default: ""
  tuning_no_port:
    description:
      - Disable port in default server.
    type: bool
    default: false
  tuning_http_reuse:
    description:
      - HTTP connection reuse policy.
    type: str
    choices: ["", "never", "safe", "aggressive", "always"]
    default: never
  linked_actions:
    description:
      - List of action names linked to this backend (order-sensitive).
    type: list
    elements: str
    default: []
  linked_errorfiles:
    description:
      - List of errorfile names linked to this backend.
    type: list
    elements: str
    default: []
  state:
    description:
      - Whether the backend should exist or not.
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
  - module: opnsense_haproxy_server
  - module: opnsense_haproxy_healthcheck
  - module: opnsense_haproxy_action
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create a backend
  opnsense_haproxy_backend:
    name: api_pool
    mode: http
    algorithm: roundrobin
    linked_servers: [web1, web2, web3]
    health_check: http_check
    persistence: sticktable
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create a backend with basic auth
  opnsense_haproxy_backend:
    name: protected_pool
    mode: http
    basic_auth_enabled: true
    basic_auth_users: [admin]
    basic_auth_groups: [admins]
    linked_servers: [web1]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a backend
  opnsense_haproxy_backend:
    name: api_pool
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


class BackendModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy backend pools."""

    OBJECT_TYPE = "backend"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "enabled": dict(type="bool", default=True),
        "description": dict(type="str", default=""),
        "mode": dict(type="str", choices=["http", "tcp"], default="http"),
        "algorithm": dict(
            type="str",
            choices=["source", "roundrobin", "static-rr", "leastconn", "uri"],
            default="source",
        ),
        "proxy_protocol": dict(type="str", choices=["", "v1", "v2"], default=""),
        "linked_servers": dict(type="list", elements="str", default=[]),
        "source": dict(type="str", default=""),
        "health_check_enabled": dict(type="bool", default=True),
        "health_check": dict(type="str", default=""),
        "health_check_log_status": dict(type="bool", default=False),
        "check_interval": dict(type="str", default=""),
        "check_down_interval": dict(type="str", default=""),
        "health_check_fall": dict(type="str", default=""),
        "health_check_rise": dict(type="str", default=""),
        "persistence": dict(type="str", choices=["", "sticktable", "cookie"], default="sticktable"),
        "persistence_cookie_mode": dict(type="str", choices=["piggyback", "new"], default="piggyback"),
        "persistence_cookie_name": dict(type="str", default="SRVCOOKIE"),
        "persistence_strip_quotes": dict(type="bool", default=True),
        "stickiness_pattern": dict(
            type="str",
            choices=["", "sourceipv4", "sourceipv6", "cookievalue", "rdpcookie"],
            default="sourceipv4",
        ),
        "stickiness_data_types": dict(
            type="list",
            elements="str",
            choices=[
                "conn_cnt", "conn_cur", "conn_rate", "sess_cnt", "sess_rate",
                "http_req_cnt", "http_req_rate", "http_err_cnt", "http_err_rate",
                "bytes_in_cnt", "bytes_in_rate", "bytes_out_cnt", "bytes_out_rate",
            ],
            default=[],
        ),
        "stickiness_expire": dict(type="str", default="30m"),
        "stickiness_size": dict(type="str", default="50k"),
        "stickiness_cookie_name": dict(type="str", default=""),
        "stickiness_cookie_length": dict(type="str", default=""),
        "stickiness_conn_rate_period": dict(type="str", default="10s"),
        "stickiness_sess_rate_period": dict(type="str", default="10s"),
        "stickiness_http_req_rate_period": dict(type="str", default="10s"),
        "stickiness_http_err_rate_period": dict(type="str", default="10s"),
        "stickiness_bytes_in_rate_period": dict(type="str", default="1m"),
        "stickiness_bytes_out_rate_period": dict(type="str", default="1m"),
        "basic_auth_enabled": dict(type="bool", default=False),
        "basic_auth_users": dict(type="list", elements="str", default=[]),
        "basic_auth_groups": dict(type="list", elements="str", default=[]),
        "tuning_timeout_connect": dict(type="str", default=""),
        "tuning_timeout_check": dict(type="str", default=""),
        "tuning_timeout_server": dict(type="str", default=""),
        "tuning_retries": dict(type="str", default=""),
        "custom_options": dict(type="str", default=""),
        "tuning_default_server": dict(type="str", default=""),
        "tuning_no_port": dict(type="bool", default=False),
        "tuning_http_reuse": dict(
            type="str", choices=["", "never", "safe", "aggressive", "always"], default="never"
        ),
        "linked_actions": dict(type="list", elements="str", default=[]),
        "linked_errorfiles": dict(type="list", elements="str", default=[]),
    }

    def _build_desired_state(self):
        params = self.module.params
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")

        # Resolve reference UUIDs
        linked_servers_uuids = self._resolve_names_to_uuids(template, params["linked_servers"], "linkedServers")
        health_check_uuid = self._resolve_name_to_uuid(template, params["health_check"], "healthCheck")
        basic_auth_users_uuids = self._resolve_names_to_uuids(template, params["basic_auth_users"], "basicAuthUsers")
        basic_auth_groups_uuids = self._resolve_names_to_uuids(template, params["basic_auth_groups"], "basicAuthGroups")
        linked_actions_uuids = self._resolve_names_to_uuids(template, params["linked_actions"], "linkedActions")
        linked_errorfiles_uuids = self._resolve_names_to_uuids(
            template, params["linked_errorfiles"], "linkedErrorfiles")

        return {
            "enabled": str(int(params["enabled"])),
            "description": params["description"],
            "mode": params["mode"],
            "algorithm": params["algorithm"],
            "proxyProtocol": params["proxy_protocol"],
            "linkedServers": ",".join(linked_servers_uuids),
            "source": params["source"],
            "healthCheckEnabled": str(int(params["health_check_enabled"])),
            "healthCheck": health_check_uuid,
            "healthCheckLogStatus": str(int(params["health_check_log_status"])),
            "checkInterval": params["check_interval"],
            "checkDownInterval": params["check_down_interval"],
            "healthCheckFall": params["health_check_fall"],
            "healthCheckRise": params["health_check_rise"],
            "persistence": params["persistence"],
            "persistence_cookiemode": params["persistence_cookie_mode"],
            "persistence_cookiename": params["persistence_cookie_name"],
            "persistence_stripquotes": str(int(params["persistence_strip_quotes"])),
            "stickiness_pattern": params["stickiness_pattern"],
            "stickiness_dataTypes": ",".join(params["stickiness_data_types"]),
            "stickiness_expire": params["stickiness_expire"],
            "stickiness_size": params["stickiness_size"],
            "stickiness_cookiename": params["stickiness_cookie_name"],
            "stickiness_cookielength": params["stickiness_cookie_length"],
            "stickiness_connRatePeriod": params["stickiness_conn_rate_period"],
            "stickiness_sessRatePeriod": params["stickiness_sess_rate_period"],
            "stickiness_httpReqRatePeriod": params["stickiness_http_req_rate_period"],
            "stickiness_httpErrRatePeriod": params["stickiness_http_err_rate_period"],
            "stickiness_bytesInRatePeriod": params["stickiness_bytes_in_rate_period"],
            "stickiness_bytesOutRatePeriod": params["stickiness_bytes_out_rate_period"],
            "basicAuthEnabled": str(int(params["basic_auth_enabled"])),
            "basicAuthUsers": ",".join(basic_auth_users_uuids),
            "basicAuthGroups": ",".join(basic_auth_groups_uuids),
            "tuning_timeoutConnect": params["tuning_timeout_connect"],
            "tuning_timeoutCheck": params["tuning_timeout_check"],
            "tuning_timeoutServer": params["tuning_timeout_server"],
            "tuning_retries": params["tuning_retries"],
            "customOptions": params["custom_options"],
            "tuning_defaultserver": params["tuning_default_server"],
            "tuning_noport": str(int(params["tuning_no_port"])),
            "tuning_httpreuse": params["tuning_http_reuse"],
            "linkedActions": ",".join(linked_actions_uuids),
            "linkedErrorfiles": ",".join(linked_errorfiles_uuids),
        }

    def _diff_state(self, current, desired):
        """Custom diff for backend — handles selection fields and reference list comparisons."""
        changes = {}
        messages = []
        needs_change = False

        # API key names — the desired state is keyed the way the API expects it
        selection_fields = ["mode", "algorithm", "proxyProtocol", "persistence",
                            "persistence_cookiemode", "stickiness_pattern",
                            "tuning_httpreuse"]
        reference_fields = ["linkedServers", "healthCheck", "basicAuthUsers",
                            "basicAuthGroups", "linkedActions", "linkedErrorfiles"]

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            # Selection fields
            if prop in selection_fields:
                selected = self.api.getSelected(current_value)
                if selected != desired_value:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, desired_value))
            # Reference fields — the desired value already holds the resolved
            # UUIDs, the current one arrives as a selection dict.
            elif prop in reference_fields:
                current_keys = self._reference_keys(current_value)
                desired_keys = self._reference_keys(desired_value)
                if not self.api.compareLists(
                    current_keys, desired_keys, order_sensitive=prop == "linkedActions"
                ):
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, current_keys, desired_keys))
            # Simple fields
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = BackendModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
