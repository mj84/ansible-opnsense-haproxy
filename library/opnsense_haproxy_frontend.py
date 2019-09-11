#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_frontend
short_description: Manage HAProxy frontends on Opnsense
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
            frontend_state=dict(type='str', choices=['present', 'absent'], default='present'),
            frontend_enabled=dict(type='bool', default=True),
            frontend_name=dict(type='str', required=True),
            frontend_description=dict(type='str', default=''),
            frontend_bind=dict(type='list', required=True),
            frontend_bind_options=dict(type='str', default=''),
            frontend_mode=dict(type='str', choices=['http','ssl','tcp'], default='http'),
            frontend_default_backend=dict(type='str', default='none'),
            frontend_ssl_enabled=dict(type='bool', default=False),
            frontend_ssl_certificates=dict(type='list', default=[]),
            frontend_ssl_default_certificate=dict(type='str', default=''),
            frontend_ssl_custom_options=dict(type='str', default=''),
            frontend_ssl_advanced_enabled=dict(type='bool', default=False),
            frontend_ssl_bind_options=dict(type='list',
                elements='str',
                options=dict(
                    choices=[
                        'no-sslv3',
                        'no-tlsv10',
                        'no-tlsv11',
                        'no-tlsv12',
                        'no-tls-tickets',
                        'force-sslv3',
                        'force-tlsv10',
                        'force-tlsv11',
                        'force-tlsv12',
                        'strict-sni'],
                ),
                default=[]),
            frontend_ssl_cipher_list=dict(type='str', default='ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256'),
            frontend_ssl_http2_enabled=dict(type='bool', default=False),
            frontend_ssl_hsts_enabled=dict(type='bool', default=True),
            frontend_ssl_hsts_include_sub_domains=dict(type='bool', default=False),
            frontend_ssl_hsts_preload=dict(type='bool', default=False),
            frontend_ssl_hsts_max_age=dict(type='str', default='15768000'),
            frontend_ssl_client_auth_enabled=dict(type='bool', default=False),
            frontend_ssl_client_auth_verify=dict(type='str', choices=['none', 'optional', 'required'], default='none'),
            frontend_ssl_client_auth_cas=dict(type='list', default=[]),
            frontend_ssl_client_auth_crls=dict(type='list', default=[]),
            frontend_basic_auth_enabled=dict(type='bool', default=False),
            frontend_basic_auth_users=dict(type='list', default=[]),
            frontend_basic_auth_groups=dict(type='list', default=[]),
            frontend_tuning_max_connections=dict(type='str', default=''),
            frontend_tuning_timeout_client=dict(type='str', default=''),
            frontend_tuning_timeout_http_req=dict(type='str', default=''),
            frontend_tuning_timeout_http_keep_alive=dict(type='str', default=''),
            frontend_linked_cpu_affinity_rules=dict(type='list', default=[]),
            frontend_logging_dont_log_null=dict(type='bool', default=False),
            frontend_logging_dont_log_normal=dict(type='bool', default=False),
            frontend_logging_log_separate_errors=dict(type='bool', default=False),
            frontend_logging_detailed_log=dict(type='bool', default=False),
            frontend_logging_socket_stats=dict(type='bool', default=False),
            frontend_stickiness_pattern=dict(type='str', choices=['ipv4','ipv6','integer','string','binary'], default='ipv4'),
            frontend_stickiness_data_types=dict(type='list',
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
            frontend_stickiness_expire=dict(type='str', default='30m'),
            frontend_stickiness_size=dict(type='str', default='50k'),
            frontend_stickiness_counter=dict(type='bool', default=True),
            frontend_stickiness_counter_key=dict(type='str', default='src'),
            frontend_stickiness_length=dict(type='str', default=''),
            frontend_stickiness_conn_rate_period=dict(type='str', default='10s'),
            frontend_stickiness_sess_rate_period=dict(type='str', default='10s'),
            frontend_stickiness_http_req_rate_period=dict(type='str', default='10s'),
            frontend_stickiness_http_err_rate_period=dict(type='str', default='10s'),
            frontend_stickiness_bytes_in_rate_period=dict(type='str', default='1m'),
            frontend_stickiness_bytes_out_rate_period=dict(type='str', default='1m'),
            frontend_forward_for=dict(type='bool', default=False),
            frontend_connection_behaviour=dict(type='str',
                 choices=[
                    'http-keep-alive',
                    'http-tunnel',
                    'httpclose',
                    'http-server-close',
                    'forceclose'
                ],
                default='http-keep-alive'),
            frontend_custom_options=dict(type='str', default=''),
            frontend_linked_actions=dict(type='list', default=[]),
            frontend_linked_errorfiles=dict(type='list', default=[]),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of frontend
    frontend_state = module.params['frontend_state']
    frontend_enabled = str(int(module.params['frontend_enabled']))
    frontend_name = module.params['frontend_name']
    frontend_description = module.params['frontend_description']
    frontend_bind = module.params['frontend_bind']
    frontend_bind_options = module.params['frontend_bind_options']
    frontend_mode = module.params['frontend_mode']
    frontend_default_backend = module.params['frontend_default_backend']
    frontend_ssl_enabled = module.params['frontend_ssl_enabled']
    frontend_ssl_certificates = module.params['frontend_ssl_certificates']
    frontend_ssl_default_certificate = module.params['frontend_ssl_default_certificate']
    frontend_ssl_custom_options = module.params['frontend_ssl_custom_options']
    frontend_ssl_advanced_enabled = module.params['frontend_ssl_advanced_enabled']
    frontend_ssl_bind_options = module.params['frontend_ssl_bind_options']
    frontend_ssl_cipher_list = module.params['frontend_ssl_cipher_list']
    frontend_ssl_http2_enabled = module.params['frontend_ssl_http2_enabled']
    frontend_ssl_hsts_enabled = module.params['frontend_ssl_hsts_enabled']
    frontend_ssl_hsts_include_sub_domains = module.params['frontend_ssl_hsts_include_sub_domains']
    frontend_ssl_hsts_preload = module.params['frontend_ssl_hsts_preload']
    frontend_ssl_hsts_max_age = module.params['frontend_ssl_hsts_max_age']
    frontend_ssl_client_auth_enabled = module.params['frontend_ssl_client_auth_enabled']
    frontend_ssl_client_auth_verify = module.params['frontend_ssl_client_auth_verify']
    frontend_ssl_client_auth_cas = module.params['frontend_ssl_client_auth_cas']
    frontend_ssl_client_auth_crls = module.params['frontend_ssl_client_auth_crls']
    frontend_basic_auth_enabled = module.params['frontend_basic_auth_enabled']
    frontend_basic_auth_users = module.params['frontend_basic_auth_users']
    frontend_basic_auth_groups = module.params['frontend_basic_auth_groups']
    frontend_tuning_max_connections = module.params['frontend_tuning_max_connections']
    frontend_tuning_timeout_client = module.params['frontend_tuning_timeout_client']
    frontend_tuning_timeout_http_req = module.params['frontend_tuning_timeout_http_req']
    frontend_tuning_timeout_http_keep_alive = module.params['frontend_tuning_timeout_http_keep_alive']
    frontend_linked_cpu_affinity_rules = module.params['frontend_linked_cpu_affinity_rules']
    frontend_logging_dont_log_null = module.params['frontend_logging_dont_log_null']
    frontend_logging_dont_log_normal = module.params['frontend_logging_dont_log_normal']
    frontend_logging_log_separate_errors = module.params['frontend_logging_log_separate_errors']
    frontend_logging_detailed_log = module.params['frontend_logging_detailed_log']
    frontend_logging_socket_stats = module.params['frontend_logging_socket_stats']
    frontend_stickiness_pattern = module.params['frontend_stickiness_pattern']
    frontend_stickiness_data_types = module.params['frontend_stickiness_data_types']
    frontend_stickiness_expire = module.params['frontend_stickiness_expire']
    frontend_stickiness_size = module.params['frontend_stickiness_size']
    frontend_stickiness_counter = module.params['frontend_stickiness_counter']
    frontend_stickiness_counter_key = module.params['frontend_stickiness_counter_key']
    frontend_stickiness_length = module.params['frontend_stickiness_length']
    frontend_stickiness_conn_rate_period = module.params['frontend_stickiness_conn_rate_period']
    frontend_stickiness_sess_rate_period = module.params['frontend_stickiness_sess_rate_period']
    frontend_stickiness_http_req_rate_period = module.params['frontend_stickiness_http_req_rate_period']
    frontend_stickiness_http_err_rate_period = module.params['frontend_stickiness_http_err_rate_period']
    frontend_stickiness_bytes_in_rate_period = module.params['frontend_stickiness_bytes_in_rate_period']
    frontend_stickiness_bytes_out_rate_period = module.params['frontend_stickiness_bytes_out_rate_period']
    frontend_forward_for = module.params['frontend_forward_for']
    frontend_connection_behaviour = module.params['frontend_connection_behaviour']
    frontend_custom_options = module.params['frontend_custom_options']
    frontend_linked_actions = module.params['frontend_linked_actions']
    frontend_linked_errorfiles = module.params['frontend_linked_errorfiles']

    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of frontends
    frontends = apiconnection.listObjects('frontend')

    # Need to get UUIDs for:
    # defaultBackend, basicAuthUsers, basicAuthGroups, linkedCpuAffinityRules, linkedActions, linkedErrorfiles
    frontend_default_backend_uuid = ''
    if frontend_default_backend != 'none':
        frontend_default_backend_uuid = apiconnection.getUuidByName('backend', frontend_default_backend)
    frontend_basic_auth_users_uuids = apiconnection.getUuidsFromNames('user', frontend_basic_auth_users)
    frontend_basic_auth_groups_uuids = apiconnection.getUuidsFromNames('group', frontend_basic_auth_groups)
    frontend_linked_cpu_affinity_rules_uuids = apiconnection.getUuidsFromNames('cpu', frontend_linked_cpu_affinity_rules)
    frontend_linked_actions_uuids = apiconnection.getUuidsFromNames('action', frontend_linked_actions)
    frontend_linked_errorfiles_uuids = apiconnection.getUuidsFromNames('errorfile', frontend_linked_errorfiles)
    # Get an empty default object to retrieve UUIDs for:
    # ssl_certificates, ssl_default_certificate, ssl_clientAuthCAs, ssl_clientAuthCRLs
    empty_frontend = apiconnection.getObjectByUuid('frontend', '')
    frontend_ssl_certificates_uuids = apiconnection.getSslObjectKeys(empty_frontend['ssl_certificates'], frontend_ssl_certificates)
    # Only fetch default SSL cert uuid when one is set, otherwise supply an empty string
    frontend_ssl_default_certificate_uuid = ''
    if frontend_ssl_default_certificate != '':
        frontend_ssl_default_certificate_uuid = apiconnection.getSslObjectKeys(empty_frontend['ssl_default_certificate'], [frontend_ssl_default_certificate])[0]
    frontend_ssl_client_auth_cas_uuids = apiconnection.getSslObjectKeys(empty_frontend['ssl_clientAuthCAs'], frontend_ssl_client_auth_cas)
    frontend_ssl_client_auth_crls_uuids = apiconnection.getSslObjectKeys(empty_frontend['ssl_clientAuthCRLs'], frontend_ssl_client_auth_crls)
    # Build dict with desired state
    desired_properties = {
        'enabled': frontend_enabled,
        'description': frontend_description,
        'bind': ','.join(frontend_bind),
        'bindOptions': frontend_bind_options,
        'mode': frontend_mode,
        'defaultBackend': frontend_default_backend_uuid,
        'ssl_enabled': str(int(frontend_ssl_enabled)),
        'ssl_certificates': ','.join(frontend_ssl_certificates_uuids),
        'ssl_default_certificate': frontend_ssl_default_certificate_uuid,
        'ssl_customOptions': frontend_ssl_custom_options,
        'ssl_advancedEnabled': str(int(frontend_ssl_advanced_enabled)),
        'ssl_bindOptions': ','.join(frontend_ssl_bind_options),
        'ssl_cipherList': frontend_ssl_cipher_list,
        'ssl_http2Enabled': str(int(frontend_ssl_http2_enabled)),
        'ssl_hstsEnabled': str(int(frontend_ssl_hsts_enabled)),
        'ssl_hstsIncludeSubDomains': str(int(frontend_ssl_hsts_include_sub_domains)),
        'ssl_hstsPreload': str(int(frontend_ssl_hsts_preload)),
        'ssl_hstsMaxAge': frontend_ssl_hsts_max_age,
        'ssl_clientAuthEnabled': str(int(frontend_ssl_client_auth_enabled)),
        'ssl_clientAuthVerify': frontend_ssl_client_auth_verify,
        'ssl_clientAuthCAs': ','.join(frontend_ssl_client_auth_cas_uuids),
        'ssl_clientAuthCRLs': ','.join(frontend_ssl_client_auth_crls_uuids),
        'basicAuthEnabled': str(int(frontend_basic_auth_enabled)),
        'basicAuthUsers': ','.join(frontend_basic_auth_users_uuids),
        'basicAuthGroups': ','.join(frontend_basic_auth_groups_uuids),
        'tuning_maxConnections': frontend_tuning_max_connections,
        'tuning_timeoutClient': frontend_tuning_timeout_client,
        'tuning_timeoutHttpReq': frontend_tuning_timeout_http_req,
        'tuning_timeoutHttpKeepAlive': frontend_tuning_timeout_http_keep_alive,
        'linkedCpuAffinityRules': ','.join(frontend_linked_cpu_affinity_rules_uuids),
        'logging_dontLogNull': str(int(frontend_logging_dont_log_null)),
        'logging_dontLogNormal': str(int(frontend_logging_dont_log_normal)),
        'logging_logSeparateErrors': str(int(frontend_logging_log_separate_errors)),
        'logging_detailedLog': str(int(frontend_logging_detailed_log)),
        'logging_socketStats': str(int(frontend_logging_socket_stats)),
        'stickiness_pattern': frontend_stickiness_pattern,
        'stickiness_dataTypes': ','.join(frontend_stickiness_data_types),
        'stickiness_expire': frontend_stickiness_expire,
        'stickiness_size': frontend_stickiness_size,
        'stickiness_counter': str(int(frontend_stickiness_counter)),
        'stickiness_counter_key': frontend_stickiness_counter_key,
        'stickiness_length': frontend_stickiness_length,
        'stickiness_connRatePeriod': frontend_stickiness_conn_rate_period,
        'stickiness_sessRatePeriod': frontend_stickiness_sess_rate_period,
        'stickiness_httpReqRatePeriod': frontend_stickiness_http_req_rate_period,
        'stickiness_httpErrRatePeriod': frontend_stickiness_http_err_rate_period,
        'stickiness_bytesInRatePeriod': frontend_stickiness_bytes_in_rate_period,
        'stickiness_bytesOutRatePeriod': frontend_stickiness_bytes_out_rate_period,
        'forwardFor': str(int(frontend_forward_for)),
        'connectionBehaviour': frontend_connection_behaviour,
        'customOptions': frontend_custom_options,
        'linkedActions': ','.join(frontend_linked_actions_uuids),
        'linkedErrorfiles': ','.join(frontend_linked_errorfiles_uuids)
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if frontend object with specified name exists
    for frontend in frontends:
        if frontend['name'] == frontend_name:
            uuid = frontend['uuid']
            break
    frontend_exists = (uuid != '')
    if frontend_state == 'present':
        if frontend_exists:
            frontend = apiconnection.getObjectByName('frontend', frontend_name)
            for prop in desired_properties.keys():
                # Special cases for complex propertierts:
                if prop == 'bind':
                    current_binds = apiconnection.getSelectedList(frontend[prop])
                    if not apiconnection.compareLists(frontend_bind, frontend[prop]):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Property %s must be changed' % prop)
                elif prop == 'mode':
                    current_mode = apiconnection.getSelected(frontend[prop])
                    if current_mode != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Property %s must be changed' % prop)
                elif prop == 'defaultBackend':
                    current_default_backend = apiconnection.getSelected(frontend[prop],retval='value')
                    if current_default_backend != frontend_default_backend:
                        # Check if current default backend is an empty string and we don't want to have one:
                        if current_default_backend == '' and frontend_default_backend == 'none':
                            pass
                        else:
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_default_backend, desired_properties[prop]))
                elif prop == 'ssl_certificates' and frontend_ssl_enabled:
                    current_ssl_certificates = apiconnection.getSelectedList(frontend[prop], retval='key')
                    if not apiconnection.compareLists(current_ssl_certificates, frontend_ssl_certificates_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Property %s must be changed' % prop)
                elif prop == 'ssl_default_certificate' and frontend_ssl_enabled:
                    current_ssl_default_certificate = apiconnection.getSelected(frontend[prop])
                    if current_ssl_default_certificate != desired_properties[prop]:
                        # Check if current default certificate is an empty string and we don't want to have one:
                        #if current_ssl_default_certificate == '' and frontend_ssl_default_certificate == 'none':
                        #    pass
                        #else:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_ssl_default_certificate, desired_properties[prop]))
                elif prop == 'ssl_bindOptions' and frontend_ssl_enabled:
                    current_ssl_bind_options = apiconnection.getSelectedList(frontend[prop])
                    if not apiconnection.compareLists(current_ssl_bind_options, frontend_ssl_bind_options):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_ssl_bind_options, desired_properties[prop]))
                # only care about ssl_clientAuthVerify when SSL client auth is enabled
                elif prop == 'ssl_clientAuthVerify' and frontend_ssl_enabled:
                    if not frontend_ssl_client_auth_enabled:
                        pass
                    else:
                        current_ssl_client_auth_verify = apiconnection.getSelected(frontend[prop])
                        if current_ssl_client_auth_verify != desired_properties[prop]:
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_ssl_client_auth_verify, desired_properties[prop]))
                # only care about ssl_clientAuthVerify when SSL client auth is enabled
                elif prop == 'ssl_clientAuthCAs' and frontend_ssl_enabled:
                    if not frontend_ssl_client_auth_enabled:
                        pass
                    else:
                        current_ssl_client_auth_cas = apiconnection.getSelectedList(frontend[prop])
                        if not apiconnection.compareLists(current_ssl_client_auth_cas, frontend_ssl_client_auth_cas_uuids):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_ssl_client_auth_cas, desired_properties[prop]))
                # only care about ssl_clientAuthVerify when SSL client auth is enabled
                elif prop == 'ssl_clientAuthCRLs' and frontend_ssl_enabled:
                    if not frontend_ssl_client_auth_enabled:
                        pass
                    else:
                        current_ssl_client_auth_crls = apiconnection.getSelectedList(frontend[prop])
                        if not apiconnection.compareLists(current_ssl_client_auth_crls, frontend_ssl_client_auth_crls_uuids):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_ssl_client_auth_crls, desired_properties[prop]))
                elif prop == 'basicAuthUsers':
                    # only care about basicAuthUsers when basic auth is enabled
                    if frontend_basic_auth_enabled:
                        current_basic_auth_users = apiconnection.getSelectedList(frontend[prop])
                        if not apiconnection.compareLists(current_basic_auth_users, frontend_basic_auth_users):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_basic_auth_users, desired_properties[prop]))
                elif prop == 'basicAuthGroups':
                    # only care about basicAuthGroups when basic auth is enabled
                    if frontend_basic_auth_enabled:
                        current_basic_auth_groups = apiconnection.getSelectedList(frontend[prop])
                        if not apiconnection.compareLists(current_basic_auth_groups, frontend_basic_auth_groups):
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, current_basic_auth_groups, desired_properties[prop]))
                elif prop == 'stickiness_pattern':
                    current_stickiness_pattern = apiconnection.getSelected(frontend[prop])
                    if current_stickiness_pattern != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_stickiness_pattern, desired_properties[prop]))
                elif prop == 'stickiness_dataTypes':
                    current_stickiness_data_types = apiconnection.getSelected(frontend[prop])
                    if not apiconnection.compareLists(current_stickiness_data_types, frontend_stickiness_data_types):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_stickiness_data_types, desired_properties[prop]))
                    pass
                elif prop == 'connectionBehaviour':
                    current_connection_behaviour = apiconnection.getSelected(frontend[prop])
                    if current_connection_behaviour != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_connection_behaviour, desired_properties[prop]))
                elif prop == 'linkedCpuAffinityRules':
                    current_linked_cpu_affinity_rules = apiconnection.getSelectedList(frontend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_cpu_affinity_rules, frontend_linked_cpu_affinity_rules):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_cpu_affinity_rules, desired_properties[prop]))
                elif prop == 'linkedActions':
                    current_linked_actions = apiconnection.getSelectedList(frontend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_actions, frontend_linked_actions_uuids, order_sensitive=True):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_actions, desired_properties[prop]))
                elif prop == 'linkedErrorfiles':
                    current_linked_errorfiles = apiconnection.getSelectedList(frontend[prop], retval='key')
                    if not apiconnection.compareLists(current_linked_errorfiles, frontend_linked_errorfiles_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_linked_errorfiles, desired_properties[prop]))
                else:
                    # only care about SSL properties when it should be enabled
                    if 'ssl' in prop and not frontend_ssl_enabled:
                        # SSL enabled must still be evaluated
                        if prop == 'ssl_enabled' and frontend[prop] != desired_properties[prop]:
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, frontend[prop], desired_properties[prop]))
                        else:
                            pass
                    elif 'ssl' in prop and frontend_ssl_enabled:
                        # Some properties are only stored when enabling advanced SSL options
                        if not frontend_ssl_advanced_enabled and prop == 'ssl_bindOptions':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_cipherList':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_http2Enabled':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_hstsEnabled':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_hstsIncludeSubdomains':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_hstsPreload':
                            pass
                        elif not frontend_ssl_advanced_enabled and prop == 'ssl_hstsMaxAge':
                            pass
                        else:
                            if prop not in frontend:
                                # prop might not be present in current state
                                needs_change = True
                                changed_properties[prop] = desired_properties[prop]
                                additional_msg.append('Changing %s: %s => %s' %(prop, '', desired_properties[prop]))
                            else:
                                if frontend[prop] != desired_properties[prop]:
                                    needs_change = True
                                    changed_properties[prop] = desired_properties[prop]
                                    additional_msg.append('Changing %s: %s => %s' %(prop, frontend[prop], desired_properties[prop]))
                    # catch all other properties
                    else:
                        if frontend[prop] != desired_properties[prop]:
                            needs_change = True
                            changed_properties[prop] = desired_properties[prop]
                            additional_msg.append('Changing %s: %s => %s' %(prop, frontend[prop], desired_properties[prop]))

            if not needs_change:
                result = {'changed': False, 'msg': ['Frontend already present: %s' %frontend_name, additional_msg]}
            else:
                if not module.check_mode:
                    # workaround for https://github.com/opnsense/plugins/issues/1494
                    # any change must include the linkedActions to maintain the correct order
                    changed_properties['linkedActions'] = desired_properties['linkedActions']
                    additional_msg.append(apiconnection.updateObject('frontend', frontend_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Frontend %s must be changed.' %frontend_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('frontend', frontend_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Frontend %s must be created.' %frontend_name, additional_msg]}
    else:
        if frontend_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('frontend', frontend_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Frontend %s must be deleted.' %frontend_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Frontend %s is not present.' %frontend_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
