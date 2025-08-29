// Copyright (c) 2025, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Manager', {
	setup(frm) {
		frm.set_query("department", function() {
			return {
				filters: {
					"disabled": 0
				}
			};
		});
	},
});
