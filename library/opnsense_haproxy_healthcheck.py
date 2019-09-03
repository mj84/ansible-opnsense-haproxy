#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_healthcheck
short_description: Manage HAProxy healthchecks on Opnsense
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
            healthcheck_state=dict(type='str', choices=['present', 'absent'], default='present'),
            healthcheck_name=dict(type='str', required=True),
            healthcheck_type=dict(type='str', choices=['tcp', 'http', 'agent', 'ldap', 'mysql', 'pgsql', 'redis', 'smtp', 'esmtp', 'ssl'], default='http'),
            healthcheck_description=dict(type='str', default=''),
            healthcheck_interval=dict(type='str', default='2s'),
            healthcheck_force_ssl=dict(type='bool', default=False),
            healthcheck_checkport=dict(type='str', default=''),
            healthcheck_http_method=dict(type='str', default='options'),
            healthcheck_http_uri=dict(type='str', default='/'),
            healthcheck_http_version=dict(type=str, choices=['http10', 'http11'], default='http10'),
            healthcheck_http_host=dict(type='str', default='localhost'),
            healthcheck_http_expression_enabled=dict(type='bool', default=False),
            healthcheck_http_expression=dict(type='str', choices=['', 'status', 'rstatus', 'string', 'rstring'], default=''),
            healthcheck_http_negate=dict(type='bool', default=False),
            healthcheck_http_value=dict(type='str', default=''),
            healthcheck_tcp_enabled=dict(type='bool', default=False),
            healthcheck_tcp_send_value=dict(type='str', default=''),
            healthcheck_tcp_match_type=dict(type='str', choices=['', 'string', 'rstring', 'binary'], default=''),
            healthcheck_tcp_negate=dict(type='bool', default=False),
            healthcheck_tcp_match_value=dict(type='str', default=''),
            healthcheck_agent_port=dict(type='str', default=''),
            healthcheck_mysql_user=dict(type='str', default=''),
            healthcheck_mysql_post41=dict(type='bool', default=False),
            healthcheck_pgsql_user=dict(type='str', default=''),
            healthcheck_smtp_domain=dict(type='str', default=''),
            healthcheck_esmtp_domain=dict(type='str', default=''),
            healthcheck_db_user=dict(type='str', default=''),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of healthcheck
    healthcheck_state = module.params['healthcheck_state']
    healthcheck_name = module.params['healthcheck_name']
    healthcheck_description = module.params['healthcheck_description']
    healthcheck_type = module.params['healthcheck_type']
    healthcheck_interval = module.params['healthcheck_interval']
    healthcheck_force_ssl = module.params['healthcheck_force_ssl']
    healthcheck_checkport = module.params['healthcheck_checkport']
    healthcheck_http_method = module.params['healthcheck_http_method']
    healthcheck_http_uri = module.params['healthcheck_http_uri']
    healthcheck_http_version = module.params['healthcheck_http_version']
    healthcheck_http_host = module.params['healthcheck_http_host']
    healthcheck_http_expression = module.params['healthcheck_http_expression']
    healthcheck_http_expression_enabled = module.params['healthcheck_http_expression_enabled']
    healthcheck_http_negate =  module.params['healthcheck_http_negate']
    healthcheck_http_value = module.params['healthcheck_http_value']
    healthcheck_tcp_enabled = module.params['healthcheck_tcp_enabled']
    healthcheck_tcp_send_value = module.params['healthcheck_tcp_send_value']
    healthcheck_tcp_match_type = module.params['healthcheck_tcp_match_type']
    healthcheck_tcp_negate = module.params['healthcheck_tcp_negate']
    healthcheck_tcp_match_value = module.params['healthcheck_tcp_match_value']
    healthcheck_agent_port = module.params['healthcheck_agent_port']
    healthcheck_mysql_user = module.params['healthcheck_mysql_user']
    healthcheck_mysql_post41 = module.params['healthcheck_mysql_post41']
    healthcheck_pgsql_user = module.params['healthcheck_pgsql_user']
    healthcheck_smtp_domain = module.params['healthcheck_smtp_domain']
    healthcheck_esmtp_domain =  module.params['healthcheck_esmtp_domain']
    healthcheck_db_user = module.params['healthcheck_db_user']

    # Instantiate API connection
    api_url = module.params['api_url']
    api_auth = (module.params['api_key'], module.params['api_secret'])
    api_ssl_verify = module.params['api_ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(api_url, api_auth, api_ssl_verify)

    # Fetch list of healthchecks
    healthchecks = apiconnection.listObjects('healthcheck')

    # Build dict with desired state
    desired_properties = {
        'description': healthcheck_description,
        'type': healthcheck_type,
        'interval': healthcheck_interval,
        'force_ssl': str(int(healthcheck_force_ssl)),
        'checkport': healthcheck_checkport,
        'http_method': healthcheck_http_method,
        'http_uri': healthcheck_http_uri,
        'http_version': healthcheck_http_version,
        'http_host': healthcheck_http_host,
        'http_expressionEnabled': str(int(healthcheck_http_expression_enabled)),
        'http_expression': healthcheck_http_expression,
        'http_negate': str(int(healthcheck_http_negate)),
        'http_value': healthcheck_http_value,
        'tcp_enabled': str(int(healthcheck_tcp_enabled)),
        'tcp_sendValue': healthcheck_tcp_send_value,
        'tcp_matchType': healthcheck_tcp_match_type,
        'tcp_negate': str(int(healthcheck_tcp_negate)),
        'tcp_matchValue': healthcheck_tcp_match_value,
        'agent_port': healthcheck_agent_port,
        'mysql_user': healthcheck_mysql_user,
        'mysql_post41': str(int(healthcheck_mysql_post41)),
        'pgsql_user': healthcheck_pgsql_user,
        'smtp_domain': healthcheck_smtp_domain,
        'esmtp_domain': healthcheck_esmtp_domain,
        'agentPort': healthcheck_agent_port,
        'smtpDomain': healthcheck_smtp_domain
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if healthcheck object with specified name exists
    for healthcheck in healthchecks:
        if healthcheck['name'] == healthcheck_name:
            uuid = healthcheck['uuid']
            break
    healthcheck_exists = (uuid != '')
    if healthcheck_state == 'present':
        if healthcheck_exists:
            healthcheck = apiconnection.getObjectByName('healthcheck', healthcheck_name)
            for prop in desired_properties.keys():
                # Special cases for complex propertierts:
                if prop == 'type':
                    current_type = apiconnection.getSelected(healthcheck[prop])
                    if current_type != healthcheck_type:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_type, desired_properties[prop]))
                elif prop == 'http_method':
                    current_http_method = apiconnection.getSelected(healthcheck[prop])
                    if current_http_method != healthcheck_http_method:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_http_method, desired_properties[prop]))
                elif prop == 'http_version':
                    current_http_version = apiconnection.getSelected(healthcheck[prop])
                    if current_http_version != healthcheck_http_version:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_http_version, desired_properties[prop]))
                elif prop == 'http_expression':
                    current_http_expression = apiconnection.getSelected(healthcheck[prop])
                    if current_http_expression != healthcheck_http_expression:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_http_expression, desired_properties[prop]))
                elif prop == 'tcp_matchType':
                    current_tcp_match_type = apiconnection.getSelected(healthcheck[prop])
                    if current_tcp_match_type != healthcheck_tcp_match_type:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, current_tcp_match_type, desired_properties[prop]))
                else:
                    # catch all other properties
                    if healthcheck[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, healthcheck[prop], desired_properties[prop]))

            if not needs_change:
                result = {'changed': False, 'msg': ['Healthcheck already present: %s' %healthcheck_name, additional_msg]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.updateObject('healthcheck', healthcheck_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Healthcheck %s must be changed.' %healthcheck_name, additional_msg]}
        else:
            if not module.check_mode:
                additional_msg.append(apiconnection.createObject('healthcheck', healthcheck_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Healthcheck %s must be created.' %healthcheck_name, additional_msg]}
    else:
        if healthcheck_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.deleteObject('healthcheck', healthcheck_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Healthcheck %s must be deleted.' %healthcheck_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Healthcheck %s is not present.' %healthcheck_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
