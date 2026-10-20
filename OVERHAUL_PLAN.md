# Ansible Role Overhaul Plan — `local.maj.opnsense.haproxy`

## Current State Summary

14 custom modules + 1 shared API client. No CI, no lint, no tests, no galaxy metadata, no EXAMPLES/RETURN docs. All modules use Python 2 patterns (`iteritems()`, `from __future__`, global `module` variable). The API client is the only non-trivial shared code. Every module follows the same CRUD boilerplate (~100–500 lines each) with manual diff logic, UUID resolution loops, and `exit_json` calls duplicated 14 times.

---

## Phase 1 — Foundation & Metadata

### 1.1 Add `galaxy.yml`
Modern Ansible roles require this. Populate author, description, license, version, and tags. Set `min_ansible_version` to 2.15+ (Python 3 only).

### 1.2 Add `requirements.yml`
Document the `community.general` and `ansible.netcommon` collection dependencies (if any are needed). Currently there are none — the role only needs `requests` on the controller, which is standard.

### 1.3 Remove empty stubs
Delete the empty `handlers/main.yml`, `defaults/main.yml`, `vars/main.yml`. If defaults are needed later, create them properly — don't keep dead files.

### 1.4 Add `.ansible-lint` config
Configure rules to skip or enforce:
- `no-jinja-when` (acceptable here since we pass raw values)
- `role-name` (role name is `local.maj.opnsense.haproxy` — may need renaming)
- Custom excludes for legacy patterns being phased out

---

## Phase 2 — API Client Modernization

### 2.1 Python 3 migration
Replace all `.iteritems()` with `.items()` in `module_utils/opnsense_utils/OpnsenseApi.py`. Remove `from __future__` imports everywhere. Drop Python 2 compatibility.

### 2.2 Add proper error handling
- Raise custom exceptions (`OpnsenseApiError`, `ObjectNotFoundError`) instead of bare `ValueError`/`KeyError`
- Add retry logic with exponential backoff for transient API failures
- Add timeout configuration for `requests` calls

### 2.3 Add type hints and docstrings
Every method in `OpnsenseApi.Haproxy` needs:
- Type hints on parameters and return values
- A docstring describing purpose, parameters, and return type
- A short example in the class docstring

### 2.4 Add unit tests for the API client
Create `tests/unit/test_opnsense_api.py` using `pytest` + `unittest.mock`. Mock the `requests` layer and test:
- `listObjects` parsing
- `getObjectByName` / `getObjectByUuid`
- `createObject`, `updateObject`, `deleteObject`
- `applyConfig` success and failure paths
- `getUuidByName` missing object error
- `compareLists` with and without order sensitivity
- `getSelected` / `getSelectedList` edge cases (empty dicts, no selected item)

---

## Phase 3 — Module Refactoring (Core)

This is the biggest change. All 14 modules share the same structural pattern. The goal is to eliminate ~80% of duplicated code.

### 3.1 Create a base module class
Create `module_utils/opnsense_utils/OpnsenseModule.py` — a base class that all modules inherit from. It provides:

```python
class OpnsenseHaproxyModule:
    """Base class for all HAProxy management modules."""
    
    OBJECT_TYPE = None          # e.g., 'backend', 'frontend'
    ARGUMENT_SPEC = None        # Module-specific params (set in subclass)
    
    def __init__(self, argument_spec=None, supports_check_mode=True):
        # Merges base params (api_url, api_key, api_secret, api_ssl_verify, 
        # haproxy_reload) with subclass-specific params
        # Creates AnsibleModule
        # Initializes OpnsenseApi client
        pass
    
    def run_module(self):
        # Orchestrates: load current state → diff → apply → reload
        pass
    
    def _load_current_state(self):
        # listObjects(type), then getObjectByName if found
        pass
    
    def _resolve_name_to_uuid(self, ref_type, name):
        # Uses empty-object template lookup (same pattern all modules use)
        pass
    
    def _resolve_list_refs(self, ref_type, names, template_key):
        # Resolves a list of names to UUIDs using the empty-object template
        pass
    
    def _compare_selected(self, current_dict, desired_value):
        # Uses OpnsenseApi.getSelected() to compare dict-with-selected vs string
        pass
    
    def _compare_list_refs(self, current_dict, desired_names, ref_type):
        # Compares currently-selected list refs against desired names
        pass
    
    def _build_desired_state(self):
        # Abstract — implemented by each subclass
        pass
    
    def _diff_state(self, current, desired):
        # Compares current vs desired, returns (changed: bool, changes: dict, messages: list)
        # Handles both simple value comparison and complex selected-dict comparison
        pass
    
    def _apply_changes(self, changed_properties):
        # Calls updateObject or createObject, optionally applyConfig
        pass
```

### 3.2 Reduce each module to ~40–60 lines
Each module becomes a subclass that only defines:
1. `OBJECT_TYPE` (string)
2. `ARGUMENT_SPEC` (dict of module-specific params)
3. `_build_desired_state()` (returns dict of properties to send to API)
4. `_diff_state()` override (only if the module has unusual comparison logic)

Modules like `opnsense_haproxy_lua`, `opnsense_haproxy_mapfile`, `opnsense_haproxy_errorfile` are trivial — they have no complex comparisons. They become ~30 lines.

Modules like `opnsense_haproxy_action` and `opnsense_haproxy_frontend` have the most complex diff logic (HTTP header actions, SSL conditionals, stickiness). They need custom `_diff_state()` but still drop from ~500 lines to ~80.

### 3.3 Add proper DOCUMENTATION, EXAMPLES, RETURN blocks
Every module's `DOCUMENTATION` string needs:
- Full YAML doc block (currently only has `module` and `short_description`)
- `author`, `description`, `options` (all parameters documented with type, default, required, description)
- `seealso` referencing the role
- `examples` showing a minimal usage
- `return` block describing the output

### 3.4 Remove the global `module` variable
The `global module` pattern is an anti-pattern. The base class stores `self.module` as an instance attribute.

### 3.5 Standardize parameter naming
Currently modules use `acl_`-prefixed params (`acl_name`, `acl_state`) which is the old Ansible convention. Modern convention is to use the object name directly (`name`, `state`). However, since this is a breaking change for existing playbooks, offer both:
- New: `name`, `state`, `enabled`, etc.
- Deprecated: `acl_name`, `acl_state` (with warnings)
- Use `AnsibleModule`'s `deprecated` feature for the old params

---

## Phase 4 — Role Structure Improvements

### 4.1 Add `defaults/main.yml` with all role variables
Document every variable (`opnsense_haproxy_acls`, `opnsense_haproxy_backends`, etc.) with:
- Type hints (dict)
- Default value (empty dict `{}`)
- Description of the expected structure
- Example nested structure

### 4.2 Add `tasks/main.yml` improvements
- Add `when: opnsense_haproxy_<type>` guards so empty dicts skip execution
- Add `loop_control` with `label` for readable output
- Add `check_mode` handling for the `haproxy_reload` parameter (don't reload in check mode)
- Add `block/rescue` for better error reporting

### 4.3 Create example playbooks
Add `examples/` directory with:
- `site.yml` — minimal playbook showing role usage
- `group_vars/all.yml` — example variable definitions for a simple setup (one frontend, one backend, one server)
- `group_vars/load_balanced.yml` — more complex example with ACLs, actions, healthchecks

### 4.4 Add a `meta/runtime.yml`
Declare Ansible collection compatibility and deprecation metadata.

---

## Phase 5 — Testing Infrastructure

### 5.1 Install `molecule`
`molecule` is the standard for testing Ansible roles. Configure it with:
- Driver: `docker` (or `podman`)
- Provisioner: Ansible
- Verifier: `pytest`

### 5.2 Create Molecule scenarios
At minimum two scenarios:

**`create`** — Tests creating objects:
```yaml
- name: Create ACL, backend, server, frontend
  opnsense_haproxy_acl:
    name: test-acl
    expression: path
    value: /api
    api_url: "{{ opnsense_url }}"
    api_key: "{{ opnsense_key }}"
    api_secret: "{{ opnsense_secret }}"
  register: result
  check_mode: true

- name: Verify idempotency (second run should report changed: false)
  opnsense_haproxy_acl:
    name: test-acl
    expression: path
    value: /api
    api_url: "{{ opnsense_url }}"
    api_key: "{{ opnsense_key }}"
    api_secret: "{{ opnsense_secret }}"
  register: result
```

**`destroy`** — Tests deletion:
```yaml
- name: Delete objects
  opnsense_haproxy_acl:
    name: test-acl
    state: absent
    api_url: "{{ opnsense_url }}"
    ...
```

### 5.3 Unit tests for modules
Create `tests/unit/test_modules.py` using `pytest` + `unittest.mock`:
- Mock `AnsibleModule` and `OpnsenseApi`
- Test `_build_desired_state()` for each module type
- Test `_diff_state()` with various current/desired combinations
- Test UUID resolution logic
- Test that check mode doesn't call `updateObject`/`createObject`

### 5.4 Integration test playbook
Create `tests/integration/test_role.yml` that exercises the full role with realistic data:
```yaml
- hosts: localhost
  gather_facts: no
  tasks:
    - name: Configure HAProxy via role
      ansible.builtin.include_role:
        name: local.maj.opnsense.haproxy
      vars:
        opnsense_api_url: "https://firewall.local"
        opnsense_api_key: "test_key"
        opnsense_api_secret: "test_secret"
        opnsense_haproxy_acls:
          api_acl:
            expression: path
            value: /api
        opnsense_haproxy_backends:
          api_backend:
            mode: http
            algorithm: roundrobin
            linked_servers: [web1, web2]
        opnsense_haproxy_servers:
          web1:
            address: 10.0.0.1
            port: 8080
          web2:
            address: 10.0.0.2
            port: 8080
        opnsense_haproxy_frontends:
          web_frontend:
            bind: ["*:443"]
            mode: http
            default_backend: api_backend
            ssl_enabled: true
            ssl_certificates: [my_cert]
```

---

## Phase 6 — Linting & CI

### 6.1 Ansible-lint rules
Create `.ansible-lint` with project-specific config. Key rules to enforce:
- `yaml` — valid YAML
- `jinja` — proper Jinja2 syntax
- `command-instead-of-module` — use proper modules
- `no-changed-when` — modules must report `changed` correctly
- `schema` — metadata validation

### 6.2 Add pre-commit hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/ansible-community/ansible-lint
    rev: v6.22.0
    hooks:
      - id: ansible-lint
        files: \.(yaml|yml)$
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        files: library/|module_utils/
```

### 6.3 Add GitHub Actions workflow
`.github/workflows/ci.yml`:
```yaml
name: CI
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ansible-lint flake8 pytest
      - run: ansible-lint
      - run: flake8 library/ module_utils/
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest tests/unit/
```

---

## Phase 7 — Documentation

### 7.1 Rewrite `README.md`
Structure:
1. **Overview** — what the role does, what HAProxy object types it manages
2. **Prerequisites** — OPNsense with HAProxy plugin, Python 3 on controller, `requests` library
3. **Role Variables** — table of all variables with type, default, description
4. **Example Usage** — minimal playbook + variable block
5. **Module Parameters** — link to auto-generated docs (or table)
6. **Dependencies** — none
7. **Limitations** — SSL CA/CRL two-step workflow
8. **Contributing** — how to add new modules

### 7.2 Auto-generate module docs
Use `ansible-doc` or a simple script to generate per-module documentation from the `DOCUMENTATION` blocks. Place in `docs/modules/`.

### 7.3 Add CHANGELOG.md
Start with a v2.0.0 entry documenting all breaking changes from the refactor.

---

## Implementation Order (Recommended)

| Step | What | Effort | Risk |
|------|------|--------|------|
| 1 | `galaxy.yml` + `.ansible-lint` + Python 3 fixes | Small | Low |
| 2 | API client: error handling, type hints, unit tests | Medium | Low |
| 3 | Base module class `OpnsenseModule.py` | Medium | Medium |
| 4 | Refactor 2–3 simple modules first (lua, mapfile, errorfile) | Medium | Medium |
| 5 | Refactor remaining 11 modules | Large | Medium |
| 6 | Add DOCUMENTATION/EXAMPLES/RETURN to all modules | Medium | Low |
| 7 | `defaults/main.yml` + `tasks/main.yml` improvements | Medium | Low |
| 8 | Molecule + integration tests | Large | High |
| 9 | GitHub Actions CI | Small | Low |
| 10 | Rewrite README.md + examples | Medium | Low |

---

## Breaking Changes (for CHANGELOG)

1. **Python 3 only** — drops Python 2 support
2. **Parameter renaming** — `acl_name` → `name`, `backend_name` → `name`, etc. (old names still work with deprecation warnings)
3. **Module return value structure** — `msg` changes from `list` to `dict` with `changed`, `msg`, `diff` keys
4. **Removed global `module` variable** — internal change, no user impact
5. **`haproxy_reload` default** — stays `false`, but check mode now explicitly skips reload regardless