#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_group
short_description: Manage HAProxy groups on Opnsense
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
            group_name=dict(type='str', required=True),
            group_enabled=dict(type='bool', default=True),
            group_description=dict(type='str', default=''),
            group_members=dict(type='list', default=[]),
            group_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of group
    group_name = module.params['group_name']
    group_enabled = str(int(module.params['group_enabled']))
    group_members = module.params['group_members']
    group_state = module.params['group_state']
    group_description = module.params['group_description']
    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of groups
    groups = apiconnection.listObjects('group')

    # Get an empty group object to lookup UUIDs for group members
    empty_group = apiconnection.getObjectByUuid('group', '')
    group_members_uuids = []
    for group_member in group_members:
        for key,value in empty_group['members']:
            if value['value'] == group_member:
                group_members_uuids.append(key)

    # Build dict with desired state
    desired_properties = {
        'enabled': group_enabled,
        'description': group_description,
        'members': ','.join(group_members_uuids)
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if group object with specified name exists
    for group in groups:
        if group['name'] == group_name:
            uuid = group['uuid']
            break
    group_exists = (uuid != '')
    if group_state == 'present':
        if group_exists:
            group = apiconnection.getObjectByName('group', group_name)
            for prop in desired_properties.keys():
                # Special case for members where two lists have to be compared
                if prop == 'members':
                    current_members_keys = apiconnection.getSelectedList(group[prop])
                    if not apiconnection.compareLists(current_members_keys, group_members):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing members: %s => %s' %(current_members_keys, desired_properties[prop]))
                else:
                    if group[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, group[prop], desired_properties[prop]))
            if not needs_change:
                result = {'changed': False, 'msg': ['Group already present: %s' %group_name]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('group', group_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Group %s must be changed.' %group_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('group', group_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Group %s must be created.' %group_name, additional_msg]}
    else:
        if group_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('group', group_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Group %s must be deleted.' %group_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Group %s is not present.' %group_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
