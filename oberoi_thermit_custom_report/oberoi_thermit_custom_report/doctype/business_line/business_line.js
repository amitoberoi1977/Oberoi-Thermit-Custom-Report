// Copyright (c) 2025, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Business Line', {
	onload: function(frm) {
		frm.call({
			method:"get_series",
			doc:frm.doc,
			callback:function(r){
				frm.set_df_property('proforma_invoice_series', 'options', [''].concat(r.message.proforma_invoice_series));
			}
		})
	}
});
