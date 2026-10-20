# Changelog

## [2.0.0] - 2026-XX-XX

### Breaking Changes

- **Python 3 only** — Dropped Python 2 support. All modules now require Python 3.
- **Parameter renaming** — Module parameters now use the object name directly instead of type-prefixed names:
  - `acl_name` → `name`
  - `backend_name` → `name`
  - `frontend_name` → `name`
  - `server_name` → `name`
  - `action_name` → `name`
  - `healthcheck_name` → `name`
  - `lua_name` → `name`
  - `mapfile_name` → `name`
  - `errorfile_name` → `name`
  - `user_name` → `name`
  - `group_name` → `name`
  - `cpu_name` → `name`
  - `acl_state` → `state` (and similarly for all other types)
- **Removed `global module` pattern** — Internal change; modules now use instance attributes.
- **`msg` return value** — Changed from `list` to `str` for cleaner output.

### Added

- **Base module class** (`OpnsenseHaproxyModule`) — Eliminates ~80% of duplicated CRUD code across all 12 modules.
- **Custom exceptions** — `OpnsenseApiError`, `ObjectNotFoundError`, `ObjectTypeError`, `ConfigTestError`.
- **Type hints and docstrings** — All API client methods are now typed and documented.
- **Full module documentation** — Every module now has complete `DOCUMENTATION`, `EXAMPLES`, and `RETURN` blocks.
- **`galaxy.yml`** — Proper Ansible Galaxy metadata.
- **`.ansible-lint`** — Linting configuration.
- **Structured tasks** — Each object type has its own task file (`manage_acls.yml`, `manage_backends.yml`, etc.).
- **`defaults/main.yml`** — All role variables documented with examples.
- **Example playbooks** — `examples/site.yml` and `examples/group_vars/all.yml`.
- **`CHANGELOG.md`** — Version history.

### Changed

- **API client** — Added `timeout=30` to all `requests` calls.
- **API client** — `iteritems()` replaced with `.items()` for Python 3 compatibility.
- **API client** — `compareLists()` is now a `@staticmethod`.
- **Server module** — SSL CA/CRL/client certificate names are resolved when the server is created, so one step is enough.

### Fixed

The role could report success without configuring anything. Every
`tasks/manage_*.yml` passed only the connection arguments to its module, so the
objects from the `opnsense_haproxy_*` dicts were never sent to the API.

- **Task files** — each task now merges the shared connection arguments, the
  object's parameters and its name (the dict key) into one argument set.
  Per-object `state: absent` and `haproxy_reload` work as documented.
- **Module imports** — the `from __future__ import` block sat below
  `DOCUMENTATION` in every module file, so all 12 modules failed to import.
- **Module argument spec** — `_create_ansible_module()` used the base class's
  empty spec, so no module parameter was declared and every parameter was
  rejected or silently dropped.
- **Module names in tasks** — modules were called as
  `local.maj.opnsense_haproxy_*`; role-local `library/` modules are only
  reachable by their short name.
- **`postRequest`** — assumed a dict response; the configtest and reconfigure
  endpoints answer with a plain string, which raised `AttributeError` on every
  run with `haproxy_reload: true`.
- **ACL module** — `description` was never declared, although the defaults
  example used it.
- **Server module** — `sslCA`/`sslCRL`/`sslClientCertificate` were dropped when
  creating a server, contradicting the documented one-step usage.
- **Map files** — the module existed but had no task file, so
  `opnsense_haproxy_mapfiles` could not be used.
- **Selection fields** — `getSelected()`/`getSelectedList()` compared
  `selected == 1`, but the API flags the chosen option with the string `"1"`,
  so a second run reported changes it could not avoid. Both helpers now match
  either form, and `_diff_state()` recognises the selection-dict shape without
  raising on plain values.
- **Reference fields** — backends, frontends, servers, groups, actions and ACLs
  compared the UUID keys the API reports against the *names* the user wrote, so
  they were rewritten on every run. The diff now compares the resolved UUIDs
  that `_build_desired_state()` already computed; the new `_reference_keys()`
  helper in the base class reduces the selection dict, the comma-joined string
  and a plain list to the same key list.
- **Field names in the diffs** — the backend and frontend `_diff_state()`
  overrides listed parameter names (`persistence_cookie_mode`,
  `connection_behaviour`, `basic_auth_users`) while they iterate the API keys
  (`persistence_cookiemode`, `connectionBehaviour`, `basicAuthUsers`), so those
  fields fell through to a raw comparison and always looked changed.
- **Action module** — `use_backend` was compared as a plain value although the
  API reports it as a selection dict.
- **CPU module** — `cpu_id` compared the API's option keys against the raw
  parameter list.
- **CPU example** — `cpu_id: x0` is not offered by the API; the example uses `x1`.
- **Role metadata** — `galaxy.yml` dependencies and `meta/main.yml` placement
  fixed, `meta/runtime.yml` added, so the role can be installed and linted.


### Migration Guide

1. Update your playbooks to use the new parameter names (`name` instead of `acl_name`, etc.).
2. Ensure Python 3 is available on the controller.
3. Run `ansible-galaxy install local.maj_opnsense_haproxy` if installing from Galaxy.
