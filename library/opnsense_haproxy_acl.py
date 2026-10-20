#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
"""Manage HAProxy ACLs (Conditions) on OPNsense."""

from __future__ import absolute_import, division, print_function

DOCUMENTATION = r"""
---
module: opnsense_haproxy_acl
short_description: Manage HAProxy ACLs on OPNsense
description:
  - Creates, updates, or deletes HAProxy ACLs (conditions) via the OPNsense API.
author:
  - Markus Joosten (@mj84)
options:
  name:
    description:
      - The name of the ACL (must be unique).
    type: str
    required: true
  description:
    description:
      - A description for the ACL.
    type: str
    default: ""
  expression:
    description:
      - The ACL expression type.
    type: str
    required: true
    choices:
      - http_auth
      - hdr_beg
      - hdr_end
      - hdr
      - hdr_reg
      - hdr_sub
      - path_beg
      - path_end
      - path
      - path_reg
      - path_dir
      - path_sub
      - url_param
      - ssl_c_verify
      - ssl_c_verify_code
      - ssl_c_ca_commonname
      - src
      - src_is_local
      - src_port
      - src_bytes_in_rate
      - src_bytes_out_rate
      - src_kbytes_in
      - src_kbytes_out
      - src_conn_cnt
      - src_conn_cur
      - src_conn_rate
      - src_http_err_cnt
      - src_http_err_rate
      - src_http_req_cnt
      - src_http_req_rate
      - src_sess_rate
      - nbsrv
      - traffic_is_http
      - traffic_is_ssl
      - ssl_fc
      - ssl_fc_sni
      - ssl_sni
      - ssl_sni_sub
      - ssl_sni_beg
      - ssl_sni_end
      - ssl_sni_reg
      - custom_acl
  negate:
    description:
      - Negate the ACL expression.
    type: bool
    default: false
  hdr_beg:
    description:
      - Header begin value (used with hdr_beg expression).
    type: str
    default: ""
  hdr_end:
    description:
      - Header end value (used with hdr_end expression).
    type: str
    default: ""
  hdr:
    description:
      - Header name (used with hdr expression).
    type: str
    default: ""
  hdr_reg:
    description:
      - Header regex (used with hdr_reg expression).
    type: str
    default: ""
  hdr_sub:
    description:
      - Header substring (used with hdr_sub expression).
    type: str
    default: ""
  path_beg:
    description:
      - Path begin value.
    type: str
    default: ""
  path_end:
    description:
      - Path end value.
    type: str
    default: ""
  path:
    description:
      - Exact path value.
    type: str
    default: ""
  path_reg:
    description:
      - Path regex.
    type: str
    default: ""
  path_dir:
    description:
      - Path directory value.
    type: str
    default: ""
  path_sub:
    description:
      - Path substring value.
    type: str
    default: ""
  url_param:
    description:
      - URL parameter name.
    type: str
    default: ""
  url_param_value:
    description:
      - URL parameter value.
    type: str
    default: ""
  ssl_c_verify_code:
    description:
      - SSL client verify code.
    type: str
    default: ""
  ssl_c_ca_commonname:
    description:
      - SSL CA common name.
    type: str
    default: ""
  src:
    description:
      - Source address/value.
    type: str
    default: ""
  src_bytes_in_rate_comparison:
    description:
      - Comparison operator for src_bytes_in_rate.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_bytes_in_rate:
    description:
      - Bytes in rate value.
    type: str
    default: ""
  src_bytes_out_rate_comparison:
    description:
      - Comparison operator for src_bytes_out_rate.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_bytes_out_rate:
    description:
      - Bytes out rate value.
    type: str
    default: ""
  src_conn_cnt_comparison:
    description:
      - Comparison operator for src_conn_cnt.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_conn_cnt:
    description:
      - Connection count value.
    type: str
    default: ""
  src_conn_rate_comparison:
    description:
      - Comparison operator for src_conn_rate.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_conn_rate:
    description:
      - Connection rate value.
    type: str
    default: ""
  src_http_err_cnt_comparison:
    description:
      - Comparison operator for src_http_err_cnt.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_http_err_cnt:
    description:
      - HTTP error count value.
    type: str
    default: ""
  src_http_err_rate_comparison:
    description:
      - Comparison operator for src_http_err_rate.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_http_err_rate:
    description:
      - HTTP error rate value.
    type: str
    default: ""
  src_http_req_rate_comparison:
    description:
      - Comparison operator for src_http_req_rate.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_http_req_rate:
    description:
      - HTTP request rate value.
    type: str
    default: ""
  src_kbytes_in_comparison:
    description:
      - Comparison operator for src_kbytes_in.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_kbytes_in:
    description:
      - Kbytes in value.
    type: str
    default: ""
  src_kbytes_out_comparison:
    description:
      - Comparison operator for src_kbytes_out.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_kbytes_out:
    description:
      - Kbytes out value.
    type: str
    default: ""
  src_port_comparison:
    description:
      - Comparison operator for src_port.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_port:
    description:
      - Source port value.
    type: str
    default: ""
  src_sess_cnt_comparison:
    description:
      - Comparison operator for src_sess_cnt.
    type: str
    choices: ["", "gt", "ge", "eq", "lt", "le"]
    default: "gt"
  src_sess_cnt:
    description:
      - Session count value.
    type: str
    default: ""
  nbsrv:
    description:
      - Number of servers threshold.
    type: str
    default: ""
  nbsrv_backend:
    description:
      - Backend name for nbsrv ACLs.
    type: str
    default: ""
  ssl_fc_sni:
    description:
      - SSL FC SNI value.
    type: str
    default: ""
  ssl_sni:
    description:
      - SNI value.
    type: str
    default: ""
  ssl_sni_sub:
    description:
      - SNI substring value.
    type: str
    default: ""
  ssl_sni_beg:
    description:
      - SNI begin value.
    type: str
    default: ""
  ssl_sni_end:
    description:
      - SNI end value.
    type: str
    default: ""
  ssl_sni_reg:
    description:
      - SNI regex value.
    type: str
    default: ""
  custom_acl:
    description:
      - Custom ACL expression.
    type: str
    default: ""
  value:
    description:
      - The ACL value.
    type: str
    default: ""
  query_backend:
    description:
      - Backend for query-based ACLs.
    type: str
    default: ""
  allowed_users:
    description:
      - List of users allowed by this ACL.
    type: list
    elements: str
    default: []
  allowed_groups:
    description:
      - List of groups allowed by this ACL.
    type: list
    elements: str
    default: []
  state:
    description:
      - Whether the ACL should exist or not.
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
  - module: opnsense_haproxy_action
  - module: opnsense_haproxy_frontend
"""

EXAMPLES = r"""
- name: Create an ACL
  opnsense_haproxy_acl:
    name: api_path
    expression: path_beg
    value: /api
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Create an ACL with allowed users
  opnsense_haproxy_acl:
    name: internal_acl
    expression: hdr_beg
    hdr: Host
    value: internal.local
    allowed_users: [admin, operator]
    allowed_groups: [admins]
    api_url: "https://firewall.local"
    api_key: "my_key"
    api_secret: "my_secret"

- name: Delete an ACL
  opnsense_haproxy_acl:
    name: api_path
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


class AclModule(OpnsenseHaproxyModule):
    """Module for managing HAProxy ACLs."""

    OBJECT_TYPE = "acl"
    ARGUMENT_SPEC = {
        "name": dict(type="str", required=True),
        "description": dict(type="str", default=""),
        "expression": dict(
            type="str",
            required=True,
            choices=[
                "http_auth", "hdr_beg", "hdr_end", "hdr", "hdr_reg", "hdr_sub",
                "path_beg", "path_end", "path", "path_reg", "path_dir", "path_sub",
                "url_param", "ssl_c_verify", "ssl_c_verify_code", "ssl_c_ca_commonname",
                "src", "src_is_local", "src_port",
                "src_bytes_in_rate", "src_bytes_out_rate",
                "src_kbytes_in", "src_kbytes_out",
                "src_conn_cnt", "src_conn_cur", "src_conn_rate",
                "src_http_err_cnt", "src_http_err_rate",
                "src_http_req_cnt", "src_http_req_rate",
                "src_sess_rate", "nbsrv",
                "traffic_is_http", "traffic_is_ssl",
                "ssl_fc", "ssl_fc_sni",
                "ssl_sni", "ssl_sni_sub", "ssl_sni_beg", "ssl_sni_end", "ssl_sni_reg",
                "custom_acl",
            ],
        ),
        "negate": dict(type="bool", default=False),
        "hdr_beg": dict(type="str", default=""),
        "hdr_end": dict(type="str", default=""),
        "hdr": dict(type="str", default=""),
        "hdr_reg": dict(type="str", default=""),
        "hdr_sub": dict(type="str", default=""),
        "path_beg": dict(type="str", default=""),
        "path_end": dict(type="str", default=""),
        "path": dict(type="str", default=""),
        "path_reg": dict(type="str", default=""),
        "path_dir": dict(type="str", default=""),
        "path_sub": dict(type="str", default=""),
        "url_param": dict(type="str", default=""),
        "url_param_value": dict(type="str", default=""),
        "ssl_c_verify_code": dict(type="str", default=""),
        "ssl_c_ca_commonname": dict(type="str", default=""),
        "src": dict(type="str", default=""),
        "src_bytes_in_rate_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_bytes_in_rate": dict(type="str", default=""),
        "src_bytes_out_rate_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_bytes_out_rate": dict(type="str", default=""),
        "src_conn_cnt_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_conn_cnt": dict(type="str", default=""),
        "src_conn_rate_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_conn_rate": dict(type="str", default=""),
        "src_http_err_cnt_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_http_err_cnt": dict(type="str", default=""),
        "src_http_err_rate_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_http_err_rate": dict(type="str", default=""),
        "src_http_req_rate_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_http_req_rate": dict(type="str", default=""),
        "src_kbytes_in_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_kbytes_in": dict(type="str", default=""),
        "src_kbytes_out_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_kbytes_out": dict(type="str", default=""),
        "src_port_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_port": dict(type="str", default=""),
        "src_sess_cnt_comparison": dict(
            type="str", choices=["", "gt", "ge", "eq", "lt", "le"], default="gt"
        ),
        "src_sess_cnt": dict(type="str", default=""),
        "nbsrv": dict(type="str", default=""),
        "nbsrv_backend": dict(type="str", default=""),
        "ssl_fc_sni": dict(type="str", default=""),
        "ssl_sni": dict(type="str", default=""),
        "ssl_sni_sub": dict(type="str", default=""),
        "ssl_sni_beg": dict(type="str", default=""),
        "ssl_sni_end": dict(type="str", default=""),
        "ssl_sni_reg": dict(type="str", default=""),
        "custom_acl": dict(type="str", default=""),
        "value": dict(type="str", default=""),
        "query_backend": dict(type="str", default=""),
        "allowed_users": dict(type="list", elements="str", default=[]),
        "allowed_groups": dict(type="list", elements="str", default=[]),
    }

    def _build_desired_state(self):
        params = self.module.params
        # Resolve reference UUIDs
        template = self.api.getObjectByUuid(self.OBJECT_TYPE, "")
        nbsrv_backend_uuid = self._resolve_name_to_uuid(template, params["nbsrv_backend"], "nbsrv_backend")
        query_backend_uuid = self._resolve_name_to_uuid(template, params["query_backend"], "queryBackend")
        allowed_users_uuids = self._resolve_names_to_uuids(template, params["allowed_users"], "allowedUsers")
        allowed_groups_uuids = self._resolve_names_to_uuids(template, params["allowed_groups"], "allowedGroups")

        return {
            "description": params.get("description", ""),
            "expression": params["expression"],
            "negate": str(int(params["negate"])),
            "hdr_beg": params["hdr_beg"],
            "hdr_end": params["hdr_end"],
            "hdr": params["hdr"],
            "hdr_reg": params["hdr_reg"],
            "hdr_sub": params["hdr_sub"],
            "path_beg": params["path_beg"],
            "path_end": params["path_end"],
            "path": params["path"],
            "path_reg": params["path_reg"],
            "path_dir": params["path_dir"],
            "path_sub": params["path_sub"],
            "url_param": params["url_param"],
            "url_param_value": params["url_param_value"],
            "ssl_c_verify_code": params["ssl_c_verify_code"],
            "ssl_c_ca_commonname": params["ssl_c_ca_commonname"],
            "src": params["src"],
            "src_bytes_in_rate_comparison": params["src_bytes_in_rate_comparison"],
            "src_bytes_in_rate": params["src_bytes_in_rate"],
            "src_bytes_out_rate_comparison": params["src_bytes_out_rate_comparison"],
            "src_bytes_out_rate": params["src_bytes_out_rate"],
            "src_conn_cnt_comparison": params["src_conn_cnt_comparison"],
            "src_conn_cnt": params["src_conn_cnt"],
            "src_conn_rate_comparison": params["src_conn_rate_comparison"],
            "src_conn_rate": params["src_conn_rate"],
            "src_http_err_cnt_comparison": params["src_http_err_cnt_comparison"],
            "src_http_err_cnt": params["src_http_err_cnt"],
            "src_http_err_rate_comparison": params["src_http_err_rate_comparison"],
            "src_http_err_rate": params["src_http_err_rate"],
            "src_http_req_rate_comparison": params["src_http_req_rate_comparison"],
            "src_http_req_rate": params["src_http_req_rate"],
            "src_kbytes_in_comparison": params["src_kbytes_in_comparison"],
            "src_kbytes_in": params["src_kbytes_in"],
            "src_kbytes_out_comparison": params["src_kbytes_out_comparison"],
            "src_kbytes_out": params["src_kbytes_out"],
            "src_port_comparison": params["src_port_comparison"],
            "src_port": params["src_port"],
            "src_sess_cnt_comparison": params["src_sess_cnt_comparison"],
            "src_sess_cnt": params["src_sess_cnt"],
            "nbsrv": params["nbsrv"],
            "nbsrv_backend": nbsrv_backend_uuid,
            "ssl_fc_sni": params["ssl_fc_sni"],
            "ssl_sni": params["ssl_sni"],
            "ssl_sni_sub": params["ssl_sni_sub"],
            "ssl_sni_beg": params["ssl_sni_beg"],
            "ssl_sni_end": params["ssl_sni_end"],
            "ssl_sni_reg": params["ssl_sni_reg"],
            "custom_acl": params["custom_acl"],
            "value": params["value"],
            "queryBackend": query_backend_uuid,
            "allowedUsers": ",".join(allowed_users_uuids),
            "allowedGroups": ",".join(allowed_groups_uuids),
        }

    def _diff_state(self, current, desired):
        """Custom diff for ACL — handles selection fields and reference list comparisons."""
        changes = {}
        messages = []
        needs_change = False
        params = self.module.params

        selection_fields = ["expression"]
        comparison_fields = [
            "src_bytes_in_rate_comparison", "src_bytes_out_rate_comparison",
            "src_conn_cnt_comparison", "src_conn_rate_comparison",
            "src_http_err_cnt_comparison", "src_http_err_rate_comparison",
            "src_http_req_rate_comparison", "src_kbytes_in_comparison",
            "src_kbytes_out_comparison", "src_port_comparison",
            "src_sess_cnt_comparison",
        ]
        reference_fields = {
            "nbsrv_backend": ("nbsrv_backend", "nbsrv_backend"),
            "queryBackend": ("query_backend", "queryBackend"),
            "allowedUsers": ("allowed_users", "allowedUsers"),
            "allowedGroups": ("allowed_groups", "allowedGroups"),
        }

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
            # Comparison fields
            elif prop in comparison_fields:
                selected = self.api.getSelected(current_value)
                if selected != desired_value:
                    needs_change = True
                    changes[prop] = desired_value
                    messages.append("Changing %s: %s => %s" % (prop, selected, desired_value))
            # Reference fields (UUID lists)
            elif prop in reference_fields:
                param_name, template_key = reference_fields[prop]
                if param_name.endswith("_users") or param_name.endswith("_groups"):
                    current_list = self.api.getSelectedList(current_value)
                    if not self.api.compareLists(current_list, params[param_name]):
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_list, params[param_name]))
                elif param_name in ("nbsrv_backend", "query_backend"):
                    current_ref = self.api.getSelected(current_value)
                    if current_ref != params[param_name]:
                        needs_change = True
                        changes[prop] = desired_value
                        messages.append("Changing %s: %s => %s" % (prop, current_ref, params[param_name]))
            # Simple fields
            elif current_value != desired_value:
                needs_change = True
                changes[prop] = desired_value
                messages.append("Changing %s: %s => %s" % (prop, current_value, desired_value))

        return needs_change, changes, messages


def main():
    module = AclModule()
    state = module.module.params.get("state", "present")
    if state == "absent":
        result = module.run_absent()
    else:
        result = module.run()
    module.module.exit_json(**result)


if __name__ == "__main__":
    main()
