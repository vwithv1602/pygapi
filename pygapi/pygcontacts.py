import httplib2
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from globalconstants import *
import frappe
from .vlog import vwrite
from datetime import datetime

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
# google_settings = frappe.get_doc("Google Account Setup")
FLOW = OAuth2WebServerFlow(
    # client_id=google_settings.client_id,
    # client_secret=google_settings.client_secret,
    client_id=YOUR_CLIENT_ID,
    client_secret=YOUR_CLIENT_SECRET,
    scope=YOUR_SCOPE,
    user_agent=YOUR_APPLICATION_NAME_AND_APPLICATION_VERSION)

# If the Credentials don't exist or are invalid, run through the
# installed application flow. The Storage object will ensure that,
# if successful, the good Credentials will get written back to a
# file.
storage = Storage('/home/vamc/frappe-bench/apps/pygapi/pygapi/info.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = tools.run_flow(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and
# authorize it with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API.
people_service = build(serviceName='people', version='v1', http=http)

# fetch all contacts
def fetch_contacts():
  contacts_query = people_service.people().connections().list(resourceName='people/me', pageSize=2000, personFields='names,phoneNumbers')
  contacts_result = contacts_query.execute()
  contacts = []
  for contact in contacts_result.get("connections"):
    try:
      name = contact.get("names")[0].get("displayName")
      mobile = contact.get("phoneNumbers")[0].get("canonicalForm")
      if not mobile:
        mobile = contact.get("phoneNumbers")[0].get("value")
      contacts.append({"resourceName":contact.get("resourceName"),"name":name,"mobile":mobile})
    except Exception, e:
      exceptionflag = 1
      # vwrite("Exception raised in fetch_contacts")
      # vwrite(e.message)
      # vwrite(contact)
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
  contactToCreate = {"names":[{"givenName":contact.get("name")}],"phoneNumbers":[{"value":contact.get("mobile")}]}
  createdContact = people_service.people().createContact(body=contactToCreate).execute()
  return createdContact

# update contact (condition: where mobile='%s')
# will update contact based on mobile number
# usage:
# contact = {"name":"Updated Name","mobile":"1234567890"}
# update_contact(contact)
def update_contact(contact):
  contact_result = get_contact_by_number(contact.get("mobile"))
  if contact_result:
    etag = contact_result.get("etag")
    resourceName = contact_result.get("resourceName")
    contactToUpdate = {"names":[{"givenName":contact.get("name")}],"etag":etag}
    updatedContact = people_service.people().updateContact(resourceName=resourceName,updatePersonFields="names",body=contactToUpdate).execute()
  return updatedContact

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
      exceptionflag = 1
      # vwrite("Exception raised in create_contact_if_not_exists for contact: %s (%s)" % (mobile,lead_name))
      # vwrite(e.message)

# export_leads_to_google_contacts - Create google contact for leads (past 1 day)
def export_leads_to_google_contacts():
  latest_leads_query = """ select lead_name,mobile_no from `tabLead` where creation > NOW() - INTERVAL 2 DAY """
  for lead in frappe.db.sql(latest_leads_query, as_dict=1):
    lead_name = lead.get("lead_name")
    mobile = lead.get("mobile_no")
    if mobile:
      create_contact_if_not_exists(mobile,lead_name)
  # For each lead: call create_contact_if_not_exists(mobile,lead_name)

@frappe.whitelist()
def test():
  vwrite("In test")
  contact = get_contact_by_number("07013011867")
  vwrite(contact)
  return contact