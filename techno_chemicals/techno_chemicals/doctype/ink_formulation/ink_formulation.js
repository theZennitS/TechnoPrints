// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ink Formulation", {
	setup: function(frm) {
		frm.set_query("item_to_produce", function() {
			return {
				filters: {
					is_stock_item: 1,
					include_item_in_manufacturing: 1
				}
			};
		});
	},

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

		// Update stock for all rows on refresh
		(frm.doc.items || []).forEach(row => {
			if (row.item_code && !row.available_stock_kg) {
				fetch_row_stock(frm, row.doctype, row.name, row.item_code);
			}
		});
	},

	shade_match_request: function(frm) {
		if (frm.doc.shade_match_request) {
			frappe.db.get_doc("Shade Match Request", frm.doc.shade_match_request).then(smr => {
				if (smr) {
					if (!frm.doc.formula_name) {
						frm.set_value("formula_name", smr.target_shade_name || smr.pantone_reference);
					}
					if (smr.commercial_item) {
						frm.set_value("item_to_produce", smr.commercial_item);
					}
				}
			});
		}
	},

	base_batch_size_kg: function(frm) {
		calculate_formulation_totals(frm);
	}
});

frappe.ui.form.on("Ink Formulation Item", {
	item_code: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.item_code) {
			frappe.model.set_value(cdt, cdn, "available_stock_kg", 0);
			return;
		}
		fetch_row_stock(frm, cdt, cdn, row.item_code);
	},
	percentage: function(frm, cdt, cdn) {
		calculate_formulation_totals(frm);
	},
	items_remove: function(frm) {
		calculate_formulation_totals(frm);
	}
});

function fetch_row_stock(frm, cdt, cdn, item_code) {
	frappe.call({
		method: "techno_chemicals.api.get_item_stock",
		args: { item_code: item_code },
		callback: function(r) {
			if (r.message !== undefined) {
				frappe.model.set_value(cdt, cdn, "available_stock_kg", flt(r.message));
			}
		}
	});
}

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
