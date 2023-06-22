#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_acl
short_description: Manage HAProxy acls on Opnsense
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
            acl_state=dict(type='str', choices=['present', 'absent'], default='present'),
            acl_name=dict(type='str', required=True),
            acl_description=dict(type='str', default=''),
            acl_expression=dict(type='str',
                choices=[
                    'http_auth',
                    'hdr_beg',
                    'hdr_end',
                    'hdr',
                    'hdr_reg',
                    'hdr_sub',
                    'path_beg',
                    'path_end',
                    'path',
                    'path_reg',
                    'path_dir',
                    'path_sub',
                    'url_param',
                    'ssl_c_verify',
                    'ssl_c_verify_code',
                    'ssl_c_ca_commonname',
                    'src',
                    'src_is_local',
                    'src_port',
                    'src_bytes_in_rate',
                    'src_bytes_out_rate',
                    'src_kbytes_in',
                    'src_kbytes_out',
                    'src_conn_cnt',
                    'src_conn_cur',
                    'src_conn_rate',
                    'src_http_err_cnt',
                    'src_http_err_rate',
                    'src_http_req_cnt',
                    'src_http_req_rate',
                    'src_sess_rate',
                    'nbsrv',
                    'traffic_is_http',
                    'traffic_is_ssl',
                    'ssl_fc',
                    'ssl_fc_sni',
                    'ssl_sni',
                    'ssl_sni_sub',
                    'ssl_sni_beg',
                    'ssl_sni_end',
                    'ssl_sni_reg',
                    'custom_acl'
                ], required=True),
            acl_negate=dict(type='bool', default=False),
            acl_hdr_beg=dict(type='str', default=''),
            acl_hdr_end=dict(type='str', default=''),
            acl_hdr=dict(type='str', default=''),
            acl_hdr_reg=dict(type='str', default=''),
            acl_hdr_sub=dict(type='str', default=''),
            acl_path_beg=dict(type='str', default=''),
            acl_path_end=dict(type='str', default=''),
            acl_path=dict(type='str', default=''),
            acl_path_reg=dict(type='str', default=''),
            acl_path_dir=dict(type='str', default=''),
            acl_path_sub=dict(type='str', default=''),
            acl_url_param=dict(type='str', default=''),
            acl_url_param_value=dict(type='str', default=''),
            acl_ssl_c_verify_code=dict(type='str', default=''),
            acl_ssl_c_ca_commonname=dict(type='str', default=''),
            acl_src=dict(type='str', default=''),
            acl_src_bytes_in_rate_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_bytes_in_rate=dict(type='str', default=''),
            acl_src_bytes_out_rate_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_bytes_out_rate=dict(type='str', default=''),
            acl_src_conn_cnt_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_conn_cnt=dict(type='str', default=''),
            acl_src_conn_rate_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_conn_rate=dict(type='str', default=''),
            acl_src_http_err_cnt_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_http_err_cnt=dict(type='str', default=''),
            acl_src_http_err_rate_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_http_err_rate=dict(type='str', default=''),
            acl_src_http_req_rate_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_http_req_rate=dict(type='str', default=''),
            acl_src_kbytes_in_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_kbytes_in=dict(type='str', default=''),
            acl_src_kbytes_out_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_kbytes_out=dict(type='str', default=''),
            acl_src_port_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_port=dict(type='str', default=''),
            acl_src_sess_cnt_comparison=dict(type='str', choices=['', 'gt', 'ge', 'eq', 'lt', 'le'], default='gt'),
            acl_src_sess_cnt=dict(type='str', default=''),
            acl_nbsrv=dict(type='str', default=''),
            acl_nbsrv_backend=dict(type='str', default=''),
            acl_ssl_fc_sni=dict(type='str', default=''),
            acl_ssl_sni=dict(type='str', default=''),
            acl_ssl_sni_sub=dict(type='str', default=''),
            acl_ssl_sni_beg=dict(type='str', default=''),
            acl_ssl_sni_end=dict(type='str', default=''),
            acl_ssl_sni_reg=dict(type='str', default=''),
            acl_custom_acl=dict(type='str', default=''),
            acl_value=dict(type='str', default=''),
            acl_query_backend=dict(type='str', default=''),
            acl_allowed_users=dict(type='list', default=[]),
            acl_allowed_groups=dict(type='list', default=[]),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Prepare properties of acl
    haproxy_reload = module.params['haproxy_reload']
    acl_state = module.params['acl_state']
    acl_name = module.params['acl_name']
    acl_description = module.params['acl_description']
    acl_expression = module.params['acl_expression']
    acl_negate = module.params['acl_negate']
    acl_hdr_beg = module.params['acl_hdr_beg']
    acl_hdr_end = module.params['acl_hdr_end']
    acl_hdr = module.params['acl_hdr']
    acl_hdr_reg = module.params['acl_hdr_reg']
    acl_hdr_sub = module.params['acl_hdr_sub']
    acl_path_beg = module.params['acl_path_beg']
    acl_path_end = module.params['acl_path_end']
    acl_path = module.params['acl_path']
    acl_path_reg = module.params['acl_path_reg']
    acl_path_dir = module.params['acl_path_dir']
    acl_path_sub = module.params['acl_path_sub']
    acl_url_param = module.params['acl_url_param']
    acl_url_param_value = module.params['acl_url_param_value']
    acl_ssl_c_verify_code = module.params['acl_ssl_c_verify_code']
    acl_ssl_c_ca_commonname = module.params['acl_ssl_c_ca_commonname']
    acl_src = module.params['acl_src']
    acl_src_bytes_in_rate_comparison = module.params['acl_src_bytes_in_rate_comparison']
    acl_src_bytes_in_rate = module.params['acl_src_bytes_in_rate']
    acl_src_bytes_out_rate_comparison = module.params['acl_src_bytes_out_rate_comparison']
    acl_src_bytes_out_rate = module.params['acl_src_bytes_out_rate']
    acl_src_conn_cnt_comparison = module.params['acl_src_conn_cnt_comparison']
    acl_src_conn_cnt = module.params['acl_src_conn_cnt']
    acl_src_conn_rate_comparison = module.params['acl_src_conn_rate_comparison']
    acl_src_conn_rate = module.params['acl_src_conn_rate']
    acl_src_http_err_cnt_comparison = module.params['acl_src_http_err_cnt_comparison']
    acl_src_http_err_cnt = module.params['acl_src_http_err_cnt']
    acl_src_http_err_rate_comparison = module.params['acl_src_http_err_rate_comparison']
    acl_src_http_err_rate = module.params['acl_src_http_err_rate']
    acl_src_http_req_rate_comparison = module.params['acl_src_http_req_rate_comparison']
    acl_src_http_req_rate = module.params['acl_src_http_req_rate']
    acl_src_kbytes_in_comparison = module.params['acl_src_kbytes_in_comparison']
    acl_src_kbytes_in = module.params['acl_src_kbytes_in']
    acl_src_kbytes_out_comparison = module.params['acl_src_kbytes_out_comparison']
    acl_src_kbytes_out = module.params['acl_src_kbytes_out']
    acl_src_port_comparison = module.params['acl_src_port_comparison']
    acl_src_port = module.params['acl_src_port']
    acl_src_sess_cnt_comparison = module.params['acl_src_sess_cnt_comparison']
    acl_src_sess_cnt = module.params['acl_src_sess_cnt']
    acl_nbsrv = module.params['acl_nbsrv']
    acl_nbsrv_backend = module.params['acl_nbsrv_backend']
    acl_ssl_fc_sni = module.params['acl_ssl_fc_sni']
    acl_ssl_sni = module.params['acl_ssl_sni']
    acl_ssl_sni_sub = module.params['acl_ssl_sni_sub']
    acl_ssl_sni_beg = module.params['acl_ssl_sni_beg']
    acl_ssl_sni_end = module.params['acl_ssl_sni_end']
    acl_ssl_sni_reg = module.params['acl_ssl_sni_reg']
    acl_custom_acl = module.params['acl_custom_acl']
    acl_value = module.params['acl_value']
    acl_query_backend = module.params['acl_query_backend']
    acl_allowed_users = module.params['acl_allowed_users']
    acl_allowed_groups = module.params['acl_allowed_groups']

    # Get empty ACL object to lookup UUIDs for allowedUsers, allowedGroups, nbsrv_backend, queryBackend
    empty_acl = apiconnection.getObjectByUuid('acl', '')
    #acl_nbsrv_backend = apiconnection.getUuidByName('backend', module.params['acl_nbsrv_backend'])
    acl_nbsrv_backend_uuid = ''
    if acl_nbsrv_backend != '':
        for key,value in empty_acl['nbsrv_backend'].items():
            if value['value'] == acl_nbsrv_backend:
                acl_nbsrv_backend_uuid = key
    #acl_query_backend = apiconnection.getUuidByName('backend', module.params['acl_query_backend'])
    acl_query_backend_uuid = ''
    if acl_query_backend != '':
        for key,value in empty_acl['queryBackend'].items():
            if value['value'] == acl_query_backend:
                acl_query_backend_uuid = key
    # Resolve UUIDs for users
    acl_allowed_users_uuids = []
    for acl_allowed_user in acl_allowed_users:
        #acl_allowed_users_uuids.append(apiconnection.getUuidByName('user', acl_allowed_user))
        for key,value in empty_acl['allowedUsers'].items():
            if value['value'] == acl_allowed_user:
                acl_allowed_users_uuids.append(key)
    # Resolve UUIDs for allowedGroups
    acl_allowed_groups_uuids = []
    for acl_allowed_group in acl_allowed_groups:
        #acl_allowed_groups_uuids.append(apiconnection.getUuidByName('group', acl_allowed_group))
        for key,value in empty_acl['allowedGroups'].items():
            if value['value'] == acl_allowed_group:
                acl_allowed_groups_uuids.append(key)

    # Fetch list of acls
    acls = apiconnection.listObjects('acl')

    # Build dict with desired state
    desired_properties = {
        'description': acl_description,
        'expression': acl_expression,
        'negate': str(int(acl_negate)),
        'hdr_beg': acl_hdr_beg,
        'hdr_end': acl_hdr_end,
        'hdr': acl_hdr,
        'hdr_reg': acl_hdr_beg,
        'hdr_sub': acl_hdr_sub,
        'path_beg': acl_path_beg,
        'path_end': acl_path_end,
        'path': acl_path,
        'path_reg': acl_path_reg,
        'path_dir': acl_path_dir,
        'path_sub': acl_path_sub,
        'url_param': acl_url_param,
        'url_param_value': acl_url_param_value,
        'ssl_c_verify_code': acl_ssl_c_verify_code,
        'ssl_c_ca_commonname': acl_ssl_c_ca_commonname,
        'src': acl_src,
        'src_bytes_in_rate_comparison': acl_src_bytes_in_rate_comparison,
        'src_bytes_in_rate': acl_src_bytes_in_rate,
        'src_bytes_out_rate_comparison': acl_src_bytes_out_rate_comparison,
        'src_bytes_out_rate': acl_src_bytes_out_rate,
        'src_conn_cnt_comparison': acl_src_conn_cnt_comparison,
        'src_conn_cnt': acl_src_conn_cnt,
        'src_conn_rate_comparison': acl_src_conn_rate_comparison,
        'src_conn_rate': acl_src_conn_rate,
        'src_http_err_cnt_comparison': acl_src_http_err_cnt_comparison,
        'src_http_err_cnt': acl_src_http_err_cnt,
        'src_http_err_rate_comparison': acl_src_http_err_rate_comparison,
        'src_http_err_rate': acl_src_http_err_rate,
        'src_http_req_rate_comparison':  acl_src_http_req_rate_comparison,
        'src_http_req_rate': acl_src_http_req_rate,
        'src_kbytes_in_comparison': acl_src_kbytes_in_comparison,
        'src_kbytes_in': acl_src_kbytes_in,
        'src_kbytes_out_comparison': acl_src_kbytes_out_comparison,
        'src_kbytes_out': acl_src_kbytes_out,
        'src_port_comparison': acl_src_port_comparison,
        'src_port': acl_src_port,
        'src_sess_cnt_comparison': acl_src_sess_cnt_comparison,
        'src_sess_cnt': acl_src_sess_cnt,
        'nbsrv': acl_nbsrv,
        'nbsrv_backend': acl_nbsrv_backend_uuid,
        'ssl_fc_sni': acl_ssl_fc_sni,
        'ssl_sni': acl_ssl_sni,
        'ssl_sni_sub': acl_ssl_sni_sub,
        'ssl_sni_beg': acl_ssl_sni_beg,
        'ssl_sni_end': acl_ssl_sni_end,
        'ssl_sni_reg': acl_ssl_sni_reg,
        'custom_acl': acl_custom_acl,
        'value': acl_value,
        'queryBackend': acl_query_backend,
        'allowedUsers': ','.join(acl_allowed_users_uuids),
        'allowedGroups': ','.join(acl_allowed_groups_uuids)
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if acl object with specified name exists
    for acl in acls:
        if acl['name'] == acl_name:
            uuid = acl['uuid']
            break
    acl_exists = (uuid != '')
    if acl_state == 'present':
        if acl_exists:
            acl = apiconnection.getObjectByName('acl', acl_name)
            for prop in desired_properties.keys():
                # Special cases for complex propertierts:
                if prop == 'expression':
                    current_expression = apiconnection.getSelected(acl[prop])
                    if current_expression != acl_expression:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_expression, desired_properties[prop]))
                # Catch all _comparison properties
                elif '_comparison' in prop:
                    current_comparison = apiconnection.getSelected(acl[prop])
                    if current_comparison != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_comparison, desired_properties[prop]))
                elif prop == 'nbsrv_backend':
                    current_nbsrv_backend = apiconnection.getSelected(acl[prop])
                    if current_nbsrv_backend != acl_nbsrv_backend:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_nbsrv_backend, desired_properties[prop]))
                elif prop == 'queryBackend':
                    current_query_backend = apiconnection.getSelected(acl[prop])
                    if current_query_backend != acl_query_backend:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_query_backend, desired_properties[prop]))
                elif prop == 'allowedUsers':
                    current_allowed_users = apiconnection.getSelectedList(acl[prop])
                    if not apiconnection.compareLists(current_allowed_users, acl_allowed_users_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_allowed_users, desired_properties[prop]))
                elif prop == 'allowedGroups':
                    current_allowed_groups = apiconnection.getSelectedList(acl[prop])
                    if not apiconnection.compareLists(current_allowed_groups, acl_allowed_groups_uuids):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_allowed_groups, desired_properties[prop]))
                else:
                    # catch all other properties
                    if acl[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, acl[prop], desired_properties[prop]))

            if not needs_change:
                result = {'changed': False, 'msg': ['Acl already present: %s' %acl_name, additional_msg]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('acl', acl_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Acl %s must be changed.' %acl_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('acl', acl_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Acl %s must be created.' %acl_name, additional_msg]}
    else:
        if acl_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('acl', acl_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Acl %s must be deleted.' %acl_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Acl %s is not present.' %acl_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
