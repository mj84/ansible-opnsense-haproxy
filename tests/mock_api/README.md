# Mock OPNsense HAProxy API

A stand-in for the OPNsense HAProxy plugin's settings API, so the role can be
run end to end without a firewall. Nothing below the HTTP layer is mocked: the
real role, the real modules and the real `ansible-playbook` command are used.

## What it reproduces

The parts of the API that make the role's logic non-obvious:

| Behaviour | Endpoint |
| --- | --- |
| Empty-object template: every selectable field carries the full catalog of objects it can point at. The modules use it to resolve names to UUIDs. | `GET /api/haproxy/settings/get<type>/` (empty UUID) |
| Object list | `GET /api/haproxy/settings/search<type>s` |
| Object detail, with selection fields reported as `{"<option>": {"selected": "1", "value": "…"}}` — the flag is the **string** `"1"` | `GET /api/haproxy/settings/get<type>/<uuid>` |
| Create / edit / delete | `POST add<type>`, `set<type>/<uuid>`, `del<type>/<uuid>` |
| Reload, whose `result` is a plain string, not a dict | `POST /api/haproxy/service/configtest`, `…/reconfigure` |

SSL CA, CRL and certificate objects are pre-seeded (`my_ca`, `my_crl`,
`my_cert`) because they are managed outside this role.

## Manual run

```sh
pip install requests            # the modules import it, on the controller here
python tests/mock_api/server.py 8761 &

ANSIBLE_CONFIG=tests/mock_api/ansible.cfg \
ANSIBLE_ROLES_PATH=/path/to/roles \
ansible-playbook -i tests/mock_api/inventory tests/mock_api/site.yml
```

`ANSIBLE_ROLES_PATH` must contain a directory named
`local.maj.opnsense.haproxy` pointing at the repository:

```sh
mkdir -p /tmp/roles && ln -s "$PWD" /tmp/roles/local.maj.opnsense.haproxy
```

The first run reports 12 changes (one per object type); a second run reports
none. `tests/mock_api/site.yml` exposes one knob, `backend_algorithm`, so a
single change can be observed:

```sh
ansible-playbook … tests/mock_api/site.yml -e backend_algorithm=source   # 1 change
```

`tests/mock_api/absent.yml` then removes two objects by name alone.

## Automated run

`tests/e2e/test_role_against_mock_api.py` starts the mock in a thread on an
ephemeral port, builds the roles path in a temp directory, and asserts on both
the playbook recap and the mock's stored state:

```sh
pytest tests/e2e/
```
