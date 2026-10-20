# AGENTS.md — `local.maj.opnsense.haproxy`

## What this is
An Ansible role that manages HAProxy configuration **on OPNsense firewalls** via the OPNsense plugin API. It ships 12 custom Python modules (one per HAProxy object type) and a shared API client (`module_utils/opnsense_utils/`).

## Running / Testing
- **Lint:** `ansible-lint` (config in `.ansible-lint`) and `flake8 library/ module_utils/ tests/` (config in `setup.cfg`)
- **Unit tests:** `pytest tests/unit/` (requires `pytest`)
- **End-to-end tests:** `pytest tests/e2e/` — runs the real role through
  `ansible-playbook` against `tests/mock_api/server.py`, a mock of the OPNsense
  settings API. Needs `ansible-core` and `requests` in the test interpreter, no
  firewall. See `tests/mock_api/README.md`.
- **Integration test:** `tests/test.yml` — requires a live OPNsense box
- **CI:** `.github/workflows/ci.yml` runs ansible-lint, flake8, pytest (unit) and pytest (e2e)

## Architecture
- `library/` — 12 custom Ansible modules. Each inherits from `OpnsenseHaproxyModule` base class.
- `module_utils/opnsense_utils/OpnsenseApi.py` — shared REST client with type hints and custom exceptions.
- `module_utils/opnsense_utils/OpnsenseModule.py` — base module class extracting shared CRUD/diff logic.
- `tasks/` — `main.yml` plus one task file per object type, included in dependency order.
- `defaults/main.yml` — all role variables documented with examples.
- `vars/main.yml` — `opnsense_haproxy_connection_args`, the API arguments merged into every module call. Not meant to be overridden by users.
- `tests/unit/` — pytest, no network. `tests/mock_api/` — the mock settings API
  and the playbooks that drive it. `tests/e2e/` — pytest, runs the role against
  that mock through `ansible-playbook`.

## Critical gotchas

### The role name has dots
Playbooks address the role as `local.maj.opnsense.haproxy`, and it must be
installed under a directory of that exact name. That name is **not** a valid
Galaxy role or collection name (Galaxy forbids dots), so there is no `galaxy.yml`
— it could not express the name and `ansible-lint` rejects it — and `role-name`
is in the `.ansible-lint` `skip_list`. Do not "fix" either of those by renaming
the role or re-adding `galaxy.yml`.

### Task files pass arguments as one merged template
Each `tasks/manage_<type>.yml` loops over its `opnsense_haproxy_<type>s` dict and hands the module a single templated argument set:

```yaml
opnsense_haproxy_acl: "{{ opnsense_haproxy_connection_args | combine(item.value, {'name': item.key}) }}"
```

Two rules that are easy to get wrong:
- Modules must be called by their **short name** (`opnsense_haproxy_acl`). The
  FQCN-style `local.maj.opnsense_haproxy_acl` never resolves for role-local
  `library/` modules, and the task then fails to find the module.
- The object's own parameters have to be part of that argument set. A task that
  passes only the connection arguments runs "successfully" and changes nothing.
  `tests/unit/test_role_wiring.py` guards both.

### SSL CA / CRL / client certificate resolution
SSL CA, CRL, and client certificate objects are referenced by internal UUIDs, but modules resolve names to UUIDs at runtime using the empty-object template (which contains the full API catalog of all SSL objects). No two-step workflow is required — you can specify SSL references when creating a server.

If multiple SSL objects share the same description, the module warns and uses the last match (YAML-style dedup). Descriptions should be kept unique to avoid ambiguity.

### Dependency ordering in `tasks/main.yml`
The task include order is deliberate and reflects OPNsense's internal dependency graph:
1. ACLs → 2. CPUs → 3. Errorfiles → 4. Mapfiles → 5. Healthchecks → 6. Lua → 7. Servers → 8. Users → 9. Groups → 10. Backends → 11. Actions → 12. Frontends

Changing this order will cause API errors because referenced objects must exist first. A new object type needs its `tasks/manage_<type>.yml` included at the right place in that chain — `tests/unit/test_role_wiring.py` checks the order.

### UUIDs are opaque
OPNsense uses internal UUIDs for all objects. Users interact exclusively by **name**, which must be unique. Modules resolve names to UUIDs at runtime via the API, using an empty-object template (`getObjectByUuid(type, '')`).

### Selection fields come back as dicts
A single-choice field (a backend's `healthCheck`, an action's `type`) is **not** a plain value in a GET response. The API returns `{"<uuid>": {"selected": "1", "name": "…"}}` for every option, with the chosen one flagged. `api.getSelected()` / `getSelectedList()` reduce that to the key or name, and `OpnsenseHaproxyModule._is_selection_dict()` recognises the shape in `_diff_state()`. Note the API flags selection with the **string** `"1"`, not the int `1`.

### Compare references as UUIDs, and name fields the API's way
`_build_desired_state()` resolves every reference name to its UUID and joins
lists with commas — that is what gets sent to the API, so it is also what the
diff has to compare. Comparing the current UUID against
`self.module.params[...]` (still a name) makes the object look out of date on
every run. `OpnsenseHaproxyModule._reference_keys()` reduces the three shapes a
reference arrives in — the API's selection dict, the comma-joined string, a
plain list — to one list of keys; use it on both sides.

The same trap applies to the field lists inside a `_diff_state()` override: the
loop iterates **API keys**, so `selection_fields`/`reference_fields` must hold
`persistence_cookiemode`, `connectionBehaviour`, `basicAuthUsers` — not the
parameter names `persistence_cookie_mode`, `connection_behaviour`,
`basic_auth_users`. A name that never matches falls through to a raw
comparison, which always reports a change for a selection dict.

### `haproxy_reload` parameter
Each module accepts `haproxy_reload` (default `false`). When `true`, the module runs OPNsense's `configtest` + `reconfigure` API calls after making changes. Set this selectively — unnecessary reloads cause brief service interruptions. Those two endpoints answer with a plain string in `result`, not a dict; `postRequest()` handles both.

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
2. `ARGUMENT_SPEC` — module-specific parameter definitions. `_create_ansible_module()` merges these with the base class spec (`name`, `state`, the API arguments, `haproxy_reload`), so do not redeclare those.
3. `_build_desired_state()` — returns a dict of properties for the API, keyed and
   valued the way the API wants them (API key names, references resolved to UUIDs,
   lists comma-joined, booleans as `"0"`/`"1"`).
4. Optional `_diff_state()` override — only needed for complex comparison logic (conditional SSL blocks, order-sensitive links). The base class already handles selection dicts and reference lists via `_reference_keys()`.

In every module file the `from __future__ import …` block must stay the first statement, above `DOCUMENTATION`, or the module will not import. The `module_utils` import belongs after the documentation blocks, which is why flake8 ignores `E402` (see `setup.cfg`).

When adding a new object type:
1. Copy a simple module (e.g. `opnsense_haproxy_lua.py`) and adjust the four items above.
2. Add the type to `Haproxy.OBJECT_TYPES` in `OpnsenseApi.py`.
3. Add `opnsense_haproxy_<type>s: {}` to `defaults/main.yml` with an example.
4. Add `tasks/manage_<type>.yml` following the merged-template pattern, and include it in `tasks/main.yml` at the right point in the dependency chain.
5. `ansible-lint`, `flake8 library/ module_utils/` and `pytest tests/unit/` must stay clean — `tests/unit/test_role_wiring.py` covers the wiring for every type.

## Overhaul plan
See `OVERHAUL_PLAN.md` for the remaining work (Molecule testing against a live box, pre-commit hooks, full documentation).
