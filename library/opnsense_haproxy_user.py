#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_users
short_description: Manage HAProxy users on Opnsense
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
            user_name=dict(type='str', required=True),
            user_password=dict(type='str', default='', no_log=True),
            user_enabled=dict(type='bool', default=True),
            user_description=dict(type='str', default=''),
            user_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of user
    user_name = module.params['user_name']
    user_password = module.params['user_password']
    user_enabled = str(int(module.params['user_enabled']))
    user_state = module.params['user_state']
    user_description = module.params['user_description']
    # Instantiate API connection
    api_url = module.params['api_url']
    auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, auth, api_ssl_verify)

    # Fetch list of users
    users = apiconnection.listObjects('user')

    # Build dict with desired state
    desired_properties = {'password': user_password, 'enabled': user_enabled, 'description': user_description}
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if user object with specified name exists
    for user in users:
        if user['name'] == user_name:
            user_exists = True
            uuid = user['uuid']
            additional_msg.append(uuid)
            break
    user_exists = (uuid != '')

    if user_state == 'present':
        if user_exists:
            user = apiconnection.getObjectByName('user', user_name)
            for prop in desired_properties.keys():
                if user[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
                    additional_msg.append('Changing %s: %s => %s' %(prop, user[prop], desired_properties[prop]))
            if not needs_change:
                result = {'changed': False, 'msg': ['User already present: %s' %user_name]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('user', user_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['User %s must be changed.' %user_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('user', user_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['User %s must be created.' %user_name, additional_msg]}
    else:
        if user_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('user', user_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['User %s must be deleted.' %user_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['User %s is not present.' %user_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
