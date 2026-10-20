# AGENTS.md — `local.maj.opnsense.haproxy`

## What this is
An Ansible role that manages HAProxy configuration **on OPNsense firewalls** via the OPNsense plugin API. It ships 14 custom Python modules (one per HAProxy object type) and a shared API client (`module_utils/opnsense_utils/`).

## Running / Testing
- **Lint:** `ansible-lint` (config in `.ansible-lint`)
- **Unit tests:** `pytest tests/unit/` (requires `pytest`)
- **Integration test:** `tests/test.yml` — requires a live OPNsense box
- No CI pipeline yet (see `OVERHAUL_PLAN.md` Phase 6)

## Architecture
- `library/` — 14 custom Ansible modules. Each inherits from `OpnsenseHaproxyModule` base class.
- `module_utils/opnsense_utils/OpnsenseApi.py` — shared REST client with type hints and custom exceptions.
- `module_utils/opnsense_utils/OpnsenseModule.py` — base module class extracting shared CRUD/diff logic.
- `tasks/` — 11 task files (one per object type), included from `tasks/main.yml` in dependency order.
- `defaults/main.yml` — all role variables documented with examples.

## Critical gotchas

### SSL CA / CRL / client certificate two-step workflow
OPNsense's API does not allow querying SSL CA, CRL, or client certificate objects by name — they are referenced by internal UUIDs unknown at creation time. When a server needs one of these:
1. Create/update the server **without** the SSL reference.
2. Run the same task again with the SSL reference populated.

### Dependency ordering in `tasks/main.yml`
The task include order is deliberate and reflects OPNsense's internal dependency graph:
1. ACLs → 2. CPUs → 3. Errorfiles → 4. Healthchecks → 5. Lua → 6. Servers → 7. Users → 8. Groups → 9. Backends → 10. Actions → 11. Frontends

Changing this order will cause API errors because referenced objects must exist first.

### UUIDs are opaque
OPNsense uses internal UUIDs for all objects. Users interact exclusively by **name**, which must be unique. Modules resolve names to UUIDs at runtime via the API, using an empty-object template (`getObjectByUuid(type, '')`).

### `haproxy_reload` parameter
Each module accepts `haproxy_reload` (default `false`). When `true`, the module runs OPNsense's `configtest` + `reconfigure` API calls after making changes. Set this selectively — unnecessary reloads cause brief service interruptions.

### Variable naming convention
All role variables use the prefix `opnsense_haproxy_` followed by the plural object name:
- `opnsense_haproxy_acls` — dict of ACL configs
- `opnsense_haproxy_backends` — dict of backend configs
- `opnsense_haproxy_frontends` — dict of frontend configs
- etc.

Each dict key is the object name (must be unique). Values are dicts of the module parameters.

## Module development pattern
Every module is a subclass of `OpnsenseHaproxyModule` that defines:
1. `OBJECT_TYPE` — the OPNsense API type string (e.g. `'backend'`)
2. `ARGUMENT_SPEC` — module-specific parameter definitions
3. `_build_desired_state()` — returns a dict of properties for the API
4. Optional `_diff_state()` override — only needed for complex comparison logic (selection dicts, reference lists)

When adding a new module, copy an existing simple module (e.g. `opnsense_haproxy_lua.py`) and adjust the three items above. Add a corresponding `tasks/manage_<type>.yml` task file and include it in `tasks/main.yml`.

## Overhaul plan
See `OVERHAUL_PLAN.md` for the remaining work (Molecule testing, CI, pre-commit hooks, full documentation).
