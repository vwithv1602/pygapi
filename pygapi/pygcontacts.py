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
    client_id=google_settings.client_id,
    client_secret=google_settings.client_secret,
    scope=YOUR_SCOPE,
    user_agent=YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION)

# If the Credentials don't exist or are invalid, run through the
# installed application flow. The Storage object will ensure that,
# if successful, the good Credentials will get written back to a
# file.
storage = Storage('/home/frappe/frappe-bench/apps/pygapi/pygapi/info.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = tools.run_flow(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and
# authorize it with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API.
people_service = build(serviceName='people', version='v1', http=http)

# create/update queued contacts in google
def process_queued_contacts():
  google_peoples_api_limit = 90
  queued_contacts = frappe.get_all('Queue Google Contacts',
		filters={"status":"queued"},
		fields = ["name", "contact_name", "mobile", "action", "status"],
    order_by = 'modified asc',
		limit_page_length = google_peoples_api_limit)
  for queued_contact in queued_contacts:
    if queued_contact.get("action") == 'create':
      contactToCreate = {"names":[{"givenName":queued_contact.get("contact_name")}],"phoneNumbers":[{"value":queued_contact.get("mobile")}]}
      createdContact = people_service.people().createContact(body=contactToCreate).execute()
    else:
      contact_result = get_contact_by_number(queued_contact.get("mobile"))
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

# add contact to queue
def queue_contact(contact,action):
  try:
    queue_rec = frappe.get_doc({
			"doctype": "Queue Google Contacts",
			"contact_name" : contact.get("name"),
			"mobile": contact.get("mobile"),
			"action": action
		})
    queue_rec.flags.ignore_mandatory = True
    queue_rec.insert()
    frappe.db.commit()

  except Exception, e:
    vwrite("Exception raised in queue_contact for %s" % action)
    vwrite(e.message)
    vwrite(contact)

# fetch all contacts
def fetch_contacts():
  contacts_query = people_service.people().connections().list(resourceName='people/me', pageSize=2000, personFields='names,phoneNumbers')
  contacts_result = contacts_query.execute()
  contacts = []
  for contact in contacts_result.get("connections"):
    try:
      name = contact.get("names")[0].get("displayName")
      mobile = contact.get("phoneNumbers")[0].get("canonicalForm")
      contacts.append({"resourceName":contact.get("resourceName"),"name":name,"mobile":mobile})
    except Exception, e:
      vwrite("Exception raised in fetch_contacts")
      vwrite(e.message)
      vwrite(contact)
  return contacts

# fetch contact by mobile number
def get_contact_by_number(number):
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
    contact_query = people_service.people().get(resourceName=resourceName,personFields="names,phoneNumbers")
    contact_result = contact_query.execute()
    return contact_result
# create new contact
# format: contact = {"name":"contact name","mobile":"1234567890"}
# usage:
# contact = {"name":"Contact Name","mobile":"1234567890"}
# create_contact(contact)
def create_contact(contact):
  #gist_write("in create_contact")
  queue_contact(contact,"create")
  return True

# update contact (condition: where mobile='%s')
# will update contact based on mobile number
# usage:
# contact = {"name":"Updated Name","mobile":"1234567890"}
# update_contact(contact)
def update_contact(contact):
  queue_contact(contact,"update")
  return True

@frappe.whitelist()
def create_contact_if_not_exists(mobile,lead_name=None):
  if not lead_name:
    lead_name = mobile
  contact = get_contact_by_number(mobile)
  if not contact:
    new_contact = {"name":lead_name,"mobile":mobile}
    try:
      create_contact(new_contact)
    except Exception, e:
      vwrite("Exception raised in create_contact_if_not_exists for contact: %s (%s)" % (mobile,lead_name))
      vwrite(e.message)