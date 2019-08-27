Role Name
=========

This Ansible role is meant for managing HAProxy installations running as a plugin on OPNsense firewalls (see https://opnsense.org)

The configuration occurs via the OPNsene API and as of now the following HAProxy datatypes can be managed:

* ACLs (Conditions)
* Actions (Rules)
* Errorfiles (Error Messages)
* Frontends (Public Services)
* Groups
* LUA services
* Maps (Map Files)
* Servers
* Users

The goal of this role is to be feature-complete, so the following datatypes are currently being implemented:

* Backend Pools
* CPUs (CPU Affinity Rules)
* Healthchecks

Requirements
------------

No role dependencies from Ansible Galaxy or elsewhere. You only need python requests (currently 2.x) on the executing node.
I recommend delegating the tasks to your Ansible master.

OPNsense internally organizes its API objects with a UUID. 
These UUIDs are not very human-readable (and can also not be specified by the user).
So every object of every type gets managed through its name, which therefore has to be unique (which I would recommend anyway).

Also, the order of objects has to be correct.
For example, when managing an Action (Rule), the necessary ACLs (Conditions) must already be present on the system.
The tasks in tasks/main.yml file should already take care of this.

Limitations
--------------

As of now, the following object types cannot be queried directly through the OPNsense API:

* SSL CAs
* SSL CRLs
* SSL Client Certificates

Since these objects are also addressed through an internal id, these ids are unknown at creation time of an object which references these object types (such as a server object).
As of now, when one of these parameters should be set, the task for managing e.g. a server needs to run twice:

1. Create the server object with every parameter but SSL CA, SSL CRL or SSL Client Certificate.
2. Update the server object and reference these other objects.

Update 2019-08-26:
While implementing support for frontend objects, I can get the SSL object id's by retrieving an empty frontend object.
This functionality needs to be ported to other data types using SSL objects.


Order of lists:  
The included Ansible modules take the order of elements within a list into account (e.g. for linked actions or SSL certificates).
However, the order of elements in a list, is not always being reflected through the OPNsense API (might be a bug).  
Therefore, only the actual elements in a list are being compared, not the order of elements.  
If the order of elements needs to be changed, I recommend doing a dummy change by adding or removing an element (and reversing that dummy change).

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
