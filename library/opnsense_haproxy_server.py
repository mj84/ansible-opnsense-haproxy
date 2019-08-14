#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

DOCUMENTATION =r'''
---
module: opnsense_haproxy_server
short_description: Manage HAProxy servers on Opnsense
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
            server_enabled=dict(type='bool', default=True),
            server_name=dict(type='str', required=True),
            server_address=dict(type='str', default=True),
            server_description=dict(type='str', default=''),
            server_port=dict(type='str', required=True),
            server_checkport=dict(type='str', default=''),
            server_mode=dict(type='str', default='active'),
            server_ssl=dict(type='bool', default=False),
            server_ssl_verify=dict(type='bool', default=True),
            server_ssl_ca=dict(type='list', default=[]),
            server_ssl_crl=dict(type='str', default=''),
            server_ssl_client_certificate=dict(type='str', default=''),
            server_weight=dict(type='str', default=''),
            server_check_interval=dict(type='str', default=''),
            server_check_down_interval=dict(type='str', default=''),
            server_source=dict(type='str', default=''),
            server_advanced=dict(type='str', default=''),
            server_state=dict(type='str', choices=['present', 'absent'], default='present'),
            haproxy_reload=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )
    haproxy_reload = module.params['haproxy_reload']
    # Prepare properties of server
    server_enabled = module.params['server_enabled']
    server_name = module.params['server_name']
    server_description = module.params['server_description']
    server_address = module.params['server_address']
    server_port = module.params['server_port']
    server_checkport = module.params['server_port']
    server_mode = module.params['server_mode']
    server_ssl = module.params['server_ssl']
    server_ssl_verify = module.params['server_ssl_verify']
    server_ssl_ca = module.params['server_ssl_ca']
    server_ssl_crl = module.params['server_ssl_crl']
    server_ssl_client_certificate = module.params['server_ssl_client_certificate']
    server_weight = module.params['server_weight']
    server_check_interval = module.params['server_check_interval']
    server_check_down_interval = module.params['server_check_down_interval']
    server_source = module.params['server_source']
    server_advanced = module.params['server_advanced']
    server_state = module.params['server_state']
    server_description = module.params['server_description']
    # Instantiate API connection
    url = module.params['url']
    auth = (module.params['api_key'], module.params['api_secret'])
    ssl_verify = module.params['ssl_verify']
    apiconnection = OpnsenseApi.Haproxy(url, auth, ssl_verify)

    # Fetch list of servers
    servers = apiconnection.listServers()

    # Build dict with desired state
    desired_properties = {
        'name': server_name,
        'address': server_address,
        'description': server_description,
        'port': server_port,
        'checkport': server_checkport,
        'mode': server_mode,
        'ssl': str(int(server_ssl)),
        'sslVerify': str(int(server_ssl_verify)),
        'sslCA': server_ssl_ca,
        'sslCRL': server_ssl_crl,
        'sslClientCertificate': server_ssl_client_certificate,
        'weight': server_weight,
        'checkInterval': server_check_interval,
        'checkDownInterval': server_check_down_interval,
        'source': server_source,
        'advanced': server_advanced,
    }
    # Prepare dict with properties needing change
    changed_properties = {}
    # Prepare result dict
    result = {}
    additional_msg = []
    # Initialize some control vars
    needs_change = False
    uuid = ''
    # Check if server object with specified name exists
    for server in servers:
        if server['name'] == server_name:
            server_exists = True
            uuid = server['uuid']
            break
    server_exists = (uuid != '')

    if server_state == 'present':
        if server_exists:
            server = apiconnection.getObjectByName('server', server_name)
            #for prop in ['code', 'content', 'description']:
            for prop in desired_properties.keys():
                # Special case for mode where selected element must be determined
                if prop == 'mode':
                    current_mode = apiconnection.getSelected(server[prop])
                    if current_mode != server_mode:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing mode: %s => %s' %(current_mode, server_mode))
                # Special case for sslCA where a list must be compared to a dict
                elif prop == 'sslCA':
                    # Get current list of selected CAs by their name
                    current_ssl_ca = apiconnection.getSelectedList(server[prop])
                    # Build list with keys of desired CAs
                    desired_ssl_ca = []
                    # Search the ids of desired ssl_ca names
                    for ca in server_ssl_ca:
                        ca_key = apiconnection.findValueInDict(
                            server[prop],
                            searchvalue=ca
                        )
                        if ca_key != '':
                            desired_ssl_ca.append(ca_key)
                    # Compare current and desired list of CA names
                    if not apiconnection.compareLists(current_ssl_ca, server_ssl_ca):
                        needs_change = True
                        changed_properties['sslCA'] = ','.join(desired_ssl_ca)
                        additional_msg.append('Changing sslCA: %s => %s' % (current_ssl_ca, desired_ssl_ca))
                # Special case for sslCRL where a list must be compared to a dict
                elif prop == 'sslCRL':
                    current_ssl_crl = apiconnection.getSelected(server[prop])
                    # Find id of sslCRL with desired name
                    desired_ssl_crl = apiconnection.findValueInDict(server[prop], searchvalue=server_ssl_crl)
                    if not current_ssl_crl == desired_ssl_crl:
                        needs_change = True
                        changed_properties['sslCRL'] = desired_ssl_crl
                        additional_msg.append('Changing sslCRL: %s => %s' % (current_ssl_crl, server_ssl_crl))
                # Special case for sslClientCertificate where a single object must be determined from a list
                elif prop == 'sslClientCertificate':
                    current_ssl_client_certificate = apiconnection.getSelected(server[prop], retval='value')
                    if current_ssl_client_certificate != server_ssl_client_certificate:
                        needs_change = True
                        desired_ssl_client_certificate = apiconnection.findValueInDict(
                            server[prop],
                            searchvalue=server_ssl_client_certificate                           
                        )
                        changed_properties['sslClientCertificate'] = desired_ssl_client_certificate
                        additional_msg.append('Changing sslClientCertificate: %s => %s' % (current_ssl_client_certificate, server_ssl_client_certificate))
                # Standard case for regular simple values
                else:
                    if server[prop] != desired_properties[prop]:
                        needs_change = True
                        changed_properties[prop] = desired_properties[prop]
                        additional_msg.append('Changing %s: %s => %s' %(prop, server[prop], desired_properties[prop]))
            if not needs_change:
                result = {'changed': False, 'msg': ['Server already present: %s' %server_name, additional_msg]}
            else:
                if not module.check_mode:
                    additional_msg.append(apiconnection.setServer(server_name, changed_properties))
                    if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
                result = {'changed': True, 'msg': ['Server %s must be changed.' %server_name, additional_msg]}
        else:
            if not module.check_mode:
                # clear parameters sslCA, sslCRL and sslClientCertificate, because we can't get their available ids at this time
                desired_properties['sslCA'] = ''
                desired_properties['sslCRL'] = ''
                desired_properties['sslClientCertificate'] = ''
                additional_msg.append(apiconnection.addServer(server_name, desired_properties))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Server %s must be created.' %server_name, additional_msg]}
    else:
        if server_exists:
            if not module.check_mode:
                additional_msg.append(apiconnection.delServer(server_name))
                if haproxy_reload: additional_msg.append(apiconnection.applyConfig())
            result = {'changed': True, 'msg': ['Server %s must be deleted.' %server_name, additional_msg]}
        else:
            result = {'changed': False, 'msg': ['Server %s is not present.' %server_name]}

    module.exit_json(**result)


if __name__ == '__main__':
    main()
