# -*- coding: utf-8 -*-
# Copyright (c) 2025, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BusinessLine(Document):
    def get_series(self):
        proforma_invoice_series = (
            frappe.get_meta("Proforma Invoice")
            .get_field("naming_series")
            .options.split("\n")
        )
        return dict(proforma_invoice_series=proforma_invoice_series)
