# opnsense_haproxy

[![License: GPL-2.0](https://img.shields.io/badge/License-GPLv2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)

Ansible role for managing HAProxy configuration on **OPNsense firewalls** via the OPNsense HAProxy plugin API.

## Supported Object Types

| Type | Module | Description |
|------|--------|-------------|
| ACL | `opnsense_haproxy_acl` | Conditions (header, path, source, SSL, rate, etc.) |
| Action | `opnsense_haproxy_action` | Rules (redirect, deny, use_backend, header manipulation) |
| Backend | `opnsense_haproxy_backend` | Backend pools with servers, healthchecks, persistence |
| CPU | `opnsense_haproxy_cpu` | CPU affinity rules |
| Errorfile | `opnsense_haproxy_errorfile` | Custom error pages (403, 503, etc.) |
| Frontend | `opnsense_haproxy_frontend` | Public services with binds, SSL, stickiness |
| Group | `opnsense_haproxy_group` | User groups |
| Healthcheck | `opnsense_haproxy_healthcheck` | Healthchecks (HTTP, TCP, MySQL, PostgreSQL, etc.) |
| Lua | `opnsense_haproxy_lua` | Lua scripts |
| Mapfile | `opnsense_haproxy_mapfile` | Map files |
| Server | `opnsense_haproxy_server` | Backend servers |
| User | `opnsense_haproxy_user` | Users |

## Prerequisites

- Python 3 on the Ansible controller
- OPNsense firewall with the HAProxy plugin installed
- API credentials with HAProxy management permissions
- `requests` Python library (usually pre-installed)

## Role Variables

### API Connection (required)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `opnsense_api_url` | string | `""` | OPNsense firewall URL (e.g. `https://firewall.local`) |
| `opnsense_api_key` | string | `""` | API key |
| `opnsense_api_secret` | string | `""` | API secret |
| `opnsense_api_ssl_verify` | bool | `false` | Verify SSL certificate |
| `opnsense_haproxy_reload` | bool | `false` | Reload HAProxy after changes |

### Object Collections

All object types use a dictionary keyed by name. Each name must be unique.

```yaml
opnsense_haproxy_<type>:
  object_name:
    param1: value1
    param2: value2
```

See the [examples](examples/) directory for complete variable definitions.

## Example Usage

```yaml
- name: Configure HAProxy on OPNsense
  hosts: localhost
  connection: local
  gather_facts: no

  vars:
    opnsense_api_url: "https://firewall.local"
    opnsense_api_key: "my_key"
    opnsense_api_secret: "my_secret"
    opnsense_haproxy_acls:
      api_path:
        expression: path_beg
        value: /api
    opnsense_haproxy_servers:
      web1:
        address: 10.0.0.1
        port: "8080"
    opnsense_haproxy_backends:
      api_pool:
        mode: http
        algorithm: roundrobin
        linked_servers: [web1]
    opnsense_haproxy_frontends:
      web_https:
        bind: ["*:443"]
        mode: http
        default_backend: api_pool
        ssl_enabled: true
        ssl_certificates: [my_cert]

  tasks:
    - name: Apply HAProxy configuration
      ansible.builtin.include_role:
        name: local.maj.opnsense.haproxy
```

See [examples/site.yml](examples/site.yml) and [examples/group_vars/all.yml](examples/group_vars/all.yml) for a complete working example.

## Limitations

### SSL CA / CRL / Client Certificate Two-Step Workflow

OPNsense's API does not allow querying SSL CA, CRL, or client certificate objects by name — they are referenced by internal UUIDs unknown at creation time. When a server needs one of these:

1. Create/update the server **without** the SSL reference.
2. Run the same task again with the SSL reference populated.

```yaml
# First run — create server without SSL refs
opnsense_haproxy_servers:
  web1:
    address: 10.0.0.1
    port: "443"
    ssl: true

# Second run — add SSL CA reference
opnsense_haproxy_servers:
  web1:
    address: 10.0.0.1
    port: "443"
    ssl: true
    ssl_ca: [my_ca]
```

## Dependencies

None. This role has no Ansible Galaxy or other dependencies.

## Module Parameters

Each module accepts the common API parameters (`api_url`, `api_key`, `api_secret`, `api_ssl_verify`, `haproxy_reload`, `state`) plus type-specific parameters. See the module's `DOCUMENTATION` block (run `ansible-doc local.maj.opnsense_haproxy_<type>`) for the full parameter list.

## License

GPL-2.0-or-later

## Author

Markus Joosten — [https://github.com/mj84](https://github.com/mj84)
