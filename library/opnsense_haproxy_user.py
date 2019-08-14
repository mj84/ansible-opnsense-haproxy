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
            username=dict(type='str', required=True),
            password=dict(type='str', default='', no_log=True),
            enabled=dict(type='bool', default=True),
            description=dict(type='str', default=''),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of user
    username = module.params['username']
    password = module.params['password']
    enabled = str(int(module.params['enabled']))
    state = module.params['state']
    description = module.params['description']
    # Instantiate API connection
    api_url = module.params['api_url']
    auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, auth, api_ssl_verify)

    # Fetch list of users
    users = apiconnection.listObjects('user')

    # Build dict with desired state
    desired_properties = {'password': password, 'enabled': enabled, 'description': description}
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
        if user['name'] == username:
            user_exists = True
            uuid = user['uuid']
            additional_msg.append(uuid)
            break
    user_exists = (uuid != '')

    if state == 'present':
        if user_exists:
            user = apiconnection.getObjectByName('user', username)
            for prop in ['password', 'enabled', 'description']:
                if user[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
            if not needs_change:
                result = {'changed': False, 'msg': ['User already present: %s' %username]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('user', username, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['User %s must be changed.' %username, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('user', username, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['User %s must be created.' %username, additional_msg]}
    else:
        if user_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('user', username))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['User %s must be deleted.' %username, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['User %s is not present.' %username]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
