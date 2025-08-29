# Copyright (c) 2013, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt

def execute(filters=None):
    columns = get_columns()
    data = []

    # Step 0: Fetch cut-off date (earliest WPE date_from)
    cut_off_date = frappe.db.sql("""
        SELECT MIN(date_from)
        FROM `tabWork Progress Entry`
        WHERE docstatus = 1
    """)[0][0]

    if not cut_off_date:
        return columns, []

    cut_off_date = getdate(cut_off_date)

    # Step 1: Fetch all WPE entries >= cut-off date
    wpe_entries = frappe.db.get_all(
        "Work Progress Entry",
        fields=[
            "order_no",
            "business_vertical",
            "date_from",
            "date_to",
            "rate_of_item_in_sales_order",
            "no_of_welds"
        ],
        filters={
            "docstatus": 1,
            "date_from": [">=", cut_off_date]
        }
    )

    for wpe in wpe_entries:
        if not wpe.order_no or not (wpe.date_from and wpe.date_to):
            continue

        date_from = getdate(wpe.date_from)
        date_to = getdate(wpe.date_to)
        sales_order = wpe.order_no

        # Revenue = Rate × Quantity
        revenue = flt(wpe.rate_of_item_in_sales_order) * flt(wpe.no_of_welds)

        # Step 2: Imprest total between date range and after cut-off
        imprest_total = frappe.db.sql("""
            SELECT SUM(d.amount_to_transfer)
            FROM `tabPayment Request Initiation Details` d
            JOIN `tabPayment Request Initiation` p ON d.parent = p.name
            WHERE d.sales_order = %s
              AND d.reason_for_transfer = 'Imprest'
              AND p.docstatus = 1
              AND p.date_of_request_initiation BETWEEN %s AND %s
              AND p.date_of_request_initiation >= %s
        """, (sales_order, date_from, date_to, cut_off_date))[0][0] or 0

        # Step 3: Site Expense total between date range and after cut-off
        site_expense_total = frappe.db.sql("""
            SELECT SUM(total_amount_to_transfer)
            FROM `tabSkilled Additional Labor Fund Transfer`
            WHERE sales_order = %s
              AND docstatus = 1
              AND date BETWEEN %s AND %s
              AND date >= %s
        """, (sales_order, date_from, date_to, cut_off_date))[0][0] or 0

        # Net Imprest & % Calculation
        net_imprest = flt(imprest_total) - flt(site_expense_total)
        percentage = round((net_imprest / revenue) * 100, 2) if revenue else 0

        data.append([
            sales_order,
            wpe.business_vertical,
            date_from,
            date_to,
            revenue,
            net_imprest,
            f"{percentage} %"
        ])

    return columns, data


def get_columns():
    return [
        {"label": "Sales Order", "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 140},
        {"label": "Business Vertical", "fieldname": "business_vertical", "fieldtype": "Data", "width": 140},
        {"label": "Date From", "fieldname": "date_from", "fieldtype": "Date", "width": 100},
        {"label": "Date To", "fieldname": "date_to", "fieldtype": "Date", "width": 100},
        {"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": "Imprest", "fieldname": "imprest", "fieldtype": "Currency", "width": 120},
        {"label": "%age Imprest", "fieldname": "percentage_imprest", "fieldtype": "Data", "width": 120},
    ]
