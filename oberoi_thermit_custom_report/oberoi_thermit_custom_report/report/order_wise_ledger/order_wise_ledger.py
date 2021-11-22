# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    if filters.get('soa_as_per_pi') == 1:
        columns[6]["hidden"] = 1
        columns[3]["hidden"] = 1
        data = get_data(filters)
        # return columns, data
    if filters.get('soa_as_per_si') == 1:
        columns[5]["hidden"] = 1
        columns[2]["hidden"] = 1
        data = get_data(filters)
    return columns, data



def get_columns(filters=None):
    return [
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 150
        },
        {
            "label": _("PI No"),
            "fieldname": "pi_no",
            "fieldtype": "Link",
            "options": "Proforma Invoice",
            "width": 200
        },
        {
            "label": _("Invoice No"),
            "fieldname": "invoice_no",
            "fieldtype": "Link",
            "options": "Sales Invoice"
        },
        {
            "label": _("Payment Entry No"),
            "fieldname": "payment_entry_no",
            "fieldtype": "Link",
            "options": "Payment Entry",
            "width": 150
        },
        {
            "label": _("Payment Claimed in PI"),
            "fieldname": "payment_claimed_pi",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Payment Claimed in SI"),
            "fieldname": "payment_claimed_si",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Payment Received"),
            "fieldname": "payment_received",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Balance"),
            "fieldname": "balance",
            "fieldtype": "Currency",
            "width": 150
        }
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    if filters.get('soa_as_per_si') == 1 and filters.get('soa_as_per_pi') == 1:
        frappe.throw("SOA As Per SI/SOA As Per PI Select Only One")
    data = []
    if not filters.get('soa_as_per_si') == 1:
        proforma = get_proforma_invoice(conditions, filters)
        jv_debit = get_debit(filters)
        jv_credit = get_credit(filters)
        data.extend(proforma)
        data.extend(jv_debit)
        data.extend(jv_credit)
    if not filters.get('soa_as_per_pi') == 1:
        invoices = get_sales_incoice(conditions, filters)
        jv_debit = get_debit(filters)
        # jv_credit = get_credit(filters)
        data.extend(invoices)
        data.extend(jv_debit)
        # data.extend(jv_credit)
    pe_details = get_payment_entry(filters)
    data.extend(pe_details)
    final_data = sorted(data, key=lambda i: i['date'])
    return update_balance(final_data,filters)


def update_balance(data,filters):
    first = True
    last_balance = 0
    for row in data:
        if first:
            if filters.get('soa_as_per_si') == 1:
                row.balance = flt(row.payment_claimed_si, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
            elif filters.get('soa_as_per_pi') == 1:
                row.balance = flt(row.payment_claimed_pi, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
            else:
                row.balance = (flt(row.payment_claimed_pi, 0) - flt(row.payment_claimed_si, 0)
                            ) + flt(row.payment_claimed_si, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
            first = False
        else:
            if filters.get('soa_as_per_si') == 1:
                row.balance = last_balance + flt(row.payment_claimed_si, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
            elif filters.get('soa_as_per_pi') == 1:
                row.balance = last_balance + flt(row.payment_claimed_pi, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
            else:
                row.balance = last_balance + (flt(row.payment_claimed_pi, 0) - flt(
                    row.payment_claimed_si, 0)) + flt(row.payment_claimed_si, 0) - flt(row.payment_received, 0)
                last_balance = row.balance
    return data


def get_proforma_invoice(conditions, filters):
    proforma_invoice_details = frappe.db.sql(
        """select posting_date as 'date',sales_order,name as 'pi_no','' as 'invoice_no','' as 'payment_entry_no',grand_total_to_pay_now as 'payment_claimed_pi','' as 'payment_claimed_si','' as 'payment_received','' as 'balance' from `tabProforma Invoice` where docstatus<>2 %s""" % conditions, filters, as_dict=1)
    return proforma_invoice_details


def get_sales_incoice(conditions, filters):
    sales_invoice_details = frappe.db.sql(
        """select posting_date as 'date',sales_order,'' as 'pi_no',name as 'invoice_no','' as 'payment_entry_no','' as 'payment_claimed_pi',grand_total as 'payment_claimed_si','' as 'payment_received','' as 'balance' from `tabSales Invoice`where docstatus<>2 %s""" % conditions, filters, as_dict=1)
    return sales_invoice_details


def get_payment_entry(filters):
    conditions = get_conditions(filters, pe=True)
    pe_details = frappe.db.sql("""SELECT p.posting_date as 'date',p.sales_order as 'sales_order','' as 'pi_no','' as 'invoice_no',p.name as 'payment_entry_no','' as 'payment_claimed_pi','' as 'payment_claimed_si',sum(ifnull(p.paid_amount,0)+
             (SELECT ifnull(sum(amount),0)
              FROM `tabPayment Entry Deduction`
              WHERE parent=p.name)+ifnull(p.sd_amount,0)+ifnull(p.sd_amount_1_percent,0)) AS 'payment_received','' as 'balance'
FROM `tabPayment Entry` AS p
WHERE p.docstatus=1
  AND p.payment_type='Receive' %s group by p.name""" % conditions, filters, as_dict=1)
    return pe_details


def get_conditions(filters, pe=False):
    conditions = ""
    if pe:
        conditions += " and payment_type='Receive'"
    if filters.get('select_by') == "Customer":
        if pe:
            conditions += " and p.party_type='Customer' and p.party=%(selected)s"
        else:
            conditions += " and customer=%(selected)s"
    if filters.get('select_by') == "Sales Order":
        if pe:
            conditions += " and p.sales_order=%(selected)s"
        else:
            conditions += " and sales_order=%(selected)s"
    return conditions


def get_debit(filters):
    conditions = " and jva.debit>0 and jv.docstatus<>2"
    if filters.get('select_by') == "Customer":
        conditions += " and jva.party=%(selected)s"
    if filters.get('select_by') == "Sales Order":
        conditions += " and jv.sales_order=%(selected)s"
    fields = ""
    if filters.get("soa_as_per_si"):
        fields += "jv.posting_date as 'date',jv.sales_order,'' as 'pi_no',jv.name as 'invoice_no','' as 'payment_entry_no','' as 'payment_claimed_pi',jva.debit as 'payment_claimed_si','' as 'payment_received','' as 'balance'"
    if filters.get("soa_as_per_pi"):
        fields += "jv.posting_date as 'date',jv.sales_order,jv.name as 'pi_no','' as 'invoice_no','' as 'payment_entry_no',jva.debit as 'payment_claimed_pi','' as 'payment_claimed_si','' as 'payment_received','' as 'balance'"
    opening_data = frappe.db.sql(
        """SELECT {fields}
FROM `tabJournal Entry` AS jv
INNER JOIN `tabJournal Entry Account` AS jva ON jv.name=jva.parent
WHERE jva.party_type='Customer'
  AND jv.customer_group='Private'
  AND jv.is_opening='Yes' {conditions}""".format(fields=fields,conditions=conditions),filters, as_dict=1)
    return opening_data

def get_credit(filters):
    conditions = " and jva.credit>0 and jv.docstatus<>2"
    if filters.get('select_by') == "Customer":
        conditions += " and jva.party=%(selected)s"
    if filters.get('select_by') == "Sales Order":
        conditions += " and jv.sales_order=%(selected)s"
    fields = ""
    if filters.get("soa_as_per_si"):
        fields += "jv.posting_date as 'date',jv.sales_order,'' as 'pi_no','' as 'invoice_no',jv.name as 'payment_entry_no','' as 'payment_claimed_pi','' as 'payment_claimed_si',jva.credit as 'payment_received','' as 'balance'"
    if filters.get("soa_as_per_pi"):
        fields += "jv.posting_date as 'date',jv.sales_order,'' as 'pi_no','' as 'invoice_no',jv.name as 'payment_entry_no','' as 'payment_claimed_pi','' as 'payment_claimed_si',jva.credit as 'payment_received','' as 'balance'"
    opening_data = frappe.db.sql(
        """SELECT {fields}
FROM `tabJournal Entry` AS jv
INNER JOIN `tabJournal Entry Account` AS jva ON jv.name=jva.parent
WHERE jva.party_type='Customer'
  AND jv.customer_group='Private'
  AND jv.is_opening='Yes' {conditions}""".format(fields=fields,conditions=conditions),filters, as_dict=1)
    return opening_data