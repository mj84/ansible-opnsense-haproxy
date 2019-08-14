#!/usr/bin/python# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

import requests
import json

class Haproxy:
    def __init__(self, url, auth, ssl_verify):
        self.url = url
        self.auth = auth
        self.ssl_verify = ssl_verify
        self.objecttypes = ['acl', 'action', 'backend', 'errorfile', 'frontend', 'healthcheck', 'lua', 'server', 'user']
        if not self.ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def getRequest(self, url):
        r = requests.get(url, auth=self.auth, verify=self.ssl_verify)
        return r.json()

    def postRequest(self, url, data):
        r = requests.post(url, auth=self.auth, verify=self.ssl_verify, json=data)
        r_json = r.json()
        # maybe need some better status checking here
        if 'result' in r_json and 'failed' in r_json['result']:
            raise ValueError('API threw an error: %s' % r_json)
        return r_json

    def getUuidByName(self, objecttype, name):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        objects = []
        objects = self.listObjects(objecttype)
        for obj in objects:
            if obj['name'] == name:
                return obj['uuid']
        raise KeyError('Found no object of type %s with name %s!' %(objecttype, name))

    def getSelected(self, valuesdict, retval='key'):
        for key, value in valuesdict.iteritems():
            if value['selected'] == 1:
                if retval == 'key':
                    return key
                else:
                    if retval not in value:
                        raise KeyError('%s is no key in dict %s' %(retval, value))
                    return value[retval]
        return ''

    def getSelectedList(self, valuesdict):
        selected_items = []
        for key, value in valuesdict.iteritems():
            if value['selected'] == 1:
                selected_items.append(value['value'])
        return selected_items

    def findValueInDict(self, valuesdict, searchvalue, prop='value', retval='key'):
        for key, value in valuesdict.iteritems():
            if prop in value and value[prop] == searchvalue:
                if retval == 'key':
                    return key
                else:
                    if retval not in value:
                        raise KeyError('%s is no key in dict %s' %(retval, value))
                    return value[retval]
        return ''        

    def compareLists(self, list_one, list_two):
        lists_match = True
        # Check if list_two contains elements not in list_one
        for item in list_two:
            if item not in list_one:
                lists_match = False
        # Check if list_one contains elements not in list_two
        for item in list_one:
            if item not in list_two:
                lists_match = False
        return lists_match

    def getCommaSeparatedUuidsFromListOfNames(self, objecttype, names):
        uuid_list = []
        for name in names:
            uuid = self.getUuidByName(objecttype, name)
            uuid_list.append(uuid)
        return ','.join(uuid_list)

    def getCommaSeparatedSelectedKeysFromDict(self, objs):
        selected_items = []
        for key, value in objs.iteritems():
            if 'selected' in value and value['selected'] == '1':
                selected_items.append(key)
        return ','.join(selected_items)

    def applyConfig(self):
        configtesturl = self.url + '/api/haproxy/service/configtest'
        reconfigureurl = self.url + '/api/haproxy/service/reconfigure'
        configtest = self.postRequest(configtesturl, {})
        if 'is valid' in configtest['result']:
            reconfigure = self.postRequest(reconfigureurl, {})
            return configtest, reconfigure
        else:
            raise ValueError('Configtest did not succeed!')

    def createObject(self, objecttype, objectname, properties):
        properties['name'] = objectname
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        url = self.url + '/api/haproxy/settings/add' + objecttype
        obj = {objecttype: properties}
        response = self.postRequest(url, obj)
        #return 'createObject sending object data: %s' % obj, 'to url: %s' % url, 'createObject received response: ', response
        return response

    def deleteObject(self, objecttype, objectname):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        uuid = self.getUuidByName(objecttype, objectname)
        url = self.url + '/api/haproxy/settings/del' + objecttype + '/' + uuid
        response = self.postRequest(url, {})
        return response

    def listObjects(self, objecttype):
        if objecttype not in self.objecttypes:
            raise KeyError('%s is no valid object type!' % objecttype)
        url = self.url + '/api/haproxy/settings/search' + str(objecttype) + 's'
        objs = self.getRequest(url)
        return objs['rows']

    def getObjectByName(self, objecttype, name):
        uuid = self.getUuidByName(objecttype, name)
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        obj = self.getRequest(url)[objecttype]
        return obj

    def getObjectByUuid(self, objecttype, uuid):
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        obj = self.getRequest(url)[objecttype]
        return obj

    def updateObject(self, objecttype, objectname, obj):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        uuid = self.getUuidByName(objecttype, objectname)
        url = self.url + '/api/haproxy/settings/set' + objecttype + '/' + uuid
        response = self.postRequest(url, obj)
        return  response
