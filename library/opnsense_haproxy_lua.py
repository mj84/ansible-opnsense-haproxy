#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_lua
short_description: Manage HAProxy luas on Opnsense
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
            lua_name=dict(type='str', required=True),
            lua_enabled=dict(type='bool', default=True),
            lua_description=dict(type='str', default=''),
            lua_content=dict(type='str', default=''),
            lua_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of lua
    lua_name = module.params['lua_name']
    lua_enabled = str(int(module.params['lua_enabled']))
    lua_content = module.params['lua_content']
    lua_state = module.params['lua_state']
    lua_description = module.params['lua_description']
    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of luas
    luas = apiconnection.listObjects('lua')

    # Build dict with desired state
    desired_properties = {'enabled': lua_enabled, 'description': lua_description, 'content': lua_content}
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if lua object with specified name exists
    for lua in luas:
        if lua['name'] == lua_name:
            uuid = lua['uuid']
            break
    lua_exists = (uuid != '')

    if lua_state == 'present':
        if lua_exists:
            lua = apiconnection.getObjectByName('lua', lua_name)
            for prop in desired_properties.keys():
                if lua[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
            if not needs_change:
                result = {'changed': False, 'msg': ['Lua already present: %s' %lua_name]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('lua', lua_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Lua %s must be changed.' %lua_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('lua', lua_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Lua %s must be created.' %lua_name, additional_msg]}
    else:
        if lua_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('lua', lua_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Lua %s must be deleted.' %lua_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Lua %s is not present.' %lua_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
