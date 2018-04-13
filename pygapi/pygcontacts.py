import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from globalconstants import *
import frappe
from .vlog import vwrite
# Note. If you need to change permissions like scope, you need to delete info.dat file to update the new permissions

# Helpful URLs
# https://developers.google.com/people/api/rest/v1/people.connections/list
# https://developers.google.com/apis-explorer/?hl=en_US#p/people/v1/people.people.createContact
# https://developers.google.com/people/
# https://developers.google.com/people/v1/read-people
# https://developers.google.com/api-client-library/python/



# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for
# installed applications.
#
# Go to the Google API Console, open your application's
# credentials page, and copy the client ID and client secret.
# Then paste them into the following code.
google_settings = frappe.get_doc("Google Account Setup")
FLOW = OAuth2WebServerFlow(
    # client_id=google_settings.client_id,
    # client_secret=google_settings.client_secret,
    client_id="686828027298-s4q9dgv7muifiivn323v4up28cqopuhr.apps.googleusercontent.com", # visheshhanda
    client_secret="WZ3biLU9yWtJAKcMKiu4GqOd",
    
    scope=YOUR_SCOPE,
    user_agent=YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION)

# If the Credentials don't exist or are invalid, run through the
# installed application flow. The Storage object will ensure that,
# if successful, the good Credentials will get written back to a
# file.
storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/visheshhanda.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = tools.run_flow(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and
# authorize it with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API.
people_service = build(serviceName='people', version='v1', http=http)

@frappe.whitelist()
def get_access_to_account(owner=None):
  # get default google account for the owner
  pre_queued_contacts = frappe.get_all('ERPNext Mobile Addon Users',
		filters={"username":owner},
		fields = ["google_account"],
    order_by = 'modified desc')
  if len(pre_queued_contacts) > 0:
    account = pre_queued_contacts[0].get("google_account")
  else:
    account = "sales@usedyetnew.com"
  if account == "visheshhanda@usedyetnew.com":
    storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/visheshhanda.dat')
  elif account == "care@usedyetnew.com":
    storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/care.dat')
  elif account == "sales@usedyetnew.com":
    storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/sales.dat')
  elif account == "marketing@usedyetnew.com":
    storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/marketing.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    credentials = tools.run_flow(FLOW, storage)
  http = httplib2.Http()
  http = credentials.authorize(http)
  people_service = build(serviceName='people', version='v1', http=http)
  return people_service

@frappe.whitelist()
def process_pre_queued_contacts():
  pre_queued_contacts = frappe.get_all('Pre Queue Google Contacts',
		filters={"status":"queued"},
		fields = ["name", "contact_name", "mobile", "status"],
    order_by = 'modified asc')
  # for selective google account access, filtering by owner
  owner_sql = "SELECT DISTINCT owner FROM `tabPre Queue Google Contacts` WHERE status='queued' group by owner order by creation desc"
  owner_res = frappe.db.sql(owner_sql, as_dict=1)
  for owner_obj in owner_res:
    pre_queued_contacts_sql = "SELECT DISTINCT mobile, name, contact_name, status, owner FROM `tabPre Queue Google Contacts` WHERE status='queued' and owner='%s' group by mobile order by creation desc" % owner_obj.get("owner")
    pre_queued_contacts = frappe.db.sql(pre_queued_contacts_sql, as_dict=1)
    google_contacts = fetch_contacts(owner_obj.get("owner"))
    
    # filter pre_queued_contacts so that it contains only single mobile number
    
    for pre_queued_contact in pre_queued_contacts:
      action = "create"
      for google_contact in google_contacts:
        if google_contact.get("mobile") and (pre_queued_contact.get("mobile") == google_contact.get("mobile")[1:] or pre_queued_contact.get("mobile") == google_contact.get("mobile")[3:]):
          action = "update"
          break
      contact = {"name":pre_queued_contact.get("contact_name"),"mobile":pre_queued_contact.get("mobile")}
      queue_contact(contact,action,pre_queued_contact.get("owner"))
      
      # update pre queued contact status to completed
      if frappe.db.get_value("Pre Queue Google Contacts", pre_queued_contact.get("name"), "status"):
        complete_query = """ update `tabPre Queue Google Contacts` set status='completed' where name='%s'""" % pre_queued_contact.get("name")
        frappe.db.sql(complete_query)
      else:
        vwrite("contact doesn't exist")

# clean_queue - removes duplicates in `tabQueue Google Contacts`
def clean_queue():
  clean_create_sql = """ select distinct mobile from `tabQueue Google Contacts` where action='create' order by creation desc """
  clean_create_res = frappe.db.sql(clean_create_sql)
  for record in clean_create_res:
    duplicate_sql = """ select name,creation from  `tabQueue Google Contacts` where action='create' and mobile='%s' order by creation desc """ % record
    duplicate_result = frappe.db.sql(duplicate_sql)
    delete_sql = """ delete from `tabQueue Google Contacts` where name <> '%s' and action='create' and mobile='%s'""" %(duplicate_result[0][0],record[0])
    frappe.db.sql(delete_sql)
  clean_update_sql = """ select distinct mobile from `tabQueue Google Contacts` where action='update' order by creation desc """
  clean_update_res = frappe.db.sql(clean_update_sql)
  for record in clean_update_res:
    duplicate_sql = """ select name,creation from  `tabQueue Google Contacts` where action='update' and mobile='%s' order by creation desc """ % record
    duplicate_result = frappe.db.sql(duplicate_sql)
    delete_sql = """ delete from `tabQueue Google Contacts` where name <> '%s' and action='update' and mobile='%s'""" %(duplicate_result[0][0],record[0])
    frappe.db.sql(delete_sql)
  # clearing prequeue
  clean_create_sql = """ select distinct mobile from `tabPre Queue Google Contacts` order by creation desc """
  clean_create_res = frappe.db.sql(clean_create_sql)
  for record in clean_create_res:
    duplicate_sql = """ select name,creation from  `tabPre Queue Google Contacts` where mobile='%s' order by creation desc """ % record
    duplicate_result = frappe.db.sql(duplicate_sql)
    delete_sql = """ delete from `tabPre Queue Google Contacts` where name <> '%s' and mobile='%s'""" %(duplicate_result[0][0],record[0])
    frappe.db.sql(delete_sql)


# create/update queued contacts in google
@frappe.whitelist()
def process_queued_contacts():
  clean_queue()
  google_peoples_api_limit = 10
  queued_contacts = frappe.get_all('Queue Google Contacts',
		filters={"status":"queued"},
		fields = ["name", "contact_name", "mobile", "action", "status", "owner"],
    order_by = 'modified asc',
		limit_page_length = google_peoples_api_limit)
  for queued_contact in queued_contacts:
    people_service = get_access_to_account(queued_contact.get("owner"))
    if queued_contact.get("action") == 'create':
      contactToCreate = {"names":[{"givenName":queued_contact.get("contact_name")}],"phoneNumbers":[{"value":queued_contact.get("mobile")}]}
      createdContact = people_service.people().createContact(body=contactToCreate).execute()
    else:
      contact_result = get_contact_by_number(queued_contact.get("mobile"),queued_contact.get("owner"))
      if contact_result:
        etag = contact_result.get("etag")
        resourceName = contact_result.get("resourceName")
        contactToUpdate = {"names":[{"givenName":queued_contact.get("contact_name")}],"etag":etag}
        updatedContact = people_service.people().updateContact(resourceName=resourceName,updatePersonFields="names",body=contactToUpdate).execute()
    
    # update queued contact status to completed
    if frappe.db.get_value("Queue Google Contacts", queued_contact.get("name"), "status"):
      complete_query = """ update `tabQueue Google Contacts` set status='completed' where name='%s'""" % queued_contact.get("name")
      frappe.db.sql(complete_query)
    else:
      vwrite("contact doesn't exist")

# add contact to pre-queue
def pre_queue_contact(contact,owner="Administrator"):
  if contact.get("name")[-3:].upper()=='_NF':
    contact_name = contact.get("name").replace("_NF","")+"_NF"
  else:
    contact_name = contact.get("name")
  try:
    pre_queue_rec = frappe.get_doc({
			"doctype": "Pre Queue Google Contacts",
			"contact_name" : contact_name,
			"mobile": contact.get("mobile"),
      "owner":owner
		})
    pre_queue_rec.flags.ignore_mandatory = True
    pre_queue_rec.save(ignore_permissions=True)
    frappe.db.commit()

  except Exception, e:
    vwrite("Exception raised in pre_queue_contact for %s" % contact.get("mobile"))
    vwrite(e)
    vwrite(contact)

# add contact to queue
def queue_contact(contact,action,owner="Administrator"):
  if contact.get("name")[-3:].upper()=='_NF':
    contact_name = contact.get("name").replace("_NF","")+"_NF"
  else:
    contact_name = contact.get("name")
  try:
    queue_rec = frappe.get_doc({
			"doctype": "Queue Google Contacts",
			"contact_name" : contact_name,
			"mobile": contact.get("mobile"),
			"action": action,
      "owner": owner
		})
    queue_rec.flags.ignore_mandatory = True
    queue_rec.save(ignore_permissions=True)
    frappe.db.commit()

  except Exception, e:
    vwrite("Exception raised in queue_contact for %s" % action)
    vwrite(e.message)
    vwrite(contact)

# fetch all contacts
def fetch_contacts(owner="Administrator"):
  people_service = get_access_to_account(owner)
  contacts_query = people_service.people().connections().list(resourceName='people/me', pageSize=2000, personFields='names,phoneNumbers')
  contacts_result = contacts_query.execute()
  contacts = []
  for contact in contacts_result.get("connections"):
    try:
      if "names" in contact and "phoneNumbers" in contact:
        name = contact.get("names")[0].get("displayName")
        mobile = contact.get("phoneNumbers")[0].get("canonicalForm")
        contacts.append({"resourceName":contact.get("resourceName"),"name":name,"mobile":mobile})
    except Exception, e:
      vwrite("Exception raised in fetch_contacts")
      vwrite(e.message)
      vwrite(contact)
  return contacts

# fetch contact by mobile number
def get_contact_by_number(number,owner="Administrator"):
  number = number[-10:]
  contacts = fetch_contacts()
  resourceName = None
  for contact in contacts:
    mobile_formatted = ""
    if contact.get("mobile"):
      mobile_formatted = contact.get("mobile")[-10:]
      # mobile_formatted = contact.get("mobile")[3:len(contact.get("mobile"))]
    if(contact.get("mobile")==number or mobile_formatted==number):
      resourceName = contact.get("resourceName")
  if resourceName:
    people_service = get_access_to_account(owner)
    contact_query = people_service.people().get(resourceName=resourceName,personFields="names,phoneNumbers")
    contact_result = contact_query.execute()
    return contact_result
# create new contact
# format: contact = {"name":"contact name","mobile":"1234567890"}
# usage:
# contact = {"name":"Contact Name","mobile":"1234567890"}
# create_contact(contact)
def create_contact(contact,owner):
  #gist_write("in create_contact")
  queue_contact(contact,"create",owner)
  return True

# update contact (condition: where mobile='%s')
# will update contact based on mobile number
# usage:
# contact = {"name":"Updated Name","mobile":"1234567890"}
# update_contact(contact)
def update_contact(contact,owner):
  queue_contact(contact,"update",owner)
  return True

@frappe.whitelist()
def create_contact_if_not_exists(mobile,lead_name=None,owner="Administrator"):
  if not lead_name:
    lead_name = mobile
  contact = get_contact_by_number(mobile)
  if not contact:
    new_contact = {"name":lead_name,"mobile":mobile}
    try:
      create_contact(new_contact,owner)
    except Exception, e:
      vwrite("Exception raised in create_contact_if_not_exists for contact: %s (%s)" % (mobile,lead_name))
      vwrite(e.message)
