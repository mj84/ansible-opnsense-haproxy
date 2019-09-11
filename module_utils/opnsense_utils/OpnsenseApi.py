#!/usr/bin/python# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Markus Joosten https://github.com/mj84
from __future__ import absolute_import, division, print_function

import requests
import json
from collections import OrderedDict

class Haproxy:
    def __init__(self, url, auth, ssl_verify):
        self.url = url
        self.auth = auth
        self.ssl_verify = ssl_verify
        self.objecttypes = ['acl', 'action', 'cpu', 'backend', 'errorfile', 'frontend', 'group', 'healthcheck', 'lua', 'mapfile', 'server', 'user']
        if not self.ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def getRequest(self, url):
        r = requests.get(url, auth=self.auth, verify=self.ssl_verify)
        # We need to parse the JSON response as an OrderedDict, so we can preserve the order of some properties
        r_ordered = json.loads(r.content, object_pairs_hook=OrderedDict)
        return r_ordered

    def postRequest(self, url, data):
        r = requests.post(url, auth=self.auth, verify=self.ssl_verify, json=data)
        r_json = r.json()
        #print(data)
        # maybe need some better status checking here
        if ('result' in r_json and 'failed' in r_json['result']) or 'errorMessage' in r_json:
            raise ValueError('API threw an error: %s' % r_json)
        return r_json

    def getUuidByName(self, objecttype, name):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        if name == '':
            return ''
        objects = []
        objects = self.listObjects(objecttype)
        for obj in objects:
            if obj['name'] == name:
                return obj['uuid']
        raise KeyError('Found no object of type %s with name %s!' %(objecttype, name))

    def getSslObjectKeys(self, ssl_objects, names):
        ssl_object_keys = []
        for name in names:
            ssl_object_key = self.findValueInDict(ssl_objects, name)
            if ssl_object_key == '':
                raise KeyError('No SSL object with name %s', name)
            else:
                ssl_object_keys.append(ssl_object_key)
        return ssl_object_keys

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

    def getSelectedList(self, valuesdict, retval='value'):
        selected_items = []
        # Catch empty list, which is specified as an actual JSON list
        if type(valuesdict) == list and valuesdict == []:
            return []
        for key, value in valuesdict.iteritems():
            if value['selected'] == 1:
                if retval == 'key':
                    selected_items.append(key)
                else:
                    if not retval in value:
                        raise KeyError('%s is no key in dict %s' %(retval, value))
                    selected_items.append(value[retval])
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

    def compareLists(self, list_one, list_two, order_sensitive=False):
        # This function compares if two lists contain the same elements.
        # If necessary, the order can be checked as well.
        lists_match = True
        # Check if list_two contains elements not in list_one
        for item in list_two:
            if item not in list_one:
                lists_match = False
        # Check if list_one contains elements not in list_two
        for item in list_one:
            if item not in list_two:
                lists_match = False
        # If order is relevant, check if both lists are identical
        if lists_match and order_sensitive:
            if list_one != list_two:
                lists_match = False
        return lists_match

    def getUuidsFromNames(self, objecttype, names):
        uuid_list = []
        for name in names:
            uuid = self.getUuidByName(objecttype, name)
            uuid_list.append(uuid)
        return uuid_list

    def getSelectedKeysFromDict(self, objs):
        selected_items = []
        for key, value in objs.iteritems():
            if 'selected' in value and value['selected'] == '1':
                selected_items.append(key)
        return selected_items

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
        #objs = self.getRequest(url)
        objs = dict(self.getRequest(url))
        return objs['rows']

    def getObjectByName(self, objecttype, name):
        uuid = self.getUuidByName(objecttype, name)
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        #obj = self.getRequest(url)[objecttype]
        obj = dict(self.getRequest(url)[objecttype])
        return obj

    def getObjectByUuid(self, objecttype, uuid):
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        #obj = self.getRequest(url)[objecttype]
        obj = dict(self.getRequest(url)[objecttype])
        return obj

    def updateObject(self, objecttype, objectname, obj):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        uuid = self.getUuidByName(objecttype, objectname)
        url = self.url + '/api/haproxy/settings/set' + objecttype + '/' + uuid
        objdict = {objecttype: obj}
        response = self.postRequest(url, objdict)
        return  response
