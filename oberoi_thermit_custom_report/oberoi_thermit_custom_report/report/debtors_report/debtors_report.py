# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr
from erpnext.stock.utils import get_stock_balance


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters=None):
    return [
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 150
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "fieldtype": "Link",
            "options": "Customer Group",
            "width": 200
        },
        {
            "label": _("Business Line"),
            "fieldname": "business_line",
            "fieldtype": "Data"
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Opening Debit Balance"),
            "fieldname": "opening_debit_balance",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Opening Credit Balance"),
            "fieldname": "opening_credit_balance",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Warehouse Details"),
            "fieldname": "warehouse_details",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150
        },
        {
            "label": _("Warehouse Value"),
            "fieldname": "warehouse_value",
            "fieldtype": "HTML",
            "width": 150
        },
        {
            "label": _("PI Details"),
            "fieldname": "pi_details",
            "fieldtype": "Link",
            "options": "Proforma Invoice",
            "width": 250
        },
        {
            "label": _("Total PI Amount"),
            "fieldname": "total_pi_amount",
            "fieldtype": "Currency"
        },
        {
            "label": _("SI Details"),
            "fieldname": "si_details",
            "fieldtype": "Link",
            "options": "Sales Invoice"
        },
        {
            "label": _("Total SI Amount"),
            "fieldname": "total_si_amount",
            "fieldtype": "Currency"
        },
        {
            "label": _("Total PI receivables"),
            "fieldname": "total_pi_receivables",
            "fieldtype": "Currency"
        },
        {
            "label": _("Total SI receivables"),
            "fieldname": "total_si_receivables",
            "fieldtype": "Currency"
        },
        {
            "label": _("Total Receivables (Claimed)"),
            "fieldname": "total_receivables_claimed",
            "fieldtype": "Currency"
        },
        {
            "label": _("Total Receivables (Including Unclaimed)"),
            "fieldname": "total_receivables_unclaimed",
            "fieldtype": "Currency"
        },
        {
            "label": _("Balance to Claim"),
            "fieldname": "balance_to_claim",
            "fieldtype": "Currency"
        },
        {
            "label": _("Total Payment Received"),
            "fieldname": "total_payment_received",
            "fieldtype": "Currency"
        },
        {
            "label": _("Payment Details"),
            "fieldname": "payment_entry_link",
            "fieldtype": "Link",
            "options": "Payment Entry"
        },
        {
            "label": _("Balance To Receive As Per Payment Terms"),
            "fieldname": "balance_to_receive",
            "fieldtype": "Currency"
        },
        {
            "label": _("Actual Balance to Receive (Incl Unclaimed)"),
            "fieldname": "actual_balance_to_receive",
            "fieldtype": "Currency"
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Data",
            "hidden": 1
        },
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order_end",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 150
        }

    ]


def get_data(filters):
    conditions = get_conditions(filters)
    sales_order_data = frappe.db.sql("""SELECT so.name AS 'sales_order',
       so.customer_group AS 'customer_group',
       so.business_line AS 'business_line',
       so.customer_name AS 'customer_name',
       '' As 'opening_debit_balance',
       '' As 'opening_credit_balance',
       'Click Here' AS 'warehouse_details',
       '' AS 'amount',
       'Click Here' AS 'pi_details',

  (SELECT sum(grand_total_to_pay_now)
   FROM `tabProforma Invoice`
   WHERE docstatus=1
     AND sales_order=so.name) AS 'total_pi_amount',
       'Click Here' AS 'si_details',

  (SELECT sum(grand_total)
   FROM `tabSales Invoice`
   WHERE docstatus=1
     AND sales_order=so.name) AS 'total_si_amount',
       '' AS 'total_pi_receivable',
       '' AS 'total_si_receivable',
       '' AS 'total_receivable_claimed',
       '' AS 'total_receivable_unclaimed',
       '' AS 'balance_to_claim',
       '' AS 'total_payment_received',
	   'Click Here' AS 'payment_entry_link',
       '' AS 'balance_to_receive_as_per_terms',
       '' AS 'actual_balance_to_receive',

  (SELECT name
   FROM `tabWarehouse`
   WHERE sales_order=so.name
   LIMIT 1) AS 'warehouse',
    so.name AS 'sales_order_end'
FROM `tabSales Order` AS so
WHERE so.docstatus<>2 %s""" % conditions, filters, as_list=1)
    get_other_details(sales_order_data)
    return filter_final_data(filters, sales_order_data)


def filter_final_data(filters, order_data):
    '''apply additional filters'''
    data = []
    for order in order_data:
        if filters.get('actual_balnace_not_equal_zero'):
            if flt(order[16]) == 0 and flt(order[17]) == 0:
                continue
        if filters.get('actual_balnace_greater_than_zero'):
            if flt(order[16]) <= 0 and flt(order[17]) <= 0:
                continue
        data.append(order)
    return data


def get_conditions(filters):
    conditions = ""

    if filters.get("customer"):
        conditions += "and so.customer = %(customer)s"
    if filters.get("business_line"):
        conditions += "and so.business_line = %(business_line)s"
    if filters.get("sales_order"):
        conditions += " and so.name = %(sales_order)s"
    if filters.get("customer_group"):
        conditions += " and so.customer_group = %(customer_group)s"
    if filters.get("item"):
        conditions += " and soi.item_code = %(item)s"
    return conditions


def get_other_details(order_data):
    for order in order_data:
        items = frappe.get_doc("Sales Order", order[0]).items
        warehouse_balance = get_warehouse_balance_qty(order[0], items)
        opening_debit,opening_credit = get_opening_balance(order[0])
        order[4]= opening_debit
        order[5]= opening_credit
        order[7] = warehouse_balance

        if flt(order[9], 0) > 0:
            order[12] = order[9] - flt(order[11], 0)  # Total PI receivables
        else:
            order[12] = 0  # Total PI receivables
        order[13] = order[11]  # Total SI receivables
        # Total Receivables (Claimed)
        order[14] = flt(order[12], 0) + flt(order[13], 0) + flt(order[4],0)
        # Total Receivables (Including Unclaimed)
        order[15] = flt(order[11], 0) + warehouse_balance + flt(order[4],0) - flt(order[5],0)
        order[16] = flt(order[15], 0) - flt(order[14], 0)  # Balance to Claim
        order[17] = get_payment_details(order)  # Total Payment Received
        if order[17]:
            # Balance To receive As per Payment Terms
            order[19] = order[14] - order[17]
            # Actual Balance to Receive (Incl Unclaimed)
            order[20] = order[15] - order[17]
        else:
            order[19] = order[14]  # Balance To receive As per Payment Terms
            order[20] = order[15]  # Actual Balance to Receive (Incl Unclaimed)

def get_warehouse_balance_qty(order, items):
    '''get billing warehouse value which is linked with sales order'''

    warehouses = frappe.db.sql("""SELECT name
FROM `tabWarehouse`
WHERE sales_order=%s
  AND is_group=0""", order, as_dict=1)

    total_balance_value = 0
    if len(warehouses) >= 1:
        for item in items:
            if item.rate > 0:
                for warehouse in warehouses:
                    total_balance_value += flt(get_stock_balance(
                        item.item_code, warehouse.name)) * get_tax_rate(order,item.rate)
    return total_balance_value

def get_tax_rate(order,rate):
    tax = frappe.db.sql("""select rate from `tabSales Taxes and Charges` where parent=%s and charge_type='On Net Total'""",order,as_dict=1)
    if len(tax) >= 1:
        if tax[0].rate:
            rate = rate + rate * flt(tax[0].rate)/100
    return rate

def get_payment_details(order):
    order_data = frappe.db.sql("""SELECT sum(ifnull(p.paid_amount,0)+
             (SELECT ifnull(sum(amount),0)
              FROM `tabPayment Entry Deduction`
              WHERE parent=p.name)+ifnull(p.sd_amount,0)+ifnull(p.sd_amount_1_percent,0)) AS 'payment_amount'
FROM `tabPayment Entry` AS p
WHERE p.sales_order=%s
  AND p.docstatus=1
  AND p.payment_type='Receive'""", order[0], as_dict=1)
    if len(order_data) >= 1:
        return order_data[0].payment_amount
    else:
        return 0


def get_opening_balance(order):
    opening_data = frappe.db.sql(
        """SELECT ifnull(sum(jva.debit),0) as 'debit',ifnull(sum(jva.credit),0) as 'credit'
FROM `tabJournal Entry` AS jv
INNER JOIN `tabJournal Entry Account` AS jva ON jv.name=jva.parent
WHERE jva.party_type='Customer'
  AND jv.customer_group='Private'
  AND jv.is_opening='Yes'
  AND jv.sales_order=%s""", order, as_dict=1)
    opening_debit = opening_credit = 0
    if len(opening_data) >= 1:
        if opening_data[0].debit:
            opening_debit = flt(opening_data[0].debit,0)
        if opening_data[0].credit:
            opening_credit = flt(opening_data[0].credit,0)
    return opening_debit,opening_credit
