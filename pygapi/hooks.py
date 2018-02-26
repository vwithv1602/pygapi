# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "pygapi"
app_title = "Pygapi"
app_publisher = "vavcoders"
app_description = "Python library for Google APIs"
app_icon = "octicon octicon-file-directory"
app_color = "#3498db"
app_email = "vavcoders@gmail.com"
app_license = "license.txt"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pygapi/css/pygapi.css"
# app_include_js = "/assets/pygapi/js/pygapi.js"

# include js, css files in header of web template
# web_include_css = "/assets/pygapi/css/pygapi.css"
# web_include_js = "/assets/pygapi/js/pygapi.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "pygapi.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "pygapi.install.before_install"
# after_install = "pygapi.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pygapi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pygapi.tasks.all"
# 	],
# 	"daily": [
# 		"pygapi.tasks.daily"
# 	],
# 	"hourly": [
# 		"pygapi.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pygapi.tasks.weekly"
# 	]
# 	"monthly": [
# 		"pygapi.tasks.monthly"
# 	]
# }
scheduler_events = {
	"hourly": [
		"pygapi.pygcontacts.process_queued_contacts"
	]
}
# Testing
# -------

# before_tests = "pygapi.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pygapi.event.get_events"
# }

