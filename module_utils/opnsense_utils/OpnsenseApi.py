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
        #return 'postRequest posting data: %s' % json.dumps(data), 'to url: ', url, 'postRequest received json: ', r.json()
        r_json = r.json()
        # maybe need some better status checking here
        if 'result' in r_json and 'failed' in r_json['result']:
            raise ValueError('API threw an error: %s' % r_json)
        return r_json

    def getUuidByName(self, objecttype, name):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        objects = []
        if objecttype == 'acl':
            objects = self.listAcls()
        elif objecttype == 'action':
            objects = self.listActions()
        elif objecttype == 'backend':
            objects = self.listBackends()
        elif objecttype == 'errorfile':
            objects = self.listErrorfiles()
        elif objecttype == 'frontend':
            objects = self.listFrontends()
        elif objecttype == 'healthcheck':
            objects = self.listHealthchecks()
        elif objecttype == 'lua':
            objects = self.listLuas()
        elif objecttype == 'server':
            objects = self.listServers()
        elif objecttype == 'user':
            objects = self.listUsers()
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

    def createObject(self, objecttype, properties):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        url = self.url + '/api/haproxy/settings/add' + objecttype
        obj = {objecttype: properties}
        response = self.postRequest(url, obj)
        #return 'createObject sending object data: %s' % obj, 'to url: %s' % url, 'createObject received response: ', response
        return response

    def deleteObject(self, objecttype, uuid):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        url = self.url + '/api/haproxy/settings/del' + objecttype + '/' + uuid
        response = self.postRequest(url, {})
        return response

    def getObjectByName(self, objecttype, name):
        uuid = self.getUuidByName(objecttype, name)
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        obj = self.getRequest(url)[objecttype]
        return obj

    def getObjectByUuid(self, objecttype, uuid):
        url = self.url + '/api/haproxy/settings/get' + objecttype + '/' + uuid
        obj = self.getRequest(url)[objecttype]
        return obj

    def updateObject(self, objecttype, uuid, obj):
        if objecttype not in self.objecttypes:
            raise KeyError('Objecttype %s not supported!' % objecttype)
        url = self.url + '/api/haproxy/settings/set' + objecttype + '/' + uuid
        response = self.postRequest(url, obj)
        #return 'updateObject sending object data: %s' % obj, 'to url: %s' % url, 'updateObject received response: ', response
        return  response

    def addAcl(self, aclname, properties):
        properties['name'] = aclname
        response = self.createObject('acl', properties)
        return response

    def delAcl(self, aclname):
        uuid = self.getUuidByName('acl', aclname)
        response = self.deleteObject('acl', uuid)
        return response

    def listAcls(self):
        url = self.url + '/api/haproxy/settings/searchacls'
        acls = self.getRequest(url)
        return acls['rows']

    def setAcl(self, aclname, properties):
        uuid = self.getUuidByName('acl', aclname)
        obj = {'acl': properties}
        response = self.updateObject('acl', uuid, obj)
        return response

    def addAction(self, actionname, properties):
        properties['name'] = actionname
        response = self.createObject('action', properties)
        return response

    def delAction(self, actionname):
        uuid = self.getUuidByName('action', actionname)
        response = self.deleteObject('action', uuid)
        return response

    def listActions(self):
        url = self.url + '/api/haproxy/settings/searchactions'
        actions = self.getRequest(url)
        return actions['rows']

    def setAction(self, actionname, properties):
        uuid = self.getUuidByName('action', actionname)
        obj = {'action': properties}
        response = self.updateObject('action', uuid, obj)
        return response

    def listBackends(self):
        url = self.url + '/api/haproxy/settings/searchbackends'
        backends = self.getRequest(url)
        return backends['rows']

    def addErrorfile(self, errorfilename, properties):
        properties['name'] = errorfilename
        response = self.createObject('errorfile', properties)
        return response

    def delErrorfile(self, errorfilename):
        uuid = self.getUuidByName('errorfile', errorfilename)
        response = self.deleteObject('errorfile', uuid)
        return response

    def listErrorfiles(self):
        url = self.url + '/api/haproxy/settings/searcherrorfiles'
        errorfiles = self.getRequest(url)['rows']
        return errorfiles

    def setErrorfile(self, errorfilename, properties):
        uuid = self.getUuidByName('errorfile', errorfilename)
        obj = {'errorfile': properties}
        response = self.updateObject('errorfile', uuid, obj)
        return response

    def listFrontends(self):
        url = self.url + '/api/haproxy/settings/searchfrontends'
        frontends = self.getRequest(url)
        return frontends['rows']

    def listHealthchecks(self):
        url = self.url + '/api/haproxy/settings/searchhealthchecks'
        healthchecks = self.getRequest(url)
        return healthchecks['rows']

    def addLua(self, luaname, properties):
        properties['name'] = luaname
        response = self.createObject('lua', properties)
        return response

    def delLua(self, luaname):
        uuid = self.getUuidByName('lua', luaname)
        response = self.deleteObject('lua', uuid)
        return response

    def listLuas(self):
        url = self.url + '/api/haproxy/settings/searchluas'
        luas = self.getRequest(url)
        return luas['rows']

    def setLua(self, luaname, properties):
        uuid = self.getUuidByName('lua', luaname)
        obj = {'lua': properties}
        response = self.updateObject('lua', uuid, obj)
        return response

    def addServer(self, servername, properties):
        properties['name'] = servername
        response = self.createObject('server', properties)
        return response

    def delServer(self, servername):
        uuid = self.getUuidByName('server', servername)
        response = self.deleteObject('server', uuid)
        return response

    def listServers(self):
        url = self.url + '/api/haproxy/settings/searchservers'
        servers = self.getRequest(url)
        return servers['rows']

    def setServer(self, servername, properties):
        uuid = self.getUuidByName('server', servername)
        obj = {'server': properties}
        response = self.updateObject('server', uuid, obj)
        return response

    def addUser(self, username, properties):
        properties['name'] = username
        response = self.createObject('user', properties)
        return response

    def delUser(self, username):
        uuid = self.getUuidByName('user', username)
        response = self.deleteObject('user', uuid)
        return response

    def listUsers(self):
        url = self.url + '/api/haproxy/settings/searchusers'
        users = self.getRequest(url)
        return users['rows']

    def setUser(self, username, properties):
        uuid = self.getUuidByName('user', username)
        obj = {'user': properties}
        response = self.updateObject('user', uuid, obj)
        return response
