#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_action
short_description: Manage HAProxy actions (Rules) on Opnsense
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
            actionname=dict(type='str', required=True),
            description=dict(type='str', default=''),
            test_type=dict(type='str', choices=['if', 'unless'], default='if'),
            linked_acls=dict(type='list', default=[]),
            operator=dict(type='str', choices=['and', 'or'], default='and'),
            action_type=dict(type='str', choices=[
                'use_backend',
                'use_server',
                'map_use_backend',
                'http-request_allow',
                'http-request_deny',
                'http-request_tarpit',
                'http-request_auth',
                'http-request_redirect',
                'http-request_lua',
                'http-request_use-service',
                'http-request_add-header',
                'http-request_set-header',
                'http-request_del-header',
                'http-request_replace-header',
                'http-request_replace-value',
                'http-request_set-path',
                'http-response_allow',
                'http-response_deny',
                'http-response_lua',
                'http-response_add-header',
                'http-response_set-header',
                'http-response_del-header',
                'http-response_replace-header',
                'http-response_replace-value',
                'http-response_set-status',
                'tcp-request_connection_accept',
                'tcp-request_connection_reject',
                'tcp-request_content_accept',
                'tcp-request_content_reject',
                'tcp-request_content_lua',
                'tcp-request_content_use-service',
                'tcp-request_inspect-delay',
                'tcp-response_content_accept',
                'tcp-response_content_reject',
                'tcp-response_content_lua',
                'tcp-response_inspect-delay',
                'custom'
            ], required=True),
            action_value=dict(type='str', required=True),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of action
    actionname = module.params['actionname']
    test_type = module.params['test_type']
    action_type = module.params['action_type']
    action_value = module.params['action_value']
    linked_acls = module.params['linked_acls']
    operator = module.params['operator']
    description = module.params['description']
    state = module.params['state']
    # Instantiate API connection
    api_url = module.params['api_url']
    auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, auth, api_ssl_verify)

    # Fetch list of acls
    actions = apiconnection.listObjects('action')

    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []

    # Replace all dashes in action_type since their keys only use underscores:
    action_type_key = action_type.replace('-', '_')
    # Build dict with desired state
    desired_properties = {'description': description, 'testType': test_type, 'operator': operator, 'type': action_type, action_type_key: action_value, 'linkedAcls': ''}
    # Special case for linkedAcls which are a comma-separated list
    desired_properties['linkedAcls'] = apiconnection.getCommaSeparatedUuidsFromListOfNames('acl', linked_acls)
    #for acl in linked_acls:
    #    acl_uuid = apiconnection.getUuidByName('acl', acl)
    #    desired_properties['linkedAcls'] += acl_uuid
    #    if acl != linked_acls[-1]: desired_properties['linkedAcls'] += ','
    # Special case for several http actions which use 2 fields:
    if 'http' in action_type and 'header' in action_type:
        # del only needs the name of HTTP header to delete
        if 'del' in action_type:
            desired_properties[action_type_key + '_name'] = action_value
        else:
            value_name = action_value.split('::')[0]
            desired_properties[action_type_key + '_name'] = value_name
            # regex actions have _name and _regex
            if 'regex' in action_type:
                value_regex = action_value.split('::')[1]
                desired_properties[action_type_key + '_regex'] = value_regex
            else:
                value_content = action_value.split('::')[1]
                desired_properties[action_type_key + '_content'] = value_content
    # Special case for http_*_replace_value which also needs http_*_replace_regex
    elif 'http' in action_type and 'value' in action_type:
        value_name = action_value.split('::')[0]
        desired_properties[action_type_key + '_name'] = value_name
        value_regex = action_value.split('::')[1]
        desired_properties[action_type_key + '_regex'] = value_regex
    elif 'http' in action_type and 'status' in action_type:
        value_code = action_value.split('::')[0]
        desired_properties[action_type_key + '_code'] = value_code
        value_reason = action_value.split('::')[1]
        desired_properties[action_type_key + '_reason'] = value_reason
    else:
        desired_properties[action_type_key] = action_value
    
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if action object with specified name exists
    for action in actions:
        if action['name'] == actionname:
            uuid = action['uuid']
            additional_msg.append('Found action with uuid %s' % uuid)
            break
    action_exists = (uuid != '')

    if state == 'present':
        if action_exists:
            action = apiconnection.getObjectByName('action', actionname)
            # Check if simple properties differ
            for prop in ['description']:
                if action[prop] != desired_properties[prop]:
                    needs_change = True
                    additional_msg.append('simple prop')
                    changed_properties[prop] = desired_properties[prop]
            # Check if action_type_key is already present, if not, replace the whole dict
            if action_type_key not in action:
                # Special cases will be handled a bit further below
                if 'http' in action_type and ('header' in action_type or 'value' in action_type or 'status' in action_type):
                    pass
                else:
                    needs_change = True
                    changed_properties = desired_properties
                    additional_msg.append('action_type_key %s not in action' % action_type_key)
            # Entries in testType, operator and type dicts must be checked separately if property selected == 1:
            complex_types_list = ['testType', 'operator', 'type']
            for complex_type in complex_types_list:
                for key, value in action[complex_type].iteritems():
                    if value['selected'] == '1' and key != desired_properties[complex_type]:
                    # Currently selected type value does not match desired type value, replace the whole dict:
                        additional_msg.append('%s not selected' %(complex_type))
                        needs_change = True
                        changed_properties = desired_properties
            # Check special cases where differently named properties exist (HTTP header):
            if not needs_change and 'http' in action_type and ('header' in action_type or 'value' in action_type or 'status' in action_type):
                if action[action_type_key + '_name'] != desired_properties[action_type_key + '_name']:
                    needs_change = True
                    changed_properties[action_type_key + '_name'] = desired_properties[action_type_key + '_name']
                for special_property in [ action_type_key + '_name', action_type_key + '_regex', action_type_key + '_content' ]:
                    if special_property in desired_properties:
                        if special_property not in action:
                        # Current property is missing completely
                            additional_msg.append('property %s missing' % special_property)
                            needs_change = True
                            changed_properties = desired_properties
                        else:
                            if action[special_property] != desired_properties[special_property]:
                            # Current property exists, but value is different, change it
                                additional_msg.append('action value differs')
                                needs_change = True
                                changed_properties[special_property] = desired_properties[special_property]
                
            # Check if currently an acl is linked which should not be linked:
            for key, value in action['linkedAcls'].iteritems():
                if value['selected'] == 1:
                    # Get name of linkedAcl and compare with linked_acls list
                    acl = apiconnection.getObjectByUuid('acl', key)
                    additional_msg.append('Found a linked acl with name: %s' % acl['name'])
                    if acl['name'] not in linked_acls:
                    # Current element is not in linked_acls, rebuild linkedAcls completely
                        needs_change = True
                        additional_msg.append('linkedAcls containing unwanted element')
                        changed_properties['linkedAcls'] = desired_properties['linkedAcls']
            # Reverse acl check, make sure every entry in linked_acl is included in action object
            for acl in linked_acls:
                acl_uuid = apiconnection.getUuidByName('acl', acl)
                if action['linkedAcls'][acl_uuid]['selected'] == 0:
                    needs_change = True
                    changed_properties['linkedAcls'] = desired_properties['linkedAcls']
            if not needs_change:
                result = {'changed': False, 'msg': ['Action already present: %s' %actionname, additional_msg]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('action', actionname, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Action %s must be changed.' %actionname, additional_msg]}
        else:
            if not module.check_mode:
                desired_properties['type'] = action_type
                action_type_key = action_type.replace('-','_')
                # Special case for http header which have a _name and a _content field:
                if 'http' in action_type and 'header' in action_type:
                    # del only needs the name of HTTP header to delete
                    if 'del' in action_type:
                        desired_properties[action_type_key + '_name'] = action_value
                    else:
                        value_name = action_value.split('::')[0]
                        desired_properties[action_type_key + '_name'] = value_name
                        # regex actions have _name and _regex
                        if 'regex' in action_type:
                            value_regex = action_value.split('::')[1]
                            desired_properties[action_type_key + '_regex'] = value_regex
                        else:
                            value_content = action_value.split('::')[1]
                            desired_properties[action_type_key + '_content'] = value_content
                # Special case for http_*_replace_value which also needs http_*_replace_regex
                elif 'http' in action_type and 'value' in action_type:
                    value_name = action_value.split('::')[0]
                    desired_properties[action_type_key + '_name'] = value_name
                    value_regex = action_value.split('::')[1]
                    desired_properties[action_type_key + '_regex'] = value_regex
                elif 'http' in action_type and 'status' in action_type:
                    value_code = action_value.split('::')[0]
                    desired_properties[action_type_key + '_code'] = value_code
                    value_reason = action_value.split('::')[1]
                    desired_properties[action_type_key + '_reason'] = value_reason
                else:
                    desired_properties[action_type_key] = action_value
                additional_msg.append(apiconnection.createObject('action', actionname, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Action %s must be created.' %actionname, additional_msg]}
    else:
        if action_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('action', actionname))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Action %s must be deleted.' %actionname, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Action %s is not present.' %actionname]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
