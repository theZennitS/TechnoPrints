// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ink Formulation", {
	refresh: function(frm) {
		if (!frm.is_new() && frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Create ERPNext BOM"), function() {
				frm.call({
					doc: frm.doc,
					method: "create_bom",
					freeze: true,
					freeze_message: __("Generating Production BOM..."),
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__("BOM {0} generated successfully!", [r.message]));
							frm.reload_doc();
						}
					}
				});
			}, __("Actions"));
		}
	},
	base_batch_size_kg: function(frm) {
		calculate_formulation_totals(frm);
	}
});

frappe.ui.form.on("Ink Formulation Item", {
	percentage: function(frm, cdt, cdn) {
		calculate_formulation_totals(frm);
	},
	items_remove: function(frm) {
		calculate_formulation_totals(frm);
	}
});

function calculate_formulation_totals(frm) {
	let total_pct = 0.0;
	let base_size = flt(frm.doc.base_batch_size_kg) || 100.0;

	(frm.doc.items || []).forEach(row => {
		let pct = flt(row.percentage);
		total_pct += pct;
		row.quantity_kg = flt((pct / 100.0) * base_size, 3);
	});

	frm.set_value("total_percentage", total_pct);
	frm.refresh_field("items");
}
