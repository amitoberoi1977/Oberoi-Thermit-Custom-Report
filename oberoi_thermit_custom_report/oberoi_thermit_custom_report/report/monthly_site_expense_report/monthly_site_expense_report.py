import frappe
from frappe.utils import getdate, flt
from collections import defaultdict

def execute(filters=None):
    columns = get_columns()
    data = []

    # Step 0: Get system-wide cut-off date
    cut_off_date = frappe.db.sql("""
        SELECT MIN(date_from)
        FROM `tabWork Progress Entry`
        WHERE docstatus = 1
    """)[0][0]

    if not cut_off_date:
        return columns, []

    cut_off_date = getdate(cut_off_date)

    grouped_data = defaultdict(lambda: {
        "revenue": 0,
        "imprest": 0,
        "site_expense": 0,
    })

    # Step 1: Collect WPE → Revenue
    wpe_entries = frappe.db.get_all(
        "Work Progress Entry",
        fields=[
            "order_no",
            "business_vertical",
            "date_from",
            "rate_of_item_in_sales_order",
            "no_of_welds"
        ],
        filters={
            "docstatus": 1,
            "date_from": [">=", cut_off_date]
        }
    )

    for row in wpe_entries:
        if not (row.order_no and row.date_from):
            continue

        key = (
            row.order_no,
            row.business_vertical,
            getdate(row.date_from).strftime("%b %Y")
        )

        grouped_data[key]["revenue"] += flt(row.rate_of_item_in_sales_order) * flt(row.no_of_welds)

    # Step 2: Collect Imprest (with cut-off in SQL)
    imprest_entries = frappe.db.sql("""
        SELECT 
            d.sales_order,
            d.amount_to_transfer,
            d.business_vertical,
            p.date_of_request_initiation
        FROM 
            `tabPayment Request Initiation Details` d
        JOIN 
            `tabPayment Request Initiation` p ON d.parent = p.name
        WHERE 
            d.reason_for_transfer = 'Imprest'
            AND d.sales_order IS NOT NULL
            AND p.date_of_request_initiation >= %s
            AND p.docstatus = 1
    """, (cut_off_date,), as_dict=True)

    for row in imprest_entries:
        key = (
            row.sales_order,
            row.business_vertical or "",
            getdate(row.date_of_request_initiation).strftime("%b %Y")
        )
        grouped_data[key]["imprest"] += flt(row.amount_to_transfer)

    # Step 3: Collect Site Expense (with cut-off in filters)
    site_expense_entries = frappe.db.get_all(
        "Skilled Additional Labor Fund Transfer",
        fields=["sales_order", "date", "total_amount_to_transfer", "business_line"],
        filters={
            "docstatus": 1,
            "date": [">=", cut_off_date]
        }
    )

    for row in site_expense_entries:
        if not (row.sales_order and row.date):
            continue

        key = (
            row.sales_order,
            row.business_line or "",
            getdate(row.date).strftime("%b %Y")
        )
        grouped_data[key]["site_expense"] += flt(row.total_amount_to_transfer)

    # Final Output
    for (so, bv, my), values in grouped_data.items():
        revenue = values["revenue"]
        net_imprest = values["imprest"] - values["site_expense"]
        percentage = round((net_imprest / revenue) * 100, 2) if revenue else 0

        data.append([
            so,
            bv,
            my,
            revenue,
            net_imprest,
            f"{percentage} %"
        ])

    return columns, data


def get_columns():
    return [
        {"label": "Sales Order", "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 140},
        {"label": "Business Vertical", "fieldname": "business_vertical", "fieldtype": "Data", "width": 140},
        {"label": "Month/Year", "fieldname": "month_year", "fieldtype": "Data", "width": 120},
        {"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 120},
        {"label": "Imprest", "fieldname": "imprest", "fieldtype": "Currency", "width": 120},
        {"label": "%age Imprest", "fieldname": "percentage_imprest", "fieldtype": "Data", "width": 120},
    ]
