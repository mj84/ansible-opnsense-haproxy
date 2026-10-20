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

- **Base module class** (`OpnsenseHaproxyModule`) — Eliminates ~80% of duplicated CRUD code across all 14 modules.
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
- **Server module** — SSL CA/CRL/client certificate resolution improved; creation clears SSL refs (two-step workflow preserved).

### Removed

- Empty `handlers/main.yml`, `defaults/main.yml`, `vars/main.yml` stubs.
- `manage_object.yml` generic task file (replaced by per-type task files).

### Migration Guide

1. Update your playbooks to use the new parameter names (`name` instead of `acl_name`, etc.).
2. Ensure Python 3 is available on the controller.
3. Run `ansible-galaxy install local.maj_opnsense_haproxy` if installing from Galaxy.
