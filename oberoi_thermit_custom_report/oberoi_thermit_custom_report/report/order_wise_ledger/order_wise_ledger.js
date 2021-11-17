

frappe.query_reports["Order Wise Ledger"] = {
    "filters": [
        {
            "fieldname": "select_by",
            "label": __("Select By "),
            "fieldtype": "Link",
            "options": "DocType",
            "reqd":1,
            get_query: () => {
                return {
                    filters: [
                        ['name', 'in', ['Customer', 'Sales Order']]
                    ]

                };
            }
        },
        {
            "fieldname": "selected",
            "label": __("Select"),
            "fieldtype": "DynamicLink",
            "options": "select_by",
            "reqd":1
        },
        {
            "fieldname": "soa_as_per_si",
            "label": __("SOA As Per SI"),
            "fieldtype": "Check"
        },
        {
            "fieldname": "soa_as_per_pi",
            "label": __("SOA As Per PI"),
            "fieldtype": "Check"
        }
    ]


}