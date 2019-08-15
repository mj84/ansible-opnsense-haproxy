#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_mapfile
short_description: Manage HAProxy mapfiles on Opnsense
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
            mapfile_name=dict(type='str', required=True),
            mapfile_description=dict(type='str', default=''),
            mapfile_content=dict(type='str', default=''),
            mapfile_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of mapfile
    mapfile_name = module.params['mapfile_name']
    mapfile_content = module.params['mapfile_content']
    mapfile_state = module.params['mapfile_state']
    mapfile_description = module.params['mapfile_description']
    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of mapfiles
    mapfiles = apiconnection.listObjects('mapfile')

    # Build dict with desired state
    desired_properties = {'description': mapfile_description, 'content': mapfile_content}
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if mapfile object with specified name exists
    for mapfile in mapfiles:
        if mapfile['name'] == mapfile_name:
            uuid = mapfile['uuid']
            break
    mapfile_exists = (uuid != '')

    if mapfile_state == 'present':
        if mapfile_exists:
            mapfile = apiconnection.getObjectByName('mapfile', mapfile_name)
            for prop in desired_properties.keys():
                if mapfile[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
            if not needs_change:
                result = {'changed': False, 'msg': ['Mapfile already present: %s' %mapfile_name]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('mapfile', mapfile_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Mapfile %s must be changed.' %mapfile_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('mapfile', mapfile_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Mapfile %s must be created.' %mapfile_name, additional_msg]}
    else:
        if mapfile_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('mapfile', mapfile_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Mapfile %s must be deleted.' %mapfile_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Mapfile %s is not present.' %mapfile_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
