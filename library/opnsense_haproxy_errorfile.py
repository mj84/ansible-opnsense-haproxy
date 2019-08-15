#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_errorfile
short_description: Manage HAProxy errorfiles on Opnsense
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
            errorfile_name=dict(type='str', required=True),
            errorfile_code=dict(type='str', required=True),
            errorfile_description=dict(type='str', default=''),
            errorfile_content=dict(type='str', default=''),
            errorfile_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of errorfile
    errorfile_name = module.params['errorfile_name']
    errorfile_code = module.params['errorfile_code']
    errorfile_content = module.params['errorfile_content']
    errorfile_state = module.params['errorfile_state']
    errorfile_description = module.params['errorfile_description']
    # Instantiate API connection
    api_url = module.params['api_url']
    auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, auth, api_ssl_verify)

    # Fetch list of errorfiles
    errorfiles = apiconnection.listObjects('errorfile')

    # Build dict with desired state
    desired_properties = {'code': errorfile_code, 'description': errorfile_description, 'content': errorfile_content}
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if errorfile object with specified name exists
    for errorfile in errorfiles:
        if errorfile['name'] == errorfile_name:
            errorfile_exists = True
            uuid = errorfile['uuid']
            additional_msg.append(uuid)
            break
    errorfile_exists = (uuid != '')

    if errorfile_state == 'present':
        if errorfile_exists:
            errorfile = apiconnection.getObjectByName('errorfile', errorfile_name)
            for prop in desired_properties.keys():
                # Special case for code
                if prop == 'code':
                    current_code = apiconnection.getSelected(errorfile[prop])
                    if current_code != desired_properties[prop]:
                        changed_properties[prop] = desired_properties[prop]
                else:
                    if errorfile[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, errorfile[prop], desired_properties[prop]))
            if not needs_change:
                result = {'changed': False, 'msg': ['Errorfile already present: %s' %errorfile_name]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('errorfile', errorfile_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Errorfile %s must be changed.' %errorfile_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('errorfile', errorfile_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Errorfile %s must be created.' %errorfile_name, additional_msg]}
    else:
        if errorfile_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('errorfile', errorfile_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Errorfile %s must be deleted.' %errorfile_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Errorfile %s is not present.' %errorfile_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
