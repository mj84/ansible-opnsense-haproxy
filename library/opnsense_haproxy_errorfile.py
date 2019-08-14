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
            url=dict(type='str', required=True),
            api_key=dict(type='str', required=True, no_log=True),
            api_secret=dict(type='str', required=True, no_log=True),
            ssl_verify=dict(type='bool', default=False),
            errorfilename=dict(type='str', required=True),
            code=dict(type='str', required=True),
            description=dict(type='str', default=''),
            content=dict(type='str', default=''),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of errorfile
    errorfilename = module.params['errorfilename']
    code = module.params['code']
    content = module.params['content']
    state = module.params['state']
    description = module.params['description']
    # Instantiate API connection
    url = module.params['url']
    auth = (module.params['api_key'], module.params['api_secret'])
    ssl_verify = module.params['ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(url, auth, ssl_verify)

    # Fetch list of errorfiles
    errorfiles = apiconnection.listErrorfiles()

    # Build dict with desired state
    desired_properties = {'code': code, 'description': description, 'content': content}
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
        if errorfile['name'] == errorfilename:
            errorfile_exists = True
            uuid = errorfile['uuid']
            additional_msg.append(uuid)
            break
    errorfile_exists = (uuid != '')

    if state == 'present':
        if errorfile_exists:
            errorfile = apiconnection.getObjectByName('errorfile', errorfilename)
            for prop in ['code', 'content', 'description']:
                if errorfile[prop] != desired_properties[prop]:
                    needs_change = True
                    changed_properties[prop] = desired_properties[prop]
            if not needs_change:
                result = {'changed': False, 'msg': ['Errorfile already present: %s' %errorfilename]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.setErrorfile(errorfilename, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Errorfile %s must be changed.' %errorfilename, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.addErrorfile(errorfilename, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Errorfile %s must be created.' %errorfilename, additional_msg]}
    else:
        if errorfile_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.delErrorfile(errorfilename))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Errorfile %s must be deleted.' %errorfilename, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Errorfile %s is not present.' %errorfilename]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
