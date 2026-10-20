#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mock of the OPNsense HAProxy settings API.

The role talks to a real firewall through the plugin's settings endpoints. This
module reproduces just enough of those endpoints to run the role end to end
without a firewall, and it reproduces the shapes that make the role's diffing
logic non-obvious:

* ``get<type>`` with an empty UUID returns the *empty object template*, whose
  selectable fields hold the full catalog of every object the field can point
  at. The modules use it to resolve names to UUIDs.
* A single-choice field is not a plain string in a response. It comes back as
  ``{"<option>": {"selected": "1", "value": "..."}}`` with the chosen option
  flagged, and the flag is the **string** ``"1"``, not the int ``1``.
* ``configtest`` and ``reconfigure`` answer with a plain string in ``result``.

Run standalone for manual experiments::

    python tests/mock_api/server.py 8761

The pytest suite in ``tests/e2e/`` starts it in a thread on an ephemeral port.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
import re
import threading
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer

# Object types the role manages, used for the /search<type>s endpoints.
OBJECT_TYPES = [
    'acl', 'action', 'cpu', 'backend', 'errorfile', 'frontend', 'group',
    'healthcheck', 'lua', 'mapfile', 'server', 'user',
]

# SSL objects live on the firewall already; the role only points at them.
SEEDED = {
    'sslca': {'ca-001': {'name': 'my_ca'}},
    'sslcrl': {'crl-001': {'name': 'my_crl'}},
    'sslcert': {'cert-001': {'name': 'my_cert'}},
}

# Field name -> the object type its value refers to.
CATALOG_KEYS = {
    'linkedServers': 'server',
    'linkedAcls': 'acl',
    'linkedActions': 'action',
    'linkedCpuAffinityRules': 'cpu',
    'linkedErrorfiles': 'errorfile',
    'healthCheck': 'healthcheck',
    'members': 'user',
    'basicAuthUsers': 'user',
    'basicAuthGroups': 'group',
    'ssl_certificates': 'sslcert',
    'ssl_default_certificate': 'sslcert',
    'ssl_clientAuthCAs': 'sslca',
    'ssl_clientAuthCRLs': 'sslcrl',
    'allowedUsers': 'user',
    'allowedGroups': 'group',
    'queryBackend': 'backend',
    'defaultBackend': 'backend',
    'use_backend': 'backend',
    'map_use_backend': 'backend',
    'use_server': 'server',
    'nbsrv_backend': 'backend',
    'sslCA': 'sslca',
    'sslCRL': 'sslcrl',
    'sslClientCertificate': 'sslcert',
}

# Fields the API reports as a selection dict rather than a plain string.
# Multi-value fields carry one entry per comma-separated part.
ENUM_FIELDS = {
    'expression', 'mode', 'algorithm', 'proxyProtocol', 'persistence',
    'persistence_cookiemode', 'stickiness_pattern', 'tuning_httpreuse',
    'stickiness_dataTypes', 'ssl_bindOptions', 'connectionBehaviour',
    'ssl_clientAuthVerify', 'testType', 'operator', 'type', 'http_method',
    'http_version', 'http_expression', 'tcp_matchType', 'process_id',
    'thread_id',
    'src_bytes_in_rate_comparison', 'src_bytes_out_rate_comparison',
    'src_conn_cnt_comparison', 'src_conn_rate_comparison',
    'src_http_err_cnt_comparison', 'src_http_err_rate_comparison',
    'src_http_req_rate_comparison', 'src_kbytes_in_comparison',
    'src_kbytes_out_comparison', 'src_port_comparison',
    'src_sess_cnt_comparison',
}

GET_SEARCH = re.compile(r'^/api/haproxy/settings/search(\w+)s$')
GET_OBJECT = re.compile(r'^/api/haproxy/settings/get(\w+)/([\w-]*)$')
POST_ADD = re.compile(r'^/api/haproxy/settings/add(\w+)$')
POST_SET = re.compile(r'^/api/haproxy/settings/set(\w+)/([\w-]+)$')
POST_DEL = re.compile(r'^/api/haproxy/settings/del(\w+)/([\w-]+)$')


def _parts(value):
    """Split a comma-joined stored value into its non-empty parts."""
    return [part for part in value.split(',') if part]


class MockHaproxyApi(object):
    """In-memory HAProxy settings API plus the HTTP layer in front of it."""

    def __init__(self):
        self.state = defaultdict(dict)  # type -> {uuid: {property: value}}
        self.requests = []              # every request, for assertions
        self._serial = 0
        for otype, objects in SEEDED.items():
            self.state[otype] = dict(objects)
        self._server = None
        self._thread = None

    # -- lifecycle ---------------------------------------------------------

    def start(self):
        """Serve on an ephemeral localhost port and return that port."""
        handler = _Handler.for_api(self)
        self._server = HTTPServer(('127.0.0.1', 0), handler)
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()
        return self.port

    def stop(self):
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._thread.join(timeout=5)
            self._server = None
            self._thread = None

    @property
    def port(self):
        return self._server.server_address[1]

    # -- state inspection, for tests ---------------------------------------

    def objects(self, otype):
        """Stored properties of every object of a type, keyed by UUID."""
        return self.state[otype]

    def by_name(self, otype, name):
        """The one stored object with that name, or None."""
        found = [p for p in self.state[otype].values() if p.get('name') == name]
        return found[0] if found else None

    def uuid_of(self, otype, name):
        """The UUID the API gave the object with that name, or None."""
        for uuid, props in self.state[otype].items():
            if props.get('name') == name:
                return uuid
        return None

    def paths(self, method=None):
        """Request paths, optionally filtered by HTTP method."""
        return [r['path'] for r in self.requests if method is None or r['method'] == method]

    def new_uuid(self):
        self._serial += 1
        return 'uuid-%03d' % self._serial

    # -- request handling --------------------------------------------------

    def handle_get(self, path):
        self.requests.append({'method': 'GET', 'path': path})

        match = GET_SEARCH.match(path)
        if match:
            objects = self.state[match.group(1)]
            rows = [{'uuid': uuid, 'name': props.get('name', '')}
                    for uuid, props in objects.items()]
            return {'rows': rows, 'total': len(rows)}, 200

        match = GET_OBJECT.match(path)
        if match:
            otype, uuid = match.groups()
            if uuid == '':
                # Empty-object template: the catalog of everything selectable.
                return {otype: self.template_catalogs()}, 200
            obj = self.state[otype].get(uuid)
            if obj is None:
                return {'status': 'not found'}, 404
            return {otype: self.render(obj)}, 200

        return {'error': 'unhandled GET %s' % path}, 400

    def handle_post(self, path, body):
        self.requests.append({'method': 'POST', 'path': path, 'body': body})

        match = POST_ADD.match(path)
        if match:
            props = body.get(match.group(1), {})
            uuid = self.new_uuid()
            self.state[match.group(1)][uuid] = dict(props)
            return {'result': {'uuid': uuid}}, 200

        match = POST_SET.match(path)
        if match:
            otype, uuid = match.groups()
            self.state[otype].setdefault(uuid, {}).update(body.get(otype, {}))
            return {'result': {'saved': 'true'}}, 200

        match = POST_DEL.match(path)
        if match:
            self.state[match.group(1)].pop(match.group(2), None)
            return {'result': {'deleted': 'true'}}, 200

        if path == '/api/haproxy/service/configtest':
            return {'result': 'Config file is valid, no changes needed.'}, 200
        if path == '/api/haproxy/service/reconfigure':
            return {'result': 'OK'}, 200

        return {'error': 'unhandled POST %s' % path}, 400

    # -- API shapes --------------------------------------------------------

    def template_catalogs(self):
        """The empty-object template: every selectable field as a catalog."""
        catalogs = defaultdict(dict)
        for key in CATALOG_KEYS:
            catalogs[key]  # present even when nothing refers to it yet
        for key, otype in CATALOG_KEYS.items():
            for uuid, props in self.state[otype].items():
                catalogs[key][uuid] = {'value': props.get('name', ''), 'selected': 0}
        return dict(catalogs)

    def render(self, props):
        """Stored properties in the shape the real API reports them."""
        out = {}
        for key, value in props.items():
            if key in CATALOG_KEYS and isinstance(value, str) and value != '':
                out[key] = {}
                for uid in _parts(value):
                    name = self.state[CATALOG_KEYS[key]].get(uid, {}).get('name', uid)
                    out[key][uid] = {'selected': '1', 'value': name, 'name': name}
            elif key in ENUM_FIELDS and isinstance(value, str) and value != '':
                out[key] = {part: {'selected': '1', 'value': part} for part in _parts(value)}
            else:
                out[key] = value
        return out


class _Handler(BaseHTTPRequestHandler):
    """Thin HTTP layer over a MockHaproxyApi instance."""

    def __init__(self, api, *args):
        self.api = api
        # BaseHTTPRequestHandler handles the request inside __init__.
        BaseHTTPRequestHandler.__init__(self, *args)

    @classmethod
    def for_api(cls, api):
        def factory(*args):
            return cls(api, *args)
        return factory

    def log_message(self, *args):
        pass

    def _send(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get('Content-Length') or 0)
        return json.loads(self.rfile.read(length) or b'{}')

    def do_GET(self):
        payload, code = self.api.handle_get(self.path)
        self._send(payload, code)

    def do_POST(self):
        payload, code = self.api.handle_post(self.path, self._body())
        self._send(payload, code)

    def do_PUT(self):
        self.do_POST()


if __name__ == '__main__':
    import sys

    api = MockHaproxyApi()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8761
    server = HTTPServer(('127.0.0.1', port), _Handler.for_api(api))
    print('Mock OPNsense HAProxy API on http://127.0.0.1:%d' % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
