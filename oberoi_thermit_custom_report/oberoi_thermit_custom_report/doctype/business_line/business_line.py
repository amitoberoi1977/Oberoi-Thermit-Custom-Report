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

    def validate(self):
        self.update_report_to()
    
    def update_report_to(self):
        if self.reporting_manager or self.external_reporting_manager:
            employees = frappe.get_all("Employee",filters={"business_vertical": self.name,"is_team_leader":1},fields=["name","reports_to","external_report_to"])
            for employee in employees:
                manager_update = False
                if self.reporting_manager and employee.get("reports_to") != self.reporting_manager:
                    manager_update = True
                if self.external_reporting_manager and employee.get("external_report_to") != self.external_reporting_manager:
                    manager_update = True
                if manager_update:
                    employee_doc = frappe.get_doc("Employee", employee.name)
                    if self.reporting_manager:
                        employee_doc.reports_to = self.reporting_manager
                        employee_doc.external_report_to = None
                        employee_doc.external_reporting_manager = 0
                    if self.external_reporting_manager:
                        employee_doc.reports_to = None
                        employee_doc.external_report_to = self.external_reporting_manager
                        employee_doc.external_reporting_manager = 1
                    employee_doc.save(ignore_permissions=True)