# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = '0.0.1'

import frappe,json
from frappe import _
from vlog import vwrite

@frappe.whitelist()
def lead_hook_create__google_contact(lead,method):
    lead_name = lead.__dict__.get("lead_name")
    mobile_no = lead.__dict__.get("mobile_no")
    owner = lead.__dict__.get("owner")
    from pygcontacts import pre_queue_contact
    contact = {
        "name": lead_name,
        "mobile": mobile_no
    }
    pre_queue_contact(contact,owner)