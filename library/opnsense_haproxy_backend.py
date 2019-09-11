#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_backend
short_description: Manage HAProxy backends on Opnsense
'''

from ansible.module_utils.opnsense_utils import OpnsenseApi

from ansible.module_utils.basic import AnsibleModule

# There will only be a single AnsibleModule object per module
module = None


def main():

    global module
    # Instantiate module
    module = AnsibleModule(
        argument_spec=dict(
            api_url=dict(type='str', required=True),
            api_key=dict(type='str', required=True, no_log=True),
            api_secret=dict(type='str', required=True, no_log=True),
            api_ssl_verify=dict(type='bool', default=False),
            backend_state=dict(type='str', choices=['present', 'absent'], default='present'),
            backend_enabled=dict(type='bool', default=True),
            backend_name=dict(type='str', required=True),
            backend_description=dict(type='str', default=''),
            backend_mode=dict(type='str', choices=['http', 'tcp'], default='http'),
            backend_algorithm=dict(type='str', choices=['source', 'roundrobin', 'static-rr', 'leastconn', 'uri'], default='source'),
            backend_proxy_protocol=dict(type='str', choices=['', 'v1', 'v2'], default=''),
            backend_linked_servers=dict(type='list', default=[]),
            backend_source=dict(type='str', default=''),
            backend_health_check_enabled=dict(type='bool', default=True),
            backend_health_check=dict(type='str', default=''),
            backend_health_check_log_status=dict(type='bool', default=False),
            backend_check_interval=dict(type='str', default=''),
            backend_check_down_interval=dict(type='str', default=''),
            backend_health_check_fall=dict(type='str', default=''),
            backend_health_check_rise=dict(type='str', default=''),
            backend_persistence=dict(type='str', choices=['', 'sticktable', 'cookie'], default='sticktable'),
            backend_persistence_cookie_mode=dict(type='str', choices=['piggyback', 'new'], default='piggyback'),
            backend_persistence_cookie_name=dict(type='str', default='SRVCOOKIE'),
            backend_persistence_strip_quotes=dict(type='bool', default=True),
            backend_stickiness_pattern=dict(type='str', choices=['', 'sourceipv4', 'sourceipv6', 'cookievalue', 'rdpcookie'], default='sourceipv4'),
            backend_stickiness_data_types=dict(type='list',
                elements='str',
                options=dict(
                    choices=[
                        'conn_cnt',
                        'conn_cur',
                        'conn_rate',
                        'sess_cnt',
                        'sess_rate',
                        'http_req_cnt',
                        'http_req_rate',
                        'http_err_cnt',
                        'http_err_rate',
                        'bytes_in_cnt',
                        'bytes_in_rate',
                        'bytes_out_cnt',
                        'bytes_out_rate'],
                ),
                default=[]),
            backend_stickiness_expire=dict(type='str', default='30m'),
            backend_stickiness_size=dict(type='str', default='50k'),
            backend_stickiness_cookie_name=dict(type='str', default=''),
            backend_stickiness_cookie_length=dict(type='str', default=''),
            backend_stickiness_conn_rate_period=dict(type='str', default='10s'),
            backend_stickiness_sess_rate_period=dict(type='str', default='10s'),
            backend_stickiness_http_req_rate_period=dict(type='str', default='10s'),
            backend_stickiness_http_err_rate_period=dict(type='str', default='10s'),
            backend_stickiness_bytes_in_rate_period=dict(type='str', default='1m'),
            backend_stickiness_bytes_out_rate_period=dict(type='str', default='1m'),
            backend_basic_auth_enabled=dict(type='bool', default=False),
            backend_basic_auth_users=dict(type='list', default=[]),
            backend_basic_auth_groups=dict(type='list', default=[]),
            backend_tuning_timeout_connect=dict(type='str', default=''),
            backend_tuning_timeout_check=dict(type='str', default=''),
            backend_tuning_timeout_server=dict(type='str', default=''),
            backend_tuning_retries=dict(type='str', default=''),
            backend_custom_options=dict(type='str', default=''),
            backend_tuning_default_server=dict(type='str', default=''),
            backend_tuning_no_port=dict(type='bool', default=False),
            backend_tuning_http_reuse=dict(type='str', choices=['', 'never', 'safe', 'aggressive', 'always'], default='never'),
            backend_linked_actions=dict(type='list', default=[]),
            backend_linked_errorfiles=dict(type='list', default=[]),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of backend
    backend_state = module.params['backend_state']
    backend_enabled = str(int(module.params['backend_enabled']))
    backend_name = module.params['backend_name']
    backend_description = module.params['backend_description']
    backend_mode = module.params['backend_mode']
    backend_algorithm = module.params['backend_algorithm']
    backend_proxy_protocol = module.params['backend_proxy_protocol']
    backend_linked_servers = module.params['backend_linked_servers']
    backend_source = module.params['backend_source']
    backend_health_check_enabled = module.params['backend_health_check_enabled']
    backend_health_check = module.params['backend_health_check']
    backend_health_check_log_status = module.params['backend_health_check_log_status']
    backend_check_interval = module.params['backend_check_interval']
    backend_check_down_interval = module.params['backend_check_down_interval']
    backend_health_check_fall = module.params['backend_health_check_fall']
    backend_health_check_rise = module.params['backend_health_check_rise']
    backend_persistence = module.params['backend_persistence']
    backend_persistence_cookie_mode = module.params['backend_persistence_cookie_mode']
    backend_persistence_cookie_name = module.params['backend_persistence_cookie_name']
    backend_persistence_strip_quotes = module.params['backend_persistence_strip_quotes']
    backend_stickiness_pattern = module.params['backend_stickiness_pattern']
    backend_stickiness_data_types = module.params['backend_stickiness_data_types']
    backend_stickiness_expire = module.params['backend_stickiness_expire']
    backend_stickiness_size = module.params['backend_stickiness_size']
    backend_stickiness_cookie_name = module.params['backend_stickiness_cookie_name']
    backend_stickiness_cookie_length = module.params['backend_stickiness_cookie_length']
    backend_stickiness_conn_rate_period = module.params['backend_stickiness_conn_rate_period']
    backend_stickiness_sess_rate_period = module.params['backend_stickiness_sess_rate_period']
    backend_stickiness_http_req_rate_period = module.params['backend_stickiness_http_req_rate_period']
    backend_stickiness_http_err_rate_period = module.params['backend_stickiness_http_err_rate_period']
    backend_stickiness_bytes_in_rate_period = module.params['backend_stickiness_bytes_in_rate_period']
    backend_stickiness_bytes_out_rate_period = module.params['backend_stickiness_bytes_out_rate_period']
    backend_basic_auth_enabled = module.params['backend_basic_auth_enabled']
    backend_basic_auth_users = module.params['backend_basic_auth_users']
    backend_basic_auth_groups = module.params['backend_basic_auth_groups']
    backend_tuning_timeout_connect = module.params['backend_tuning_timeout_connect']
    backend_tuning_timeout_check = module.params['backend_tuning_timeout_check']
    backend_tuning_timeout_server = module.params['backend_tuning_timeout_server']
    backend_tuning_retries = module.params['backend_tuning_retries']
    backend_custom_options = module.params['backend_custom_options']
    backend_tuning_default_server = module.params['backend_tuning_default_server']
    backend_tuning_no_port = module.params['backend_tuning_no_port']
    backend_tuning_http_reuse = module.params['backend_tuning_http_reuse']
    backend_linked_actions = module.params['backend_linked_actions']
    backend_linked_errorfiles = module.params['backend_linked_errorfiles']

    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of backends
    backends = apiconnection.listObjects('backend')

    # Need to get UUIDs for:
    # linkedServers, healthCheck, basicAuthUsers, basicAuthGroups, linkedActions, linkedErrorfiles
    backend_linked_servers_uuids = apiconnection.getUuidsFromNames('server', backend_linked_servers)
    backend_health_check_uuid = ''
    if backend_health_check != '':
        backend_health_check_uuid = apiconnection.getUuidByName('healthcheck', backend_health_check)
    backend_basic_auth_users_uuids = apiconnection.getUuidsFromNames('user', backend_basic_auth_users)
    backend_basic_auth_groups_uuids = apiconnection.getUuidsFromNames('group', backend_basic_auth_groups)
    backend_linked_actions_uuids = apiconnection.getUuidsFromNames('action', backend_linked_actions)
    backend_linked_errorfiles_uuids = apiconnection.getUuidsFromNames('errorfile', backend_linked_errorfiles)
    # Build dict with desired state
    desired_properties = {
        'enabled': backend_enabled,
        'description': backend_description,
        'mode': backend_mode,
        'algorithm': backend_algorithm,
        'proxyProtocol': backend_proxy_protocol,
        'linkedServers': ','.join(backend_linked_servers_uuids),
        'source': backend_source,
        'healthCheckEnabled': str(int(backend_health_check_enabled)),
        'healthCheck': backend_health_check_uuid,
        'healthCheckLogStatus': str(int(backend_health_check_log_status)),
        'checkInterval': backend_check_interval,
        'checkDownInterval': backend_check_down_interval,
        'healthCheckFall': backend_health_check_fall,
        'healthCheckRise': backend_health_check_rise,
        'persistence': backend_persistence,
        'persistence_cookiemode': backend_persistence_cookie_mode,
        'persistence_cookiename': backend_persistence_cookie_name,
        'persistence_stripquotes': str(int(backend_persistence_strip_quotes)),
        'stickiness_pattern': backend_stickiness_pattern,
        'stickiness_dataTypes': ','.join(backend_stickiness_data_types),
        'stickiness_expire': backend_stickiness_expire,
        'stickiness_size': backend_stickiness_size,
        'stickiness_cookiename': backend_stickiness_cookie_name,
        'stickiness_cookielength': backend_stickiness_cookie_length,
        'stickiness_connRatePeriod': backend_stickiness_conn_rate_period,
        'stickiness_sessRatePeriod': backend_stickiness_sess_rate_period,
        'stickiness_httpReqRatePeriod': backend_stickiness_http_req_rate_period,
        'stickiness_httpErrRatePeriod': backend_stickiness_http_err_rate_period,
        'stickiness_bytesInRatePeriod': backend_stickiness_bytes_in_rate_period,
        'stickiness_bytesOutRatePeriod': backend_stickiness_bytes_out_rate_period,
        'basicAuthEnabled': str(int(backend_basic_auth_enabled)),
        'basicAuthUsers': ','.join(backend_basic_auth_users_uuids),
        'basicAuthGroups': ','.join(backend_basic_auth_groups_uuids),
        'tuning_timeoutConnect': backend_tuning_timeout_connect,
        'tuning_timeoutCheck': backend_tuning_timeout_check,
        'tuning_timeoutServer': backend_tuning_timeout_server,
        'tuning_retries': backend_tuning_retries,
        'customOptions': backend_custom_options,
        'tuning_defaultserver': backend_tuning_default_server,
        'tuning_noport': str(int(backend_tuning_no_port)),
        'tuning_httpreuse': backend_tuning_http_reuse,
        'linkedActions': ','.join(backend_linked_actions_uuids),
        'linkedErrorfiles': ','.join(backend_linked_errorfiles_uuids)
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if backend object with specified name exists
    for backend in backends:
        if backend['name'] == backend_name:
            uuid = backend['uuid']
            break
    backend_exists = (uuid != '')
    if backend_state == 'present':
        if backend_exists:
            backend = apiconnection.getObjectByName('backend', backend_name)
            for prop in desired_properties.keys():
                # Special cases for complex propertierts:
                if prop == 'mode':
                    current_mode = apiconnection.getSelected(backend[prop])
                    if current_mode != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_mode, desired_properties[prop]))
                elif prop == 'algorithm':
                    current_algorithm = apiconnection.getSelected(backend[prop])
                    if current_algorithm != backend_algorithm:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_algorithm, desired_properties[prop]))
                elif prop == 'proxyProtocol':
                    current_proxy_protocol = apiconnection.getSelected(backend[prop])
                    if current_proxy_protocol != backend_proxy_protocol:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_proxy_protocol, desired_properties[prop]))
                elif prop == 'linkedServers':
                    current_linked_servers = apiconnection.getSelectedList(backend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_servers, backend_linked_servers_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_servers, desired_properties[prop]))
                elif prop == 'healthCheck':
                    current_health_check = apiconnection.getSelected(backend[prop], retval='value')
                    if current_health_check != backend_health_check:
                        if current_health_check == 'none' and backend_health_check == '':
                            pass
                        else:
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_health_check, desired_properties[prop]))
                elif prop == 'persistence':
                    current_persistence = apiconnection.getSelected(backend[prop], retval='key')
                    if current_persistence != backend_persistence:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_persistence, desired_properties[prop]))
                elif prop == 'persistence_cookiemode':
                    current_persistence_cookie_mode = apiconnection.getSelected(backend[prop], retval='key')
                    if current_persistence_cookie_mode != backend_persistence_cookie_mode:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_persistence_cookie_mode, desired_properties[prop]))
                elif prop == 'stickiness_pattern':
                    current_stickiness_pattern = apiconnection.getSelected(backend[prop])
                    if current_stickiness_pattern != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_stickiness_pattern, desired_properties[prop]))
                elif prop == 'stickiness_dataTypes':
                    current_stickiness_data_types = apiconnection.getSelected(backend[prop])
                    if not apiconnection.compareLists(current_stickiness_data_types, backend_stickiness_data_types):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_stickiness_data_types, desired_properties[prop]))
                elif prop == 'basicAuthUsers':
                    # only care about basicAuthUsers when basic auth is enabled
                    if backend_basic_auth_enabled:
                        current_basic_auth_users = apiconnection.getSelectedList(backend[prop])
                        if not apiconnection.compareLists(current_basic_auth_users, backend_basic_auth_users):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_basic_auth_users, desired_properties[prop]))
                elif prop == 'basicAuthGroups':
                    # only care about basicAuthGroups when basic auth is enabled
                    if backend_basic_auth_enabled:
                        current_basic_auth_groups = apiconnection.getSelectedList(backend[prop])
                        if not apiconnection.compareLists(current_basic_auth_groups, backend_basic_auth_groups):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_basic_auth_groups, desired_properties[prop]))
                elif prop == 'tuning_httpreuse':
                    current_tuning_httpreuse = apiconnection.getSelected(backend[prop])
                    if current_tuning_httpreuse != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_tuning_httpreuse, desired_properties[prop]))
                elif prop == 'linkedActions':
                    current_linked_actions = apiconnection.getSelectedList(backend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_actions, backend_linked_actions_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_actions, desired_properties[prop]))
                elif prop == 'linkedErrorfiles':
                    current_linked_errorfiles = apiconnection.getSelectedList(backend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_errorfiles, backend_linked_errorfiles_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_errorfiles, desired_properties[prop]))
                else:
                    # catch all other properties
                    if backend[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, backend[prop], desired_properties[prop]))

            if not needs_change:
                result = {'changed': False, 'msg': ['Backend already present: %s' %backend_name, additional_msg]}
            else:
                if not module.check_mode:
                    # workaround for https://github.com/opnsense/plugins/issues/1494
                    # any change must include the linkedActions to maintain the correct order
                    changed_properties['linkedActions'] = desired_properties['linkedActions']
                    additional_msg.append(apiconnection.updateObject('backend', backend_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Backend %s must be changed.' %backend_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('backend', backend_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Backend %s must be created.' %backend_name, additional_msg]}
    else:
        if backend_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('backend', backend_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Backend %s must be deleted.' %backend_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Backend %s is not present.' %backend_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
