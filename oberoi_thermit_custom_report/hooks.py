# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "oberoi_thermit_custom_report"
app_title = "Oberoi Thermit Custom Report"
app_publisher = "Bhavesh Maheshwari"
app_description = "Oberoi Thermit Custom Report"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "maheshwaribhavesh95863@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/oberoi_thermit_custom_report/css/oberoi_thermit_custom_report.css"
# app_include_js = "/assets/oberoi_thermit_custom_report/js/oberoi_thermit_custom_report.js"

# include js, css files in header of web template
# web_include_css = "/assets/oberoi_thermit_custom_report/css/oberoi_thermit_custom_report.css"
# web_include_js = "/assets/oberoi_thermit_custom_report/js/oberoi_thermit_custom_report.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "oberoi_thermit_custom_report.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "oberoi_thermit_custom_report.install.before_install"
# after_install = "oberoi_thermit_custom_report.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "oberoi_thermit_custom_report.notifications.get_notification_config"

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
# 		"oberoi_thermit_custom_report.tasks.all"
# 	],
# 	"daily": [
# 		"oberoi_thermit_custom_report.tasks.daily"
# 	],
# 	"hourly": [
# 		"oberoi_thermit_custom_report.tasks.hourly"
# 	],
# 	"weekly": [
# 		"oberoi_thermit_custom_report.tasks.weekly"
# 	]
# 	"monthly": [
# 		"oberoi_thermit_custom_report.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "oberoi_thermit_custom_report.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "oberoi_thermit_custom_report.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "oberoi_thermit_custom_report.task.get_dashboard_data"
# }

fixtures = [
    {"dt": "Custom Field", "filters": [["Custom Field","name","in",["Stock Entry-employee","Stock Entry-warehouse_entry"]]]},
    {
        "doctype": "Custom Script",
        "filters": [
            [
                "name",
                "in",
                [
                    "Payment Entry-Client"
                ],
            ],
        ],
    },
    {
        "doctype": "DocType",
        "filters": [
            [
                "name",
                "in",
                [
                    "Proforma Invoice",
                ],
            ],
        ],
    }
]