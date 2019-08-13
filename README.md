Role Name
=========

This Ansible role is meant for managing HAProxy installations running as a plugin on OPNsense firewalls (see https://opnsense.org)

The configuration occurs via the OPNsene API and as of now the following HAProxy datatypes can be managed:

* ACLs (Conditions)
* Actions (Rules)
* Errorfiles (Error Messages)
* Users

The goal of this role is to be feature-complete, so the following datatypes are currently being implemented:

* Backend Pools
* Frontends (Public Services)
* Groups
* Healthchecks
* LUA services
* Servers

Requirements
------------

No role dependencies from Ansible Galaxy or elsewhere. You only need python requests (currently 2.x) on the executing node.
I recommend delegating the tasks to your Ansible master.

Role Variables
--------------

These are quite a lot and will follow soon.


Example Playbook
----------------

Will also follow soon.

License
-------

I don't know yet. Copying for private purposes is fine.

Author Information
------------------

Markus Joosten
