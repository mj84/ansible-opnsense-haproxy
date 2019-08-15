#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_acl
short_description: Manage HAProxy ACLs (Conditions) on Opnsense
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
            acl_name=dict(type='str', required=True),
            acl_description=dict(type='str', default=''),
            acl_negate=dict(type='bool', default=False),
            acl_condition_type=dict(type='str', choices=[
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
                'ssl_fc',
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
                'src_sess_cnt',
                'src_sess_rate',
                'nbsrv',
                'traffic_is_http',
                'traffic_is_ssl',
                'ssl_sni',
                'ssl_sni_sub',
                'ssl_sni_beg',
                'ssl_sni_end',
                'ssl_sni_reg',
                'custom_acl'
            ], required=True),
            acl_condition_value=dict(type='str', required=True),
            acl_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of acl
    acl_name = module.params['acl_name']
    acl_negate = str(int(module.params['acl_negate']))
    acl_condition_type = module.params['acl_condition_type']
    acl_condition_value = module.params['acl_condition_value']
    acl_description = module.params['acl_description']
    acl_state = module.params['acl_state']
    # Instantiate API connection
    api_url = module.params['api_url']
    auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, auth, api_ssl_verify)

    # Fetch list of acls
    acls = apiconnection.listObjects('acl')

    # Build dict with desired state
    desired_properties = {'description': acl_description, 'negate': acl_negate, 'expression': acl_condition_type, acl_condition_type: acl_condition_value}
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
            acl_exists = True
            uuid = acl['uuid']
            additional_msg.append(uuid)
            break
    acl_exists = (uuid != '')

    if acl_state == 'present':
        if acl_exists:
            acl = apiconnection.getObjectByName('acl', acl_name)
            # Check if properties differ
            for prop in ['description', 'negate', acl_condition_type]:
                if acl[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
                    additional_msg.append('Changing %s: %s => %s' %(prop, acl[prop], desired_properties[prop]))
            # Entries in expression dict must be checked seperately if selected == 1:
            for key, value in acl['expression'].iteritems():
                if value['selected'] == '1' and key != acl_condition_type:
                # Currently selected acl_condition_type does not match, set both _type and _value
                    needs_change = True
                    changed_properties['expression'] = acl_condition_type
                    changed_properties[acl_condition_type] = acl_condition_value
            if not needs_change:
                result = {'changed': False, 'msg': ['Acl already present: %s' %acl_name]}
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
