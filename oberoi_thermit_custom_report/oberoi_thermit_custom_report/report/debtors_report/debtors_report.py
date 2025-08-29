# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cstr
from erpnext.stock.utils import get_stock_balance

COLUMN_INDEX = {
    "sales_order": 0,
    "customer_group": 1,
    "business_line": 2,
    "customer_name": 3,
    "opening_debit_balance": 4,
    "opening_credit_balance": 5,
    "warehouse_details": 6,
    "warehouse_value": 7,
    "pi_details": 8,
    "total_pi_amount": 9,
    "si_details": 10,
    "total_si_amount": 11,
    "total_pi_receivables": 12,
    "total_si_receivables": 13,
    "total_receivables_claimed": 14,
    "total_receivables_unclaimed": 15,
    "balance_to_claim": 16,
    "total_payment_received": 17,
    "payment_entry_link": 18,
    "balance_to_receive": 19,
    "actual_balance_to_receive": 20,
    "warehouse": 21,
    "sales_order_end": 22,
    "delivery_total": 23
}

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
    
    # Build date conditions for each document type
    pi_date_condition = ""
    payment_date_condition = ""
    transfer_date_condition = ""
    si_date_condition = ""
    dn_date_condition = ""
    
    if filters.get("date"):
        pi_date_condition = "AND pi.posting_date <= %(date)s"
        payment_date_condition = "AND posting_date <= %(date)s"
        transfer_date_condition = "AND ptf.date <= %(date)s"
        si_date_condition = "AND posting_date <= %(date)s"
        dn_date_condition = "AND posting_date <= %(date)s"
    
    sql_query = """SELECT so.name AS 'sales_order',
       so.customer_group AS 'customer_group',
       so.business_line AS 'business_line',
       so.customer_name AS 'customer_name',
       '' AS 'opening_debit_balance',
       '' AS 'opening_credit_balance',
       'Click Here' AS 'warehouse_details',
       '' AS 'amount',
       'Click Here' AS 'pi_details',
    (
        IFNULL((
            SELECT SUM(pi.total_including_tax)
            FROM `tabProforma Invoice` pi
            WHERE pi.docstatus = 1
            AND pi.sales_order = so.name
            AND pi.date_of_equipment_set_receipt is null 
            """ + pi_date_condition + """
            AND (
                pi.is_equipment_set_security != 1
                OR (
                    pi.is_equipment_set_security = 1
                    AND (
                        SELECT IFNULL(SUM(paid_amount), 0)
                        FROM `tabPayment Entry`
                        WHERE proforma_invoice = pi.name
                        AND docstatus = 1
                        """ + payment_date_condition + """
                    ) < pi.total_including_tax
                )
            )
        ), 0) 
        - 
        IFNULL((
            SELECT SUM(ptf.amount)
            FROM `tabPayment Transfer From One Order To Another` ptf
            WHERE ptf.from_sales_order = so.name
            AND ptf.docstatus = 1
            """ + transfer_date_condition + """
        ), 0)
    ) AS `total_pi_amount`,
       'Click Here' AS 'si_details',
  (SELECT sum(grand_total)
   FROM `tabSales Invoice`
   WHERE docstatus=1
     AND sales_order=so.name
     """ + si_date_condition + """) AS 'total_si_amount',
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
       so.name AS 'sales_order_end',

  (SELECT sum(dn.grand_total)
   FROM `tabDelivery Note` AS dn
   WHERE dn.docstatus=1
     AND dn.sales_order=so.name
     AND dn.invoice_sending_with_material='NO'
     """ + dn_date_condition + """
     AND NOT EXISTS
       (SELECT si.name
        FROM `tabSales Invoice` AS si
        INNER JOIN `tabSales Invoice Item` AS sii on si.name=sii.parent
        WHERE sii.delivery_note=dn.name and si.docstatus=1)) AS 'delivery_total'
FROM `tabSales Order` AS so
WHERE so.docstatus<>2 """ + conditions
    
    sales_order_data = frappe.db.sql(sql_query, filters, as_list=1)
    get_other_details(sales_order_data, filters)
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
    if filters.get("date"):
        conditions += " and so.transaction_date <= %(date)s"
    return conditions


def get_other_details(order_data, filters):
    for order in order_data:
        items = frappe.get_doc("Sales Order", order[0]).items
        warehouse_balance = get_warehouse_balance_qty(order[0], items)
        opening_debit,opening_credit = get_opening_balance(order[0], filters)
        compliance_total = get_complience_entry_total(order[0], filters)
        order[4]= opening_debit
        order[5]= opening_credit
        order[7] = warehouse_balance
        order[11] = flt(order[11], 0) + flt(order[23],0)

        if flt(order[9], 0) > 0:
            order[12] = order[9] - flt(order[11], 0)  # Total PI receivables
        else:
            order[12] = 0  # Total PI receivables
        order[13] = order[11]  # Total SI receivables
        # Total Receivables (Claimed)
        order[14] = flt(order[12], 0) + flt(order[13], 0) + flt(order[4],0) + flt(compliance_total, 0)
        # Total Receivables (Including Unclaimed)
        order[15] = flt(order[11], 0) + warehouse_balance + flt(order[4],0) - flt(order[5],0) + flt(compliance_total, 0)
        order[16] = flt(order[15], 0) - flt(order[14], 0)  # Balance to Claim
        order[17] = get_payment_details(order, filters)  # Total Payment Received
        if order[17]:
            # Balance To receive As per Payment Terms
            order[19] = order[14] - order[17]
            # Actual Balance to Receive (Incl Unclaimed)
            order[20] = order[15] - order[17]
        else:
            order[19] = order[14]  # Balance To receive As per Payment Terms
            order[20] = order[15]  # Actual Balance to Receive (Incl Unclaimed)

def get_complience_entry_total(sales_order, filters):
    date_condition = ""
    if filters.get("date"):
        date_condition = "and date <= %s"
    
    query = """select sum(amount) from `tabCompliances Related Entry` 
               where docstatus=1 and sales_order=%s """ + date_condition
    
    if filters.get("date"):
        totals = frappe.db.sql(query, (sales_order, filters.get("date")))
    else:
        totals = frappe.db.sql(query, sales_order)
    
    if totals and totals[0][0]:
        return totals[0][0]
    return 0

def get_warehouse_balance_qty(order, items):
    '''get billing warehouse value which is linked with sales order'''

    warehouses = frappe.db.sql("""SELECT name
FROM `tabWarehouse`
WHERE sales_order=%s
  AND is_group=0 AND name like %s""", (order,'Billing%'), as_dict=1,debug=1)

    total_balance_value = 0
    if len(warehouses) >= 1:
        for item in items:
            if item.rate > 0:
                for warehouse in warehouses:
                    total_balance_value += flt(get_stock_balance(
                        item.item_code, warehouse.name)) * get_tax_rate(order,item.rate)
    return total_balance_value

def get_tax_rate(order,rate):
    tax = frappe.db.sql("""select rate from `tabSales Taxes and Charges` where parent=%s and charge_type='On Net Total' and included_in_print_rate=0""",order,as_dict=1)
    if len(tax) >= 1:
        if tax[0].rate:
            rate = rate + rate * flt(tax[0].rate)/100
    return rate

def get_payment_details(order, filters):
    date_condition = ""
    if filters.get("date"):
        date_condition = "AND p.posting_date <= %s"
    
    query = """SELECT SUM(
    IFNULL(p.paid_amount, 0)
    + (SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry Deduction` WHERE parent = p.name)
    + IFNULL(p.sd_amount, 0)
    + IFNULL(p.sd_amount_1_percent, 0)
) AS payment_amount
FROM `tabPayment Entry` AS p
WHERE p.sales_order = %s
  AND p.docstatus = 1
  AND p.payment_type = 'Receive'
  AND p.name NOT LIKE %s
  AND p.name NOT LIKE %s
  """ + date_condition + """
  AND (
    p.proforma_invoice IS NULL
    OR EXISTS (
      SELECT 1 FROM `tabProforma Invoice` pi
      WHERE pi.name = p.proforma_invoice
      AND (
        pi.is_equipment_set_security != 1
        OR (
          pi.is_equipment_set_security = 1
          AND pi.date_of_equipment_set_receipt IS NOT NULL
        )
      )
    )
  )"""
    
    if filters.get("date"):
        order_data = frappe.db.sql(query, (order[0],'PEEMD%','PESDEMD%', filters.get("date")), as_dict=1)
    else:
        order_data = frappe.db.sql(query, (order[0],'PEEMD%','PESDEMD%'), as_dict=1)
    
    if len(order_data) >= 1:
        payment_amount = flt(order_data[0].payment_amount)
        payment_amount = payment_amount + flt(get_transfer_amount_deduct(order[0], filters))
        payment_amount = payment_amount + flt(get_transfer_amount_add(order[0], filters))

        return payment_amount
    else:
        return 0


def get_transfer_amount_deduct(sales_order, filters):
    date_condition = ""
    if filters.get("date"):
        date_condition = "and date <= %s"
    
    query = """select sum(amount)*-1 as 'amount' from `tabPayment Transfer From One Order To Another` 
               where from_sales_order=%s and docstatus=1 """ + date_condition
    
    if filters.get("date"):
        payment_transfer = frappe.db.sql(query, (sales_order, filters.get("date")), as_dict=1)
    else:
        payment_transfer = frappe.db.sql(query, sales_order, as_dict=1)
    
    if len(payment_transfer) >= 1:
        return payment_transfer[0].amount
    else:
        return 0

def get_transfer_amount_add(sales_order, filters):
    date_condition = ""
    if filters.get("date"):
        date_condition = "and date <= %s"
    
    query = """select sum(amount) as 'amount' from `tabPayment Transfer From One Order To Another` 
               where to_sales_order=%s and docstatus=1 """ + date_condition
    
    if filters.get("date"):
        payment_transfer = frappe.db.sql(query, (sales_order, filters.get("date")), as_dict=1)
    else:
        payment_transfer = frappe.db.sql(query, sales_order, as_dict=1)
    
    if len(payment_transfer) >= 1:
        return payment_transfer[0].amount
    else:
        return 0

def get_opening_balance(order, filters):
    date_condition = ""
    if filters.get("date"):
        date_condition = "AND jv.posting_date <= %s"
    
    query = """SELECT ifnull(sum(jva.debit),0) as 'debit',ifnull(sum(jva.credit),0) as 'credit'
FROM `tabJournal Entry` AS jv
INNER JOIN `tabJournal Entry Account` AS jva ON jv.name=jva.parent
WHERE jva.party_type='Customer'
  AND jv.customer_group='Private'
  AND jv.is_opening='Yes'
  AND jv.docstatus=1
  AND jv.sales_order=%s
  """ + date_condition
    
    if filters.get("date"):
        opening_data = frappe.db.sql(query, (order, filters.get("date")), as_dict=1)
    else:
        opening_data = frappe.db.sql(query, order, as_dict=1)
    
    opening_debit = opening_credit = 0
    if len(opening_data) >= 1:
        if opening_data[0].debit:
            opening_debit = flt(opening_data[0].debit,0)
        if opening_data[0].credit:
            opening_credit = flt(opening_data[0].credit,0)
    return opening_debit,opening_credit
