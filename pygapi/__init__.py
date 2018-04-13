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
    status = lead.__dict__.get("status")
    prefix_name = ""
    if status=="Open":
        prefix_name = "New - "
    else:
        prefix_name = "%s - " % status
    interested_in = lead.__dict__.get("interested_in")
    if interested_in:
        prefix_name = "%s%s - " % (prefix_name,interested_in)
    lead_name = "%s%s" %(prefix_name,lead_name)
    owner = lead.__dict__.get("owner")
    from pygcontacts import pre_queue_contact
    contact = {
        "name": lead_name,
        "mobile": mobile_no
    }
    pre_queue_contact(contact,owner)