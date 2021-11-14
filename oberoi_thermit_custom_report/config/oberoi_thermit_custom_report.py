from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
	    {
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "Debtors Report",
					"doctype": "Sales Order"				}
			]
		}
    ]