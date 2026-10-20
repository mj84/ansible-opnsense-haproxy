#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy frontends on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_frontend
short_description: Manage HAProxy frontends on OPNsense
description:
  - Creates, updates, or deletes HAProxy frontends via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the frontend (must be unique).
    type: str
    required: true
  enabled:
    description:
      - Whether the frontend is enabled.
    type: bool
    default: true
  description:
    description:
      - A description for the frontend.
    type: str
    default: ""
  bind:
    description:
      - List of bind addresses/ports (e.g. ``["*:443", "0.0.0.0:80"]``).
    type: list
    elements: str
    required: true
  bind_options:
    description:
      - Additional bind options string.
    type: str
    default: ""
  mode:
    description:
      - The frontend mode.
    type: str
    choices: [http, ssl, tcp]
    default: http
  default_backend:
    description:
      - Default backend name. Use ``none`` for no backend.
    type: str
    default: "none"
  ssl_enabled:
    description:
      - Enable SSL for this frontend.
    type: bool
    default: false
  ssl_certificates:
    description:
      - List of SSL certificate names.
    type: list
    elements: str
    default: []
  ssl_default_certificate:
    description:
      - Default SSL certificate name.
    type: str
    default: ""
  ssl_custom_options:
    description:
      - Custom SSL options string.
    type: str
    default: ""
  ssl_advanced_enabled:
    description:
      - Enable advanced SSL options.
    type: bool
    default: false
  ssl_bind_options:
    description:
      - List of SSL bind options.
    type: list
    elements: str
    default: []
    choices:
      - no-sslv3
      - no-tlsv10
      - no-tlsv11
      - no-tlsv12
      - no-tls-tickets
      - force-sslv3
      - force-tlsv10
      - force-tlsv11
      - force-tlsv12
      - strict-sni
  ssl_cipher_list:
    description:
      - SSL cipher list.
    type: str
    default: >-
      ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:
      ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:
      ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
      ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:
      ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256
  ssl_http2_enabled:
    description:
      - Enable HTTP/2.
    type: bool
    default: false
  ssl_hsts_enabled:
    description:
      - Enable HSTS.
    type: bool
    default: true
  ssl_hsts_include_sub_domains:
    description:
      - Include subdomains in HSTS.
    type: bool
    default: false
  ssl_hsts_preload:
    description:
      - Preload HSTS.
    type: bool
    default: false
  ssl_hsts_max_age:
    description:
      - HSTS max age in seconds.
    type: str
    default: "15768000"
  ssl_client_auth_enabled:
    description:
      - Enable SSL client authentication.
    type: bool
    default: false
  ssl_client_auth_verify:
    description:
      - Client certificate verification mode.
    type: str
    choices: [none, optional, required]
    default: none
  ssl_client_auth_cas:
    description:
      - List of SSL CA names for client auth.
    type: list
    elements: str
    default: []
  ssl_client_auth_crls:
    description:
      - List of SSL CRL names for client auth.
    type: list
    elements: str
    default: []
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
  tuning_max_connections:
    description:
      - Maximum connections.
    type: str
    default: ""
  tuning_timeout_client:
    description:
      - Client timeout.
    type: str
    default: ""
  tuning_timeout_http_req:
    description:
      - HTTP request timeout.
    type: str
    default: ""
  tuning_timeout_http_keep_alive:
    description:
      - HTTP keep-alive timeout.
    type: str
    default: ""
  linked_cpu_affinity_rules:
    description:
      - List of CPU affinity rule names.
    type: list
    elements: str
    default: []
  logging_dont_log_null:
    description:
      - Don't log null connections.
    type: bool
    default: false
  logging_dont_log_normal:
    description:
      - Don't log normal connections.
    type: bool
    default: false
  logging_log_separate_errors:
    description:
      - Log separate errors.
    type: bool
    default: false
  logging_detailed_log:
    description:
      - Enable detailed logging.
    type: bool
    default: false
  logging_socket_stats:
    description:
      - Enable socket statistics logging.
    type: bool
    default: false
  stickiness_pattern:
    description:
      - Stickiness pattern.
    type: str
    choices: [ipv4, ipv6, integer, string, binary]
    default: ipv4
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
  stickiness_counter:
    description:
      - Enable stickiness counter.
    type: bool
    default: true
  stickiness_counter_key:
    description:
      - Stickiness counter key.
    type: str
    default: src
  stickiness_length:
    description:
      - Stickiness length.
    type: str
    default: ""
  stickiness_conn_rate_period:
    description:
      - Connection rate period.
    type: str
    default: "10s"
  stickiness_sess_rate_period:
    description:
      - Session rate period.
    type: str
    default: "10s"
  stickiness_http_req_rate_period:
    description:
      - HTTP request rate period.
    type: str
    default: "10s"
  stickiness_http_err_rate_period:
    description:
      - HTTP error rate period.
    type: str
    default: "10s"
  stickiness_bytes_in_rate_period:
    description:
      - Bytes in rate period.
    type: str
    default: "1m"
  stickiness_bytes_out_rate_period:
    description:
      - Bytes out rate period.
    type: str
    default: "1m"
  forward_for:
    description:
      - Enable X-Forwarded-For.
    type: bool
    default: false
  connection_behaviour:
    description:
      - Connection behaviour.
    type: str
    choices:
      - http-keep-alive
      - http-tunnel
      - httpclose
      - http-server-close
      - forceclose
    default: http-keep-alive
  custom_options:
    description:
      - Custom HAProxy options string.
    type: str
    default: ""
  linked_actions:
    description:
      - List of action names linked to this frontend (order-sensitive).
    type: list
    elements: str
    default: []
  linked_errorfiles:
    description:
      - List of errorfile names linked to this frontend.
    type: list
    elements: str
    default: []
  state:
    description:
      - Whether the frontend should exist or not.
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
  - module: opnsense_haproxy_action
  - module: opnsense_haproxy_acl
"""

EXAMPLES = r"""
- name: Create an HTTP frontend
  opnsense_haproxy_frontend:
    name: web_http
    bind: ["*:80"]
    mode: http
    default_backend: web_pool
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create an HTTPS frontend
  opnsense_haproxy_frontend:
    name: web_https
    bind: ["*:443"]
    mode: http
    default_backend: web_pool
    ssl_enabled: true
    ssl_certificates: [my_cert]
    ssl_default_certificate: my_cert
    ssl_hsts_enabled: true
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete a frontend
  opnsense_haproxy_frontend:
    name: web_https
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


class FrontendModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy frontends."""

    OBJECT_TYPE = "frontend"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "enabled": dict(type="bool", default=True),
        "description": dict(type="str", default=""),
        "bind": dict(type="list", elements="str", required=True),
        "bind_options": dict(type="str", default=""),
        "mode": dict(type="str", choices=["http", "ssl", "tcp"], default="http"),
        "default_backend": dict(type="str", default="none"),
        "ssl_enabled": dict(type="bool", default=False),
        "ssl_certificates": dict(type="list", elements="str", default=[]),
        "ssl_default_certificate": dict(type="str", default=""),
        "ssl_custom_options": dict(type="str", default=""),
        "ssl_advanced_enabled": dict(type="bool", default=False),
        "ssl_bind_options": dict(
            type="list",
            elements="str",
            choices=[
                "no-sslv3", "no-tlsv10", "no-tlsv11", "no-tlsv12", "no-tls-tickets",
                "force-sslv3", "force-tlsv10", "force-tlsv11", "force-tlsv12", "strict-sni",
            ],
            default=[],
        ),
        "ssl_cipher_list": dict(
            type="str",
            default="ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:"
                    "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:"
                    "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
                    "ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:"
                    "ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256",
        ),
        "ssl_http2_enabled": dict(type="bool", default=False),
        "ssl_hsts_enabled": dict(type="bool", default=True),
        "ssl_hsts_include_sub_domains": dict(type="bool", default=False),
        "ssl_hsts_preload": dict(type="bool", default=False),
        "ssl_hsts_max_age": dict(type="str", default="15768000"),
        "ssl_client_auth_enabled": dict(type="bool", default=False),
        "ssl_client_auth_verify": dict(
            type="str", choices=["none", "optional", "required"], default="none"
        ),
        "ssl_client_auth_cas": dict(type="list", elements="str", default=[]),
        "ssl_client_auth_crls": dict(type="list", elements="str", default=[]),
        "basic_auth_enabled": dict(type="bool", default=False),
        "basic_auth_users": dict(type="list", elements="str", default=[]),
        "basic_auth_groups": dict(type="list", elements="str", default=[]),
        "tuning_max_connections": dict(type="str", default=""),
        "tuning_timeout_client": dict(type="str", default=""),
        "tuning_timeout_http_req": dict(type="str", default=""),
        "tuning_timeout_http_keep_alive": dict(type="str", default=""),
        "linked_cpu_affinity_rules": dict(type="list", elements="str", default=[]),
        "logging_dont_log_null": dict(type="bool", default=False),
        "logging_dont_log_normal": dict(type="bool", default=False),
        "logging_log_separate_errors": dict(type="bool", default=False),
        "logging_detailed_log": dict(type="bool", default=False),
        "logging_socket_stats": dict(type="bool", default=False),
        "stickiness_pattern": dict(
            type="str", choices=["ipv4", "ipv6", "integer", "string", "binary"], default="ipv4"
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
        "stickiness_counter": dict(type="bool", default=True),
        "stickiness_counter_key": dict(type="str", default="src"),
        "stickiness_length": dict(type="str", default=""),
        "stickiness_conn_rate_period": dict(type="str", default="10s"),
        "stickiness_sess_rate_period": dict(type="str", default="10s"),
        "stickiness_http_req_rate_period": dict(type="str", default="10s"),
        "stickiness_http_err_rate_period": dict(type="str", default="10s"),
        "stickiness_bytes_in_rate_period": dict(type="str", default="1m"),
        "stickiness_bytes_out_rate_period": dict(type="str", default="1m"),
        "forward_for": dict(type="bool", default=False),
        "connection_behaviour": dict(
            type="str",
            choices=["http-keep-alive", "http-tunnel", "httpclose", "http-server-close", "forceclose"],
            default="http-keep-alive",
        ),
        "custom_options": dict(type="str", default=""),
        "linked_actions": dict(type="list", elements="str", default=[]),
        "linked_errorfiles": dict(type="list", elements="str", default=[]),
    }

    def _build_desired_state(self):
        params = self.module.params
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")

        # Resolve reference UUIDs
        default_backend_uuid = ""
        if params["default_backend"] != "none":
            default_backend_uuid = self._resolve_name_to_uuid(template, params["default_backend"], "defaultBackend")

        basic_auth_users_uuids = self._resolve_names_to_uuids(template, params["basic_auth_users"], "basicAuthUsers")
        basic_auth_groups_uuids = self._resolve_names_to_uuids(template, params["basic_auth_groups"], "basicAuthGroups")
        cpu_affinity_uuids = self._resolve_names_to_uuids(template, params["linked_cpu_affinity_rules"], "linkedCpuAffinityRules")
        linked_actions_uuids = self._resolve_names_to_uuids(template, params["linked_actions"], "linkedActions")
        linked_errorfiles_uuids = self._resolve_names_to_uuids(template, params["linked_errorfiles"], "linkedErrorfiles")

        # Resolve SSL references
        ssl_cert_uuids = self.api.getSslObjectKeys(template["ssl_certificates"], params["ssl_certificates"])
        ssl_default_cert_uuid = ""
        if params["ssl_default_certificate"]:
            ssl_default_cert_uuid = self.api.getSslObjectKeys(template["ssl_default_certificate"], [params["ssl_default_certificate"]])[0]
        ssl_cas_uuids = self.api.getSslObjectKeys(template["ssl_clientAuthCAs"], params["ssl_client_auth_cas"])
        ssl_crls_uuids = self.api.getSslObjectKeys(template["ssl_clientAuthCRLs"], params["ssl_client_auth_crls"])

        return {
            "enabled": str(int(params["enabled"])),
            "description": params["description"],
            "bind": ",".join(params["bind"]),
            "bindOptions": params["bind_options"],
            "mode": params["mode"],
            "defaultBackend": default_backend_uuid,
            "ssl_enabled": str(int(params["ssl_enabled"])),
            "ssl_certificates": ",".join(ssl_cert_uuids),
            "ssl_default_certificate": ssl_default_cert_uuid,
            "ssl_customOptions": params["ssl_custom_options"],
            "ssl_advancedEnabled": str(int(params["ssl_advanced_enabled"])),
            "ssl_bindOptions": ",".join(params["ssl_bind_options"]),
            "ssl_cipherList": params["ssl_cipher_list"],
            "ssl_http2Enabled": str(int(params["ssl_http2_enabled"])),
            "ssl_hstsEnabled": str(int(params["ssl_hsts_enabled"])),
            "ssl_hstsIncludeSubDomains": str(int(params["ssl_hsts_include_sub_domains"])),
            "ssl_hstsPreload": str(int(params["ssl_hsts_preload"])),
            "ssl_hstsMaxAge": params["ssl_hsts_max_age"],
            "ssl_clientAuthEnabled": str(int(params["ssl_client_auth_enabled"])),
            "ssl_clientAuthVerify": params["ssl_client_auth_verify"],
            "ssl_clientAuthCAs": ",".join(ssl_cas_uuids),
            "ssl_clientAuthCRLs": ",".join(ssl_crls_uuids),
            "basicAuthEnabled": str(int(params["basic_auth_enabled"])),
            "basicAuthUsers": ",".join(basic_auth_users_uuids),
            "basicAuthGroups": ",".join(basic_auth_groups_uuids),
            "tuning_maxConnections": params["tuning_max_connections"],
            "tuning_timeoutClient": params["tuning_timeout_client"],
            "tuning_timeoutHttpReq": params["tuning_timeout_http_req"],
            "tuning_timeoutHttpKeepAlive": params["tuning_timeout_http_keep_alive"],
            "linkedCpuAffinityRules": ",".join(cpu_affinity_uuids),
            "logging_dontLogNull": str(int(params["logging_dont_log_null"])),
            "logging_dontLogNormal": str(int(params["logging_dont_log_normal"])),
            "logging_logSeparateErrors": str(int(params["logging_log_separate_errors"])),
            "logging_detailedLog": str(int(params["logging_detailed_log"])),
            "logging_socketStats": str(int(params["logging_socket_stats"])),
            "stickiness_pattern": params["stickiness_pattern"],
            "stickiness_dataTypes": ",".join(params["stickiness_data_types"]),
            "stickiness_expire": params["stickiness_expire"],
            "stickiness_size": params["stickiness_size"],
            "stickiness_counter": str(int(params["stickiness_counter"])),
            "stickiness_counter_key": params["stickiness_counter_key"],
            "stickiness_length": params["stickiness_length"],
            "stickiness_connRatePeriod": params["stickiness_conn_rate_period"],
            "stickiness_sessRatePeriod": params["stickiness_sess_rate_period"],
            "stickiness_httpReqRatePeriod": params["stickiness_http_req_rate_period"],
            "stickiness_httpErrRatePeriod": params["stickiness_http_err_rate_period"],
            "stickiness_bytesInRatePeriod": params["stickiness_bytes_in_rate_period"],
            "stickiness_bytesOutRatePeriod": params["stickiness_bytes_out_rate_period"],
            "forwardFor": str(int(params["forward_for"])),
            "connectionBehaviour": params["connection_behaviour"],
            "customOptions": params["custom_options"],
            "linkedActions": ",".join(linked_actions_uuids),
            "linkedErrorfiles": ",".join(linked_errorfiles_uuids),
        }

    def _diff_state(self, current, desired):
        """Custom diff for frontend — handles many selection fields and conditional SSL checks."""
        changes = {}
        messages = []
        needs_change = False
        params = self.module.params
        ssl_enabled = params["ssl_enabled"]
        ssl_advanced = params["ssl_advanced_enabled"]

        selection_fields = ["mode", "stickiness_pattern", "connection_behaviour"]
        reference_fields = {
            "defaultBackend": ("default_backend", "defaultBackend"),
            "linkedCpuAffinityRules": ("linked_cpu_affinity_rules", "linkedCpuAffinityRules"),
            "linkedActions": ("linked_actions", "linkedActions"),
            "linkedErrorfiles": ("linked_errorfiles", "linkedErrorfiles"),
        }
        list_fields = ["bind", "ssl_certificates", "ssl_bind_options",
                       "stickiness_data_types", "basic_auth_users", "basic_auth_groups"]

        for prop, desired_value in desired.items():
            current_value = current.get(prop)

            if prop == "name":
                continue

            # Skip SSL properties if SSL is not enabled
            if prop.startswith("ssl") and not ssl_enabled:
                if prop == "ssl_enabled":
                    pass  # Still check ssl_enabled itself
                else:
                    continue

            # Skip advanced SSL properties if not enabled
            if ssl_advanced is False and prop in ("ssl_bindOptions", "ssl_cipherList",
                                                   "ssl_http2Enabled", "ssl_hstsEnabled",
                                                   "ssl_hstsIncludeSubdomains", "ssl_hstsPreload",
                                                   "ssl_hstsMaxAge"):
                continue

            # Client auth properties only matter when client auth is enabled
            if prop in ("ssl_clientAuthVerify", "ssl_clientAuthCAs", "ssl_clientAuthCRLs"):
                if not params["ssl_client_auth_enabled"]:
                    continue

            # Basic auth properties only matter when basic auth is enabled
            if prop in ("basicAuthUsers", "basicAuthGroups"):
                if not params["basic_auth_enabled"]:
                    continue

            # Selection fields
            if prop in selection_fields:
                selected = self.api.getSelected(current_value)
                if selected != desired_value:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, desired_value))
            # List fields (bind, stickiness_data_types, etc.)
            elif prop in list_fields:
                if prop == "bind":
                    if not self.api.compareLists(params["bind"], current_value):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s" % prop)
                elif prop == "stickiness_data_types":
                    current_list = self.api.getSelected(current_value)
                    if not self.api.compareLists(current_list, params["stickiness_data_types"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params["stickiness_data_types"]))
                elif prop == "ssl_certificates" and ssl_enabled:
                    current_list = self.api.getSelectedList(current_value, retval="key")
                    if not self.api.compareLists(current_list, params["ssl_certificates"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s" % prop)
                elif prop == "ssl_bind_options" and ssl_enabled:
                    current_list = self.api.getSelectedList(current_value)
                    if not self.api.compareLists(current_list, params["ssl_bind_options"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params["ssl_bind_options"]))
                elif prop == "basic_auth_users" and params["basic_auth_enabled"]:
                    current_list = self.api.getSelectedList(current_value)
                    if not self.api.compareLists(current_list, params["basic_auth_users"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params["basic_auth_users"]))
                elif prop == "basic_auth_groups" and params["basic_auth_enabled"]:
                    current_list = self.api.getSelectedList(current_value)
                    if not self.api.compareLists(current_list, params["basic_auth_groups"]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params["basic_auth_groups"]))
                else:
                    if current_value != desired_value:
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))
            # Reference fields
            elif prop in reference_fields:
                param_name, _ = reference_fields[prop]
                if prop == "defaultBackend":
                    current_ref = self.api.getSelected(current_value, retval="value")
                    if current_ref != params[param_name]:
                        if current_ref == "" and params[param_name] == "none":
                            pass
                        else:
                            needs_change = True
                            changes[prop] = desired_value
                            messages.append("Changing %s: %s => %s" % (prop, current_ref, params[param_name]))
                elif prop == "linkedActions":
                    current_list = self.api.getSelectedList(current_value, retval="key")
                    if not self.api.compareLists(current_list, params[param_name], order_sensitive=True):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params[param_name]))
                else:
                    current_list = self.api.getSelectedList(current_value, retval="key")
                    if not self.api.compareLists(current_list, params[param_name]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params[param_name]))
            # Simple fields
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = FrontendModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
