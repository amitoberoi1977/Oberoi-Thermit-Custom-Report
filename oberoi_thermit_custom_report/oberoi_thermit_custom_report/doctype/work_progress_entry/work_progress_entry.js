// Copyright (c) 2025, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Progress Entry', {
	refresh: function(frm) {
		frm.trigger("set_order_item")
		frm.trigger("set_item_rate")
		if(frm.doc.docstatus == 1){
			if(frm.doc.is_stock_item == 1) {
				frm.add_custom_button(__('View Stock Entry'), function () {
					frappe.route_options = {"warehouse_entry": frm.doc.name};
					frappe.set_route("List", "Stock Entry");
				}, __("View Entry"));
			}
			if(frm.doc.is_stock_item == 0) {
				frm.add_custom_button(__('View Proforma Invoice'), function () {
					frappe.route_options = {"work_progress_entry": frm.doc.name};
					frappe.set_route("List", "Proforma Invoice");
				}, __("View Entry"));
			}
		}
		if(frm.doc.business_line_manager_approved == 1) {
			frm.set_read_only()
		}
	},
	setup: function(frm) {
		frm.set_query("order_no", function () {
			return {
				filters: [
					["business_line", "=", frm.doc.business_vertical],
					["docstatus","=",1]
				]
			}
		});
		frm.set_query("warehouse", function () {
			return {
				filters: [
					["sales_order", "=", frm.doc.order_no]
				]
			}
		});
		frm.set_query("batch_no", function () {
			return {
				filters: [
					["item", "=", frm.doc.item]
				]
			}
		});
	},
	order_no: function(frm) {
		frm.trigger("set_order_item")
	},
	set_order_item: function(frm) {
		if(frm.doc.order_no) {
			frappe.call({
				method:"oberoi_thermit_custom_report.oberoi_thermit_custom_report.doctype.work_progress_entry.work_progress_entry.get_order_items",
				args:{"order_no":frm.doc.order_no},
				async:true,
				callback:function(r){
					frm.set_df_property('item', 'options', [''].concat(r.message));
				}
			})
		}
	},
	item: function(frm) {
		frm.trigger("set_item_rate")
		frm.trigger("set_bom_no")
	},
	set_bom_no: function(frm,cdt,cdn) {
		if(frm.doc.item) {
			frappe.call({
				method:"oberoi_thermit_custom_report.oberoi_thermit_custom_report.doctype.work_progress_entry.work_progress_entry.get_bom_no",
				args:{"item":frm.doc.item},
				callback:function(r){
					if(r.message) {
						frappe.model.set_value(cdt,cdn,"bom_no",r.message)
					}else{
						frappe.model.set_value(cdt,cdn,"bom_no","")
					}
				}
			})
		}
	},
	set_item_rate: function(frm) {
		if(frm.doc.item) {
			frappe.call({
				method:"oberoi_thermit_custom_report.oberoi_thermit_custom_report.doctype.work_progress_entry.work_progress_entry.get_order_item_rates",
				args:{"order_no":frm.doc.order_no,"item":frm.doc.item},
				async:true,
				callback:function(r){
					frm.set_df_property('rate_of_item_in_sales_order', 'options', [''].concat(r.message));
				}
			})
		}
	}
});
