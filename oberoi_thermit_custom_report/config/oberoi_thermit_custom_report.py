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
					"doctype": "Sales Order",
					"is_query_report": True			
				},
				{
					"type": "report",
					"name": "Order Wise Ledger",
					"doctype": "Sales Order",
					"is_query_report": True			
				}
			]
		},
	    {
			"label": _("Transactions"),
			"items": [
                {
                    "type": "doctype",
                    "name": "Work Progress Entry",
                    "label": _("Work Progress Entry"),
                },
			]
		}
    ]