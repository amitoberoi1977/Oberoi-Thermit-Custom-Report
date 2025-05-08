# -*- coding: utf-8 -*-
# Copyright (c) 2025, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowtime,cint,flt


class WorkProgressEntry(Document):
	def validate(self):
		self.validate_warehouse_field()
		self.set_item_details()

	def set_item_details(self):
		item_doc = frappe.get_doc("Item",self.item)
		self.is_stock_item = cint(item_doc.get("is_stock_item")) or 0
		self.has_batch_no = cint(item_doc.get("has_batch_no")) or 0

	def validate_warehouse_field(self):
		if self.bom_no:
			if not self.warehouse:
				frappe.throw("Warehouse is mandatory")
		if not self.bom_no:
			if not self.employee:
				frappe.throw("Employee is mandatory")
	
	def on_submit(self):
		if not self.bom_no and not self.is_stock_item:
			proforma_invoice_naming_series = frappe.db.get_value("Business Line",self.business_vertical,"proforma_invoice_series",self.name)
			if not proforma_invoice_naming_series:
				frappe.throw("Please set proforma naming series in business line")
			items = [
				{
					"item_code": self.item,
					"qty": self.no_of_welds,
					"rate": self.rate_of_item_in_sales_order
				}
			]
			create_proforma_invoice_custom(self.order_no,items,self.date_to,proforma_invoice_naming_series,self.name)
		elif self.bom_no:
			source_warehouse = self.warehouse
			target_warehouse = frappe.db.get_value("Warehouse",{"warehouse_type":"Billing","sales_order":self.order_no},"name")
			if not target_warehouse:
				frappe.throw("Billing Warehouse Not exists for the selected sales order")
			stock_entry_doc = frappe.get_doc(dict(
				doctype = "Stock Entry",
				stock_entry_type = "Manufacture",
				purpose = "Manufacture",
				company = "Oberoi Thermit Pvt. Ltd.",
				set_posting_time = 1,
				posting_date = self.date_to,
				posting_time = nowtime(),
				use_multi_level_bom=0,
				from_bom = 1,
				bom_no = self.bom_no,
				warehouse_entry = self.name,
				fg_completed_qty = self.no_of_welds,
				from_warehouse = source_warehouse,
				to_warehouse = target_warehouse
			))
			stock_entry_doc.get_items()
			for row in stock_entry_doc.items:
				if row.item_code == self.item:
					row.batch_no = self.batch_no
					break
			stock_entry_doc.flags.ignore_permissions = True
			stock_entry_doc.submit()
		elif self.employee:
			target_warehouse = frappe.db.get_value("Warehouse",{"warehouse_type":"Billing","sales_order":self.order_no},"name")
			if not target_warehouse:
				frappe.throw("Billing Warehouse Not exists for the selected sales order")
			stock_entry_doc = frappe.get_doc(dict(
				doctype = "Stock Entry",
				stock_entry_type = "Material Receipt",
				purpose = "Material Receipt",
				warehouse_entry = self.name,
				set_posting_time = 1,
				posting_time = nowtime(),
				posting_date = self.date_to,
				fg_completed_qty = self.no_of_welds,
				to_warehouse = target_warehouse,
				employee = self.employee
			))
			stock_entry_doc.append("items",dict(
				item_code = self.item,
				qty = self.no_of_welds,
				rate = self.rate_of_item_in_sales_order,
				batch_no = self.batch_no
			))
			stock_entry_doc.flags.ignore_permissions = True
			stock_entry_doc.submit()
	
	def on_cancel(self):
		if not self.is_stock_item:
			proforma_invoice_name = frappe.db.get_value("Proforma Invoice",{"work_progress_entry":self.name},"name")
			proforma_invoice_doc = frappe.get_doc("Proforma Invoice",proforma_invoice_name)
			proforma_invoice_doc.cancel()
		else:
			stock_entry_name = frappe.db.get_value("Stock Entry",{"warehouse_entry":self.name},"name")
			stock_entry_doc = frappe.get_doc("Stock Entry",stock_entry_name)
			stock_entry_doc.cancel()


@frappe.whitelist()
def get_order_items(order_no):
	items = []
	order_doc = frappe.get_doc("Sales Order",order_no)
	for row in order_doc.items:
		items.append(row.item_code)
	return items

@frappe.whitelist()
def get_order_item_rates(order_no,item):
	rates = []
	order_doc = frappe.get_doc("Sales Order",order_no)
	for row in order_doc.items:
		if row.item_code == item:
			rates.append(row.rate)
	return rates

@frappe.whitelist()
def get_bom_no(item):
	bom_no = frappe.db.get_value("BOM",{"is_active":1,"item":item},"name")
	if bom_no:
		return bom_no
	else:
		return False
	
def create_proforma_invoice_custom(sales_order_name, custom_items,date,naming_series,work_progress_entry):
	"""
	custom_items = [
		{
			"item_code": "ITEM-001",
			"qty": 5,
			"rate": 100
		},
		...
	]
	"""

	so = frappe.get_doc("Sales Order", sales_order_name)
	
	pi = frappe.new_doc("Proforma Invoice")
	pi.naming_series = naming_series
	pi.sales_order = sales_order_name
	pi.customer = so.customer
	pi.company = so.company
	pi.currency = so.currency
	pi.selling_price_list = so.selling_price_list
	pi.price_list_currency = so.price_list_currency
	pi.payment_terms_template = so.payment_terms_template
	pi.posting_date = date
	pi.posting_time = nowtime()
	pi.payment_type = "Payment after execution"

	actual_amount = 0
	total = 0

	for row in custom_items:
		item_doc = frappe.get_doc("Item",row.get("item_code"))
		item = pi.append("items", {})
		item.item_code = row.get("item_code")
		item.item_name = item_doc.get("item_name")
		item.uom = item_doc.get("stock_uom")
		item.qty = row.get("qty")
		item.rate = row.get("rate")
		item.percentage_payment = 100  # Fixed at 100%

		item.amount = flt(item.qty or 0) * flt(item.rate or 0)
		total += flt(item.amount)
		actual_amount += flt(item.amount)

	inspection = 0
	freight = 0
	tax_amount = ((actual_amount + inspection + freight) * 18) / 100
	pi.taxation_rate = "18%"
	pi.total_tax_amount = tax_amount
	pi.total_including_tax = total + tax_amount + inspection + freight
	pi.previous_amount_pending = 0
	pi.grand_total_to_pay_now = pi.total_including_tax
	pi.work_progress_entry = work_progress_entry

	pi.insert(ignore_permissions=True)
	pi.submit()

	return pi.name