"""End-to-end: the real role, through ansible-playbook, against the mock API.

These tests cover what the unit tests cannot: that the per-object data in the
``opnsense_haproxy_*`` dicts actually reaches the modules, that reference names
are stored as the UUIDs the API expects, and that a second run changes nothing.
"""

import pytest

# One task per object type; every type has at least one object in site.yml.
TYPES_IN_FIXTURE = 12


def test_first_run_creates_every_object_type(mock_api, run_playbook):
    run = run_playbook('site.yml', mock_api)
    run.assert_ran()
    assert run.changed == TYPES_IN_FIXTURE, run.output

    for otype, name in [
        ('acl', 'api_path'),
        ('cpu', 'haproxy_cpu0'),
        ('errorfile', 'custom_503'),
        ('mapfile', 'redirect_map'),
        ('healthcheck', 'http_check'),
        ('lua', 'my_script'),
        ('server', 'web1'),
        ('user', 'admin'),
        ('group', 'admins'),
        ('backend', 'api_pool'),
        ('action', 'api_redirect'),
        ('frontend', 'web_http'),
    ]:
        assert mock_api.by_name(otype, name) is not None, '%s/%s missing' % (otype, name)


def test_object_parameters_reach_the_module(mock_api, run_playbook):
    """The dict values, not just the dict keys, must arrive at the API."""
    run_playbook('site.yml', mock_api).assert_ran()

    assert mock_api.by_name('acl', 'api_path')['value'] == '/api'
    assert mock_api.by_name('acl', 'api_path')['expression'] == 'path_beg'
    assert mock_api.by_name('acl', 'api_path')['description'] == 'API path'
    assert mock_api.by_name('server', 'web1')['address'] == '10.0.0.1'
    assert mock_api.by_name('backend', 'api_pool')['algorithm'] == 'roundrobin'
    assert mock_api.by_name('frontend', 'web_http')['bind'] == '*:80'
    assert mock_api.by_name('healthcheck', 'http_check')['http_uri'] == '/health'
    assert mock_api.by_name('errorfile', 'custom_503')['code'] == '503'
    assert mock_api.by_name('user', 'admin')['password'] == 's3cret'


def test_references_are_stored_as_uuids(mock_api, run_playbook):
    """Names in the role variables resolve to the API's own UUIDs."""
    run_playbook('site.yml', mock_api).assert_ran()

    assert mock_api.by_name('backend', 'api_pool')['linkedServers'] == mock_api.uuid_of('server', 'web1')
    assert mock_api.by_name('backend', 'api_pool')['healthCheck'] == mock_api.uuid_of('healthcheck', 'http_check')
    assert mock_api.by_name('backend', 'api_pool')['basicAuthUsers'] == mock_api.uuid_of('user', 'admin')
    assert mock_api.by_name('backend', 'api_pool')['basicAuthGroups'] == mock_api.uuid_of('group', 'admins')
    assert mock_api.by_name('group', 'admins')['members'] == mock_api.uuid_of('user', 'admin')
    assert mock_api.by_name('action', 'api_redirect')['linkedAcls'] == mock_api.uuid_of('acl', 'api_path')
    assert mock_api.by_name('action', 'api_redirect')['use_backend'] == mock_api.uuid_of('backend', 'api_pool')
    assert mock_api.by_name('frontend', 'web_http')['defaultBackend'] == mock_api.uuid_of('backend', 'api_pool')
    assert mock_api.by_name('frontend', 'web_http')['linkedActions'] == mock_api.uuid_of('action', 'api_redirect')


def test_ssl_references_resolve_when_creating_a_server(mock_api, run_playbook):
    """SSL objects are pre-existing on the firewall; the role points at them."""
    run_playbook('site.yml', mock_api).assert_ran()

    server = mock_api.by_name('server', 'web_tls')
    assert server['ssl'] == '1'
    assert server['sslCA'] == 'ca-001'
    assert server['sslCRL'] == 'crl-001'
    assert server['sslClientCertificate'] == 'cert-001'

    frontend = mock_api.by_name('frontend', 'web_https')
    assert frontend['ssl_enabled'] == '1'
    assert frontend['ssl_certificates'] == 'cert-001'
    assert frontend['ssl_clientAuthCAs'] == 'ca-001'
    assert frontend['ssl_clientAuthCRLs'] == 'crl-001'


def test_second_run_changes_nothing(mock_api, run_playbook):
    first = run_playbook('site.yml', mock_api)
    first.assert_ran()
    assert first.changed == TYPES_IN_FIXTURE, first.output

    second = run_playbook('site.yml', mock_api)
    second.assert_ran()
    assert second.changed == 0, second.output


def test_one_changed_value_is_detected_and_converges(mock_api, run_playbook):
    run_playbook('site.yml', mock_api).assert_ran()

    run = run_playbook('site.yml', mock_api, extra_vars={'backend_algorithm': 'source'})
    run.assert_ran()
    assert run.changed == 1, run.output
    assert mock_api.by_name('backend', 'api_pool')['algorithm'] == 'source'

    again = run_playbook('site.yml', mock_api, extra_vars={'backend_algorithm': 'source'})
    again.assert_ran()
    assert again.changed == 0, again.output


def test_absent_needs_only_the_name(mock_api, run_playbook):
    run_playbook('site.yml', mock_api).assert_ran()
    assert mock_api.uuid_of('acl', 'api_path') is not None

    run = run_playbook('absent.yml', mock_api)
    run.assert_ran()
    # Two objects exist; the third is already gone and must not report a change.
    assert run.changed == 2, run.output

    assert mock_api.by_name('acl', 'api_path') is None
    assert mock_api.by_name('server', 'web1') is None
    assert mock_api.by_name('server', 'web_tls') is not None


def test_check_mode_reports_without_writing(mock_api, run_playbook):
    run = run_playbook('site.yml', mock_api, check=True)
    run.assert_ran()
    assert run.changed == TYPES_IN_FIXTURE, run.output
    assert mock_api.objects('acl') == {}
    assert mock_api.objects('frontend') == {}


def test_reload_runs_configtest_then_reconfigure(mock_api, run_playbook):
    """site.yml sets opnsense_haproxy_reload: true."""
    run_playbook('site.yml', mock_api).assert_ran()

    posts = mock_api.paths('POST')
    assert '/api/haproxy/service/configtest' in posts
    assert '/api/haproxy/service/reconfigure' in posts
    assert posts.index('/api/haproxy/service/configtest') < posts.index('/api/haproxy/service/reconfigure')


def test_no_reload_without_the_flag(mock_api, run_playbook):
    """absent.yml does not set haproxy_reload, so the service is left alone."""
    run_playbook('site.yml', mock_api).assert_ran()
    before = len(mock_api.paths('POST'))

    run = run_playbook('absent.yml', mock_api)
    run.assert_ran()
    reload_calls = [p for p in mock_api.paths('POST')[before:] if '/service/' in p]
    assert reload_calls == []


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(pytest.main([__file__, '-v']))
