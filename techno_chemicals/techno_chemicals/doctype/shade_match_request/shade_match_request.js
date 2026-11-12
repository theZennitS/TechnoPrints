// Copyright (c) 2026, Techno Print Chemicals Pvt Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shade Match Request", {
	refresh: function(frm) {
		if (!frm.is_new()) {
			// Action 1: Create or view Finished Item
			if (!frm.doc.commercial_item) {
				frm.add_custom_button(__("Create Target Item"), function() {
					frappe.confirm(
						__("Create a new Finished Ink Item in Item Master from this shade?"),
						function() {
							frm.call({
								doc: frm.doc,
								method: "create_finished_item",
								freeze: true,
								freeze_message: __("Creating Item in Master..."),
								callback: function(r) {
									if (r.message) {
										frappe.show_alert({
											message: __("Item {0} created successfully!", [r.message]),
											indicator: "green"
										});
										frm.reload_doc();
									}
								}
							});
						}
					);
				}).addClass("btn-primary");
			}

			// Action 2 & 3: Create Formulation and Benchmark
			if (frm.doc.commercial_item) {
				frm.add_custom_button(__("Create Formulation"), function() {
					frappe.new_doc("Ink Formulation", {
						shade_match_request: frm.doc.name,
						item_to_produce: frm.doc.commercial_item,
						formula_name: frm.doc.target_shade_name,
						base_batch_size_kg: 100.0
					});
				}, __("Actions"));

				frm.add_custom_button(__("Create Benchmark"), function() {
					frappe.new_doc("Ink Benchmark", {
						shade_match_request: frm.doc.name,
						item: frm.doc.commercial_item,
						customer: frm.doc.customer,
						target_substrate: frm.doc.target_substrate,
						benchmark_name: (frm.doc.target_shade_name || "Shade") + " Quality Benchmark"
					});
				}, __("Actions"));
			}
		}
	}
});
