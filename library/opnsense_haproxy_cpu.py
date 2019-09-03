#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_cpu
short_description: Manage HAProxy cpus on Opnsense
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
            cpu_state=dict(type='str', choices=['present', 'absent'], default='present'),
            cpu_enabled=dict(type='bool', default=True),
            cpu_name=dict(type='str', required=True),
            cpu_process_id=dict(type='str',
                choices=[
                    'all', 'odd', 'even',
                    'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10',
                    'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19', 'x20',
                    'x21', 'x22', 'x23', 'x24', 'x25', 'x26', 'x27', 'x28', 'x29', 'x30',
                    'x31', 'x32', 'x33', 'x34', 'x35', 'x36', 'x37', 'x38', 'x39', 'x40',
                    'x41', 'x42', 'x43', 'x44', 'x45', 'x46', 'x47', 'x48', 'x49', 'x50',
                    'x51', 'x52', 'x53', 'x54', 'x55', 'x56', 'x57', 'x58', 'x59', 'x60',
                    'x61', 'x62', 'x63',
                ],
                default='all'),
            cpu_thread_id=dict(type='str',
                choices=[
                    'all', 'odd', 'even',
                    'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10',
                    'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19', 'x20',
                    'x21', 'x22', 'x23', 'x24', 'x25', 'x26', 'x27', 'x28', 'x29', 'x30',
                    'x31', 'x32', 'x33', 'x34', 'x35', 'x36', 'x37', 'x38', 'x39', 'x40',
                    'x41', 'x42', 'x43', 'x44', 'x45', 'x46', 'x47', 'x48', 'x49', 'x50',
                    'x51', 'x52', 'x53', 'x54', 'x55', 'x56', 'x57', 'x58', 'x59', 'x60',
                    'x61', 'x62', 'x63',
                ],
                default='all'),
            cpu_cpu_id=dict(type='list',
                elements='str',
                options=dict(
                    choices=[
                        'all', 'odd', 'even',
                        'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 'x9', 'x10',
                        'x11', 'x12', 'x13', 'x14', 'x15', 'x16', 'x17', 'x18', 'x19', 'x20',
                        'x21', 'x22', 'x23', 'x24', 'x25', 'x26', 'x27', 'x28', 'x29', 'x30',
                        'x31', 'x32', 'x33', 'x34', 'x35', 'x36', 'x37', 'x38', 'x39', 'x40',
                        'x41', 'x42', 'x43', 'x44', 'x45', 'x46', 'x47', 'x48', 'x49', 'x50',
                        'x51', 'x52', 'x53', 'x54', 'x55', 'x56', 'x57', 'x58', 'x59', 'x60',
                        'x61', 'x62', 'x63',
                    ]
                ),
                default=['all']),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of cpu
    cpu_state = module.params['cpu_state']
    cpu_enabled = str(int(module.params['cpu_enabled']))
    cpu_name = module.params['cpu_name']
    cpu_process_id = module.params['cpu_process_id']
    cpu_thread_id = module.params['cpu_thread_id']
    cpu_cpu_id = module.params['cpu_cpu_id']

    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of cpus
    cpus = apiconnection.listObjects('cpu')

    # Build dict with desired state
    desired_properties = {
        'enabled': cpu_enabled,
        'process_id': cpu_process_id,
        'thread_id': cpu_thread_id,
        'cpu_id': ','.join(cpu_cpu_id)
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if cpu object with specified name exists
    for cpu in cpus:
        if cpu['name'] == cpu_name:
            uuid = cpu['uuid']
            break
    cpu_exists = (uuid != '')
    if cpu_state == 'present':
        if cpu_exists:
            cpu = apiconnection.getObjectByName('cpu', cpu_name)
            for prop in desired_properties.keys():
                # Special cases for complex propertierts:
                if prop == 'process_id':
                    current_process_id = apiconnection.getSelected(cpu[prop])
                    if current_process_id != cpu_process_id:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_process_id, desired_properties[prop]))
                elif prop == 'thread_id':
                    current_thread_id = apiconnection.getSelected(cpu[prop])
                    if current_thread_id != cpu_thread_id:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_thread_id, desired_properties[prop]))
                elif prop == 'cpu_id':
                    current_cpu_id = apiconnection.getSelectedList(cpu[prop], retval='key')
                    if not apiconnection.compareLists(current_cpu_id, cpu_cpu_id):
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_cpu_id, desired_properties[prop]))
                else:
                    # catch all other properties
                    if cpu[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, cpu[prop], desired_properties[prop]))

            if not needs_change:
                result = {'changed': False, 'msg': ['Cpu already present: %s' %cpu_name, additional_msg]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('cpu', cpu_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Cpu %s must be changed.' %cpu_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('cpu', cpu_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Cpu %s must be created.' %cpu_name, additional_msg]}
    else:
        if cpu_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('cpu', cpu_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Cpu %s must be deleted.' %cpu_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Cpu %s is not present.' %cpu_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
